import math
import random

import pygame

from config import BRANCO, ROXO_CLARO
from controle import (
    LARGURA,
    ALTURA,
    COR_FUNDO,
    COR_BORDA,
    COR_TEXTO,
    COR_TEXTO_SUAVE,
    COR_DOURADO,
    COR_VERDE,
    COR_VERMELHO,
    fonte,
    desenhar_texto,
    desenhar_painel,
    _calcular_escala,
    _converter_posicao,
)
from radio import _montar_som


# ============================================================
# BEN: COMBATE COM ÁGUA BENTA E FINAL DO JOGO
# ============================================================

CAMINHO_BEN_BEM = r"C:\Users\maria\Downloads\ben_bem.png"
CAMINHO_BEN_MAL = r"C:\Users\maria\Downloads\ben_mal.png"
CAMINHO_IMAGEM_FIM = r"C:\Users\maria\Downloads\fim_de_jogo.jpeg"
CAMINHO_MUSICA_FIM = r"C:\Users\maria\Downloads\som_fim.mp3"

HITS_PARA_VENCER = 5
GOTAS_NO_FRASCO = 10
ALTURA_BEN_COMBATE = 400
DURACAO_VITORIA_MS = 3000
DURACAO_TRANSFORMACAO_MS = 3500

DURACAO_FADE_FIM_MS = 5000
DURACAO_ESCURECER_MS = 2500
MS_POR_LETRA = 55
TEXTO_FIM = "Agora você pode descansar meu filho..."

COR_AGUA = (130, 200, 240)


# ============================================================
# IMAGENS
# ============================================================

_imagens = {}
_cache_escala = {}
_cache = {}


def _carregar_imagem(chave, caminho, alpha=True):
    if chave in _imagens:
        return _imagens[chave]

    imagem = None

    try:
        imagem = pygame.image.load(caminho)
        imagem = imagem.convert_alpha() if alpha else imagem.convert()

    except (pygame.error, FileNotFoundError) as erro:
        print(f"Erro ao carregar imagem: {erro}")

    _imagens[chave] = imagem
    return imagem


def carregar_imagem_ben(tipo):
    caminho = CAMINHO_BEN_BEM if tipo == "bem" else CAMINHO_BEN_MAL
    return _carregar_imagem("ben_" + tipo, caminho)


def imagem_ben_escalada(tipo, altura):
    chave = (tipo, altura)

    if chave not in _cache_escala:

        imagem = carregar_imagem_ben(tipo)

        if imagem is None:
            _cache_escala[chave] = None

        else:
            largura = max(
                1,
                int(imagem.get_width() * altura / imagem.get_height())
            )
            _cache_escala[chave] = pygame.transform.smoothscale(
                imagem,
                (largura, altura)
            )

    return _cache_escala[chave]


def _sombra_tela():
    if "sombra" not in _cache:

        camada = pygame.Surface((LARGURA, ALTURA))
        camada.fill((0, 0, 0))
        camada.set_alpha(190)
        _cache["sombra"] = camada

    return _cache["sombra"]


# ============================================================
# SONS DO COMBATE (GERADOS POR CÓDIGO)
# ============================================================

_sons = None


def _carregar_sons():
    global _sons

    if _sons is not None:
        return

    _sons = {}

    if pygame.mixer.get_init() is None:
        return

    freq = pygame.mixer.get_init()[0]

    # RESPINGO DE ÁGUA
    total = int(freq * 0.18)
    _sons["respingo"] = _montar_som([
        random.uniform(-1.0, 1.0) * (1 - i / total) ** 2 * 0.4
        for i in range(total)
    ])

    # ACERTO NO BEN
    total = int(freq * 0.35)
    valores = []
    fase = 0.0

    for i in range(total):
        fase += 2 * math.pi * (700 - 500 * i / total) / freq
        valores.append(
            (math.sin(fase) * 0.5 + random.uniform(-1.0, 1.0) * 0.2)
            * (1 - i / total)
        )

    _sons["acerto"] = _montar_som(valores)

    # FALHA
    total = int(freq * 0.5)
    valores = []
    fase = 0.0

    for i in range(total):
        fase += 2 * math.pi * (220 - 100 * i / total) / freq
        valores.append(math.sin(fase) * 0.4 * (1 - i / total))

    _sons["falha"] = _montar_som(valores)


