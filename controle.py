import math
import pygame
import functools
import math
import pygame

@functools.lru_cache(maxsize=None)
def fonte(tamanho, negrito=False):
    return pygame.font.SysFont("arial", tamanho, bold=negrito)

# ============================================================
# MINIGAME DE MANUTENCAO DO FAROL
# Versao de teste isolada.
#
# Controles:
# - Clique nas engrenagens para gira-las.
# - Clique em VERIFICAR MECANISMO para conferir a combinacao.
# - Depois de acertar, segure ABASTECER para encher a barra.
# - Pressione ESC para sair.
#
# Nesta versao isolada, o oleo e simulado. A integracao com o
# inventario e com a iluminacao do jogo sera feita depois.
# ============================================================


LARGURA = 1920
ALTURA = 1080
FPS = 60

COR_FUNDO = (18, 15, 29)
COR_PAINEL = (37, 29, 52)
COR_PAINEL_CLARO = (57, 43, 76)
COR_BORDA = (143, 100, 177)
COR_TEXTO = (244, 237, 250)
COR_TEXTO_SUAVE = (183, 169, 197)
COR_DOURADO = (224, 185, 104)
COR_VERDE = (105, 196, 133)
COR_VERMELHO = (207, 91, 103)
COR_ENGRENAGEM = (126, 105, 151)
COR_ENGRENAGEM_CLARA = (184, 158, 207)
COR_SOMBRA = (10, 8, 17)
COR_OLEO = (196, 145, 65)

# Cada engrenagem possui quatro posicoes.
# A combinacao correta e mantida fixa durante os testes.
COMBINACAO_CORRETA = [1, 3, 2]
QUANTIDADE_POSICOES = 4

DURACAO_ABASTECIMENTO_MS = 3500


def fonte(tamanho, negrito=False):
    return pygame.font.SysFont("arial", tamanho, bold=negrito)


def desenhar_texto(janela, texto, tamanho, cor, centro, negrito=False):
    imagem = fonte(tamanho, negrito).render(texto, True, cor)
    janela.blit(imagem, imagem.get_rect(center=centro))


def desenhar_painel(janela, area, cor=COR_PAINEL):
    pygame.draw.rect(janela, COR_SOMBRA, area.move(6, 7), border_radius=8)
    pygame.draw.rect(janela, cor, area, border_radius=8)
    pygame.draw.rect(janela, COR_BORDA, area, 3, border_radius=8)


def pontos_poligono(cx, cy, raio, quantidade, angulo_inicial=-math.pi / 2):
    pontos = []
    for i in range(quantidade):
        angulo = angulo_inicial + (2 * math.pi * i / quantidade)
        pontos.append((
            int(cx + math.cos(angulo) * raio),
            int(cy + math.sin(angulo) * raio)
        ))
    return pontos


