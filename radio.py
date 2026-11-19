import array
import functools
import math
import os
import random

import pygame

from controle import (
    LARGURA,
    ALTURA,
    COR_FUNDO,
    COR_PAINEL,
    COR_PAINEL_CLARO,
    COR_BORDA,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    COR_DOURADO,
    COR_VERDE,
    COR_VERMELHO,
    COR_SOMBRA,
    fonte,
    desenhar_texto,
    desenhar_painel,
    _calcular_escala,
    _converter_posicao,
)


# ============================================================
# MINIGAME DO RÁDIO
#
# Controles:
# - Setas (ou A / D) ou segurar os botões < > para girar o botão.
# - Roda do mouse para ajuste fino.
# - ESC ou VOLTAR: sai sem gastar a tentativa do dia.
# ============================================================

CAMINHOS_SONS = {
    "musica": r"C:\Users\maria\Downloads\musica_radio.mp3",
    "chiado": r"C:\Users\maria\Downloads\chiado_radio.mp3",
    "buzina": r"C:\Users\maria\Downloads\som_navio.mp3",
}

FREQ_MIN = 88.0
FREQ_MAX = 108.0
TOLERANCIA = 0.25      # distância para o sinal começar a "travar"
ZONA_SINAL = 2.5       # distância em que o sinal começa a aparecer
TEMPO_TRAVA = 0.9      # segundos com o sinal firme para revelar

CANAL_CHIADO = 1
CANAL_RESULTADO = 2
CANAL_EFEITOS = 3

RESULTADOS = ("chiado", "musica", "embarcacao")

TEXTOS = {
    "chiado": {
        "nome": "ESTÁTICA",
        "comentario": (
            "Nada além de chiado... Esse rádio está cada vez pior. "
            "Por um instante, achei que havia uma voz por trás da "
            "estática, mas deve ser só cansaço."
        ),
    },
    "musica": {
        "nome": "MÚSICA",
        "comentario": (
            "Uma música! Faz tempo que não ouço algo assim por aqui. "
            "Por alguns minutos, o farol pareceu menos silencioso."
        ),
    },
    "embarcacao": {
        "nome": "EMBARCAÇÃO",
        "comentario": (
            "Isso foi a buzina de uma embarcação, e parecia perto. "
            "Melhor manter o farol aceso. Quem está lá fora precisa "
            "dele para voltar."
        ),
    },
}


# ============================================================
# SONS
# ============================================================

_sons = None


def _montar_som(valores):
    iniciado = pygame.mixer.get_init()

    if iniciado is None:
        return None

    _, formato, canais = iniciado

    if formato != -16:
        return None

    dados = array.array("h")

    for v in valores:
        amostra = int(max(-1.0, min(1.0, v)) * 32767)
        for _ in range(canais):
            dados.append(amostra)

    return pygame.mixer.Sound(buffer=dados.tobytes())


def _gerar_chiado():
    frequencia = pygame.mixer.get_init()[0]
    valores = [
        random.uniform(-1.0, 1.0) * 0.5
        for _ in range(int(frequencia * 1.5))
    ]
    return _montar_som(valores)


def _gerar_clique():
    frequencia = pygame.mixer.get_init()[0]
    total = int(frequencia * 0.03)
    valores = []

    for i in range(total):
        t = i / frequencia
        decaimento = 1.0 - i / total
        v = (
            math.sin(2 * math.pi * 180 * t) * 0.6
            + random.uniform(-1.0, 1.0) * 0.4
        ) * decaimento
        valores.append(v * 0.7)

    return _montar_som(valores)


def _gerar_bip():
    frequencia = pygame.mixer.get_init()[0]
    total = int(frequencia * 0.14)
    valores = [
        math.sin(2 * math.pi * 1000 * i / frequencia)
        * (1.0 - i / total) * 0.35
        for i in range(total)
    ]
    return _montar_som(valores)


def _carregar_arquivo(nome):
    caminho = CAMINHOS_SONS.get(nome)

    if caminho is None or not os.path.exists(caminho):
        return None

    try:
        return pygame.mixer.Sound(caminho)
    except pygame.error as erro:
        print(f"Erro ao carregar {caminho}: {erro}")

    return None

def _carregar_ou_gerar(nome, gerador):
    som = _carregar_arquivo(nome)

    if som is not None:
        return som

    return gerador()


