
import pygame

from config import (
    BRANCO,
    ROXO,
    ROXO_CLARO,
    PRETO,
    CAMINHO_TITULO_MENU
)


# IMAGEM DO TÍTULO DO MENU

imagem_titulo_menu = None


# CRIAR BOTÕES DO MENU

def criar_botoes_menu(largura, altura):

    return {

        "controles": pygame.Rect(
            largura // 2 - 200,
            altura // 2 - 95,
            400,
            70
        ),

        "recomecar": pygame.Rect(
            largura // 2 - 200,
            altura // 2 - 5,
            400,
            70
        ),

        "fechar": pygame.Rect(
            largura // 2 - 200,
            altura // 2 + 85,
            400,
            70
        ),
    }


# DESENHAR MENU DO JOGO

def desenhar_menu(janela, fontes, botoes):

    global imagem_titulo_menu

    largura, altura = janela.get_size()

    # SOMBRA DO MENU

    sombra = pygame.Surface(janela.get_size())
    sombra.set_alpha(180)
    sombra.fill(PRETO)

    janela.blit(sombra, (0, 0))

    # CARREGAR IMAGEM DO TÍTULO

    if imagem_titulo_menu is None:

        imagem_original = pygame.image.load(
            CAMINHO_TITULO_MENU
        ).convert_alpha()

        # AJUSTAR TAMANHO SEM DISTORCER A IMAGEM

        largura_maxima = 700
        altura_maxima = 200

        proporcao = min(
            largura_maxima / imagem_original.get_width(),
            altura_maxima / imagem_original.get_height()
        )

        novo_tamanho = (
            int(imagem_original.get_width() * proporcao),
            int(imagem_original.get_height() * proporcao)
        )

        imagem_titulo_menu = pygame.transform.smoothscale(
            imagem_original,
            novo_tamanho
        )

    # DESENHAR IMAGEM DO TÍTULO

    janela.blit(
        imagem_titulo_menu,
        imagem_titulo_menu.get_rect(
            center=(
                largura // 2,
                altura // 2 - 240
            )
        )
    )

    # BOTÃO CONTROLES DO JOGO

    pygame.draw.rect(
        janela,
        ROXO,
        botoes["controles"],
        border_radius=15
    )

    texto_controles = fontes["normal"].render(
        "CONTROLES DO JOGO",
        True,
        BRANCO
    )

    janela.blit(
        texto_controles,
        texto_controles.get_rect(
            center=botoes["controles"].center
        )
    )

    # BOTÃO RECOMEÇAR DO ZERO

    pygame.draw.rect(
        janela,
        ROXO,
        botoes["recomecar"],
        border_radius=15
    )

    texto_recomecar = fontes["normal"].render(
        "RECOMEÇAR JOGO",
        True,
        BRANCO
    )

    janela.blit(
        texto_recomecar,
        texto_recomecar.get_rect(
            center=botoes["recomecar"].center
        )
    )

    # BOTÃO FECHAR

    pygame.draw.rect(
        janela,
        ROXO_CLARO,
        botoes["fechar"],
        border_radius=15
    )

    texto_fechar = fontes["normal"].render(
        "FECHAR JOGO",
        True,
        BRANCO
    )

    janela.blit(
        texto_fechar,
        texto_fechar.get_rect(
            center=botoes["fechar"].center
        )
    )


# CRIAR BOTÃO VOLTAR DOS CONTROLES

def criar_botao_voltar_controles(largura, altura):

    return pygame.Rect(
        largura // 2 - 150,
        altura - 150,
        300,
        65
    )


# DESENHAR TELA DE CONTROLES

def desenhar_controles(janela, fontes, botao_voltar):

    largura, altura = janela.get_size()

    # FUNDO ESCURECIDO

    sombra = pygame.Surface(janela.get_size())
    sombra.set_alpha(245)
    sombra.fill(PRETO)

    janela.blit(sombra, (0, 0))

    # TÍTULO

    titulo = fontes["titulo"].render(
        "CONTROLES DO JOGO",
        True,
        BRANCO
    )

    janela.blit(
        titulo,
        titulo.get_rect(
            center=(largura // 2, 180)
        )
    )

    # COMANDOS

    controles = [
        ("M", "Abrir ou fechar o menu"),
        ("J", "Abrir ou fechar o diário"),
        ("SETAS", "Navegar pelas páginas do diário"),
        ("TAB", "Abrir ou fechar o inventário"),
        ("SHIFT", "Visualizar os indicadores de status"),
        ("E", "Interagir com os itens"),
        ("C", "Entrar no modo de combate"),
        ("ESC", "Voltar ou alternar a tela"),
    ]

    posicao_y = 300

    for tecla, descricao in controles:

        texto = fontes["negrito"].render(
            f"{tecla}  -  {descricao}",
            True,
            BRANCO
        )

        janela.blit(
            texto,
            texto.get_rect(
                center=(largura // 2, posicao_y)
            )
        )

        posicao_y += 55

    # BOTÃO VOLTAR

    pygame.draw.rect(
        janela,
        ROXO_CLARO,
        botao_voltar,
        border_radius=15
    )

    texto_voltar = fontes["negrito"].render(
        "VOLTAR",
        True,
        BRANCO
    )

    janela.blit(
        texto_voltar,
        texto_voltar.get_rect(
            center=botao_voltar.center
        )
    )
