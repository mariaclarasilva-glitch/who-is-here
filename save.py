import pygame

pygame.init()

# JANELA
janela = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("who is here?")

# IMAGENS DO JOGO
imagem_inicio_original = pygame.image.load(
    r"C:\Users\maria\Downloads\let’s play!.png"
)

imagem_cenario_original = pygame.image.load(
    r"C:\Users\maria\Downloads\let’s play!\1.png"
)

imagem_controle_original = pygame.image.load(
    r"C:\Users\maria\Downloads\let’s play!\3.png"
)

# DICIONÁRIO DE ITENS (O óleo começa vazio aqui e será adicionado ao coletar)
itens = {
    "Cerveja": pygame.image.load(
        r"C:\Users\maria\Downloads\cerveja.png"
    ),
    "Rádio": pygame.image.load(
        r"C:\Users\maria\Downloads\radio.png"
    ),
    "Água benta": pygame.image.load(
        r"C:\Users\maria\Downloads\agua benta.png"
    )
}

# VARIÁVEL DE CONTROLE DO ÓLEO
oleo_coletado = False
imagem_oleo_original = pygame.image.load(
    r"C:\Users\maria\Downloads\oleo.png"
)

# FUNÇÃO PARA AJUSTAR O TAMANHO DOS ITENS NO INVENTÁRIO
def ajustar_item(imagem, tamanho):
    imagem = imagem.convert_alpha()
    largura_original, altura_original = imagem.get_size()
    
    if largura_original == 0 or altura_original == 0:
        return imagem

    escala = min(
        tamanho[0] / largura_original,
        tamanho[1] / altura_original
    )

    nova_largura = max(1, int(largura_original * escala))
    nova_altura = max(1, int(altura_original * escala))

    imagem = pygame.transform.smoothscale(
        imagem, (nova_largura, nova_altura)
    )

    return imagem

# CONTROLE DAS TELAS
tela_cheia = True
rodando = True
menu_aberto = False
inventario_aberto = False

tela_atual = "inicio"

relogio = pygame.time.Clock()

# FONTES
fonte = pygame.font.SysFont("arial", 26)
fonte_titulo = pygame.font.SysFont("arial", 60)
fonte_item = pygame.font.SysFont("arial", 23)

# CORES
BRANCO = (255, 255, 255)
ROXO = (100, 40, 130)
ROXO_CLARO = (145, 80, 170)
PRETO = (0, 0, 0)


# AJUSTAR IMAGENS
def atualizar_imagens():
    global imagem_inicio, imagem_cenario, imagem_controle

    tamanho = janela.get_size()

    imagem_inicio = pygame.transform.scale(
        imagem_inicio_original, tamanho
    )

    imagem_cenario = pygame.transform.scale(
        imagem_cenario_original, tamanho
    )

    imagem_controle = pygame.transform.scale(
        imagem_controle_original, tamanho
    )


atualizar_imagens()


# REINICIAR JOGO
def reiniciar_jogo():
    global tela_atual, menu_aberto, inventario_aberto, oleo_coletado

    tela_atual = "inicio"
    menu_aberto = False
    inventario_aberto = False
    oleo_coletado = False
    # Remove o óleo do inventário ao reiniciar, se já tiver sido coletado
    if "Óleo" in itens:
        del itens["Óleo"]