def carregar_sons_radio():
    global _sons

    if _sons is not None:
        return

    _sons = {}

    if pygame.mixer.get_init() is None:
        return

    _sons["chiado"] = _carregar_ou_gerar("chiado", _gerar_chiado)
    _sons["clique"] = _carregar_ou_gerar("clique", _gerar_clique)
    _sons["bip"] = _carregar_ou_gerar("bip", _gerar_bip)
    _sons["musica"] = _carregar_arquivo("musica")
    _sons["buzina"] = _carregar_arquivo("buzina")

    for nome in ("musica", "buzina"):
        if _sons[nome] is None:
            print(f"Aviso: som '{nome}' não encontrado: {CAMINHOS_SONS[nome]}")


def _tocar_canal(indice, som, loops=0, volume=1.0):
    if som is None or pygame.mixer.get_init() is None:
        return

    canal = pygame.mixer.Channel(indice)
    canal.play(som, loops=loops)
    canal.set_volume(max(0.0, min(1.0, volume)))


def _volume_canal(indice, volume):
    if pygame.mixer.get_init() is None:
        return

    pygame.mixer.Channel(indice).set_volume(max(0.0, min(1.0, volume)))


def _parar_canal(indice):
    if pygame.mixer.get_init() is None:
        return

    pygame.mixer.Channel(indice).stop()


def _tocar_efeito(nome):
    _tocar_canal(CANAL_EFEITOS, _sons.get(nome), 0, 0.6)


def _som_do_resultado(resultado):
    if resultado == "musica":
        return _sons.get("musica")

    if resultado == "embarcacao":
        return _sons.get("buzina")

    return None


def _iniciar_sons(estado):
    _tocar_canal(CANAL_CHIADO, _sons.get("chiado"), -1, 0.6)

    # O SOM DO RESULTADO COMEÇA BAIXINHO E SOBE CONFORME O SINAL
    som = _som_do_resultado(estado["resultado"])

    if som is not None:
        _tocar_canal(CANAL_RESULTADO, som, -1, 0.0)


def _som_revelacao(estado):
    resultado = estado["resultado"]
    som = _som_do_resultado(resultado)

    if som is not None:
        _parar_canal(CANAL_RESULTADO)
        _tocar_canal(
            CANAL_RESULTADO,
            som,
            -1 if resultado == "musica" else 0,
            1.0
        )

    _tocar_efeito("bip")


def parar_sons_radio():
    for canal in (CANAL_CHIADO, CANAL_RESULTADO, CANAL_EFEITOS):
        _parar_canal(canal)


# ============================================================
# ESTADO E LÓGICA
# ============================================================

def criar_estado_radio():
    carregar_sons_radio()

    resultado = random.choice(RESULTADOS)
    alvo = round(random.uniform(FREQ_MIN + 2.0, FREQ_MAX - 2.0), 1)

    inicio = alvo
    while abs(inicio - alvo) < 5.0:
        inicio = round(random.uniform(FREQ_MIN, FREQ_MAX), 1)

    estado = {
        "fase": "sintonizando",
        "resultado": resultado,
        "alvo": alvo,
        "freq": inicio,
        "sinal": 0.0,
        "trava": 0.0,
        "travando": False,
        "tempo_giro": 0.0,
        "direcao": 0,
        "inicio_revelado": 0,
        "pular_texto": False,
        "ultimo_tick": pygame.time.get_ticks(),
        "botao_esq": pygame.Rect(1262, 630, 80, 70),
        "botao_dir": pygame.Rect(1578, 630, 80, 70),
        "botao_sair": pygame.Rect(1440, 915, 240, 60),
    }

    _calcular_sinal(estado)
    _iniciar_sons(estado)

    return estado


def _calcular_sinal(estado):
    distancia = abs(estado["freq"] - estado["alvo"])
    estado["sinal"] = max(0.0, 1.0 - distancia / ZONA_SINAL)
    return distancia


def _mover_frequencia(estado, delta):
    antes = estado["freq"]
    estado["freq"] = max(FREQ_MIN, min(FREQ_MAX, antes + delta))

    # UM "CLIQUE" A CADA 0,5 MHz
    if int(estado["freq"] * 2) != int(antes * 2):
        _tocar_efeito("clique")


def _ler_direcao(estado, janela):
    teclas = pygame.key.get_pressed()

    esquerda = teclas[pygame.K_LEFT] or teclas[pygame.K_a]
    direita = teclas[pygame.K_RIGHT] or teclas[pygame.K_d]

    if pygame.mouse.get_pressed()[0]:

        pos = _converter_posicao(janela, pygame.mouse.get_pos())

        if estado["botao_esq"].collidepoint(pos):
            esquerda = True

        elif estado["botao_dir"].collidepoint(pos):
            direita = True

    return int(bool(direita)) - int(bool(esquerda))


