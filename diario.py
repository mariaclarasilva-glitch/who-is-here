import pygame

from config import BRANCO, PRETO
from dados_diario import PAGINAS_DIARIO


# CORES UTILIZADAS NO DIÁRIO

TEXTO = (65, 45, 30)
DETALHE = (105, 75, 48)
FUNDO_CONFIRMACAO = (25, 20, 30)
PAINEL_CONFIRMACAO = (235, 225, 205)
BOTAO_CONFIRMAR = (75, 110, 75)
BOTAO_CANCELAR = (130, 65, 65)


# CONFIGURAÇÃO DO TEXTO NAS PÁGINAS
# Valores proporcionais ao tamanho da imagem do diário.
# Isso mantém o posicionamento correto mesmo se a janela mudar de tamanho.

LIMITE_ESQUERDA_INICIO = 0.129
LIMITE_ESQUERDA_FIM = 0.445

LIMITE_DIREITA_INICIO = 0.515
LIMITE_DIREITA_FIM = 0.855

LIMITE_TEXTO_TOPO = 0.075
LIMITE_TEXTO_BASE = 0.855

# Margens internas do texto, em proporção da página.

MARGEM_TEXTO_X = 0.045
MARGEM_TEXTO_Y = 0.035

# Tamanhos das fontes.

TAMANHO_DATA = 17
TAMANHO_TITULO = 24
TAMANHO_TEXTO = 19

TAMANHO_MINIMO_DATA = 13
TAMANHO_MINIMO_TITULO = 16
TAMANHO_MINIMO_TEXTO = 14


# QUEBRAR TEXTOS EM VÁRIAS LINHAS

def quebrar_texto(texto, fonte, largura_maxima):

    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:

        if fonte.size(palavra)[0] > largura_maxima:

            if linha_atual:
                linhas.append(linha_atual)
                linha_atual = ""

            parte_atual = ""

            for caractere in palavra:

                teste = parte_atual + caractere

                if fonte.size(teste)[0] <= largura_maxima:
                    parte_atual = teste

                else:
                    if parte_atual:
                        linhas.append(parte_atual)

                    parte_atual = caractere

            linha_atual = parte_atual
            continue

        teste = (
            linha_atual + " " + palavra
            if linha_atual else palavra
        )

        if fonte.size(teste)[0] <= largura_maxima:
            linha_atual = teste

        else:
            if linha_atual:
                linhas.append(linha_atual)

            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas


# CALCULAR A POSIÇÃO DO DIÁRIO NA TELA

def obter_posicao_diario(janela, imagem_diario):

    largura, altura = janela.get_size()

    x = (largura - imagem_diario.get_width()) // 2
    y = (altura - imagem_diario.get_height()) // 2

    return x, y


# CALCULAR A ÁREA DO BOTÃO DE SALVAR

def obter_area_botao_salvar(janela, imagem_diario, imagem_salvar):

    x_diario, y_diario = obter_posicao_diario(
        janela, imagem_diario
    )

    largura_diario = imagem_diario.get_width()
    altura_diario = imagem_diario.get_height()

    largura_botao = imagem_salvar.get_width()
    altura_botao = imagem_salvar.get_height()

    x = x_diario + int(largura_diario * 0.68)
    y = y_diario + int(altura_diario * 0.78)

    return pygame.Rect(
        x,
        y,
        largura_botao,
        altura_botao
    )


# CALCULAR AS ÁREAS DE TEXTO DAS DUAS PÁGINAS

def obter_areas_paginas(x_diario, y_diario, imagem_diario):

    largura = imagem_diario.get_width()
    altura = imagem_diario.get_height()

    topo = y_diario + int(altura * LIMITE_TEXTO_TOPO)
    base = y_diario + int(altura * LIMITE_TEXTO_BASE)
    altura_texto = base - topo

    esquerda = pygame.Rect(
        x_diario + int(largura * LIMITE_ESQUERDA_INICIO),
        topo,
        int(largura * (
            LIMITE_ESQUERDA_FIM - LIMITE_ESQUERDA_INICIO
        )),
        altura_texto
    )

    direita = pygame.Rect(
        x_diario + int(largura * LIMITE_DIREITA_INICIO),
        topo,
        int(largura * (
            LIMITE_DIREITA_FIM - LIMITE_DIREITA_INICIO
        )),
        altura_texto
    )

    return esquerda, direita


# CALCULAR A POSIÇÃO DOS BOTÕES DE CONFIRMAÇÃO

