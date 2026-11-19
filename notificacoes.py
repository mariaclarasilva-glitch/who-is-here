import pygame


# CORES DAS CATEGORIAS DE NOTIFICAÇÃO

CORES_CATEGORIAS = {
    "observacao": {
        "titulo": "OBSERVAÇÃO",
        "cor": (201, 168, 255),
        "icone": "i"
    },
    "descoberta": {
        "titulo": "DESCOBERTA",
        "cor": (165, 200, 255),
        "icone": "?"
    },
    "atencao": {
        "titulo": "ATENÇÃO",
        "cor": (233, 189, 131),
        "icone": "!"
    },
    "acontecimento": {
        "titulo": "ACONTECIMENTO",
        "cor": (182, 160, 213),
        "icone": "*"
    },
    "perigo": {
        "titulo": "PERIGO",
        "cor": (235, 75, 85),
        "icone": "!"
    }
}


# CONFIGURAÇÕES VISUAIS E DE TEMPO

DURACAO_PADRAO = 2500
DURACAO_TRANSICAO = 350
LARGURA_NOTIFICACAO = 430
MARGEM_NOTIFICACAO = 35


def adicionar_notificacao(
    estado,
    mensagem,
    categoria="observacao",
    importante=False,
    duracao=DURACAO_PADRAO
):
    """
    Adiciona uma mensagem à fila.

    importante fica guardado para a futura integração com o diário.
    A gravação no diário será conectada junto ao sistema de eventos.
    """

    if not isinstance(mensagem, str) or not mensagem.strip():
        return False

    if categoria not in CORES_CATEGORIAS:
        categoria = "observacao"

    notificacao = {
        "mensagem": mensagem.strip(),
        "categoria": categoria,
        "importante": bool(importante),
        "duracao": max(1000, int(duracao))
    }

    estado.setdefault("fila_notificacoes", []).append(notificacao)

    return True


def atualizar_notificacoes(estado, agora):
    """
    Inicia a próxima mensagem quando não existe uma ativa.
    Controla o tempo da mensagem atual sem usar time.sleep.
    """

    if estado.get("notificacao_atual") is None:
        fila = estado.setdefault("fila_notificacoes", [])

        if fila:
            notificacao = fila.pop(0)
            notificacao["inicio"] = agora
            estado["notificacao_atual"] = notificacao
            return

    notificacao = estado.get("notificacao_atual")

    if notificacao is None:
        return

    tempo_decorrido = agora - notificacao["inicio"]
    tempo_total = DURACAO_TRANSICAO * 2 + notificacao["duracao"]

    if tempo_decorrido >= tempo_total:
        estado["notificacao_atual"] = None

        # A próxima mensagem começará no próximo ciclo do jogo.


def obter_transparencia_notificacao(notificacao, agora):
    """Calcula a transparência para entrada e saída suaves."""

    tempo_decorrido = agora - notificacao["inicio"]
    duracao = notificacao["duracao"]

    if tempo_decorrido < DURACAO_TRANSICAO:
        return max(
            0,
            min(255, int(255 * tempo_decorrido / DURACAO_TRANSICAO))
        )

    inicio_saida = DURACAO_TRANSICAO + duracao

    if tempo_decorrido > inicio_saida:
        tempo_saida = tempo_decorrido - inicio_saida
        return max(
            0,
            min(255, 255 - int(255 * tempo_saida / DURACAO_TRANSICAO))
        )

    return 255


def quebrar_mensagem(texto, fonte, largura_maxima):
    """Divide a mensagem em linhas que cabem dentro da caixa."""

    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        teste = palavra if not linha_atual else linha_atual + " " + palavra

        if fonte.size(teste)[0] <= largura_maxima:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas or [""]


def desenhar_notificacoes(janela, estado, agora):
    """Desenha a notificação ativa no canto superior direito."""

    notificacao = estado.get("notificacao_atual")

    if notificacao is None:
        return

    configuracao = CORES_CATEGORIAS.get(
        notificacao["categoria"],
        CORES_CATEGORIAS["observacao"]
    )

    transparencia = obter_transparencia_notificacao(
        notificacao,
        agora
    )

    if transparencia <= 0:
        return

    largura_tela, altura_tela = janela.get_size()
    largura = min(LARGURA_NOTIFICACAO, largura_tela - 40)

    fonte_titulo = pygame.font.Font(None, 27)
    fonte_mensagem = pygame.font.Font(None, 25)

    margem = 20
    largura_texto = largura - margem * 2

    linhas = quebrar_mensagem(
        notificacao["mensagem"],
        fonte_mensagem,
        largura_texto
    )

    altura = 65 + len(linhas) * 27
    altura = min(altura, max(110, altura_tela - 40))

    caixa = pygame.Surface(
        (largura, altura),
        pygame.SRCALPHA
    )

    # FUNDO ESCURO

    pygame.draw.rect(
        caixa,
        (31, 27, 39, transparencia),
        (0, 0, largura, altura),
        border_radius=12
    )

    # CONTORNO DISCRETO NA COR DA CATEGORIA

    cor = configuracao["cor"]

    pygame.draw.rect(
        caixa,
        (*cor, transparencia),
        (0, 0, largura, altura),
        width=2,
        border_radius=12
    )

    # ÍCONE

    fonte_icone = pygame.font.Font(None, 25)
    icone = fonte_icone.render(
        configuracao["icone"],
        True,
        cor
    )
    icone.set_alpha(transparencia)
    caixa.blit(icone, (margem, 16))

    # TÍTULO

    titulo = fonte_titulo.render(
        configuracao["titulo"],
        True,
        cor
    )
    titulo.set_alpha(transparencia)
    caixa.blit(titulo, (margem + 25, 14))

    # MENSAGEM

    y = 48

    for linha in linhas:
        texto = fonte_mensagem.render(
            linha,
            True,
            (245, 242, 248)
        )
        texto.set_alpha(transparencia)
        caixa.blit(texto, (margem, y))
        y += 25

    caixa.set_alpha(transparencia)

    posicao = (
        largura_tela - largura - MARGEM_NOTIFICACAO,
        MARGEM_NOTIFICACAO
    )

    janela.blit(caixa, posicao)
