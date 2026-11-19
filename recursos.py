
import pygame

from ben import carregar_imagem_ben

from config import (
    CAMINHO_INICIO,
    CAMINHO_CENARIO,
    CAMINHO_CONTROLE,
    CAMINHOS_ITENS,
    CAMINHO_DIARIO_ABERTO,
    CAMINHO_SALVAR_DIA,
    CAMINHO_ROSABELLA,
    CAMINHO_ROSABELLA_FAROL,
    CAMINHO_ANABELLE,
    CAMINHO_SOBREPOSICAO_PORTA
)


def carregar_recursos():

    # INICIALIZAR FONTES

    pygame.font.init()

    # CARREGAR IMAGENS DOS CENÁRIOS

    imagens = {
        "inicio_original": pygame.image.load(
            CAMINHO_INICIO
        ),

        "cenario_original": pygame.image.load(
            CAMINHO_CENARIO
        ),

        "controle_original": pygame.image.load(
            CAMINHO_CONTROLE
        ),

        "rosabella_original": pygame.image.load(
            CAMINHO_ROSABELLA
        ).convert_alpha(),

        "rosabella_farol_original": pygame.image.load(
            CAMINHO_ROSABELLA_FAROL
        ).convert_alpha(),

        "anabelle_original": pygame.image.load(
            CAMINHO_ANABELLE
        ).convert_alpha(),

        # BEN BONZINHO

        "ben_original": carregar_imagem_ben("bem"),

        "sobreposicao_porta_original": pygame.image.load(
            CAMINHO_SOBREPOSICAO_PORTA
        ).convert_alpha(),

        # DIÁRIO ABERTO

        "diario_original": pygame.image.load(
            CAMINHO_DIARIO_ABERTO
        ).convert_alpha(),

        # BOTÃO DE SALVAR O DIA

        "salvar_dia_original": pygame.image.load(
            CAMINHO_SALVAR_DIA
        ).convert_alpha(),
    }

    # CARREGAR ITENS DO INVENTÁRIO

    itens = {}

    for nome, caminho in CAMINHOS_ITENS.items():

        itens[nome] = pygame.image.load(caminho)

    # CARREGAR FONTES

    fontes = {
        "normal": pygame.font.SysFont("arial", 26),
        "titulo": pygame.font.SysFont("arial", 60),
        "item": pygame.font.SysFont("arial", 23),
        "pequena": pygame.font.SysFont("arial", 18),
        "negrito": pygame.font.SysFont("arial", 26, bold=True),
    }

    # RETORNAR TODOS OS RECURSOS

    return {
        "imagens": imagens,
        "itens": itens,
        "fontes": fontes,
    }


# AJUSTAR IMAGENS AO TAMANHO DA JANELA

def atualizar_imagens(janela, recursos):

    tamanho = janela.get_size()
    imagens = recursos["imagens"]

    # REDIMENSIONAR DIÁRIO

    largura_diario = int(tamanho[0] * 0.82)

    proporcao = (
        imagens["diario_original"].get_height()
        / imagens["diario_original"].get_width()
    )

    altura_diario = int(largura_diario * proporcao)

    diario = pygame.transform.smoothscale(
        imagens["diario_original"],
        (largura_diario, altura_diario)
    )

    # REDIMENSIONAR BOTÃO DE SALVAR O DIA

    largura_botao = int(tamanho[0] * 0.14)

    proporcao_botao = (
        imagens["salvar_dia_original"].get_height()
        / imagens["salvar_dia_original"].get_width()
    )

    altura_botao = int(largura_botao * proporcao_botao)

    botao_salvar = pygame.transform.smoothscale(
        imagens["salvar_dia_original"],
        (largura_botao, altura_botao)
    )

    # BEN NA PORTA

    ben_original = imagens["ben_original"]

    if ben_original is not None:

        altura_ben = 450

        largura_ben = max(
            1,
            int(
                ben_original.get_width() * altura_ben
                / ben_original.get_height()
            )
        )

        ben_porta = pygame.transform.smoothscale(
            ben_original,
            (largura_ben, altura_ben)
        )

    else:

        # DESENHAR UM VULTO CASO A IMAGEM NÃO EXISTA

        ben_porta = pygame.Surface(
            (300, 450),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            ben_porta,
            (200, 200, 230),
            ben_porta.get_rect()
        )

    # RETORNAR IMAGENS REDIMENSIONADAS

    return {
        "inicio": pygame.transform.scale(
            imagens["inicio_original"], tamanho
        ),

        "cenario": pygame.transform.scale(
            imagens["cenario_original"], tamanho
        ),

        "controle": pygame.transform.scale(
            imagens["controle_original"], tamanho
        ),

        "rosabella": pygame.transform.scale(
            imagens["rosabella_original"],
            (300, 450)
        ),

        "rosabella_farol": pygame.transform.scale(
            imagens["rosabella_farol_original"],
            (300, 450)
        ),

        "anabelle": pygame.transform.scale(
            imagens["anabelle_original"],
            (300, 450)
        ),

        "ben": ben_porta,

        "sobreposicao_porta": pygame.transform.scale(
            imagens["sobreposicao_porta_original"],
            tamanho
        ),

        "diario": diario,
        "salvar_dia": botao_salvar,
    }