def obter_botoes_confirmacao(janela):

    largura, altura = janela.get_size()

    largura_botao = 220
    altura_botao = 65

    y = altura // 2 + 55

    botao_cancelar = pygame.Rect(
        largura // 2 - largura_botao - 15,
        y,
        largura_botao,
        altura_botao
    )

    botao_confirmar = pygame.Rect(
        largura // 2 + 15,
        y,
        largura_botao,
        altura_botao
    )

    return botao_cancelar, botao_confirmar


# DESENHAR UMA ANOTAÇÃO NO DIÁRIO

def desenhar_anotacao(janela, dados, area, dia_atual):

    # MARGENS INTERNAS DA PÁGINA

    margem_x = max(8, int(area.width * MARGEM_TEXTO_X))
    margem_y = max(6, int(area.height * MARGEM_TEXTO_Y))

    x = area.x + margem_x
    y_inicial = area.y + margem_y

    largura_texto = area.width - margem_x * 2
    altura_texto = area.height - margem_y * 2

    # AJUSTAR FONTES PARA QUE TODO O CONTEÚDO CAIBA

    tamanho_data = TAMANHO_DATA
    tamanho_titulo = TAMANHO_TITULO
    tamanho_texto = TAMANHO_TEXTO

    while True:

        fonte_data = pygame.font.SysFont(
            "arial", tamanho_data, bold=True
        )

        fonte_titulo = pygame.font.SysFont(
            "arial", tamanho_titulo, bold=True
        )

        fonte_texto = pygame.font.SysFont(
            "arial", tamanho_texto
        )

        linhas_data = quebrar_texto(
            f"DIA {dia_atual} | {dados['data']}",
            fonte_data,
            largura_texto
        )

        linhas_hora = quebrar_texto(
            dados["hora"],
            fonte_data,
            largura_texto
        )

        linhas_titulo = quebrar_texto(
            dados["titulo"],
            fonte_titulo,
            largura_texto
        )

        linhas_anotacao = quebrar_texto(
            dados["texto"],
            fonte_texto,
            largura_texto
        )

        altura_data = len(linhas_data) * (
            fonte_data.get_linesize() + 2
        )

        altura_hora = len(linhas_hora) * (
            fonte_data.get_linesize() + 2
        )

        altura_titulo = len(linhas_titulo) * (
            fonte_titulo.get_linesize() + 3
        )

        altura_anotacao = len(linhas_anotacao) * (
            fonte_texto.get_linesize() + 4
        )

        altura_total = (
            altura_data
            + 4
            + altura_hora
            + 9
            + altura_titulo
            + 10
            + altura_anotacao
        )

        if altura_total <= altura_texto:
            break

        if (
            tamanho_texto > TAMANHO_MINIMO_TEXTO
            or tamanho_titulo > TAMANHO_MINIMO_TITULO
            or tamanho_data > TAMANHO_MINIMO_DATA
        ):

            if tamanho_texto > TAMANHO_MINIMO_TEXTO:
                tamanho_texto -= 1

            elif tamanho_titulo > TAMANHO_MINIMO_TITULO:
                tamanho_titulo -= 1

            elif tamanho_data > TAMANHO_MINIMO_DATA:
                tamanho_data -= 1

        else:
            # Último recurso: manter o texto legível e usar o recorte
            # da página para impedir que ele invada a outra página.
            break

    # LIMITAR O DESENHO À ÁREA INTERNA DA PÁGINA

    recorte_anterior = janela.get_clip()
    janela.set_clip(area)

    y = y_inicial

    # DATA

    for linha in linhas_data:

        texto_data = fonte_data.render(
            linha,
            True,
            DETALHE
        )

        janela.blit(texto_data, (x, y))
        y += fonte_data.get_linesize() + 2

    y += 4

    # HORÁRIO

    for linha in linhas_hora:

        texto_hora = fonte_data.render(
            linha,
            True,
            DETALHE
        )

        janela.blit(texto_hora, (x, y))
        y += fonte_data.get_linesize() + 2

    y += 9

    # TÍTULO

    for linha in linhas_titulo:

        texto_titulo = fonte_titulo.render(
            linha,
            True,
            TEXTO
        )

        janela.blit(texto_titulo, (x, y))
        y += fonte_titulo.get_linesize() + 3

    y += 10

    # TEXTO DA ANOTAÇÃO

    for linha in linhas_anotacao:

        texto = fonte_texto.render(
            linha,
            True,
            TEXTO
        )

        janela.blit(texto, (x, y))
        y += fonte_texto.get_linesize() + 4

    # RESTAURAR A ÁREA DE DESENHO ANTERIOR

    janela.set_clip(recorte_anterior)


# DESENHAR A CONFIRMAÇÃO DE ENCERRAMENTO

