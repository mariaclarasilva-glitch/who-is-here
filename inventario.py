import pygame

from config import BRANCO, ROXO_CLARO, PRETO


# DESCRIÇÕES DOS OBJETOS

DESCRICOES_ITENS = {
    "Cerveja": (
        "Uma garrafa de cerveja comum. Parece ser uma das poucas formas "
        "que o funcionário encontrou para aliviar o estresse dos longos turnos."
    ),

    "Água benta": (
        "Pequenas quantidades são enviadas mensalmente ao farol. Segundo o "
        "antigo funcionário, é importante mantê-la por perto. Ele próprio "
        "recomendou o envio antes de deixar o cargo.\n\n"
        "Não se sabe ao certo o motivo. Alguns comentários sobre sua devoção "
        "religiosa fizeram os outros funcionários suspeitarem que fosse um "
        "tanto fanático."
    ),

    "Rádio": (
        "Um rádio portátil de aparência antiga. Ainda funciona, embora "
        "apresente interferências frequentes.\n\n"
        "O funcionário costuma utilizá-lo para passar o tempo durante os "
        "turnos. Às vezes, porém, parece haver algo além de música e estática "
        "sendo transmitido."
    ),

    "Óleo": (
        "Um recipiente de óleo utilizado para manter o mecanismo de "
        "iluminação do farol funcionando. É um recurso indispensável para "
        "o trabalho.\n\n"
        "Sem ele, a luz pode enfraquecer — e, naquela região, deixar o farol "
        "apagado não parece uma boa ideia."
    ),
}


# AJUSTAR TAMANHO DOS ITENS

def ajustar_item(imagem, tamanho):

    imagem = imagem.convert_alpha()

    largura_original, altura_original = imagem.get_size()

    if largura_original == 0 or altura_original == 0:
        return imagem

    escala = min(
        tamanho[0] / largura_original,
        tamanho[1] / altura_original
    )

    nova_largura = max(
        1,
        int(largura_original * escala)
    )

    nova_altura = max(
        1,
        int(altura_original * escala)
    )

    return pygame.transform.smoothscale(
        imagem,
        (nova_largura, nova_altura)
    )


# OBTER DESCRIÇÃO DO ITEM

def obter_descricao_item(nome, estado=None):

    descricao = DESCRICOES_ITENS.get(
        nome,
        "Não há informações disponíveis sobre este objeto."
    )

    # FUTURAMENTE, EVENTOS PODERÃO DESBLOQUEAR NOVAS INFORMAÇÕES.

    if estado is not None:

        pistas = estado.get("pistas_itens", {}).get(nome, [])

        for pista in pistas:
            descricao += "\n\n" + pista

    return descricao


# OBTER ÁREA DO BOTÃO USAR

def obter_botao_usar(janela):

    largura, altura = janela.get_size()

    return pygame.Rect(
        largura // 2 - 205,
        altura // 2 + 210,
        180,
        50
    )


# OBTER ÁREA DO BOTÃO EXAMINAR

def obter_botao_examinar(janela):

    largura, altura = janela.get_size()

    return pygame.Rect(
        largura // 2 + 25,
        altura // 2 + 210,
        180,
        50
    )


# OBTER ÁREA DO BOTÃO VOLTAR DA INSPEÇÃO

def obter_botao_voltar_inspecao(janela):

    largura, altura = janela.get_size()

    return pygame.Rect(
        largura // 2 - 120,
        altura // 2 + 285,
        240,
        60
    )


# IDENTIFICAR ITEM CLICADO

def obter_item_clicado(
    itens,
    pos_mouse,
    largura,
    altura
):

    nomes_itens = list(itens.keys())

    for i, nome in enumerate(nomes_itens):

        coluna = i % 2
        linha = i // 2

        x = largura // 2 - 220 + coluna * 260
        y = altura // 2 - 100 + linha * 190

        espaco = pygame.Rect(
            x - 90,
            y - 60,
            180,
            180
        )

        if espaco.collidepoint(pos_mouse):
            return nome

    return None


# DESENHAR BOTÃO DO INVENTÁRIO

