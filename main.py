
import pygame
import traceback
import os

from jogo import executar_jogo


if __name__ == "__main__":

    try:
        pygame.init()
        executar_jogo()

    except Exception:

        caminho_erro = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "erro_diario.txt"
        )

        with open(
            caminho_erro,
            "w",
            encoding="utf-8"
        ) as arquivo:

            traceback.print_exc(file=arquivo)

        print("Ocorreu um erro! Confira o arquivo erro_diario.txt.")

    finally:
        pygame.quit()
