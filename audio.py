
import pygame
import os


# CAMINHOS DAS MÚSICAS

CAMINHO_MUSICA_MENU = (
    r"C:\Users\maria\Downloads\som_mar.mp3"
)


# CONTROLE DO ÁUDIO

musica_menu_carregada = False
musica_menu_ativa = False


# CARREGAR OS ÁUDIOS

def carregar_audios():

    global musica_menu_carregada

    if pygame.mixer.get_init() is None:
        pygame.mixer.init()

    try:

        if not os.path.exists(CAMINHO_MUSICA_MENU):
            raise FileNotFoundError(CAMINHO_MUSICA_MENU)

        pygame.mixer.music.load(CAMINHO_MUSICA_MENU)

        musica_menu_carregada = True

    except (pygame.error, FileNotFoundError) as erro:

        print(f"Erro ao carregar música do menu: {erro}")

        musica_menu_carregada = False


# INICIAR MÚSICA DO MENU

def iniciar_musica_menu():

    global musica_menu_ativa

    if not musica_menu_carregada:
        return

    if musica_menu_ativa:
        return

    pygame.mixer.music.play(-1)

    pygame.mixer.music.set_volume(0.4)

    musica_menu_ativa = True


# PARAR MÚSICA DO MENU

def parar_musica_menu():

    global musica_menu_ativa

    if musica_menu_ativa:

        pygame.mixer.music.stop()

        musica_menu_ativa = False


# ATUALIZAR ÁUDIO CONFORME A TELA

def atualizar_audio(menu_aberto):

    if menu_aberto:

        iniciar_musica_menu()

    else:

        parar_musica_menu()


# ENCERRAR ÁUDIO

# ENCERRAR ÁUDIO

def finalizar_audio():

    global musica_menu_ativa

    if pygame.mixer.get_init() is not None:

        pygame.mixer.music.stop()

        pygame.mixer.music.unload()

    musica_menu_ativa = False
