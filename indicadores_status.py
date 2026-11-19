
import pygame

from config import (
    BRANCO,
    VERDE,
    VERMELHO
)


# CONFIGURAÇÕES DOS INDICADORES

DURACAO_INDICADOR = 1800

indicadores_status = []


# REGISTRAR ALTERAÇÃO DE STATUS

def registrar_alteracao(atributo, pontos):

    if pontos == 0:
        return

    indicadores_status.append({

        "atributo": atributo,
        "pontos": pontos,
        "inicio": pygame.time.get_ticks()

    })


# DESENHAR INDICADORES NA TELA

def desenhar_indicadores(janela, fonte):

    tempo_atual = pygame.time.get_ticks()

    y = 30

    for indicador in indicadores_status[:]:

        tempo_passado = tempo_atual - indicador["inicio"]

        # REMOVER INDICADORES EXPIRADOS

        if tempo_passado >= DURACAO_INDICADOR:

            indicadores_status.remove(indicador)
            continue

        # DEFINIR COR E SINAL

        pontos = indicador["pontos"]

        if pontos > 0:
            cor = VERDE
            sinal = "+"

        else:
            cor = VERMELHO
            sinal = ""

        # MONTAR TEXTO

        texto = (
            f'{indicador["atributo"]}: '
            f'{sinal}{pontos} pontos'
        )

        imagem_texto = fonte.render(
            texto,
            True,
            cor
        )

        # DESENHAR NO CANTO SUPERIOR ESQUERDO

        janela.blit(
            imagem_texto,
            (30, y)
        )

        y += 35