def _tocar(nome):
    if _sons is None:
        return

    som = _sons.get(nome)

    if som is not None:
        som.set_volume(0.6)
        som.play()


# ============================================================
# BEN NO FAROL (CENÁRIO)
# ============================================================

def obter_area_ben(janela):
    largura, altura = janela.get_size()

    altura_ben = int(altura * 0.5)
    imagem = imagem_ben_escalada("mal", altura_ben)

    largura_ben = (
        imagem.get_width() if imagem is not None else int(altura_ben * 0.6)
    )

    area = pygame.Rect(0, 0, largura_ben, altura_ben)
    area.center = (int(largura * 0.62), int(altura * 0.52))

    return area


def _desenhar_aura(s, centro, tamanho, cor, intensidade=1.0):
    largura, altura = tamanho

    aura = pygame.Surface((largura + 160, altura + 160), pygame.SRCALPHA)

    for i in range(7):
        retangulo = aura.get_rect().inflate(-i * 20, -i * 20)
        pygame.draw.ellipse(
            aura,
            (cor[0], cor[1], cor[2], max(0, int(13 * intensidade))),
            retangulo
        )

    s.blit(aura, aura.get_rect(center=centro))


def _desenhar_figura(s, tipo, area, alpha=255, brilho=0):
    imagem = imagem_ben_escalada(tipo, area.height)

    if imagem is None:

        cor = (170, 40, 60) if tipo == "mal" else (200, 200, 230)
        pygame.draw.ellipse(s, cor, area)
        desenhar_texto(s, "BEN", 36, (255, 255, 255), area.center, True)
        return

    figura = imagem.copy()

    if brilho > 0:
        figura.fill(
            (brilho, brilho, brilho, 0),
            special_flags=pygame.BLEND_RGB_ADD
        )

    if alpha < 255:
        figura.set_alpha(max(0, alpha))

    s.blit(figura, figura.get_rect(center=area.center))


def ben_transformado(inicio):
    # SEM REGISTRO DE ENTRADA (JOGO CARREGADO): JÁ ESTÁ MALIGNO
    if inicio is None:
        return True

    return pygame.time.get_ticks() - inicio >= DURACAO_TRANSFORMACAO_MS


def desenhar_ben_farol(janela, inicio=None):
    t = pygame.time.get_ticks() / 1000.0

    area = obter_area_ben(janela).move(0, int(math.sin(t * 2.0) * 10))
    pulso = 0.8 + 0.4 * math.sin(t * 3.0)

    progresso = 1.0

    if inicio is not None:
        progresso = max(
            0.0,
            min(
                1.0,
                (pygame.time.get_ticks() - inicio) / DURACAO_TRANSFORMACAO_MS
            )
        )

    if progresso < 1.0:

        # AURA E FIGURA MUDAM DE BEM PARA MAL, COM UM CLARÃO NO MEIO
        clarao = math.sin(progresso * math.pi)

        branco = (230, 230, 255)
        vermelho = (200, 30, 55)
        cor = tuple(
            int(branco[i] + (vermelho[i] - branco[i]) * progresso)
            for i in range(3)
        )

        _desenhar_aura(
            janela, area.center, area.size, cor, pulso + 1.4 * clarao
        )
        _desenhar_figura(
            janela, "bem", area, int(255 * (1.0 - progresso)),
            int(140 * clarao)
        )
        _desenhar_figura(
            janela, "mal", area, int(255 * progresso), int(140 * clarao)
        )
        return

    _desenhar_aura(janela, area.center, area.size, (200, 30, 55), pulso)
    _desenhar_figura(janela, "mal", area)


# ============================================================
# COMBATE: ESTADO E LÓGICA
# ============================================================

def criar_estado_combate():
    _carregar_sons()

    agora = pygame.time.get_ticks()

    estado = {
        "fase": "luta",              # luta, vitoria ou derrota
        "maldade": 100.0,
        "frasco": GOTAS_NO_FRASCO,
        "tempo": 0.0,
        "fase_mov": 0.0,
        "ben": pygame.Rect(0, 0, 10, 10),
        "protegido": False,
        "proximo_escudo": 3.0,
        "fim_escudo": 0.0,
        "flash": 0.0,
        "respingos": [],
        "mensagem": "Clique no Ben para jogar água benta. Cuidado com o escudo!",
        "tipo_mensagem": "normal",
        "inicio_fase": agora,
        "ultimo_tick": agora,
    }

    _atualizar_posicao_ben(estado)

    return estado