def desenhar_botao(janela, fontes, botao, texto):

    pygame.draw.rect(
        janela,
        (110, 65, 140),
        botao,
        border_radius=12
    )

    pygame.draw.rect(
        janela,
        ROXO_CLARO,
        botao,
        2,
        border_radius=12
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


# DESENHAR INVENTÁRIO

def desenhar_inventario(
    janela,
    itens,
    fontes,
    quantidades=None,
    item_selecionado=None
):

    if quantidades is None:
        quantidades = {}

    largura, altura = janela.get_size()

    # SOMBRA DO INVENTÁRIO

    sombra = pygame.Surface(janela.get_size())
    sombra.set_alpha(170)
    sombra.fill(PRETO)
    janela.blit(sombra, (0, 0))

    # PAINEL DO INVENTÁRIO

    painel = pygame.Rect(
        largura // 2 - 450,
        altura // 2 - 300,
        900,
        600
    )

    pygame.draw.rect(
        janela,
        (45, 30, 55),
        painel,
        border_radius=20
    )

    pygame.draw.rect(
        janela,
        ROXO_CLARO,
        painel,
        4,
        border_radius=20
    )

    # TÍTULO

    titulo = fontes["titulo"].render(
        "INVENTÁRIO",
        True,
        BRANCO
    )

    janela.blit(
        titulo,
        titulo.get_rect(
            center=(largura // 2, altura // 2 - 240)
        )
    )

    # ORGANIZAR SOMENTE OS ITENS COLETADOS

    nomes_itens = list(itens.keys())

    # INVENTÁRIO VAZIO

    if not nomes_itens:

        texto_vazio = fontes["normal"].render(
            "Nenhum item coletado ainda.",
            True,
            BRANCO
        )

        janela.blit(
            texto_vazio,
            texto_vazio.get_rect(
                center=(largura // 2, altura // 2)
            )
        )

    # DESENHAR ITENS COLETADOS

    for i, nome in enumerate(nomes_itens):

        coluna = i % 2
        linha = i // 2

        x = largura // 2 - 220 + coluna * 260
        y = altura // 2 - 100 + linha * 190

        espaco = pygame.Rect(
            x - 90,
            y - 60,
            180,
            180
        )

        cor_borda = (
            (255, 255, 255)
            if nome == item_selecionado
            else ROXO_CLARO
        )

        espessura_borda = (
            5
            if nome == item_selecionado
            else 2
        )

        pygame.draw.rect(
            janela,
            (75, 55, 90),
            espaco,
            border_radius=12
        )

        pygame.draw.rect(
            janela,
            cor_borda,
            espaco,
            espessura_borda,
            border_radius=12
        )

        # IMAGEM DO ITEM

        imagem_item = ajustar_item(
            itens[nome].copy(),
            (100, 90)
        )

        janela.blit(
            imagem_item,
            imagem_item.get_rect(center=(x, y - 15))
        )

        # NOME DO ITEM

        texto_nome = fontes["item"].render(
            nome,
            True,
            BRANCO
        )

        janela.blit(
            texto_nome,
            texto_nome.get_rect(center=(x, y + 52))
        )

        # QUANTIDADE DO ITEM

        quantidade = quantidades.get(nome, 0)

        texto_quantidade = fontes["normal"].render(
            f"Quantidade: {quantidade}",
            True,
            BRANCO
        )

        janela.blit(
            texto_quantidade,
            texto_quantidade.get_rect(center=(x, y + 88))
        )

    # BOTÕES USAR E EXAMINAR

    if item_selecionado is not None:

        if quantidades.get(item_selecionado, 0) > 0:

            desenhar_botao(
                janela,
                fontes,
                obter_botao_usar(janela),
                "USAR"
            )

        desenhar_botao(
            janela,
            fontes,
            obter_botao_examinar(janela),
            "EXAMINAR"
        )

    # INSTRUÇÃO PARA FECHAR

    texto_fechar = fontes["normal"].render(
        "Pressione TAB para fechar",
        True,
        BRANCO
    )

    janela.blit(
        texto_fechar,
        texto_fechar.get_rect(
            center=(largura // 2, altura // 2 + 270)
        )
    )


# QUEBRAR TEXTO EM LINHAS PARA A INSPEÇÃO

def quebrar_texto(texto, fonte, largura_maxima):

    linhas = []

    for paragrafo in texto.split("\n"):

        if not paragrafo:
            linhas.append("")
            continue

        palavras = paragrafo.split(" ")
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

    return linhas


# DESENHAR TELA DE INSPEÇÃO DO OBJETO

def desenhar_inspecao(janela, imagem, fontes, nome_item, descricao):

    largura, altura = janela.get_size()

    # SOMBRA SOBRE O INVENTÁRIO

    sombra = pygame.Surface(janela.get_size())
    sombra.set_alpha(210)
    sombra.fill(PRETO)
    janela.blit(sombra, (0, 0))

    # PAINEL PRINCIPAL

    painel = pygame.Rect(
        largura // 2 - 550,
        altura // 2 - 350,
        1100,
        700
    )

    pygame.draw.rect(
        janela,
        (45, 30, 55),
        painel,
        border_radius=20
    )

    pygame.draw.rect(
        janela,
        ROXO_CLARO,
        painel,
        4,
        border_radius=20
    )

    # TÍTULO

    titulo = fontes["titulo"].render(
        nome_item.upper(),
        True,
        BRANCO
    )

    janela.blit(
        titulo,
        titulo.get_rect(center=(largura // 2, altura // 2 - 285))
    )

    # ÁREA DA IMAGEM

    area_imagem = pygame.Rect(
        largura // 2 - 500,
        altura // 2 - 210,
        420,
        420
    )

    pygame.draw.rect(
        janela,
        (65, 48, 78),
        area_imagem,
        border_radius=15
    )

    imagem_ampliada = ajustar_item(
        imagem.copy(),
        (380, 380)
    )

    janela.blit(
        imagem_ampliada,
        imagem_ampliada.get_rect(center=area_imagem.center)
    )

    # TÍTULO DA DESCRIÇÃO

    texto_descricao = fontes["item"].render(
        "DESCRIÇÃO",
        True,
        ROXO_CLARO
    )

    janela.blit(
        texto_descricao,
        (largura // 2 - 30, altura // 2 - 205)
    )

    # TEXTO DA DESCRIÇÃO

    fonte_descricao = fontes["normal"]
    linhas = quebrar_texto(
        descricao,
        fonte_descricao,
        510
    )

    y_texto = altura // 2 - 145
    altura_linha = fonte_descricao.get_linesize() + 8

    for linha in linhas:

        if y_texto + altura_linha > altura // 2 + 210:
            break

        if linha:

            renderizado = fonte_descricao.render(
                linha,
                True,
                BRANCO
            )

            janela.blit(
                renderizado,
                (largura // 2 - 30, y_texto)
            )

        y_texto += altura_linha

    # BOTÃO VOLTAR

    botao_voltar = obter_botao_voltar_inspecao(janela)

    desenhar_botao(
        janela,
        fontes,
        botao_voltar,
        "VOLTAR AO INVENTÁRIO"
    )