def _caracteres_visiveis(estado):
    total = len(TEXTOS[estado["resultado"]]["comentario"])

    if estado["pular_texto"]:
        return total

    passado = (
        pygame.time.get_ticks() - estado["inicio_revelado"] - 600
    )

    return max(0, min(total, int(passado / 25)))


def _texto_completo(estado):
    total = len(TEXTOS[estado["resultado"]]["comentario"])
    return _caracteres_visiveis(estado) >= total


def tratar_evento_radio(estado, evento, janela):
    # Retorna "sair" quando o jogador deve voltar ao farol.

    if estado["fase"] == "revelado":

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "sair"

        confirmou = (
            evento.type == pygame.KEYDOWN
            and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE
            )
        ) or (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
        )

        if confirmou:

            if _texto_completo(estado):
                return "sair"

            estado["pular_texto"] = True

        return None

    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
        return "sair"

    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

        pos = _converter_posicao(janela, evento.pos)

        if estado["botao_sair"].collidepoint(pos):
            return "sair"

    elif evento.type == getattr(pygame, "MOUSEWHEEL", -1):

        _mover_frequencia(estado, evento.y * 0.1)

    return None


def atualizar_radio(estado, janela):
    # Retorna o resultado ("chiado", "musica" ou "embarcacao")
    # uma única vez, no instante em que ele é revelado.

    agora = pygame.time.get_ticks()
    dt = min((agora - estado["ultimo_tick"]) / 1000.0, 0.1)
    estado["ultimo_tick"] = agora

    if estado["fase"] == "revelado":

        if estado["resultado"] == "chiado":
            estado["sinal"] = random.uniform(0.05, 0.35)
            _volume_canal(CANAL_CHIADO, 0.6)

        else:
            _volume_canal(CANAL_CHIADO, 0.04)

        return None

    direcao = _ler_direcao(estado, janela)
    estado["direcao"] = direcao

    if direcao != 0:

        estado["tempo_giro"] += dt

        # COMEÇA DEVAGAR E ACELERA ENQUANTO O BOTÃO ESTÁ PRESSIONADO
        velocidade = 0.8 + 4.0 * min(estado["tempo_giro"], 1.5) / 1.5

        _mover_frequencia(estado, direcao * velocidade * dt)

    else:

        estado["tempo_giro"] = 0.0

    distancia = _calcular_sinal(estado)

    if distancia <= TOLERANCIA:

        if not estado["travando"]:
            estado["travando"] = True
            _tocar_efeito("bip")

        estado["trava"] += dt

    else:

        estado["travando"] = False
        estado["trava"] = max(0.0, estado["trava"] - dt * 2)

    sinal = estado["sinal"]

    _volume_canal(CANAL_CHIADO, 0.08 + 0.55 * (1.0 - sinal))
    _volume_canal(CANAL_RESULTADO, 0.8 * sinal * sinal)

    if estado["trava"] >= TEMPO_TRAVA:

        estado["fase"] = "revelado"
        estado["freq"] = estado["alvo"]
        estado["sinal"] = 1.0
        estado["inicio_revelado"] = agora

        _som_revelacao(estado)

        return estado["resultado"]

    return None


# ============================================================
# DESENHO
# ============================================================

_cache = {}
_superficie = None


@functools.lru_cache(maxsize=None)
def _fonte_digital(tamanho):
    return pygame.font.SysFont(
        "consolas,couriernew,courier",
        tamanho,
        bold=True
    )


def _linhas_visor(tamanho):
    chave = ("linhas", tamanho)

    if chave not in _cache:

        camada = pygame.Surface(tamanho, pygame.SRCALPHA)

        for y in range(0, tamanho[1], 4):
            pygame.draw.line(
                camada,
                (0, 0, 0, 70),
                (0, y),
                (tamanho[0], y),
                1
            )

        _cache[chave] = camada

    return _cache[chave]


def _sombra_tela():
    if "sombra" not in _cache:

        camada = pygame.Surface((LARGURA, ALTURA))
        camada.fill((0, 0, 0))
        camada.set_alpha(170)
        _cache["sombra"] = camada

    return _cache["sombra"]