# LOOP PRINCIPAL
while rodando:

    largura, altura = janela.get_size()

    # BOTÕES DA TELA INICIAL
    largura_botao = min(400, (largura - 80) // 2)
    altura_botao = 80
    distancia = 30

    inicio_x = (largura - (largura_botao * 2 + distancia)) // 2
    pos_y = altura - 150

    botao_quarto = pygame.Rect(
        inicio_x, pos_y, largura_botao, altura_botao
    )

    botao_controle = pygame.Rect(
        inicio_x + largura_botao + distancia,
        pos_y,
        largura_botao,
        altura_botao
    )

    # BOTÃO VOLTAR
    botao_voltar = pygame.Rect(40, 40, 200, 65)

    # RETÂNGULO DE COLISÃO DO ÓLEO NO CENÁRIO DO FAROL
    # (Ajuste x, y, largura e altura conforme o local exato da imagem do óleo na tela 3)
    retangulo_oleo = pygame.Rect(largura // 2 - 60, altura // 2 - 60, 120, 120)

    # BOTÕES DO MENU
    botao_reiniciar = pygame.Rect(
        largura // 2 - 200, altura // 2, 400, 80
    )

    botao_fechar = pygame.Rect(
        largura // 2 - 200, altura // 2 + 110, 400, 80
    )

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        # TECLADO
        if evento.type == pygame.KEYDOWN:

            # ESC: ALTERNAR TELA CHEIA
            if evento.key == pygame.K_ESCAPE:

                tela_cheia = not tela_cheia

                if tela_cheia:
                    janela = pygame.display.set_mode(
                        (1920, 1080), pygame.FULLSCREEN
                    )
                else:
                    janela = pygame.display.set_mode(
                        (960, 540), pygame.RESIZABLE
                    )

                atualizar_imagens()

            # M: ABRIR MENU
            if evento.key == pygame.K_m:
                if not inventario_aberto:
                    menu_aberto = not menu_aberto

            # TAB: ABRIR INVENTÁRIO
            if evento.key == pygame.K_TAB:
                if not menu_aberto and tela_atual != "inicio":
                    inventario_aberto = not inventario_aberto

        # CLIQUES DO MOUSE
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:

            if menu_aberto:

                if botao_reiniciar.collidepoint(evento.pos):
                    reiniciar_jogo()

                elif botao_fechar.collidepoint(evento.pos):
                    rodando = False

            elif not inventario_aberto:

                # TELA INICIAL
                if tela_atual == "inicio":

                    if botao_quarto.collidepoint(evento.pos):
                        tela_atual = "quarto"

                    elif botao_controle.collidepoint(evento.pos):
                        tela_atual = "controle"

                # CONTROLE DO FAROL (Clicar no óleo para coletar)
                elif tela_atual == "controle":
                    if not oleo_coletado and retangulo_oleo.collidepoint(evento.pos):
                        oleo_coletado = True
                        itens["Óleo"] = imagem_oleo_original  # Adiciona ao inventário

                    elif botao_voltar.collidepoint(evento.pos):
                        tela_atual = "inicio"

                # VOLTAR NO QUARTO
                elif tela_atual == "quarto":

                    if botao_voltar.collidepoint(evento.pos):
                        tela_atual = "inicio"

    # TELA INICIAL
    if tela_atual == "inicio":

        janela.blit(imagem_inicio, (0, 0))

        pygame.draw.rect(
            janela, ROXO, botao_quarto, border_radius=15
        )

        texto_quarto = fonte.render(
            "IR PARA O QUARTO", True, BRANCO
        )

        janela.blit(
            texto_quarto,
            texto_quarto.get_rect(center=botao_quarto.center)
        )

        pygame.draw.rect(
            janela, ROXO_CLARO, botao_controle, border_radius=15
        )

        texto_controle = fonte.render(
            "IR PARA O CONTROLE DO FAROL", True, BRANCO
        )

        janela.blit(
            texto_controle,
            texto_controle.get_rect(center=botao_controle.center)
        )

    # CENÁRIO DO QUARTO
    elif tela_atual == "quarto":

        janela.blit(imagem_cenario, (0, 0))

        pygame.draw.rect(
            janela, ROXO, botao_voltar, border_radius=12
        )

        texto_voltar = fonte.render(
            "VOLTAR", True, BRANCO
        )

        janela.blit(
            texto_voltar,
            texto_voltar.get_rect(center=botao_voltar.center)
        )

    # CONTROLE DO FAROL
    elif tela_atual == "controle":

        janela.blit(imagem_controle, (0, 0))

        # Se o óleo ainda não foi coletado, desenha ele na tela do farol
        if not oleo_coletado:
            imagem_oleo_cenario = ajustar_item(imagem_oleo_original.copy(), (120, 120))
            janela.blit(imagem_oleo_cenario, retangulo_oleo.topleft)

        pygame.draw.rect(
            janela, ROXO, botao_voltar, border_radius=12
        )

        texto_voltar = fonte.render(
            "VOLTAR", True, BRANCO
        )

        janela.blit(
            texto_voltar,
            texto_voltar.get_rect(center=botao_voltar.center)
        )

    # INVENTÁRIO
    if inventario_aberto:

        sombra = pygame.Surface(janela.get_size())
        sombra.set_alpha(170)
        sombra.fill(PRETO)
        janela.blit(sombra, (0, 0))

        painel = pygame.Rect(
            largura // 2 - 450,
            altura // 2 - 300,
            900,
            600
        )

        pygame.draw.rect(
            janela, (45, 30, 55), painel, border_radius=20
        )

        pygame.draw.rect(
            janela, ROXO_CLARO, painel, 4, border_radius=20
        )

        titulo_inventario = fonte_titulo.render(
            "INVENTÁRIO", True, BRANCO
        )

        janela.blit(
            titulo_inventario,
            titulo_inventario.get_rect(
                center=(largura // 2, altura // 2 - 240)
            )
        )

        # DESENHANDO OS ITENS EM GRADE (2x2 ou mais dependendo dos itens coletados)
        nomes_itens = list(itens.keys())

        for i, nome in enumerate(nomes_itens):
            coluna = i % 2
            linha = i // 2

            x = largura // 2 - 220 + coluna * 260
            y = altura // 2 - 100 + linha * 190

            espaco = pygame.Rect(x - 90, y - 60, 180, 160)

            pygame.draw.rect(
                janela, (75, 55, 90), espaco,
                border_radius=12
            )

            pygame.draw.rect(
                janela, ROXO_CLARO, espaco, 2,
                border_radius=12
            )

            imagem_item = ajustar_item(
                itens[nome].copy(), (100, 90)
            )

            janela.blit(
                imagem_item,
                imagem_item.get_rect(
                    center=(x, y - 15)
                )
            )

            texto_nome = fonte_item.render(
                nome, True, BRANCO
            )

            janela.blit(
                texto_nome,
                texto_nome.get_rect(
                    center=(x, y + 65)
                )
            )

        texto_fechar_inv = fonte.render(
            "Pressione TAB para fechar", True, BRANCO
        )

        janela.blit(
            texto_fechar_inv,
            texto_fechar_inv.get_rect(
                center=(largura // 2, altura // 2 + 260)
            )
        )

    # MENU DO JOGO
    if menu_aberto:

        sombra = pygame.Surface(janela.get_size())
        sombra.set_alpha(180)
        sombra.fill(PRETO)
        janela.blit(sombra, (0, 0))

        titulo = fonte_titulo.render(
            "MENU", True, BRANCO
        )

        janela.blit(
            titulo,
            titulo.get_rect(
                center=(largura // 2, altura // 2 - 100)
            )
        )

        pygame.draw.rect(
            janela, ROXO_CLARO, botao_reiniciar,
            border_radius=15
        )

        texto_reiniciar = fonte.render(
            "REINICIAR JOGO", True, BRANCO
        )

        janela.blit(
            texto_reiniciar,
            texto_reiniciar.get_rect(
                center=botao_reiniciar.center
            )
        )

        pygame.draw.rect(
            janela, ROXO, botao_fechar,
            border_radius=15
        )

        texto_fechar = fonte.render(
            "FECHAR JOGO", True, BRANCO
        )

        janela.blit(
            texto_fechar,
            texto_fechar.get_rect(
                center=botao_fechar.center
            )
        )

    pygame.display.flip()

    relogio.tick(60)

pygame.quit()