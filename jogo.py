import pygame
import json
import os

from ben import (
    criar_estado_combate,
    tratar_evento_combate,
    atualizar_combate,
    desenhar_combate,
    criar_estado_fim,
    tratar_evento_fim,
    atualizar_fim,
    desenhar_fim,
    desenhar_ben_farol,
    ben_transformado
)

from controle import (
    criar_estado_minigame,
    tratar_evento_minigame,
    atualizar_minigame,
    desenhar_minigame
)

from radio import (
    criar_estado_radio,
    tratar_evento_radio,
    atualizar_radio,
    desenhar_radio,
    parar_sons_radio
)

from fantasmas import (
    atualizar_aparicoes,
    aplicar_efeitos_contato,
    aplicar_efeito_expulsar,
    aplicar_efeito_deixar_entrar
)

from dados_fantasmas import DADOS_FANTASMAS

from dialogos import (
    desenhar_dialogo,
    iniciar_dialogo,
    mostrar_resposta,
    encerrar_dialogo
)

from audio import (
    carregar_audios,
    atualizar_audio,
    finalizar_audio
)

from config import (
    LARGURA_TELA,
    ALTURA_TELA,
    FPS,
    TITULO_JOGO
)

from recursos import (
    carregar_recursos,
    atualizar_imagens
)

from telas import (
    criar_botoes,
    desenhar_tela,
    obter_item_sob_mouse,
    obter_area_farol
)

from diario import (
    desenhar_diario,
    obter_area_botao_salvar,
    obter_botoes_confirmacao
)

from dados_diario import PAGINAS_DIARIO, ANOTACAO_ROSABELLA, ANOTACOES_RADIO

from inventario import (
    desenhar_inventario,
    desenhar_inspecao,
    obter_descricao_item,
    obter_botao_usar,
    obter_botao_examinar,
    obter_botao_voltar_inspecao,
    obter_item_clicado
)

from status import (
    desenhar_status,
    desenhar_status_farol
)

from menu import (
    criar_botoes_menu,
    desenhar_menu,
    criar_botao_voltar_controles,
    desenhar_controles
)

from notificacoes import (
    adicionar_notificacao,
    atualizar_notificacoes,
    desenhar_notificacoes
)

from indicadores_status import (
    registrar_alteracao,
    desenhar_indicadores
)


# ORGANIZAR AS ANOTAÇÕES DISPONÍVEIS NO DIÁRIO

def obter_paginas_diario(estado):

    paginas = PAGINAS_DIARIO.copy()

    if estado.get("anotacao_rosabella_desbloqueada", False):
        paginas.append(ANOTACAO_ROSABELLA)

    # ANOTAÇÕES DO RÁDIO

    for registro in estado.get("anotacoes_radio", []):

        modelo = ANOTACOES_RADIO.get(registro["resultado"])

        if modelo is not None:

            paginas.append({
                "data": f"DIA {registro['dia']}",
                "hora": modelo["hora"],
                "titulo": modelo["titulo"],
                "texto": modelo["texto"],
            })

    return paginas


# DURAÇÃO DE CADA PARTE DA TRANSIÇÃO

DURACAO_TRANSICAO = 300


# QUANTOS DIAS CADA FANTASMA FICA NO FAROL

DIAS_ROSABELLA_NO_FAROL = 3
DIAS_ANABELLE_NO_FAROL = 2


# QUANTIDADES RECEBIDAS NA PRIMEIRA COLETA

QUANTIDADES_INICIAIS = {
    "Cerveja": 1,
    "Rádio": 1,
    "Água benta": 6,
    "Óleo": 8,
}

# ARQUIVO QUE GUARDA O PROGRESSO DOS DIAS

ARQUIVO_PROGRESSO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "progresso.json"
)


# CARREGAR O PROGRESSO SALVO