def _quebrar_linhas(texto, tamanho, largura_maxima):
    f = fonte(tamanho)
    linhas = []
    atual = ""

    for palavra in texto.split(" "):

        teste = palavra if not atual else atual + " " + palavra

        if f.size(teste)[0] <= largura_maxima:
            atual = teste

        else:
            if atual:
                linhas.append(atual)
            atual = palavra

    if atual:
        linhas.append(atual)

    return linhas


def _desenhar_neve(s, area, quantidade):
    for _ in range(quantidade):

        tamanho = random.choice((4, 6, 8))
        x = random.randint(area.x + 8, area.right - 8 - tamanho)
        y = random.randint(area.y + 8, area.bottom - 8 - tamanho)
        brilho = random.randint(70, 160)

        pygame.draw.rect(
            s,
            (brilho // 2, brilho, brilho // 2 + 10),
            (x, y, tamanho, tamanho)
        )


def _desenhar_alto_falante(s):
    area = pygame.Rect(200, 250, 560, 520)
    desenhar_painel(s, area, (28, 22, 40))

    for y in range(area.y + 40, area.bottom - 20, 44):
        for x in range(area.x + 40, area.right - 20, 44):
            pygame.draw.circle(s, (14, 11, 22), (x, y), 12)
            pygame.draw.circle(s, (70, 56, 92), (x, y), 12, 2)


def _desenhar_visor(s, estado):
    area = pygame.Rect(840, 250, 840, 240)

    pygame.draw.rect(s, COR_SOMBRA, area.move(6, 7), border_radius=8)
    pygame.draw.rect(s, (16, 36, 31), area, border_radius=8)

    # CHUVISCO: QUANTO MENOR O SINAL, MAIS CHUVISCO
    _desenhar_neve(s, area, int(900 * (1.0 - estado["sinal"]) ** 1.5))

    verde = (150, 255, 170)
    verde_escuro = (90, 170, 120)

    rotulo = "FM"

    if estado["fase"] == "revelado":
        rotulo = TEXTOS[estado["resultado"]]["nome"]

    desenhar_texto(
        s, rotulo, 22, (120, 220, 150),
        (area.x + 110, area.y + 30), True
    )

    # NÚMEROS DA FREQUÊNCIA
    digitos = _fonte_digital(120).render(
        f"{estado['freq']:.1f}", True, verde
    )
    retangulo = digitos.get_rect(center=(area.centerx - 40, area.y + 100))
    s.blit(digitos, retangulo)

    desenhar_texto(
        s, "MHz", 34, verde,
        (retangulo.right + 55, retangulo.bottom - 25), True
    )

    # ESCALA E PONTEIRO
    x0 = area.x + 60
    x1 = area.right - 60
    y_base = area.y + 195

    pygame.draw.line(s, verde_escuro, (x0, y_base), (x1, y_base), 2)

    total = int(FREQ_MAX - FREQ_MIN)

    for i in range(total + 1):

        x = int(x0 + (x1 - x0) * i / total)
        grande = i % 4 == 0

        pygame.draw.line(
            s, verde_escuro,
            (x, y_base), (x, y_base - (22 if grande else 12)), 2
        )

        if grande:
            desenhar_texto(
                s, str(int(FREQ_MIN) + i), 16, verde_escuro,
                (x, y_base + 18)
            )

    fracao = (estado["freq"] - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)
    xa = int(x0 + (x1 - x0) * fracao)

    pygame.draw.line(
        s, (235, 85, 85), (xa, y_base - 42), (xa, y_base + 6), 4
    )

    # LINHAS HORIZONTAIS DE TELA ANTIGA
    s.blit(_linhas_visor(area.size), area.topleft)

    pygame.draw.rect(s, COR_BORDA, area, 3, border_radius=8)


def _desenhar_indicador_sinal(s, estado):
    area = pygame.Rect(840, 520, 360, 250)
    desenhar_painel(s, area)

    desenhar_texto(
        s, "SINAL", 24, COR_TEXTO, (area.centerx, area.y + 35), True
    )

    sinal = estado["sinal"]
    acesas = 0 if sinal < 0.03 else min(8, math.ceil(sinal * 8))

    for i in range(8):

        altura = 20 + i * 10
        x = area.x + 33 + i * 38
        barra = pygame.Rect(x, area.y + 170 - altura, 28, altura)

        if i < acesas:
            cor = COR_VERMELHO if i < 3 else (
                COR_DOURADO if i < 6 else COR_VERDE
            )
        else:
            cor = (45, 38, 60)

        pygame.draw.rect(s, cor, barra)
        pygame.draw.rect(s, COR_SOMBRA, barra, 2)

    # BARRA DE "TRAVA" DO SINAL
    barra_trava = pygame.Rect(area.x + 33, area.y + 195, 294, 20)

    pygame.draw.rect(s, (20, 17, 29), barra_trava, border_radius=4)

    preenchido = int(
        (barra_trava.width - 6)
        * max(0.0, min(1.0, estado["trava"] / TEMPO_TRAVA))
    )

    if preenchido > 0:
        pygame.draw.rect(
            s, COR_VERDE,
            (barra_trava.x + 3, barra_trava.y + 3, preenchido,
             barra_trava.height - 6)
        )

    pygame.draw.rect(s, COR_BORDA, barra_trava, 2, border_radius=4)

    desenhar_texto(
        s, "TRAVANDO O SINAL", 16, COR_TEXTO_SUAVE,
        (area.centerx, area.y + 235)
    )


def _desenhar_seta(s, area, direcao, ativa):
    desenhar_painel(s, area, COR_PAINEL_CLARO)

    cor = COR_DOURADO if ativa else COR_TEXTO
    cx, cy = area.center

    if direcao < 0:
        pontos = [(cx + 14, cy - 18), (cx + 14, cy + 18), (cx - 16, cy)]
    else:
        pontos = [(cx - 14, cy - 18), (cx - 14, cy + 18), (cx + 16, cy)]

    pygame.draw.polygon(s, cor, pontos)


def _desenhar_botao_giratorio(s, estado):
    area = pygame.Rect(1240, 520, 440, 250)
    desenhar_painel(s, area)

    desenhar_texto(
        s, "SINTONIA", 24, COR_TEXTO, (area.centerx, area.y + 35), True
    )

    centro = (area.centerx, area.y + 145)
    raio = 68

    fracao = (estado["freq"] - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)
    giro = -150 + fracao * 300   # graus; 0 = apontando para cima

    # MARCAS AO REDOR DO BOTÃO
    for i in range(21):

        ang = math.radians(-90 - 150 + i * 15)

        p1 = (
            int(centro[0] + math.cos(ang) * (raio + 10)),
            int(centro[1] + math.sin(ang) * (raio + 10))
        )
        p2 = (
            int(centro[0] + math.cos(ang) * (raio + 18)),
            int(centro[1] + math.sin(ang) * (raio + 18))
        )

        pygame.draw.line(s, (110, 90, 135), p1, p2, 3)

    # CORPO DO BOTÃO
    pygame.draw.circle(s, COR_SOMBRA, (centro[0] + 5, centro[1] + 6), raio)
    pygame.draw.circle(s, (88, 70, 112), centro, raio)
    pygame.draw.circle(s, COR_BORDA, centro, raio, 4)

    ang_ponteiro = math.radians(-90 + giro)

    # PONTINHOS QUE GIRAM JUNTO COM O BOTÃO
    for i in range(8):

        ang = ang_ponteiro + math.radians(i * 45 + 22)

        pygame.draw.circle(
            s, (150, 128, 180),
            (int(centro[0] + math.cos(ang) * 48),
             int(centro[1] + math.sin(ang) * 48)),
            5
        )

    # PONTEIRO
    ponta = (
        int(centro[0] + math.cos(ang_ponteiro) * (raio - 12)),
        int(centro[1] + math.sin(ang_ponteiro) * (raio - 12))
    )

    pygame.draw.line(s, COR_DOURADO, centro, ponta, 8)
    pygame.draw.circle(s, (42, 33, 58), centro, 14)
    pygame.draw.circle(s, COR_DOURADO, centro, 14, 3)

    # BOTÕES < >
    _desenhar_seta(s, estado["botao_esq"], -1, estado["direcao"] < 0)
    _desenhar_seta(s, estado["botao_dir"], 1, estado["direcao"] > 0)

    desenhar_texto(
        s, "Setas, A/D ou segure os botões", 16, COR_TEXTO_SUAVE,
        (area.centerx, area.y + 232)
    )


def _mensagem(estado):
    if estado["travando"]:
        return "Sinal firme! Não mexa no botão.", COR_VERDE

    if estado["sinal"] > 0.6:
        return "Está quase lá. Ajuste devagar.", COR_TEXTO

    if estado["sinal"] > 0.15:
        return "Algo está surgindo no meio da estática...", COR_TEXTO

    return (
        "Só estática. Gire o botão para os lados até achar um sinal.",
        COR_TEXTO
    )


def _desenhar_revelacao(s, estado):
    s.blit(_sombra_tela(), (0, 0))

    painel = pygame.Rect(360, 300, 1200, 440)
    desenhar_painel(s, painel)

    dados = TEXTOS[estado["resultado"]]

    desenhar_texto(
        s, f"SINAL ENCONTRADO: {dados['nome']}", 36, COR_DOURADO,
        (painel.centerx, painel.y + 60), True
    )

    pygame.draw.line(
        s, COR_BORDA,
        (painel.x + 60, painel.y + 100),
        (painel.right - 60, painel.y + 100), 2
    )

    s.blit(
        fonte(22, True).render("FAROLEIRO", True, COR_TEXTO_SUAVE),
        (painel.x + 70, painel.y + 125)
    )

    # TEXTO DO FAROLEIRO, LETRA POR LETRA
    linhas = _quebrar_linhas(dados["comentario"], 30, 1060)
    restante = _caracteres_visiveis(estado)
    y = painel.y + 175
    f = fonte(30)

    for linha in linhas:

        if restante <= 0:
            break

        s.blit(
            f.render(linha[:restante], True, COR_TEXTO),
            (painel.x + 70, y)
        )

        restante -= len(linha) + 1
        y += 44

    rodape = (
        "ENTER  -  CONTINUAR"
        if _texto_completo(estado)
        else "ENTER  -  PULAR"
    )

    desenhar_texto(
        s, rodape, 20, COR_TEXTO_SUAVE,
        (painel.centerx, painel.bottom - 40)
    )


def _desenhar_tela(s, estado):
    s.fill(COR_FUNDO)

    for x in range(0, LARGURA, 64):
        pygame.draw.line(s, (25, 21, 37), (x, 0), (x, ALTURA), 1)

    for y in range(0, ALTURA, 64):
        pygame.draw.line(s, (25, 21, 37), (0, y), (LARGURA, y), 1)

    desenhar_painel(s, pygame.Rect(120, 55, 1680, 950))

    desenhar_texto(
        s, "RÁDIO DO FAROL", 48, COR_TEXTO, (LARGURA // 2, 125), True
    )
    desenhar_texto(
        s, "SINTONIZE A FREQUÊNCIA MANUALMENTE", 24, COR_DOURADO,
        (LARGURA // 2, 190), True
    )

    pygame.draw.line(s, COR_BORDA, (420, 225), (1500, 225), 3)

    _desenhar_alto_falante(s)
    _desenhar_visor(s, estado)
    _desenhar_indicador_sinal(s, estado)
    _desenhar_botao_giratorio(s, estado)

    # CAIXA DE MENSAGEM
    caixa = pygame.Rect(200, 800, 1480, 90)
    pygame.draw.rect(s, (27, 22, 40), caixa, border_radius=5)
    pygame.draw.rect(s, (91, 72, 112), caixa, 2, border_radius=5)

    if estado["fase"] == "sintonizando":
        texto, cor = _mensagem(estado)
    else:
        texto, cor = "Sinal encontrado!", COR_VERDE

    desenhar_texto(s, texto, 26, cor, caixa.center)

    # BOTÃO VOLTAR
    botao = estado["botao_sair"]
    desenhar_painel(s, botao, COR_PAINEL_CLARO)
    desenhar_texto(s, "VOLTAR", 22, COR_TEXTO, botao.center, True)

    desenhar_texto(
        s, "ESC  -  VOLTAR AO FAROL SEM GASTAR A TENTATIVA DE HOJE", 16,
        COR_TEXTO_SUAVE, (LARGURA // 2, 1035)
    )

    if estado["fase"] == "revelado":
        _desenhar_revelacao(s, estado)


def desenhar_radio(janela, estado):
    global _superficie

    if _superficie is None:
        _superficie = pygame.Surface((LARGURA, ALTURA))

    _desenhar_tela(_superficie, estado)

    _, x0, y0, largura_final, altura_final = _calcular_escala(janela)

    janela.fill((0, 0, 0))

    if (largura_final, altura_final) == (LARGURA, ALTURA):
        janela.blit(_superficie, (x0, y0))

    else:
        imagem = pygame.transform.smoothscale(
            _superficie,
            (largura_final, altura_final)
        )
        janela.blit(imagem, (x0, y0))