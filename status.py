import pygame


# CORES DOS PAINÉIS
BRANCO = (255, 255, 255)
FUNDO = (35, 25, 45)
CINZA = (75, 65, 85)

COR_ENERGIA = (214, 180, 92)
COR_SANIDADE = (154, 117, 214)
COR_VITALIDADE = (190, 75, 85)
COR_EXPOSICAO = (182, 90, 105)
COR_FAROL = (214, 193, 123)


def desenhar_barra(janela, fonte, nome, valor, cor, x, y, largura):

    valor = max(0, min(100, valor))

    texto = fonte.render(nome, True, BRANCO)
    janela.blit(texto, (x, y))

    texto_valor = fonte.render(f"{valor}/100", True, BRANCO)
    janela.blit(
        texto_valor,
        (x + largura - texto_valor.get_width(), y)
    )

    area_barra = pygame.Rect(x, y + 27, largura, 10)
    pygame.draw.rect(janela, CINZA, area_barra, border_radius=5)

    largura_preenchida = int(largura * valor / 100)

    if largura_preenchida > 0:

        preenchimento = pygame.Rect(
            x,
            y + 27,
            largura_preenchida,
            10
        )

        pygame.draw.rect(
            janela,
            cor,
            preenchimento,
            border_radius=5
        )


def desenhar_status(janela, fontes, estado):

    fonte_titulo = fontes["normal"]
    fonte_barra = fontes.get("pequena", pygame.font.SysFont("arial", 18))

    # EXPOSIÇÃO SÓ ENTRA NO PAINEL DEPOIS DE SER REVELADA
    atributos = [
        ("ENERGIA", estado["energia"], COR_ENERGIA),
        ("SANIDADE", estado["sanidade"], COR_SANIDADE),
        ("VITALIDADE", estado["vitalidade"], COR_VITALIDADE),
    ]

    if estado.get("exposicao_revelada", False):
        atributos.append(
            ("EXPOSIÇÃO", estado["exposicao"], COR_EXPOSICAO)
        )

    altura_painel = 105 + len(atributos) * 40
    painel = pygame.Rect(30, 30, 350, altura_painel)

    pygame.draw.rect(
        janela,
        FUNDO,
        painel,
        border_radius=15
    )

    titulo = fonte_titulo.render("STATUS", True, BRANCO)
    janela.blit(titulo, (50, 43))

    y = 82

    for nome, valor, cor in atributos:

        desenhar_barra(
            janela,
            fonte_barra,
            nome,
            valor,
            cor,
            50,
            y,
            310
        )

        y += 40


def desenhar_status_farol(janela, fontes, estado):

    fonte_titulo = fontes["normal"]
    fonte_barra = fontes.get("pequena", pygame.font.SysFont("arial", 18))

    largura, altura = janela.get_size()

    painel = pygame.Rect(
        max(30, largura - 390),
        30,
        350,
        115
    )

    pygame.draw.rect(
        janela,
        FUNDO,
        painel,
        border_radius=15
    )

    titulo = fonte_titulo.render("FAROL", True, BRANCO)
    janela.blit(titulo, (painel.x + 20, painel.y + 13))

    desenhar_barra(
        janela,
        fonte_barra,
        "ILUMINAÇÃO",
        estado["iluminacao_farol"],
        COR_FAROL,
        painel.x + 20,
        painel.y + 57,
        310
    )
