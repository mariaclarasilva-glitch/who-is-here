import pygame

from config import BRANCO, ROXO, ROXO_CLARO


# OBJETOS DISPONÍVEIS EM CADA CENÁRIO

ITENS_POR_TELA = {
    "inicio": ["Cerveja", "Água benta"],
    "porta": [],
    "controle": ["Rádio", "Óleo"],
}


# POSIÇÃO DA ANABELLE NO QUARTO (CENTRO DA IMAGEM, EM PROPORÇÃO DA TELA)
# (0.50, 0.50) = CENTRO DA TELA. AJUSTE SE QUISER MOVER ELA.

POSICAO_ANABELLE_QUARTO = (0.50, 0.50)


# CRIAR BOTÕES DAS TELAS

def criar_botoes(largura, altura):

    largura_botao = min(400, (largura - 80) // 2)
    altura_botao = 80
    distancia = 30

    inicio_x = (
        largura - (largura_botao * 2 + distancia)
    ) // 2

    pos_y = altura - 150

    return {
        "esquerda": pygame.Rect(
            inicio_x,
            pos_y,
            largura_botao,
            altura_botao
        ),

        "direita": pygame.Rect(
            inicio_x + largura_botao + distancia,
            pos_y,
            largura_botao,
            altura_botao
        ),
    }


# ÁREA CLICÁVEL DO FAROL (CANTO INFERIOR ESQUERDO)

def obter_area_farol(janela):

    largura, altura = janela.get_size()

    return pygame.Rect(
        0,
        int(altura * 0.62),
        int(largura * 0.23),
        int(altura * 0.38)
    )


# CRIAR POSIÇÕES PROVISÓRIAS DOS OBJETOS

def criar_areas_itens(largura, altura):

    tamanho_area = 130

    posicoes = {
        "Cerveja": (int(largura * 0.28), int(altura * 0.38)),
        "Água benta": (int(largura * 0.72), int(altura * 0.38)),
        "Rádio": (int(largura * 0.28), int(altura * 0.38)),
        "Óleo": (int(largura * 0.72), int(altura * 0.38)),
    }

    areas = {}

    for nome, centro in posicoes.items():

        areas[nome] = pygame.Rect(
            centro[0] - tamanho_area // 2,
            centro[1] - tamanho_area // 2,
            tamanho_area,
            tamanho_area
        )

    return areas


# DESENHAR OBJETOS NOS CENÁRIOS

def desenhar_itens_cenario(
    janela,
    tela_atual,
    itens,
    itens_coletados,
    mouse_pos
):

    largura, altura = janela.get_size()

    areas = criar_areas_itens(largura, altura)

    nomes = ITENS_POR_TELA.get(tela_atual, [])

    for nome in nomes:

        if nome in itens_coletados:
            continue

        area = areas[nome]
        mouse_sobre = area.collidepoint(mouse_pos)

        if mouse_sobre:

            brilho = pygame.Surface(
                (area.width + 24, area.height + 24),
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                brilho,
                (145, 80, 170, 65),
                brilho.get_rect(),
                border_radius=20
            )

            janela.blit(
                brilho,
                (area.x - 12, area.y - 12)
            )

            pygame.draw.rect(
                janela,
                ROXO_CLARO,
                area,
                4,
                border_radius=15
            )

        imagem = itens[nome].convert_alpha()

        largura_original, altura_original = imagem.get_size()

        escala = min(
            100 / largura_original,
            100 / altura_original
        )

        nova_largura = max(1, int(largura_original * escala))
        nova_altura = max(1, int(altura_original * escala))

        imagem = pygame.transform.smoothscale(
            imagem,
            (nova_largura, nova_altura)
        )

        janela.blit(
            imagem,
            imagem.get_rect(center=area.center)
        )

        texto = pygame.font.SysFont("arial", 23).render(
            nome,
            True,
            BRANCO
        )

        janela.blit(
            texto,
            texto.get_rect(
                center=(area.centerx, area.bottom + 18)
            )
        )

        if mouse_sobre:

            instrucao = pygame.font.SysFont("arial", 20).render(
                "APERTE E PARA COLETAR",
                True,
                BRANCO
            )

            janela.blit(
                instrucao,
                instrucao.get_rect(
                    center=(area.centerx, area.bottom + 48)
                )
            )


# IDENTIFICAR OBJETO APONTADO PELO MOUSE

def obter_item_sob_mouse(
    tela_atual,
    mouse_pos,
    largura,
    altura,
    itens_coletados
):

    areas = criar_areas_itens(largura, altura)
    nomes = ITENS_POR_TELA.get(tela_atual, [])

    for nome in nomes:

        if nome in itens_coletados:
            continue

        if areas[nome].collidepoint(mouse_pos):
            return nome

    return None


# DESENHAR BOTÕES

def desenhar_botao(janela, fontes, botao, texto, cor):

    pygame.draw.rect(
        janela,
        cor,
        botao,
        border_radius=15
    )

    texto_renderizado = fontes["normal"].render(
        texto,
        True,
        BRANCO
    )

    janela.blit(
        texto_renderizado,
        texto_renderizado.get_rect(center=botao.center)
    )


# DESENHAR A TELA ATUAL

def desenhar_tela(
    janela,
    tela_atual,
    imagens,
    fontes,
    botoes,
    itens=None,
    itens_coletados=None,
    mouse_pos=None,
    estado=None
):

    if itens_coletados is None:
        itens_coletados = set()

    if mouse_pos is None:
        mouse_pos = pygame.mouse.get_pos()

    # TELA INICIAL

    if tela_atual == "inicio":

        janela.blit(imagens["inicio"], (0, 0))

        # ANABELLE NO QUARTO

        if estado is not None and estado.get("anabelle_no_farol", False):

            imagem_anabelle = imagens["anabelle"]

            janela.blit(
                imagem_anabelle,
                (
                    int(janela.get_width() * POSICAO_ANABELLE_QUARTO[0])
                    - imagem_anabelle.get_width() // 2,

                    int(janela.get_height() * POSICAO_ANABELLE_QUARTO[1])
                    - imagem_anabelle.get_height() // 2
                )
            )

        desenhar_botao(
            janela,
            fontes,
            botoes["esquerda"],
            "IR PARA A PORTA",
            ROXO
        )

        desenhar_botao(
            janela,
            fontes,
            botoes["direita"],
            "IR PARA O CONTROLE DO FAROL",
            ROXO_CLARO
        )

    # TELA DA PORTA

    elif tela_atual == "porta":

        janela.blit(imagens["cenario"], (0, 0))

        # DESENHAR FANTASMA NA PORTA

        if estado is not None:

            fantasma = estado.get("fantasma_na_porta")

            if fantasma in ("rosabella", "anabelle", "ben"):

                imagem_fantasma = imagens[fantasma]

                janela.blit(
                    imagem_fantasma,
                    (
                        janela.get_width() // 2
                        - imagem_fantasma.get_width() // 2,

                        janela.get_height() // 2
                        - imagem_fantasma.get_height() // 2
                    )
                )

        # SOBREPOSIÇÃO DA PORTA

        janela.blit(
            imagens["sobreposicao_porta"],
            (0, 0)
        )

        desenhar_botao(
            janela,
            fontes,
            botoes["esquerda"],
            "IR PARA O QUARTO",
            ROXO
        )

        desenhar_botao(
            janela,
            fontes,
            botoes["direita"],
            "IR PARA O CONTROLE DO FAROL",
            ROXO_CLARO
        )

    # TELA DO CONTROLE DO FAROL

    elif tela_atual == "controle":

        janela.blit(imagens["controle"], (0, 0))

        # ROSABELLA NO CENÁRIO DO FAROL

        if estado is not None and estado.get("rosabella_no_farol", False):

            imagem_rosabella = imagens["rosabella_farol"]

            janela.blit(
                imagem_rosabella,
                (
                    janela.get_width() // 2
                    - imagem_rosabella.get_width() // 2,

                    janela.get_height() // 2
                    - imagem_rosabella.get_height() // 2
                )
            )

        # ANABELLE NO CENÁRIO DO FAROL

        if estado is not None and estado.get("anabelle_no_farol", False):

            imagem_anabelle = imagens["anabelle"]

            janela.blit(
                imagem_anabelle,
                (
                    int(janela.get_width() * 0.33)
                    - imagem_anabelle.get_width() // 2,

                    janela.get_height() // 2
                    - imagem_anabelle.get_height() // 2
                )
            )

        desenhar_botao(
            janela,
            fontes,
            botoes["esquerda"],
            "IR PARA O QUARTO",
            ROXO
        )

        desenhar_botao(
            janela,
            fontes,
            botoes["direita"],
            "IR PARA A PORTA",
            ROXO_CLARO
        )

    # DESENHAR ITENS DISPONÍVEIS NO CENÁRIO

    if itens is not None:

        desenhar_itens_cenario(
            janela,
            tela_atual,
            itens,
            itens_coletados,
            mouse_pos
        )