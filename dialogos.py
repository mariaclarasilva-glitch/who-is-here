import pygame


# CORES DA CAIXA DE DIÁLOGO

COR_FUNDO = (20, 14, 30)
COR_BORDA = (130, 85, 155)
COR_TEXTO = (245, 240, 250)
COR_SELECIONADA = (115, 65, 145)
COR_DICA = (205, 175, 230)

# TEXTO QUE APARECE EM NEGRITO, UMA LINHA ABAIXO DA FALA

PREFIXO_DICA = "Pressione ENTER"

_fonte_negrito = None


# FONTE EM NEGRITO PARA A DICA (CRIADA UMA SÓ VEZ)

def obter_fonte_negrito():

    global _fonte_negrito

    if _fonte_negrito is None:
        _fonte_negrito = pygame.font.SysFont("arial", 26, bold=True)

    return _fonte_negrito


# QUEBRAR UM PARÁGRAFO EM LINHAS QUE CABEM NA CAIXA

def quebrar_linhas(fonte, texto, largura_maxima):

    linhas = []
    linha_atual = ""

    for palavra in texto.split():

        teste = linha_atual + (" " if linha_atual else "") + palavra

        if fonte.size(teste)[0] <= largura_maxima:

            linha_atual = teste

        else:

            if linha_atual:
                linhas.append(linha_atual)

            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas



# CRIAR CAIXA DE DIÁLOGO

def desenhar_dialogo(janela, fontes, nome, pergunta, opcoes, opcao_selecionada):

    largura, altura = janela.get_size()

    caixa = pygame.Rect(
        int(largura * 0.08),
        int(altura * 0.58),
        int(largura * 0.84),
        int(altura * 0.38)
    )

    # FUNDO DA CAIXA

    fundo = pygame.Surface(
        (caixa.width, caixa.height),
        pygame.SRCALPHA
    )

    fundo.fill((*COR_FUNDO, 240))
    janela.blit(fundo, caixa.topleft)

    pygame.draw.rect(
        janela,
        COR_BORDA,
        caixa,
        3,
        border_radius=15
    )

    # NOME DO FANTASMA (FONTE MENOR)

    fonte_nome = pygame.font.Font(
        None,
        40
    )

    texto_nome = fonte_nome.render(
        nome,
        True,
        COR_TEXTO
    )

    janela.blit(
        texto_nome,
        (caixa.x + 25, caixa.y + 10)
    )

    # TEXTO DO DIÁLOGO COM QUEBRA AUTOMÁTICA DE LINHA
    # AS QUEBRAS DE PARÁGRAFO (\n) SÃO RESPEITADAS

    largura_maxima = caixa.width - 50

    pos_y = caixa.y + 55

    for paragrafo in pergunta.split("\n"):

        # LINHA EM BRANCO ENTRE OS PARÁGRAFOS

        if paragrafo.strip() == "":

            pos_y += 14
            continue

        # DICA "PRESSIONE ENTER": NEGRITO, UMA LINHA ABAIXO DA FALA

        if paragrafo.startswith(PREFIXO_DICA):

            fonte = obter_fonte_negrito()
            cor = COR_DICA
            pos_y += 6

        else:

            fonte = fontes["normal"]
            cor = COR_TEXTO

        for linha in quebrar_linhas(fonte, paragrafo, largura_maxima):

            texto = fonte.render(
                linha,
                True,
                cor
            )

            janela.blit(
                texto,
                (caixa.x + 25, pos_y)
            )

            pos_y += 28

    # OPÇÕES

    for indice, opcao in enumerate(opcoes):

        area_opcao = pygame.Rect(
            caixa.x + 20,
            pos_y + 5 + indice * 35,
            caixa.width - 40,
            32
        )

        if indice == opcao_selecionada:

            pygame.draw.rect(
                janela,
                COR_SELECIONADA,
                area_opcao,
                border_radius=7
            )

        texto_opcao = fontes["normal"].render(
            opcao,
            True,
            COR_TEXTO
        )

        janela.blit(
            texto_opcao,
            (area_opcao.x + 12, area_opcao.y + 4)
        )


# OPÇÕES DISPONÍVEIS DURANTE O ENCONTRO

OPCOES_FANTASMA = [
    "Fazer uma pergunta",
    "Deixar entrar",
    "Expulsar"
]

# O BEN NÃO PODE SER EXPULSO

OPCOES_BEN = [
    "Fazer uma pergunta",
    "Deixar entrar"
]


# INICIAR DIÁLOGO COM O FANTASMA

def iniciar_dialogo(estado, fantasma):

    opcoes = OPCOES_BEN if fantasma == "ben" else OPCOES_FANTASMA

    estado["dialogo_fantasma"] = {
        "fantasma": fantasma,
        "etapa": "opcoes",
        "opcao_selecionada": 0,
        "opcoes": opcoes.copy(),
        "texto": ""
    }

    # REGISTRAR PRIMEIRA INTERAÇÃO COM ROSABELLA

    if fantasma == "rosabella":
        if not estado.get("primeiro_contato_rosabella", False):
            estado["primeiro_contato_rosabella"] = True


# MOSTRAR A PERGUNTA E A RESPOSTA DO FANTASMA

def mostrar_resposta(estado, dados):

    dialogo = estado.get("dialogo_fantasma")

    if dialogo is None:
        return

    dialogo["etapa"] = "resposta"

    dialogo["texto"] = (
        dados["pergunta"] + "\n\n" + dados["resposta"]
    )


# ENCERRAR DIÁLOGO

def encerrar_dialogo(estado):

    estado["dialogo_fantasma"] = None