def desenhar_confirmacao(janela):

    largura, altura = janela.get_size()

    # ESCURECER O FUNDO

    camada = pygame.Surface(
        (largura, altura),
        pygame.SRCALPHA
    )

    camada.fill((0, 0, 0, 180))
    janela.blit(camada, (0, 0))

    # PAINEL

    painel = pygame.Rect(
        largura // 2 - 390,
        altura // 2 - 150,
        780,
        300
    )

    pygame.draw.rect(
        janela,
        PAINEL_CONFIRMACAO,
        painel,
        border_radius=15
    )

    pygame.draw.rect(
        janela,
        DETALHE,
        painel,
        width=3,
        border_radius=15
    )

    # TEXTO PRINCIPAL

    fonte_titulo = pygame.font.SysFont(
        "arial", 35, bold=True
    )

    titulo = fonte_titulo.render(
        "ENCERRAR O DIA?",
        True,
        TEXTO
    )

    janela.blit(
        titulo,
        titulo.get_rect(
            center=(largura // 2, altura // 2 - 75)
        )
    )

    # TEXTO EXPLICATIVO

    fonte_texto = pygame.font.SysFont("arial", 23)

    mensagem = fonte_texto.render(
        "Seu progresso será salvo e o próximo dia começará.",
        True,
        TEXTO
    )

    janela.blit(
        mensagem,
        mensagem.get_rect(
            center=(largura // 2, altura // 2 - 20)
        )
    )

    # BOTÕES

    botao_cancelar, botao_confirmar = obter_botoes_confirmacao(
        janela
    )

    pygame.draw.rect(
        janela,
        BOTAO_CANCELAR,
        botao_cancelar,
        border_radius=8
    )

    pygame.draw.rect(
        janela,
        BOTAO_CONFIRMAR,
        botao_confirmar,
        border_radius=8
    )

    fonte_botao = pygame.font.SysFont(
        "arial", 24, bold=True
    )

    texto_cancelar = fonte_botao.render(
        "CANCELAR",
        True,
        BRANCO
    )

    texto_confirmar = fonte_botao.render(
        "CONFIRMAR",
        True,
        BRANCO
    )

    janela.blit(
        texto_cancelar,
        texto_cancelar.get_rect(
            center=botao_cancelar.center
        )
    )

    janela.blit(
        texto_confirmar,
        texto_confirmar.get_rect(
            center=botao_confirmar.center
        )
    )


# DESENHAR O DIÁRIO COMPLETO

def desenhar_diario(
    janela,
    pagina_atual,
    imagem_diario,
    imagem_salvar,
    dia_atual,
    confirmacao_aberta=False,
    paginas_diario=None
):

    largura, altura = janela.get_size()

    # UTILIZAR A LISTA DE ANOTAÇÕES RECEBIDA

    if paginas_diario is None:
        paginas_diario = PAGINAS_DIARIO

    # ESCURECER O JOGO AO FUNDO

    camada = pygame.Surface(
        (largura, altura),
        pygame.SRCALPHA
    )

    camada.fill((0, 0, 0, 150))
    janela.blit(camada, (0, 0))

    # POSICIONAR O DIÁRIO

    x_diario, y_diario = obter_posicao_diario(
        janela, imagem_diario
    )

    janela.blit(
        imagem_diario,
        (x_diario, y_diario)
    )

    # CALCULAR AS ÁREAS SEGURAS DAS DUAS PÁGINAS

    pagina_esquerda, pagina_direita = obter_areas_paginas(
        x_diario,
        y_diario,
        imagem_diario
    )

    # DESENHAR AS ANOTAÇÕES

    if pagina_atual < len(paginas_diario):

        desenhar_anotacao(
            janela,
            paginas_diario[pagina_atual],
            pagina_esquerda,
            dia_atual
        )

    if pagina_atual + 1 < len(paginas_diario):

        desenhar_anotacao(
            janela,
            paginas_diario[pagina_atual + 1],
            pagina_direita,
            dia_atual
        )

    # DESENHAR BOTÃO DE SALVAR

    area_botao = obter_area_botao_salvar(
        janela,
        imagem_diario,
        imagem_salvar
    )

    janela.blit(
        imagem_salvar,
        area_botao.topleft
    )

    # INSTRUÇÕES

    fonte_instrucoes = pygame.font.SysFont(
        "arial", 19, bold=True
    )

    instrucoes = fonte_instrucoes.render(
        "SETAS: NAVEGAR     J OU ESC: FECHAR",
        True,
        BRANCO
    )

    janela.blit(
        instrucoes,
        instrucoes.get_rect(
            center=(largura // 2, altura - 30)
        )
    )

    # MOSTRAR CONFIRMAÇÃO SE ESTIVER ABERTA

    if confirmacao_aberta:
        desenhar_confirmacao(janela)