def carregar_progresso():

    try:

        with open(
            ARQUIVO_PROGRESSO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except (FileNotFoundError, json.JSONDecodeError):

        return {}


# INFORMAÇÕES QUE DEVEM SER SALVAS

def obter_dados_persistentes(estado):

    return {
        "ben_apareceu": estado.get("ben_apareceu", False),
        "ben_no_farol": estado.get("ben_no_farol", False),
        "ben_derrotado": estado.get("ben_derrotado", False),
        "anabelle_no_farol": estado.get("anabelle_no_farol", False),
        "dia_entrada_anabelle": estado.get("dia_entrada_anabelle"),
        "fantasma_na_porta": estado.get("fantasma_na_porta"),
        "dialogo_fantasma": None,
        "rosabella_apareceu": estado.get("rosabella_apareceu", False),
        "anotacao_rosabella_desbloqueada": estado.get(
            "anotacao_rosabella_desbloqueada", False
        ),
        "primeiro_contato_rosabella": estado.get(
            "primeiro_contato_rosabella", False
        ),
        "rosabella_no_farol": estado.get("rosabella_no_farol", False),
        "dia_entrada_rosabella": estado.get("dia_entrada_rosabella"),
        "historia_rosabella_contada": estado.get(
            "historia_rosabella_contada", False
        ),
        "dia_verificacao_fantasmas": estado.get(
            "dia_verificacao_fantasmas"
        ),
        "dia_atual": estado["dia_atual"],
        "itens_coletados": list(estado["itens_coletados"]),
        "quantidades_itens": estado["quantidades_itens"].copy(),
        "energia": estado["energia"],
        "sanidade": estado["sanidade"],
        "exposicao": estado["exposicao"],
        "exposicao_revelada": estado["exposicao_revelada"],
        "vitalidade": estado["vitalidade"],
        "iluminacao_farol": estado["iluminacao_farol"],
        "ultimo_uso_radio": estado["ultimo_uso_radio"],
        "pistas_itens": estado["pistas_itens"].copy(),
    }


# SALVAR O PROGRESSO

def salvar_progresso(estado):

    dados = obter_dados_persistentes(estado)

    with open(ARQUIVO_PROGRESSO, "w", encoding="utf-8") as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# RESTAURAR INFORMAÇÕES SALVAS

def restaurar_dados_persistentes(estado, dados):

    estado["dia_atual"] = dados.get("dia_atual", estado["dia_atual"])
    estado["itens_coletados"] = set(
        dados.get("itens_coletados", [])
    )
    estado["quantidades_itens"].update(
        dados.get("quantidades_itens", {})
    )

    estado["energia"] = dados.get("energia", estado["energia"])
    estado["sanidade"] = dados.get("sanidade", estado["sanidade"])
    estado["exposicao"] = dados.get("exposicao", estado["exposicao"])
    estado["exposicao_revelada"] = dados.get(
        "exposicao_revelada", estado["exposicao_revelada"]
    )
    estado["vitalidade"] = dados.get("vitalidade", estado["vitalidade"])

    estado["iluminacao_farol"] = dados.get(
        "iluminacao_farol", estado["iluminacao_farol"]
    )
    estado["ultimo_uso_radio"] = dados.get(
        "ultimo_uso_radio", estado["ultimo_uso_radio"]
    )

    estado["pistas_itens"] = dados.get("pistas_itens", {}).copy()
    estado["primeiro_contato_rosabella"] = dados.get(
        "primeiro_contato_rosabella", False
    )
    estado["rosabella_no_farol"] = dados.get("rosabella_no_farol", False)
    estado["dia_entrada_rosabella"] = dados.get("dia_entrada_rosabella")
    estado["historia_rosabella_contada"] = dados.get(
        "historia_rosabella_contada", False
    )
    estado["anotacao_rosabella_desbloqueada"] = dados.get(
        "anotacao_rosabella_desbloqueada", False
    )

    # RESTAURAR DADOS DO BEN

    estado["ben_apareceu"] = dados.get("ben_apareceu", False)
    estado["ben_no_farol"] = dados.get("ben_no_farol", False)
    estado["ben_derrotado"] = dados.get("ben_derrotado", False)

    # RESTAURAR DADOS DA ANABELLE

    estado["anabelle_no_farol"] = dados.get("anabelle_no_farol", False)
    estado["dia_entrada_anabelle"] = dados.get("dia_entrada_anabelle")

    # RESTAURAR DADOS DOS FANTASMAS

    estado["fantasma_na_porta"] = dados.get("fantasma_na_porta")
    estado["rosabella_apareceu"] = dados.get("rosabella_apareceu", False)
    estado["dia_verificacao_fantasmas"] = dados.get(
        "dia_verificacao_fantasmas"
    )


# ADICIONAR ITENS AO INVENTÁRIO

def adicionar_item(estado, nome, quantidade=1):

    if nome not in estado["quantidades_itens"]:
        return False

    if not isinstance(quantidade, int) or quantidade <= 0:
        return False

    estado["quantidades_itens"][nome] += quantidade

    return True


# ALTERAR ATRIBUTOS DO PERSONAGEM

def alterar_atributo(estado, atributo, quantidade):

    atributos_validos = [
        "energia",
        "sanidade",
        "exposicao",
        "vitalidade"
    ]

    if atributo not in atributos_validos:
        return False

    valor_atual = estado[atributo]
    novo_valor = valor_atual + quantidade

    estado[atributo] = max(
        0,
        min(100, novo_valor)
    )

    # CALCULAR A ALTERAÇÃO REAL

    alteracao_real = estado[atributo] - valor_atual

    # REGISTRAR ALTERAÇÃO PARA O INDICADOR VISUAL

    if alteracao_real != 0:

        registrar_alteracao(
            atributo,
            alteracao_real
        )

    return True


# REGISTRAR O PRIMEIRO CONTATO COM UM FANTASMA OU EVENTO

def registrar_contato_fantasma(estado):

    estado["exposicao_revelada"] = True


# UTILIZAR ITENS DO INVENTÁRIO

def usar_item(estado, nome):

    quantidade = estado["quantidades_itens"].get(nome, 0)

    # IMPEDIR USO SEM QUANTIDADE DISPONÍVEL

    if quantidade <= 0:
        return False

    # CERVEJA

    if nome == "Cerveja":

        alterar_atributo(estado, "sanidade", 25)
        alterar_atributo(estado, "energia", -15)
        alterar_atributo(estado, "exposicao", 10)

    # ÁGUA BENTA

    elif nome == "Água benta":

        alterar_atributo(estado, "exposicao", -25)

    # RÁDIO: USADO PELO MINIGAME (VER tentar_abrir_radio)

    elif nome == "Rádio":

        return False

    # ÓLEO

    elif nome == "Óleo":

        if estado["iluminacao_farol"] >= 100:
            return False

        estado["iluminacao_farol"] = min(
            100,
            estado["iluminacao_farol"] + 35
        )

    else:

        return False

    # CONSUMIR SOMENTE OS ITENS GASTÁVEIS

    if nome in ["Cerveja", "Água benta", "Óleo"]:

        estado["quantidades_itens"][nome] -= 1

    # LIMPAR SELEÇÃO SE NÃO HOUVER MAIS UNIDADES

    if estado["quantidades_itens"][nome] <= 0:

        estado["item_selecionado"] = None

    return True


# FINALIZAR O DIA

def finalizar_dia(estado):

    # AVANÇAR PARA O PRÓXIMO DIA

    estado["dia_atual"] += 1

    # ROSABELLA PARTE NO TERCEIRO DIA APÓS SUA ENTRADA

    if (
        estado.get("rosabella_no_farol", False)
        and estado.get("dia_entrada_rosabella") is not None
        and estado["dia_atual"] - estado["dia_entrada_rosabella"]
        >= DIAS_ROSABELLA_NO_FAROL
    ):

        estado["rosabella_no_farol"] = False

    # ANABELLE PARTE NO SEGUNDO DIA APÓS SUA ENTRADA

    if (
        estado.get("anabelle_no_farol", False)
        and estado.get("dia_entrada_anabelle") is not None
        and estado["dia_atual"] - estado["dia_entrada_anabelle"]
        >= DIAS_ANABELLE_NO_FAROL
    ):

        estado["anabelle_no_farol"] = False

    # DESBLOQUEAR ANOTAÇÃO DO PRIMEIRO CONTATO COM ROSABELLA

    if (
        estado.get("primeiro_contato_rosabella", False)
        and not estado.get("anotacao_rosabella_desbloqueada", False)
    ):

        estado["anotacao_rosabella_desbloqueada"] = True

    # CONSUMIR ILUMINAÇÃO DO FAROL DURANTE A NOITE

    estado["iluminacao_farol"] = max(
        0,
        estado["iluminacao_farol"] - 30
    )

    # SE O FAROL APAGAR, A EXPOSIÇÃO VAI PARA 98

    if estado["iluminacao_farol"] == 0:

        estado["exposicao"] = 98
        estado["exposicao_revelada"] = True

    # SALVAR PROGRESSO

    salvar_progresso(estado)

    # FECHAR O DIÁRIO

    estado["diario_aberto"] = False
    estado["confirmacao_encerramento"] = False
    estado["pagina_diario"] = 0


# INICIAR TRANSIÇÃO ENTRE CÔMODOS

def iniciar_transicao(estado, proxima_tela):

    if estado["transicao_ativa"]:
        return

    if estado["tela_atual"] == proxima_tela:
        return

    estado["transicao_ativa"] = True
    estado["fase_transicao"] = "saida"
    estado["inicio_transicao"] = pygame.time.get_ticks()
    estado["proxima_tela"] = proxima_tela
    estado["transicao_alpha"] = 0


# OBTER BOTÕES DA CONFIRMAÇÃO DE RECOMEÇO

def obter_botoes_confirmacao_recomecar(janela):

    largura, altura = janela.get_size()

    botao_cancelar = pygame.Rect(
        largura // 2 - 220,
        altura // 2 + 50,
        200,
        70
    )

    botao_confirmar = pygame.Rect(
        largura // 2 + 20,
        altura // 2 + 50,
        200,
        70
    )

    return botao_cancelar, botao_confirmar


# DESENHAR CONFIRMAÇÃO DE RECOMEÇO

def desenhar_confirmacao_recomecar(janela, fontes):

    largura, altura = janela.get_size()

    # ESCURECER O FUNDO

    sombra = pygame.Surface(janela.get_size())
    sombra.set_alpha(210)
    sombra.fill((0, 0, 0))
    janela.blit(sombra, (0, 0))

    # PAINEL DA CONFIRMAÇÃO

    painel = pygame.Rect(
        largura // 2 - 400,
        altura // 2 - 150,
        800,
        300
    )

    pygame.draw.rect(
        janela,
        (45, 25, 60),
        painel,
        border_radius=20
    )

    # PERGUNTA

    titulo = fontes["titulo"].render(
        "DESEJA RECOMEÇAR O JOGO?",
        True,
        (255, 255, 255)
    )

    janela.blit(
        titulo,
        titulo.get_rect(
            center=(
                largura // 2,
                altura // 2 - 65
            )
        )
    )

    # EXPLICAÇÃO

    texto = fontes["normal"].render(
        "Todo o progresso e histórico de dias serão apagados.",
        True,
        (255, 255, 255)
    )

    janela.blit(
        texto,
        texto.get_rect(
            center=(
                largura // 2,
                altura // 2
            )
        )
    )

    botao_cancelar, botao_confirmar = (
        obter_botoes_confirmacao_recomecar(janela)
    )

    # BOTÃO CANCELAR

    pygame.draw.rect(
        janela,
        (100, 75, 125),
        botao_cancelar,
        border_radius=12
    )

    texto_cancelar = fontes["normal"].render(
        "CANCELAR",
        True,
        (255, 255, 255)
    )

    janela.blit(
        texto_cancelar,
        texto_cancelar.get_rect(
            center=botao_cancelar.center
        )
    )

    # BOTÃO CONFIRMAR

    pygame.draw.rect(
        janela,
        (110, 35, 65),
        botao_confirmar,
        border_radius=12
    )

    texto_confirmar = fontes["normal"].render(
        "SIM, RECOMEÇAR",
        True,
        (255, 255, 255)
    )

    janela.blit(
        texto_confirmar,
        texto_confirmar.get_rect(
            center=botao_confirmar.center
        )
    )


# RECOMEÇAR JOGO DO ZERO

def recomecar_jogo(estado):

    # REINICIAR DADOS DOS FANTASMAS

    estado["fantasma_na_porta"] = None
    estado["rosabella_apareceu"] = False
    estado["dia_verificacao_fantasmas"] = None
    estado["primeiro_contato_rosabella"] = False
    estado["anotacao_rosabella_desbloqueada"] = False
    estado["rosabella_no_farol"] = False
    estado["dia_entrada_rosabella"] = None
    estado["historia_rosabella_contada"] = False
    estado["dialogo_fantasma"] = None
    estado["anotacoes_radio"] = []
    estado["anabelle_no_farol"] = False
    estado["dia_entrada_anabelle"] = None

    # REINICIAR O BEN

    estado["ben_apareceu"] = False
    estado["ben_no_farol"] = False
    estado["ben_derrotado"] = False
    estado["ben_entrada_ms"] = None
    estado["ben_dica_mostrada"] = False
    estado["combate_ben_aberto"] = False
    estado["combate_ben"] = None
    estado["fim_aberto"] = False
    estado["fim"] = None

    # APAGAR O ARQUIVO DE PROGRESSO

    try:
        os.remove(ARQUIVO_PROGRESSO)

    except FileNotFoundError:
        pass

    # VOLTAR AO DIA INICIAL

    estado["dia_atual"] = 561

    # LIMPAR OBJETOS COLETADOS

    estado["itens_coletados"].clear()

    # ZERAR QUANTIDADES DOS ITENS

    for nome in estado["quantidades_itens"]:
        estado["quantidades_itens"][nome] = 0

    # RESTAURAR ATRIBUTOS

    estado["energia"] = 100
    estado["sanidade"] = 100
    estado["exposicao"] = 0
    estado["exposicao_revelada"] = False
    estado["vitalidade"] = 100

    # RESTAURAR FAROL E RÁDIO

    estado["iluminacao_farol"] = 100
    estado["ultimo_uso_radio"] = None

    # LIMPAR PISTAS E SELEÇÕES

    estado["pistas_itens"].clear()
    estado["item_selecionado"] = None
    estado["status_farol_aberto"] = False

    # LIMPAR NOTIFICAÇÕES

    estado["fila_notificacoes"].clear()
    estado["notificacao_atual"] = None

    # VOLTAR AO CENÁRIO INICIAL

    estado["tela_atual"] = "inicio"

    # FECHAR JANELAS

    estado["menu_aberto"] = False
    estado["inventario_aberto"] = False
    estado["inspecao_aberta"] = False
    estado["controles_aberto"] = False
    estado["diario_aberto"] = False

    estado["pagina_diario"] = 0
    estado["confirmacao_encerramento"] = False
    estado["confirmacao_recomecar"] = False

    # CANCELAR TRANSIÇÕES

    estado["transicao_ativa"] = False
    estado["fase_transicao"] = None
    estado["proxima_tela"] = None
    estado["transicao_alpha"] = 0

    # SALVAR O NOVO PROGRESSO INICIAL

    salvar_progresso(estado)


# ABRIR A HISTÓRIA ESPECIAL DE ROSABELLA NO FAROL

def iniciar_historia_rosabella(estado):

    estado["dialogo_fantasma"] = {
        "tipo": "historia_rosabella",
        "fantasma": "rosabella",
        "etapa": "resposta",
        "pagina": 0,
        "opcao_selecionada": 0,
        "opcoes": [],
        "texto": DADOS_FANTASMAS["rosabella"]["historia"][0],
    }


# ÁREA DO CANTO INFERIOR ESQUERDO QUE ABRE O MINIGAME

def obter_area_minigame(janela):

    largura, altura = janela.get_size()

    return pygame.Rect(0, altura - 150, 150, 150)


# SANIDADE RECEBIDA EM CADA RESULTADO DO RÁDIO

SANIDADE_RADIO = {
    "musica": 30,
    "embarcacao": 10,
    "chiado": 0,
}


# ABRIR O MINIGAME DO RÁDIO

def tentar_abrir_radio(estado):

    # FECHAR O INVENTÁRIO PARA A MENSAGEM OU O RÁDIO APARECEREM

    estado["inventario_aberto"] = False
    estado["inspecao_aberta"] = False
    estado["item_selecionado"] = None

    if estado["tela_atual"] != "controle":

        adicionar_notificacao(
            estado,
            "O rádio só pode ser usado no controle do farol.",
            categoria="observacao"
        )
        return

    if estado.get("ultimo_uso_radio") == estado["dia_atual"]:

        adicionar_notificacao(
            estado,
            "Você já usou o rádio hoje.",
            categoria="observacao"
        )
        return

    estado["status_farol_aberto"] = False
    estado["radio"] = criar_estado_radio()
    estado["radio_aberto"] = True


# REGISTRAR O RESULTADO (A TENTATIVA SÓ É GASTA AQUI)

def registrar_resultado_radio(estado, resultado):

    estado["ultimo_uso_radio"] = estado["dia_atual"]

    estado["anotacoes_radio"].append({
        "dia": estado["dia_atual"],
        "resultado": resultado
    })

    bonus = SANIDADE_RADIO.get(resultado, 0)

    if bonus != 0:
        alterar_atributo(estado, "sanidade", bonus)


# FECHAR O MINIGAME DO RÁDIO

def fechar_radio(estado):

    revelado = (
        estado["radio"] is not None
        and estado["radio"]["fase"] == "revelado"
    )

    parar_sons_radio()

    estado["radio_aberto"] = False
    estado["radio"] = None

    if revelado:

        adicionar_notificacao(
            estado,
            "Uma anotação foi adicionada ao diário.",
            categoria="observacao"
        )


# ABRIR O COMBATE COM O BEN
# (SÓ DEPOIS QUE A TRANSFORMAÇÃO TERMINAR)

def iniciar_combate_ben(estado):

    if not ben_transformado(estado.get("ben_entrada_ms")):
        return

    estado["combate_ben"] = criar_estado_combate()
    estado["combate_ben_aberto"] = True


# FECHAR O COMBATE COM O BEN
# RESULTADO: "vitoria", "derrota" OU "sair" (DESISTIU, NÃO GASTA ÁGUA BENTA)

def finalizar_combate_ben(estado, resultado):

    estado["combate_ben_aberto"] = False
    estado["combate_ben"] = None

    if resultado in ("vitoria", "derrota"):

        estado["quantidades_itens"]["Água benta"] = max(
            0,
            estado["quantidades_itens"].get("Água benta", 0) - 1
        )

        if estado["quantidades_itens"]["Água benta"] <= 0:
            estado["item_selecionado"] = None

    if resultado == "derrota":

        adicionar_notificacao(
            estado,
            "A água benta acabou antes de enfraquecer o Ben.",
            categoria="observacao"
        )

    elif resultado == "vitoria":

        estado["ben_no_farol"] = False
        estado["ben_derrotado"] = True

        salvar_progresso(estado)

        estado["fim"] = criar_estado_fim()
        estado["fim_aberto"] = True


# EXECUTAR JOGO

def executar_jogo():

    janela = pygame.display.set_mode(
        (LARGURA_TELA, ALTURA_TELA),
        pygame.FULLSCREEN
    )

    pygame.display.set_caption(TITULO_JOGO)

    recursos = carregar_recursos()
    carregar_audios()

    imagens = atualizar_imagens(janela, recursos)
    dados_salvos = carregar_progresso()

    estado = {

        # BEN
        "ben_apareceu": False,
        "ben_no_farol": False,
        "ben_derrotado": False,
        "ben_entrada_ms": None,
        "ben_dica_mostrada": False,
        "combate_ben_aberto": False,
        "combate_ben": None,
        "fim_aberto": False,
        "fim": None,

        # MINIGAME DO RÁDIO
        "radio_aberto": False,
        "radio": None,
        "anotacoes_radio": [],

        # MINIGAME DE MANUTENÇÃO DO FAROL
        "minigame_aberto": False,
        "minigame": None,

        "rodando": True,

        # SISTEMA DE NOTIFICAÇÕES
        "fila_notificacoes": [],
        "notificacao_atual": None,

        "tela_cheia": True,
        "menu_aberto": False,
        "inventario_aberto": False,
        "inspecao_aberta": False,

        # INFORMAÇÕES DESBLOQUEADAS DOS OBJETOS
        "pistas_itens": {},

        # CONTROLE DO ITEM SELECIONADO
        "item_selecionado": None,

        # ILUMINAÇÃO DO FAROL
        "iluminacao_farol": 100,

        # ÚLTIMO DIA DE USO DO RÁDIO
        "ultimo_uso_radio": None,

        # CONTROLE DA TELA DE CONTROLES
        "controles_aberto": False,

        # CONTROLE DO DIÁRIO
        "diario_aberto": False,
        "pagina_diario": 0,
        "confirmacao_encerramento": False,

        # CONTROLE DA CONFIRMAÇÃO DE RECOMEÇO
        "confirmacao_recomecar": False,

        # PROGRESSO DOS DIAS
        "dia_atual": 561,
        "tela_atual": "inicio",

        # SISTEMA DE FANTASMAS
        "fantasma_na_porta": None,
        "dialogo_fantasma": None,
        "rosabella_apareceu": False,
        "primeiro_contato_rosabella": False,
        "anotacao_rosabella_desbloqueada": False,
        "rosabella_no_farol": False,
        "dia_entrada_rosabella": None,
        "historia_rosabella_contada": False,
        "anabelle_no_farol": False,
        "dia_entrada_anabelle": None,
        "dia_verificacao_fantasmas": None,

        # REGISTRAR ITENS COLETADOS
        "itens_coletados": set(),

        # REGISTRAR QUANTIDADES DOS ITENS
        "quantidades_itens": {
            "Cerveja": 0,
            "Rádio": 0,
            "Água benta": 0,
            "Óleo": 0,
        },

        # ATRIBUTOS DO PERSONAGEM
        "energia": 100,
        "sanidade": 100,
        "exposicao": 0,
        "exposicao_revelada": False,
        "vitalidade": 100,

        "status_farol_aberto": False,

        # CONTROLE DA TRANSIÇÃO
        "transicao_ativa": False,
        "fase_transicao": None,
        "inicio_transicao": 0,
        "proxima_tela": None,
        "transicao_alpha": 0,
    }

    # RESTAURAR PROGRESSO SALVO

    if "progresso" in dados_salvos:

        restaurar_dados_persistentes(
            estado,
            dados_salvos["progresso"]
        )

    elif "dia_atual" in dados_salvos:

        if "itens_coletados" in dados_salvos:

            restaurar_dados_persistentes(
                estado,
                dados_salvos
            )

        else:

            estado["dia_atual"] = dados_salvos["dia_atual"]

    relogio = pygame.time.Clock()

    while estado["rodando"]:

        # NO FINAL DO JOGO, A MÚSICA DO FIM NÃO PODE SER SUBSTITUÍDA

        if not estado["fim_aberto"]:
            atualizar_audio(estado["menu_aberto"])

        largura, altura = janela.get_size()

        botoes = criar_botoes(largura, altura)
        botoes_menu = criar_botoes_menu(largura, altura)

        # CRIAR BOTÃO VOLTAR DOS CONTROLES

        botao_voltar_controles = criar_botao_voltar_controles(
            largura,
            altura
        )

        # CAPTURAR EVENTOS

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                estado["rodando"] = False

            # MINIGAME ABERTO: ELE RECEBE TODOS OS EVENTOS

            if estado["minigame_aberto"]:

                resultado = tratar_evento_minigame(
                    estado["minigame"],
                    evento,
                    janela
                )

                if resultado == "sair":

                    estado["minigame_aberto"] = False
                    estado["minigame"] = None

                continue

            # RÁDIO ABERTO: ELE RECEBE TODOS OS EVENTOS

            if estado["radio_aberto"]:

                resultado = tratar_evento_radio(
                    estado["radio"],
                    evento,
                    janela
                )

                if resultado == "sair":
                    fechar_radio(estado)

                continue

            # COMBATE COM O BEN ABERTO

            if estado["combate_ben_aberto"]:

                resultado = tratar_evento_combate(
                    estado["combate_ben"],
                    evento,
                    janela
                )

                if resultado is not None:
                    finalizar_combate_ben(estado, resultado)

                continue

            # FINAL DO JOGO ABERTO

            if estado["fim_aberto"]:

                if tratar_evento_fim(estado["fim"], evento) == "encerrar":
                    estado["rodando"] = False

                continue

            # TESTE TEMPORÁRIO (APAGAR DEPOIS)

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_F9:
                    estado["ben_no_farol"] = True

                elif evento.key == pygame.K_F10:
                    iniciar_combate_ben(estado)

                elif evento.key == pygame.K_F11:
                    estado["fim"] = criar_estado_fim()
                    estado["fim_aberto"] = True

            if evento.type == pygame.KEYDOWN:

                # CONTROLAR DIÁLOGO COM FANTASMAS

                if estado["dialogo_fantasma"] is not None:

                    dialogo = estado["dialogo_fantasma"]

                    # HISTÓRIA ESPECIAL DE ROSABELLA:
                    # ENTER FECHA E MARCA COMO LIDA

                    if dialogo.get("tipo") == "historia_rosabella":

                        if evento.key in (
                            pygame.K_RETURN,
                            pygame.K_KP_ENTER
                        ):

                            estado["historia_rosabella_contada"] = True
                            encerrar_dialogo(estado)

                        elif evento.key == pygame.K_ESCAPE:

                            encerrar_dialogo(estado)

                        continue

                    # FECHAR DIÁLOGO COM ESC

                    if evento.key == pygame.K_ESCAPE:

                        encerrar_dialogo(estado)

                    # NAVEGAR PELAS OPÇÕES

                    elif dialogo["etapa"] == "opcoes":

                        if evento.key == pygame.K_UP:

                            dialogo["opcao_selecionada"] = (
                                dialogo["opcao_selecionada"] - 1
                            ) % len(dialogo["opcoes"])

                        elif evento.key == pygame.K_DOWN:

                            dialogo["opcao_selecionada"] = (
                                dialogo["opcao_selecionada"] + 1
                            ) % len(dialogo["opcoes"])

                        # CONFIRMAR OPÇÃO

                        elif evento.key in (
                            pygame.K_RETURN,
                            pygame.K_KP_ENTER
                        ):

                            opcao = dialogo["opcao_selecionada"]
                            fantasma = dialogo["fantasma"]

                            if opcao == 0:

                                mostrar_resposta(
                                    estado,
                                    DADOS_FANTASMAS[fantasma]
                                )

                            elif opcao == 1:

                                # O BEN LIGA "ben_no_farol" DENTRO DE fantasmas.py

                                aplicar_efeito_deixar_entrar(estado, fantasma)

                                # REGISTRAR A ENTRADA DE ROSABELLA NO FAROL

                                if fantasma == "rosabella":

                                    estado["rosabella_no_farol"] = True
                                    estado["dia_entrada_rosabella"] = (
                                        estado["dia_atual"]
                                    )
                                    estado["historia_rosabella_contada"] = False

                                # REGISTRAR A ENTRADA DE ANABELLE NO FAROL

                                if fantasma == "anabelle":

                                    estado["anabelle_no_farol"] = True
                                    estado["dia_entrada_anabelle"] = (
                                        estado["dia_atual"]
                                    )

                                # ENCERRAR A INTERAÇÃO PARA QUALQUER FANTASMA

                                estado["fantasma_na_porta"] = None
                                encerrar_dialogo(estado)

                            elif opcao == 2:

                                # O BEN NÃO TEM A OPÇÃO "EXPULSAR"

                                aplicar_efeito_expulsar(estado)
                                estado["fantasma_na_porta"] = None
                                encerrar_dialogo(estado)

                    # VOLTAR ÀS OPÇÕES DEPOIS DE LER A RESPOSTA

                    elif (
                        dialogo["etapa"] == "resposta"
                        and evento.key in (
                            pygame.K_RETURN,
                            pygame.K_KP_ENTER
                        )
                    ):

                        dialogo["etapa"] = "opcoes"
                        dialogo["texto"] = ""

                    # IMPEDIR OUTRAS TECLAS DE INTERFERIREM NO DIÁLOGO

                    continue

                # ESC: FECHAR JANELAS OU ALTERNAR TELA CHEIA

                if evento.key == pygame.K_ESCAPE:

                    if estado["confirmacao_recomecar"]:

                        estado["confirmacao_recomecar"] = False

                    elif estado["confirmacao_encerramento"]:

                        estado["confirmacao_encerramento"] = False

                    elif estado["controles_aberto"]:

                        estado["controles_aberto"] = False

                    elif estado["diario_aberto"]:

                        estado["diario_aberto"] = False

                    elif estado["inspecao_aberta"]:

                        estado["inspecao_aberta"] = False

                    elif estado["inventario_aberto"]:

                        estado["inventario_aberto"] = False
                        estado["item_selecionado"] = None

                    elif estado["status_farol_aberto"]:

                        estado["status_farol_aberto"] = False

                    else:

                        estado["tela_cheia"] = not estado["tela_cheia"]

                        if estado["tela_cheia"]:

                            janela = pygame.display.set_mode(
                                (LARGURA_TELA, ALTURA_TELA),
                                pygame.FULLSCREEN
                            )

                        else:

                            janela = pygame.display.set_mode(
                                (960, 540),
                                pygame.RESIZABLE
                            )

                        imagens = atualizar_imagens(
                            janela,
                            recursos
                        )

                # J: ABRIR OU FECHAR DIÁRIO

                elif evento.key == pygame.K_j:

                    if (
                        not estado["menu_aberto"]
                        and not estado["inventario_aberto"]
                        and not estado["controles_aberto"]
                        and not estado["transicao_ativa"]
                        and not estado["confirmacao_encerramento"]
                        and not estado["confirmacao_recomecar"]
                    ):

                        estado["diario_aberto"] = not estado["diario_aberto"]

                # NAVEGAR ENTRE AS PÁGINAS DO DIÁRIO

                if (
                    estado["diario_aberto"]
                    and not estado["confirmacao_encerramento"]
                ):

                    paginas_disponiveis = obter_paginas_diario(estado)

                    if evento.key == pygame.K_RIGHT:

                        if (
                            estado["pagina_diario"] + 2
                            < len(paginas_disponiveis)
                        ):

                            estado["pagina_diario"] += 2

                    elif evento.key == pygame.K_LEFT:

                        if estado["pagina_diario"] >= 2:

                            estado["pagina_diario"] -= 2

                # M: ABRIR MENU

                if evento.key == pygame.K_m:

                    if (
                        not estado["inventario_aberto"]
                        and not estado["diario_aberto"]
                        and not estado["controles_aberto"]
                        and not estado["transicao_ativa"]
                        and not estado["confirmacao_recomecar"]
                    ):

                        estado["menu_aberto"] = not estado["menu_aberto"]

                # TAB: ABRIR OU FECHAR INVENTÁRIO

                if evento.key == pygame.K_TAB:

                    if (
                        not estado["menu_aberto"]
                        and not estado["diario_aberto"]
                        and not estado["controles_aberto"]
                        and not estado["transicao_ativa"]
                        and not estado["confirmacao_recomecar"]
                    ):

                        estado["inventario_aberto"] = not estado["inventario_aberto"]

                        # LIMPAR SELEÇÃO AO FECHAR

                        if not estado["inventario_aberto"]:

                            estado["inspecao_aberta"] = False
                            estado["item_selecionado"] = None

                # C: INICIAR O COMBATE COM O BEN

                if evento.key == pygame.K_c:

                    if (
                        estado["ben_no_farol"]
                        and estado["tela_atual"] == "controle"
                        and not estado["menu_aberto"]
                        and not estado["inventario_aberto"]
                        and not estado["diario_aberto"]
                        and not estado["controles_aberto"]
                        and not estado["transicao_ativa"]
                        and not estado["confirmacao_recomecar"]
                        and ben_transformado(estado.get("ben_entrada_ms"))
                    ):

                        if estado["quantidades_itens"].get("Água benta", 0) > 0:

                            iniciar_combate_ben(estado)

                        else:

                            adicionar_notificacao(
                                estado,
                                "Você não tem água benta.",
                                categoria="observacao"
                            )

                # E: INTERAGIR COM FANTASMA, HISTÓRIA OU COLETAR OBJETO

                if evento.key == pygame.K_e:

                    if (
                        not estado["menu_aberto"]
                        and not estado["inventario_aberto"]
                        and not estado["diario_aberto"]
                        and not estado["controles_aberto"]
                        and not estado["transicao_ativa"]
                        and not estado["confirmacao_recomecar"]
                    ):

                        fantasma = estado.get("fantasma_na_porta")

                        # INTERAGIR COM FANTASMA NA PORTA

                        if (
                            estado["tela_atual"] == "porta"
                            and fantasma is not None
                            and estado["dialogo_fantasma"] is None
                        ):

                            iniciar_dialogo(
                                estado,
                                fantasma
                            )

                            aplicar_efeitos_contato(estado)
                            estado["exposicao_revelada"] = True

                        # HISTÓRIA DE ROSABELLA NO FAROL:
                        # DISPONÍVEL NO SEGUNDO DIA APÓS SUA ENTRADA

                        elif (
                            estado["tela_atual"] == "controle"
                            and estado.get("rosabella_no_farol", False)
                            and estado.get("dia_entrada_rosabella") is not None
                            and (
                                estado["dia_atual"]
                                - estado["dia_entrada_rosabella"]
                            ) == 2
                            and not estado.get(
                                "historia_rosabella_contada", False
                            )
                            and estado["dialogo_fantasma"] is None
                        ):

                            iniciar_historia_rosabella(estado)

                        # COLETAR OBJETO SE NÃO HOUVER FANTASMA NA PORTA
                        # NEM HISTÓRIA ESPECIAL SENDO ABERTA

                        elif not (
                            estado["tela_atual"] == "porta"
                            and fantasma is not None
                        ):

                            item = obter_item_sob_mouse(
                                estado["tela_atual"],
                                pygame.mouse.get_pos(),
                                largura,
                                altura,
                                estado["itens_coletados"]
                            )

                            if item is not None:

                                estado["itens_coletados"].add(item)

                                quantidade_inicial = QUANTIDADES_INICIAIS[item]

                                adicionar_item(
                                    estado,
                                    item,
                                    quantidade_inicial
                                )

                                adicionar_notificacao(
                                    estado,
                                    f"{item} foi adicionado ao inventário.",
                                    categoria="observacao"
                                )

            # CLIQUES DO MOUSE

            if (
                evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
                and estado["dialogo_fantasma"] is None
            ):

                # CLIQUES NA TELA DE CONTROLES

                if estado["controles_aberto"]:

                    if botao_voltar_controles.collidepoint(evento.pos):

                        estado["controles_aberto"] = False

                # CLIQUES NA CONFIRMAÇÃO DE RECOMEÇO

                elif estado["confirmacao_recomecar"]:

                    botao_cancelar, botao_confirmar = (
                        obter_botoes_confirmacao_recomecar(janela)
                    )

                    if botao_cancelar.collidepoint(evento.pos):

                        estado["confirmacao_recomecar"] = False

                    elif botao_confirmar.collidepoint(evento.pos):

                        recomecar_jogo(estado)

                # CLIQUES NO MENU

                elif estado["menu_aberto"]:

                    # ABRIR CONTROLES DO JOGO

                    if botoes_menu["controles"].collidepoint(evento.pos):

                        estado["controles_aberto"] = True

                    elif botoes_menu["recomecar"].collidepoint(evento.pos):

                        estado["confirmacao_recomecar"] = True

                    elif botoes_menu["fechar"].collidepoint(evento.pos):

                        estado["rodando"] = False

                # CLIQUES NO INVENTÁRIO E NA INSPEÇÃO

                elif estado["inventario_aberto"]:

                    # TELA DE INSPEÇÃO: VOLTAR AO INVENTÁRIO

                    if estado["inspecao_aberta"]:

                        if obter_botao_voltar_inspecao(janela).collidepoint(evento.pos):

                            estado["inspecao_aberta"] = False

                    else:

                        itens_inventario = {
                            nome: imagem
                            for nome, imagem in recursos["itens"].items()
                            if estado["quantidades_itens"].get(nome, 0) > 0
                        }

                        # VERIFICAR SE UM ITEM FOI CLICADO

                        item_clicado = obter_item_clicado(
                            itens_inventario,
                            evento.pos,
                            largura,
                            altura
                        )

                        if item_clicado is not None:

                            estado["item_selecionado"] = item_clicado

                        # VERIFICAR CLIQUE NO BOTÃO EXAMINAR

                        elif (
                            estado["item_selecionado"] is not None
                            and obter_botao_examinar(janela).collidepoint(evento.pos)
                        ):

                            estado["inspecao_aberta"] = True

                        # VERIFICAR CLIQUE NO BOTÃO USAR

                        elif (
                            estado["item_selecionado"] is not None
                            and obter_botao_usar(janela).collidepoint(evento.pos)
                            and estado["quantidades_itens"].get(
                                estado["item_selecionado"], 0
                            ) > 0
                        ):

                            if estado["item_selecionado"] == "Rádio":

                                tentar_abrir_radio(estado)

                            else:

                                usar_item(
                                    estado,
                                    estado["item_selecionado"]
                                )

                # CLIQUES NO DIÁRIO

                elif estado["diario_aberto"]:

                    # SE A CONFIRMAÇÃO ESTIVER ABERTA

                    if estado["confirmacao_encerramento"]:

                        botao_cancelar, botao_confirmar = (
                            obter_botoes_confirmacao(janela)
                        )

                        if botao_cancelar.collidepoint(evento.pos):

                            estado["confirmacao_encerramento"] = False

                        elif botao_confirmar.collidepoint(evento.pos):

                            finalizar_dia(estado)

                    # SE A CONFIRMAÇÃO NÃO ESTIVER ABERTA

                    else:

                        area_botao = obter_area_botao_salvar(
                            janela,
                            imagens["diario"],
                            imagens["salvar_dia"]
                        )

                        if area_botao.collidepoint(evento.pos):

                            estado["confirmacao_encerramento"] = True

                # CLIQUES NOS CENÁRIOS

                elif (
                    not estado["inventario_aberto"]
                    and not estado["diario_aberto"]
                    and not estado["transicao_ativa"]
                ):

                    # QUARTO

                    if estado["tela_atual"] == "inicio":

                        if botoes["esquerda"].collidepoint(evento.pos):

                            estado["status_farol_aberto"] = False
                            iniciar_transicao(estado, "porta")

                        elif botoes["direita"].collidepoint(evento.pos):

                            estado["status_farol_aberto"] = False
                            iniciar_transicao(estado, "controle")

                    # PORTA

                    elif estado["tela_atual"] == "porta":

                        if botoes["esquerda"].collidepoint(evento.pos):

                            iniciar_transicao(estado, "inicio")

                        elif botoes["direita"].collidepoint(evento.pos):

                            estado["status_farol_aberto"] = False
                            iniciar_transicao(estado, "controle")

                    # CONTROLE DO FAROL

                    elif estado["tela_atual"] == "controle":

                        # CLIQUE NO CANTO INFERIOR ESQUERDO: ABRIR MINIGAME

                        if obter_area_minigame(janela).collidepoint(evento.pos):

                            if estado["quantidades_itens"].get("Óleo", 0) <= 0:

                                adicionar_notificacao(
                                    estado,
                                    "Você não tem óleo para abastecer o farol.",
                                    categoria="observacao"
                                )

                            elif estado["iluminacao_farol"] >= 100:

                                adicionar_notificacao(
                                    estado,
                                    "O farol já está com a iluminação cheia.",
                                    categoria="observacao"
                                )

                            else:

                                estado["status_farol_aberto"] = False
                                estado["minigame"] = criar_estado_minigame()
                                estado["minigame_aberto"] = True

                        # CLIQUE NO FAROL: ABRIR OU FECHAR O PAINEL

                        elif obter_area_farol(janela).collidepoint(evento.pos):

                            estado["status_farol_aberto"] = not estado["status_farol_aberto"]

                        elif botoes["esquerda"].collidepoint(evento.pos):

                            estado["status_farol_aberto"] = False
                            iniciar_transicao(estado, "inicio")

                        elif botoes["direita"].collidepoint(evento.pos):

                            estado["status_farol_aberto"] = False
                            iniciar_transicao(estado, "porta")

        # ATUALIZAR O MINIGAME DO FAROL

        if estado["minigame_aberto"]:

            if atualizar_minigame(estado["minigame"]):

                usar_item(estado, "Óleo")

                adicionar_notificacao(
                    estado,
                    "O farol foi abastecido com óleo.",
                    categoria="observacao"
                )

        # ATUALIZAR O MINIGAME DO RÁDIO

        if estado["radio_aberto"]:

            resultado_radio = atualizar_radio(
                estado["radio"],
                janela
            )

            if resultado_radio is not None:
                registrar_resultado_radio(estado, resultado_radio)

        # ATUALIZAR O COMBATE COM O BEN

        if estado["combate_ben_aberto"]:

            if atualizar_combate(estado["combate_ben"]) == "vitoria":
                finalizar_combate_ben(estado, "vitoria")

        # ATUALIZAR O FINAL DO JOGO

        if estado["fim_aberto"]:
            atualizar_fim(estado["fim"])

        # ATUALIZAR ANIMAÇÃO DA TRANSIÇÃO

        if estado["transicao_ativa"]:

            tempo_atual = pygame.time.get_ticks()

            tempo_decorrido = (
                tempo_atual - estado["inicio_transicao"]
            )

            if estado["fase_transicao"] == "saida":

                estado["transicao_alpha"] = min(
                    255,
                    int(
                        255 * tempo_decorrido
                        / DURACAO_TRANSICAO
                    )
                )

                # QUANDO A TELA FICAR PRETA, TROCAR O CÔMODO

                if tempo_decorrido >= DURACAO_TRANSICAO:

                    estado["tela_atual"] = estado["proxima_tela"]
                    estado["fase_transicao"] = "entrada"
                    estado["inicio_transicao"] = tempo_atual
                    estado["transicao_alpha"] = 255

            elif estado["fase_transicao"] == "entrada":

                estado["transicao_alpha"] = max(
                    0,
                    255 - int(
                        255 * tempo_decorrido
                        / DURACAO_TRANSICAO
                    )
                )

                # FINALIZAR TRANSIÇÃO

                if tempo_decorrido >= DURACAO_TRANSICAO:

                    estado["transicao_alpha"] = 0
                    estado["transicao_ativa"] = False
                    estado["fase_transicao"] = None
                    estado["proxima_tela"] = None

        # ATUALIZAR APARIÇÕES DOS FANTASMAS

        atualizar_aparicoes(estado)

        # AVISAR COMO ENFRENTAR O BEN (UMA VEZ)

        if (
            estado["ben_no_farol"]
            and not estado.get("ben_dica_mostrada", False)
            and ben_transformado(estado.get("ben_entrada_ms"))
        ):

            estado["ben_dica_mostrada"] = True

            adicionar_notificacao(
                estado,
                "Aperte C no controle do farol para usar a água benta.",
                categoria="observacao"
            )

        # ATUALIZAR FILA E TEMPO DAS NOTIFICAÇÕES

        atualizar_notificacoes(
            estado,
            pygame.time.get_ticks()
        )

        # DESENHAR TELA ATUAL

        desenhar_tela(
            janela,
            estado["tela_atual"],
            imagens,
            recursos["fontes"],
            botoes,
            recursos["itens"],
            estado["itens_coletados"],
            pygame.mouse.get_pos(),
            estado
        )

        # DESENHAR O BEN NO FAROL (COM A TRANSFORMAÇÃO AO ENTRAR)

        if (
            estado["ben_no_farol"]
            and estado["tela_atual"] == "controle"
        ):

            desenhar_ben_farol(
                janela,
                inicio=estado.get("ben_entrada_ms")
            )

        # MOSTRAR OS PAINÉIS SEM SOBREPOR OUTRAS JANELAS

        teclas_pressionadas = pygame.key.get_pressed()

        shift_pressionado = (
            teclas_pressionadas[pygame.K_LSHIFT]
            or teclas_pressionadas[pygame.K_RSHIFT]
        )

        if not (
            estado["inventario_aberto"]
            or estado["menu_aberto"]
            or estado["controles_aberto"]
            or estado["diario_aberto"]
            or estado["confirmacao_recomecar"]
            or estado["transicao_ativa"]
        ):

            # STATUS DO PERSONAGEM: SOMENTE ENQUANTO SHIFT ESTIVER PRESSIONADO

            if shift_pressionado:

                desenhar_status(
                    janela,
                    recursos["fontes"],
                    estado
                )

            # STATUS DO FAROL

            if (
                estado["tela_atual"] == "controle"
                and estado["status_farol_aberto"]
            ):

                desenhar_status_farol(
                    janela,
                    recursos["fontes"],
                    estado
                )

        # DESENHAR INVENTÁRIO

        if estado["inventario_aberto"]:

            itens_inventario = {
                nome: imagem
                for nome, imagem in recursos["itens"].items()
                if estado["quantidades_itens"].get(nome, 0) > 0
            }

            if (
                estado["inspecao_aberta"]
                and estado["item_selecionado"] is not None
            ):

                nome_item = estado["item_selecionado"]

                desenhar_inspecao(
                    janela,
                    recursos["itens"][nome_item],
                    recursos["fontes"],
                    nome_item,
                    obter_descricao_item(nome_item, estado)
                )

            else:

                desenhar_inventario(
                    janela,
                    itens_inventario,
                    recursos["fontes"],
                    estado["quantidades_itens"],
                    estado["item_selecionado"]
                )

        # DESENHAR MENU

        if estado["menu_aberto"]:

            desenhar_menu(
                janela,
                recursos["fontes"],
                botoes_menu
            )

        # DESENHAR TELA DE CONTROLES

        if estado["controles_aberto"]:

            desenhar_controles(
                janela,
                recursos["fontes"],
                botao_voltar_controles
            )

        # DESENHAR CONFIRMAÇÃO DE RECOMEÇO

        if estado["confirmacao_recomecar"]:

            desenhar_confirmacao_recomecar(
                janela,
                recursos["fontes"]
            )

        # DESENHAR DIÁRIO

        if estado["diario_aberto"]:

            desenhar_diario(
                janela,
                estado["pagina_diario"],
                imagens["diario"],
                imagens["salvar_dia"],
                estado["dia_atual"],
                estado["confirmacao_encerramento"],
                paginas_diario=obter_paginas_diario(estado)
            )

        # DESENHAR NOTIFICAÇÕES DURANTE A JOGABILIDADE

        if not (
            estado["menu_aberto"]
            or estado["inventario_aberto"]
            or estado["controles_aberto"]
            or estado["diario_aberto"]
            or estado["confirmacao_recomecar"]
            or estado["transicao_ativa"]
        ):

            desenhar_notificacoes(
                janela,
                estado,
                pygame.time.get_ticks()
            )

        # DESENHAR DIÁLOGO COM FANTASMA OU HISTÓRIA ESPECIAL

        if estado["dialogo_fantasma"] is not None:

            dialogo = estado["dialogo_fantasma"]
            fantasma = dialogo["fantasma"]
            dados_fantasma = DADOS_FANTASMAS[fantasma]

            if dialogo.get("tipo") == "historia_rosabella":

                texto_dialogo = (
                    dialogo["texto"]
                    + "\n\nPressione ENTER para continuar."
                )

                opcoes_dialogo = []

            elif dialogo["etapa"] == "opcoes":

                texto_dialogo = "O que deseja fazer?"
                opcoes_dialogo = dialogo["opcoes"]

            else:

                texto_dialogo = (
                    dialogo["texto"]
                    + "\n\nPressione ENTER para continuar."
                )

                opcoes_dialogo = []

            desenhar_dialogo(
                janela,
                recursos["fontes"],
                dados_fantasma["nome"],
                texto_dialogo,
                opcoes_dialogo,
                dialogo["opcao_selecionada"]
            )

        # DESENHAR MINIGAME DO FAROL

        if estado["minigame_aberto"]:

            desenhar_minigame(
                janela,
                estado["minigame"]
            )

        # DESENHAR MINIGAME DO RÁDIO

        if estado["radio_aberto"]:

            desenhar_radio(
                janela,
                estado["radio"]
            )

        # DESENHAR O COMBATE COM O BEN

        if estado["combate_ben_aberto"]:

            desenhar_combate(
                janela,
                estado["combate_ben"]
            )

        # DESENHAR INDICADORES DE ALTERAÇÃO DOS ATRIBUTOS

        desenhar_indicadores(
            janela,
            recursos["fontes"]["pequena"]
        )

        # CAMADA ESCURA DA TRANSIÇÃO

        if estado["transicao_alpha"] > 0:

            camada_escura = pygame.Surface(
                janela.get_size()
            )

            camada_escura.fill((0, 0, 0))
            camada_escura.set_alpha(estado["transicao_alpha"])
            janela.blit(camada_escura, (0, 0))

        # DESENHAR O FINAL DO JOGO (POR CIMA DE TUDO)

        if estado["fim_aberto"]:

            desenhar_fim(
                janela,
                estado["fim"],
                recursos["fontes"]
            )

        pygame.display.flip()
        relogio.tick(FPS)

    finalizar_audio()
    pygame.quit()