def desenhar_estrela_pixel(janela, x, y, tamanho, cor):
    pygame.draw.rect(
        janela,
        cor,
        (x - tamanho // 2, y - tamanho // 2, tamanho, tamanho)
    )
    pygame.draw.rect(
        janela,
        cor,
        (x - 1, y - tamanho, 2, tamanho * 2)
    )
    pygame.draw.rect(
        janela,
        cor,
        (x - tamanho, y - 1, tamanho * 2, 2)
    )


def desenhar_engrenagem(janela, centro, raio, posicao, numero, selecionada=False):
    cx, cy = centro

    # Sombra e base.
    pygame.draw.circle(janela, COR_SOMBRA, (cx + 6, cy + 7), raio + 14)
    pygame.draw.circle(janela, (24, 20, 36), centro, raio + 13)
    pygame.draw.circle(
        janela,
        COR_DOURADO if selecionada else COR_BORDA,
        centro,
        raio + 13,
        4
    )

    # Dentes da engrenagem.
    quantidade_dentes = 12
    for i in range(quantidade_dentes):
        angulo = (2 * math.pi * i / quantidade_dentes) + (posicao * math.pi / 2)
        distancia = raio + 5
        dx = math.cos(angulo) * distancia
        dy = math.sin(angulo) * distancia

        dente = pygame.Rect(0, 0, 22, 28)
        dente.center = (int(cx + dx), int(cy + dy))
        pygame.draw.rect(janela, COR_ENGRENAGEM_CLARA, dente, border_radius=3)
        pygame.draw.rect(janela, COR_SOMBRA, dente, 2, border_radius=3)

    # Corpo da engrenagem.
    pygame.draw.circle(janela, COR_ENGRENAGEM, centro, raio)
    pygame.draw.circle(janela, COR_ENGRENAGEM_CLARA, centro, raio, 5)

    # Quatro marcas de posicao.
    for i in range(QUANTIDADE_POSICOES):
        angulo = -math.pi / 2 + i * math.pi / 2
        mx = int(cx + math.cos(angulo) * (raio - 24))
        my = int(cy + math.sin(angulo) * (raio - 24))
        cor = COR_DOURADO if i == posicao else (77, 64, 96)
        pygame.draw.rect(janela, cor, (mx - 7, my - 7, 14, 14))

    # Indicador central: o pequeno ponteiro gira junto da engrenagem.
    angulo_ponteiro = -math.pi / 2 + posicao * math.pi / 2
    inicio = (
        int(cx + math.cos(angulo_ponteiro) * 16),
        int(cy + math.sin(angulo_ponteiro) * 16)
    )
    fim = (
        int(cx + math.cos(angulo_ponteiro) * (raio - 42)),
        int(cy + math.sin(angulo_ponteiro) * (raio - 42))
    )
    pygame.draw.line(janela, COR_DOURADO, inicio, fim, 12)
    pygame.draw.circle(janela, (42, 33, 58), centro, 25)
    pygame.draw.circle(janela, COR_DOURADO, centro, 25, 4)
    pygame.draw.circle(janela, COR_TEXTO, centro, 7)

    desenhar_texto(
        janela,
        f"ENGRENAGEM {numero}",
        23,
        COR_TEXTO,
        (cx, cy + raio + 58),
        True
    )

    desenhar_texto(
        janela,
        f"POSICAO {posicao + 1}/4",
        18,
        COR_TEXTO_SUAVE,
        (cx, cy + raio + 87)
    )


def criar_estado_minigame():
    return {
        "posicoes": [0, 0, 0],
        "verificado": False,
        "mecanismo_correto": False,
        "abastecendo": False,
        "progresso": 0.0,
        "concluido": False,
        "mensagem": "Gire as tres engrenagens para ajustar o mecanismo.",
        "tipo_mensagem": "normal",
        "tempo_mensagem": 0,
        "oleo_disponivel": True,
        "ultimo_tick": pygame.time.get_ticks(),
        "botao_verificar": pygame.Rect(760, 800, 400, 76),
        "botao_abastecer": pygame.Rect(760, 800, 400, 76),
        "botao_sair": pygame.Rect(1500, 920, 240, 60),
        "areas_engrenagens": [
            pygame.Rect(350, 340, 300, 300),
            pygame.Rect(810, 340, 300, 300),
            pygame.Rect(1270, 340, 300, 300),
        ],
    }

def definir_mensagem(estado, mensagem, tipo="normal", duracao=2400):
    estado["mensagem"] = mensagem
    estado["tipo_mensagem"] = tipo
    estado["tempo_mensagem"] = pygame.time.get_ticks() + duracao


def tratar_clique(estado, pos_mouse):
    if estado["concluido"] or estado["abastecendo"]:
        return

    if not estado["mecanismo_correto"]:
        for i, area in enumerate(estado["areas_engrenagens"]):
            if area.collidepoint(pos_mouse):
                estado["posicoes"][i] = (
                    estado["posicoes"][i] + 1
                ) % QUANTIDADE_POSICOES
                definir_mensagem(
                    estado,
                    f"Engrenagem {i + 1} girada. Continue ajustando o mecanismo."
                )
                return

        if estado["botao_verificar"].collidepoint(pos_mouse):
            if estado["posicoes"] == COMBINACAO_CORRETA:
                estado["verificado"] = True
                estado["mecanismo_correto"] = True
                definir_mensagem(
                    estado,
                    "Mecanismo alinhado! Agora abasteca o farol.",
                    "sucesso"
                )
            else:
                estado["posicoes"] = [0, 0, 0]
                estado["verificado"] = False
                definir_mensagem(
                    estado,
                    "Combinacao incorreta! O mecanismo voltou ao inicio.",
                    "erro",
                    3000
                )
            return

    elif estado["botao_abastecer"].collidepoint(pos_mouse):
        if not estado["oleo_disponivel"]:
            definir_mensagem(
                estado,
                "Voce nao tem oleo suficiente para abastecer o farol.",
                "erro"
            )


def iniciar_abastecimento(estado, pos_mouse):
    if (
        estado["mecanismo_correto"]
        and not estado["concluido"]
        and estado["botao_abastecer"].collidepoint(pos_mouse)
        and estado["oleo_disponivel"]
    ):
        estado["abastecendo"] = True


def atualizar_estado(estado, tempo_delta):
    if estado["abastecendo"]:
        estado["progresso"] += tempo_delta / DURACAO_ABASTECIMENTO_MS
        if estado["progresso"] >= 1:
            estado["progresso"] = 1.0
            estado["abastecendo"] = False
            estado["concluido"] = True
            estado["oleo_disponivel"] = False
            definir_mensagem(
                estado,
                "Manutencao concluida! O farol recuperou 35 pontos de iluminacao.",
                "sucesso",
                10000
            )


def desenhar_barra_progresso(janela, area, progresso):
    pygame.draw.rect(janela, (20, 17, 29), area, border_radius=5)
    pygame.draw.rect(janela, COR_BORDA, area, 3, border_radius=5)

    largura_preenchida = int((area.width - 8) * max(0, min(1, progresso)))
    if largura_preenchida > 0:
        preenchimento = pygame.Rect(
            area.x + 4,
            area.y + 4,
            largura_preenchida,
            area.height - 8
        )
        pygame.draw.rect(janela, COR_OLEO, preenchimento, border_radius=3)


def desenhar_tela(janela, estado):
    janela.fill(COR_FUNDO)

    # Fundo quadriculado discreto para dar identidade de pixel art.
    for x in range(0, LARGURA, 64):
        pygame.draw.line(janela, (25, 21, 37), (x, 0), (x, ALTURA), 1)
    for y in range(0, ALTURA, 64):
        pygame.draw.line(janela, (25, 21, 37), (0, y), (LARGURA, y), 1)

    painel = pygame.Rect(120, 55, 1680, 950)
    desenhar_painel(janela, painel)

    desenhar_texto(
        janela,
        "MANUTENCAO DO FAROL",
        48,
        COR_TEXTO,
        (LARGURA // 2, 125),
        True
    )
    desenhar_texto(
        janela,
        "AJUSTE O MECANISMO DE ENGRENAGENS",
        24,
        COR_DOURADO,
        (LARGURA // 2, 190),
        True
    )

    # Linha decorativa.
    pygame.draw.line(
        janela,
        COR_BORDA,
        (420, 225),
        (1500, 225),
        3
    )

    for i, area in enumerate(estado["areas_engrenagens"]):
        desenhar_engrenagem(
            janela,
            area.center,
            105,
            estado["posicoes"][i],
            i + 1,
            selecionada=estado["mecanismo_correto"]
        )

    if not estado["mecanismo_correto"]:
        desenhar_texto(
            janela,
            "Clique em uma engrenagem para gira-la.",
            23,
            COR_TEXTO_SUAVE,
            (LARGURA // 2, 735)
        )

        botao = estado["botao_verificar"]
        desenhar_painel(janela, botao, COR_PAINEL_CLARO)
        desenhar_texto(
            janela,
            "VERIFICAR MECANISMO",
            25,
            COR_TEXTO,
            botao.center,
            True
        )

    else:
        desenhar_texto(
            janela,
            "MECANISMO ALINHADO",
            27,
            COR_VERDE,
            (LARGURA // 2, 725),
            True
        )

        botao = estado["botao_abastecer"]
        cor_botao = COR_PAINEL_CLARO if estado["oleo_disponivel"] else (65, 45, 48)
        desenhar_painel(janela, botao, cor_botao)

        if estado["concluido"]:
            texto_botao = "ABASTECIMENTO CONCLUIDO"
        elif estado["abastecendo"]:
            texto_botao = "ABASTECENDO..."
        else:
            texto_botao = "SEGURE PARA ABASTECER"

        desenhar_texto(
            janela,
            texto_botao,
            24,
            COR_TEXTO,
            botao.center,
            True
        )

        barra = pygame.Rect(610, 900, 700, 28)
        desenhar_barra_progresso(janela, barra, estado["progresso"])

        if estado["concluido"]:
            desenhar_texto(
                janela,
                "ILUMINACAO DO FAROL: +35",
                20,
                COR_VERDE,
                (LARGURA // 2, 950)
            )
        elif not estado["oleo_disponivel"]:
            desenhar_texto(
                janela,
                "OLEO UTILIZADO",
                18,
                COR_OLEO,
                (LARGURA // 2, 950)
            )

    # Caixa de instrucoes / notificacoes.
    caixa_mensagem = pygame.Rect(280, 265, 1360, 54)
    pygame.draw.rect(janela, (27, 22, 40), caixa_mensagem, border_radius=5)
    pygame.draw.rect(janela, (91, 72, 112), caixa_mensagem, 2, border_radius=5)

    cor_mensagem = COR_TEXTO
    if estado["tipo_mensagem"] == "erro":
        cor_mensagem = COR_VERMELHO
    elif estado["tipo_mensagem"] == "sucesso":
        cor_mensagem = COR_VERDE

    desenhar_texto(
        janela,
        estado["mensagem"],
        21,
        cor_mensagem,
        caixa_mensagem.center
    )

    botao_sair = estado["botao_sair"]
    desenhar_painel(janela, botao_sair, COR_PAINEL_CLARO)
    desenhar_texto(janela, "VOLTAR", 22, COR_TEXTO, botao_sair.center, True)

    desenhar_texto(
        janela,
        "ESC  -  VOLTAR AO FAROL",
        16,
        COR_TEXTO_SUAVE,
        (LARGURA // 2, 1035)
    )


def executar_teste():
    pygame.init()
    janela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Teste - Manutencao do Farol")
    relogio = pygame.time.Clock()

    estado = criar_estado()
    executando = True

    while executando:
        tempo_delta = relogio.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    executando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                tratar_clique(estado, evento.pos)
                iniciar_abastecimento(estado, evento.pos)

            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                estado["abastecendo"] = False

        if estado["abastecendo"] and not pygame.mouse.get_pressed()[0]:
            estado["abastecendo"] = False

        atualizar_estado(estado, tempo_delta)
        desenhar_tela(janela, estado)
        pygame.display.flip()

    pygame.quit()


# ============================================================
# FUNCOES USADAS PELO JOGO PRINCIPAL
# ============================================================

_superficie_minigame = None


def _calcular_escala(janela):
    largura, altura = janela.get_size()
    escala = min(largura / LARGURA, altura / ALTURA)
    largura_final = int(LARGURA * escala)
    altura_final = int(ALTURA * escala)
    x0 = (largura - largura_final) // 2
    y0 = (altura - altura_final) // 2
    return escala, x0, y0, largura_final, altura_final


def _converter_posicao(janela, pos):
    escala, x0, y0, _, _ = _calcular_escala(janela)
    return (int((pos[0] - x0) / escala), int((pos[1] - y0) / escala))


def tratar_evento_minigame(estado, evento, janela):
    # Retorna "sair" quando o jogador quiser voltar ao jogo.
    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
        return "sair"

    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
        pos = _converter_posicao(janela, evento.pos)

        if estado["botao_sair"].collidepoint(pos) and not estado["abastecendo"]:
            return "sair"

        tratar_clique(estado, pos)
        iniciar_abastecimento(estado, pos)

    elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
        estado["abastecendo"] = False

    return None


def atualizar_minigame(estado):
    # Retorna True no exato momento em que o abastecimento termina.
    agora = pygame.time.get_ticks()
    delta = agora - estado["ultimo_tick"]
    estado["ultimo_tick"] = agora

    if estado["abastecendo"] and not pygame.mouse.get_pressed()[0]:
        estado["abastecendo"] = False

    ja_concluido = estado["concluido"]
    atualizar_estado(estado, delta)

    return estado["concluido"] and not ja_concluido


def desenhar_minigame(janela, estado):
    global _superficie_minigame

    if _superficie_minigame is None:
        _superficie_minigame = pygame.Surface((LARGURA, ALTURA))

    desenhar_tela(_superficie_minigame, estado)

    _, x0, y0, largura_final, altura_final = _calcular_escala(janela)

    janela.fill((0, 0, 0))

    if (largura_final, altura_final) == (LARGURA, ALTURA):
        janela.blit(_superficie_minigame, (x0, y0))
    else:
        imagem = pygame.transform.smoothscale(
            _superficie_minigame,
            (largura_final, altura_final)
        )
        janela.blit(imagem, (x0, y0))