def _atualizar_posicao_ben(estado):
    fase_mov = estado["fase_mov"]

    x = LARGURA / 2 + math.sin(fase_mov) * 520 + math.sin(fase_mov * 2.3) * 90
    y = 640 + math.sin(fase_mov * 1.4) * 40

    imagem = imagem_ben_escalada("mal", ALTURA_BEN_COMBATE)

    largura = (
        imagem.get_width()
        if imagem is not None
        else int(ALTURA_BEN_COMBATE * 0.6)
    )

    area = pygame.Rect(0, 0, largura, ALTURA_BEN_COMBATE)
    area.center = (int(x), int(y))

    estado["ben"] = area


def _atualizar_escudo(estado):
    tempo = estado["tempo"]

    if estado["protegido"]:

        if tempo >= estado["fim_escudo"]:
            estado["protegido"] = False
            estado["proximo_escudo"] = tempo + random.uniform(2.5, 4.0)

    elif tempo >= estado["proximo_escudo"]:

        estado["protegido"] = True
        estado["fim_escudo"] = tempo + 1.3


def _lancar_agua(estado, pos):
    agora = pygame.time.get_ticks()

    estado["frasco"] -= 1

    corpo = estado["ben"].inflate(-60, -40)
    tocou = corpo.collidepoint(pos)
    acertou = tocou and not estado["protegido"]

    estado["respingos"].append({
        "x": pos[0],
        "y": pos[1],
        "t0": agora,
        "acerto": acertou
    })

    if acertou:

        estado["maldade"] = max(0.0, estado["maldade"] - 100.0 / HITS_PARA_VENCER)
        estado["flash"] = 0.35

        _tocar("acerto")

        if estado["maldade"] <= 0:

            estado["fase"] = "vitoria"
            estado["inicio_fase"] = agora
            estado["mensagem"] = "A maldade deixou o Ben..."
            estado["tipo_mensagem"] = "sucesso"
            return

        estado["mensagem"] = "Acertou! A maldade dele está diminuindo."
        estado["tipo_mensagem"] = "sucesso"

    elif tocou:

        _tocar("falha")
        estado["mensagem"] = "Ele está protegido! Espere o brilho roxo passar."
        estado["tipo_mensagem"] = "erro"

    else:

        _tocar("respingo")
        estado["mensagem"] = "Errou! A água benta se perdeu no chão."
        estado["tipo_mensagem"] = "erro"

    if estado["frasco"] <= 0:

        estado["fase"] = "derrota"
        estado["inicio_fase"] = agora


def tratar_evento_combate(estado, evento, janela):
    # Retorna "sair" (desistiu), "derrota" (acabou a água) ou None.

    if estado["fase"] == "vitoria":
        return None

    if estado["fase"] == "derrota":

        confirmou = (
            evento.type == pygame.KEYDOWN
            and evento.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
                pygame.K_ESCAPE
            )
        ) or (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
        )

        if confirmou and pygame.time.get_ticks() - estado["inicio_fase"] > 700:
            return "derrota"

        return None

    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
        return "sair"

    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

        pos = _converter_posicao(janela, evento.pos)
        _lancar_agua(estado, pos)

    return None


def atualizar_combate(estado):
    # Retorna "vitoria" quando a animação da vitória termina.

    agora = pygame.time.get_ticks()
    dt = min((agora - estado["ultimo_tick"]) / 1000.0, 0.1)
    estado["ultimo_tick"] = agora

    estado["flash"] = max(0.0, estado["flash"] - dt)

    estado["respingos"] = [
        r for r in estado["respingos"] if agora - r["t0"] < 600
    ]

    if estado["fase"] == "luta":

        estado["tempo"] += dt

        # O BEN FICA MAIS RÁPIDO CONFORME ENFRAQUECE
        velocidade = 1.0 + (1.0 - estado["maldade"] / 100.0) * 0.9
        estado["fase_mov"] += dt * velocidade

        _atualizar_escudo(estado)

    _atualizar_posicao_ben(estado)

    if (
        estado["fase"] == "vitoria"
        and agora - estado["inicio_fase"] >= DURACAO_VITORIA_MS
    ):
        return "vitoria"

    return None


# ============================================================
# COMBATE: DESENHO
# ============================================================

_superficie_combate = None


def _desenhar_combate(s, estado, mouse):
    agora = pygame.time.get_ticks()
    t = agora / 1000.0
    fase = estado["fase"]

    s.fill(COR_FUNDO)

    for x in range(0, LARGURA, 64):
        pygame.draw.line(s, (25, 21, 37), (x, 0), (x, ALTURA), 1)

    for y in range(0, ALTURA, 64):
        pygame.draw.line(s, (25, 21, 37), (0, y), (LARGURA, y), 1)

    desenhar_painel(s, pygame.Rect(120, 55, 1680, 950))

    desenhar_texto(s, "EXORCISMO", 48, COR_TEXTO, (LARGURA // 2, 125), True)
    desenhar_texto(
        s, "ENFRAQUEÇA O BEN COM A ÁGUA BENTA", 24, COR_DOURADO,
        (LARGURA // 2, 190), True
    )

    pygame.draw.line(s, COR_BORDA, (420, 225), (1500, 225), 3)

    # BARRA DE MALDADE
    barra = pygame.Rect(610, 240, 700, 32)

    pygame.draw.rect(s, (20, 17, 29), barra, border_radius=5)

    largura_barra = int((barra.width - 8) * estado["maldade"] / 100.0)

    if largura_barra > 0:
        pygame.draw.rect(
            s, (190, 40, 60),
            (barra.x + 4, barra.y + 4, largura_barra, barra.height - 8),
            border_radius=3
        )

    pygame.draw.rect(s, COR_BORDA, barra, 3, border_radius=5)

    desenhar_texto(s, "MALDADE DO BEN", 20, COR_TEXTO, (470, 256), True)

    # CAIXA DE MENSAGEM
    caixa = pygame.Rect(280, 300, 1360, 54)
    pygame.draw.rect(s, (27, 22, 40), caixa, border_radius=5)
    pygame.draw.rect(s, (91, 72, 112), caixa, 2, border_radius=5)

    cor_mensagem = {
        "erro": COR_VERMELHO,
        "sucesso": COR_VERDE
    }.get(estado["tipo_mensagem"], COR_TEXTO)

    desenhar_texto(s, estado["mensagem"], 21, cor_mensagem, caixa.center)

    # BEN
    area = estado["ben"]

    if fase == "vitoria":

        progresso = min(
            1.0,
            (agora - estado["inicio_fase"]) / DURACAO_VITORIA_MS
        )

        # O BEN VOLTA À FORMA DE ANTES, EM UM BRILHO BRANCO
        _desenhar_aura(
            s, area.center, area.size, (230, 230, 255),
            1.6 * (1.0 - abs(progresso - 0.5) * 1.2)
        )
        _desenhar_figura(
            s, "mal", area, int(255 * (1.0 - progresso)),
            int(120 * progresso)
        )
        _desenhar_figura(
            s, "bem", area, int(255 * progresso)
        )

    else:

        protegido = estado["protegido"]

        cor_aura = (120, 70, 220) if protegido else (200, 30, 55)
        intensidade = 0.8 + 0.4 * math.sin(t * 3.0) + (0.9 if protegido else 0.0)

        _desenhar_aura(s, area.center, area.size, cor_aura, intensidade)

        brilho = int(160 * min(1.0, estado["flash"] / 0.35))

        _desenhar_figura(s, "mal", area, 255, brilho)

        if protegido:
            pygame.draw.ellipse(
                s, (170, 130, 255), area.inflate(60, 40), 5
            )

    # RESPINGOS DA ÁGUA BENTA
    for r in estado["respingos"]:

        idade = (agora - r["t0"]) / 600.0
        cor = (255, 255, 255) if r["acerto"] else COR_AGUA

        for k in range(10):

            angulo = k * (2 * math.pi / 10)
            distancia = 12 + 60 * idade

            px = r["x"] + math.cos(angulo) * distancia
            py = r["y"] + math.sin(angulo) * distancia + 40 * idade * idade
            raio = max(1, int(6 * (1.0 - idade)))

            pygame.draw.circle(s, cor, (int(px), int(py)), raio)

    # FRASCO (GOTAS RESTANTES)
    desenhar_texto(s, "ÁGUA BENTA", 20, COR_TEXTO, (330, 905), True)

    for i in range(GOTAS_NO_FRASCO):

        cx = 230 + i * 44
        cheio = i < estado["frasco"]

        pygame.draw.circle(
            s, COR_AGUA if cheio else (45, 38, 60), (cx, 950), 15
        )
        pygame.draw.circle(s, COR_BORDA, (cx, 950), 15, 2)

    desenhar_texto(
        s, "ESC  -  DESISTIR (A ÁGUA BENTA NÃO É GASTA)", 16,
        COR_TEXTO_SUAVE, (LARGURA // 2, 1035)
    )

    # MIRA
    if fase == "luta":

        x, y = mouse

        pygame.draw.circle(s, COR_AGUA, (x, y), 26, 3)
        pygame.draw.line(s, COR_AGUA, (x - 40, y), (x - 14, y), 3)
        pygame.draw.line(s, COR_AGUA, (x + 14, y), (x + 40, y), 3)
        pygame.draw.line(s, COR_AGUA, (x, y - 40), (x, y - 14), 3)
        pygame.draw.line(s, COR_AGUA, (x, y + 14), (x, y + 40), 3)

    # DERROTA
    if fase == "derrota":

        s.blit(_sombra_tela(), (0, 0))

        painel = pygame.Rect(460, 380, 1000, 320)
        desenhar_painel(s, painel)

        desenhar_texto(
            s, "A ÁGUA BENTA ACABOU", 40, COR_VERMELHO,
            (painel.centerx, painel.y + 80), True
        )
        desenhar_texto(
            s, "O Ben ainda é forte demais. Respire fundo e tente de novo.",
            26, COR_TEXTO, (painel.centerx, painel.y + 160)
        )
        desenhar_texto(
            s, "ENTER  -  VOLTAR AO FAROL", 20, COR_TEXTO_SUAVE,
            (painel.centerx, painel.y + 250)
        )


def desenhar_combate(janela, estado):
    global _superficie_combate

    if _superficie_combate is None:
        _superficie_combate = pygame.Surface((LARGURA, ALTURA))

    mouse = _converter_posicao(janela, pygame.mouse.get_pos())

    _desenhar_combate(_superficie_combate, estado, mouse)

    _, x0, y0, largura_final, altura_final = _calcular_escala(janela)

    janela.fill((0, 0, 0))

    if (largura_final, altura_final) == (LARGURA, ALTURA):
        janela.blit(_superficie_combate, (x0, y0))

    else:
        imagem = pygame.transform.smoothscale(
            _superficie_combate,
            (largura_final, altura_final)
        )
        janela.blit(imagem, (x0, y0))


# ============================================================
# FINAL DO JOGO
# ============================================================

_cache_fim = {"tamanho": None, "imagem": None}


def _imagem_fim(tamanho):
    if _cache_fim["tamanho"] == tamanho:
        return _cache_fim["imagem"]

    original = _carregar_imagem("fim", CAMINHO_IMAGEM_FIM, alpha=False)
    imagem = None

    if original is not None:

        escala = min(
            tamanho[0] / original.get_width(),
            tamanho[1] / original.get_height()
        )

        nova = (
            max(1, int(original.get_width() * escala)),
            max(1, int(original.get_height() * escala))
        )

        imagem = pygame.transform.smoothscale(original, nova)

    _cache_fim["tamanho"] = tamanho
    _cache_fim["imagem"] = imagem

    return imagem


def criar_estado_fim():
    # A MÚSICA COMEÇA NO MESMO INSTANTE EM QUE A IMAGEM COMEÇA A APARECER

    if pygame.mixer.get_init() is not None:

        pygame.mixer.stop()

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(CAMINHO_MUSICA_FIM)
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play()

        except (pygame.error, FileNotFoundError) as erro:
            print(f"Erro ao tocar a música final: {erro}")

    return {
        "fase": "fade",         # fade, dialogo, escurecendo ou fim
        "inicio_fase": pygame.time.get_ticks(),
        "pular": False,
    }


def _letras_fim(estado):
    if estado["pular"]:
        return len(TEXTO_FIM)

    passado = pygame.time.get_ticks() - estado["inicio_fase"] - 400

    return max(0, min(len(TEXTO_FIM), int(passado / MS_POR_LETRA)))


def _texto_fim_completo(estado):
    return _letras_fim(estado) >= len(TEXTO_FIM)


def tratar_evento_fim(estado, evento):
    # Retorna "encerrar" quando o jogador pode fechar o jogo.

    agora = pygame.time.get_ticks()

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

    if estado["fase"] == "dialogo" and confirmou:

        if _texto_fim_completo(estado):
            estado["fase"] = "escurecendo"
            estado["inicio_fase"] = agora

        else:
            estado["pular"] = True

    elif estado["fase"] == "fim":

        sair = confirmou or (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_ESCAPE
        )

        if sair and agora - estado["inicio_fase"] > 3000:
            return "encerrar"

    return None


def atualizar_fim(estado):
    agora = pygame.time.get_ticks()
    decorrido = agora - estado["inicio_fase"]

    if estado["fase"] == "fade" and decorrido >= DURACAO_FADE_FIM_MS:

        estado["fase"] = "dialogo"
        estado["inicio_fase"] = agora
        estado["pular"] = False

    elif (
        estado["fase"] == "escurecendo"
        and decorrido >= DURACAO_ESCURECER_MS
    ):

        estado["fase"] = "fim"
        estado["inicio_fase"] = agora


def desenhar_fim(janela, estado, fontes):
    largura, altura = janela.get_size()

    agora = pygame.time.get_ticks()
    decorrido = agora - estado["inicio_fase"]
    fase = estado["fase"]

    janela.fill((0, 0, 0))

    # TRANSPARÊNCIA DA IMAGEM EM CADA FASE
    if fase == "fade":
        alpha = int(255 * min(1.0, decorrido / DURACAO_FADE_FIM_MS))

    elif fase == "dialogo":
        alpha = 255

    elif fase == "escurecendo":
        alpha = int(255 * (1.0 - min(1.0, decorrido / DURACAO_ESCURECER_MS)))

    else:
        alpha = 0

    imagem = _imagem_fim((largura, altura))

    if imagem is not None and alpha > 0:
        imagem.set_alpha(alpha)
        janela.blit(imagem, imagem.get_rect(center=(largura // 2, altura // 2)))

    # CAIXA DE DIÁLOGO
    if fase == "dialogo":

        caixa = pygame.Rect(
            int(largura * 0.1),
            int(altura * 0.74),
            int(largura * 0.8),
            int(altura * 0.2)
        )

        painel = pygame.Surface(caixa.size, pygame.SRCALPHA)

        pygame.draw.rect(
            painel, (45, 30, 55, 230), painel.get_rect(), border_radius=20
        )
        pygame.draw.rect(
            painel, ROXO_CLARO, painel.get_rect(), 4, border_radius=20
        )

        janela.blit(painel, caixa.topleft)

        texto = TEXTO_FIM[:_letras_fim(estado)]
        renderizado = fontes["normal"].render(texto, True, BRANCO)

        janela.blit(
            renderizado,
            renderizado.get_rect(
                midleft=(caixa.x + 50, caixa.centery - 10)
            )
        )

        if _texto_fim_completo(estado):

            dica = fontes["pequena"].render(
                "ENTER para continuar", True, BRANCO
            )

            janela.blit(
                dica,
                dica.get_rect(
                    bottomright=(caixa.right - 40, caixa.bottom - 20)
                )
            )

    # "FIM"
    if fase in ("escurecendo", "fim"):

        if fase == "fim":
            alpha_texto = 255

        else:
            progresso = decorrido / DURACAO_ESCURECER_MS
            alpha_texto = int(255 * max(0.0, (progresso - 0.4) / 0.6))

        texto_fim = fonte(max(40, altura // 4), True).render(
            "FIM", True, (255, 255, 255)
        )
        texto_fim.set_alpha(alpha_texto)

        janela.blit(
            texto_fim,
            texto_fim.get_rect(center=(largura // 2, altura // 2))
        )

        if fase == "fim" and decorrido > 3000:

            dica = fontes["normal"].render(
                "Pressione ESC para sair", True, BRANCO
            )

            janela.blit(
                dica,
                dica.get_rect(center=(largura // 2, int(altura * 0.88)))
            )