
import random

from notificacoes import adicionar_notificacao


# CONFIGURAÇÕES DO SISTEMA DE EVENTOS

INTERVALO_MINIMO = 60000
INTERVALO_MAXIMO = 120000


# CENÁRIOS DISPONÍVEIS

CENARIOS_VALIDOS = [
    "inicio",
    "porta",
    "controle"
]


# EVENTOS ALEATÓRIOS
#
# Os acontecimentos serão cadastrados futuramente.
# O peso determina a probabilidade de seleção.
# Eventos perigosos deverão possuir peso menor.

EVENTOS_ALEATORIOS = []


# EVENTOS PROGRAMADOS

EVENTOS_PROGRAMADOS = []


# INICIALIZAR SISTEMA DE EVENTOS

def inicializar_eventos(estado, agora):

    estado["fila_eventos"] = []

    estado["evento_ativo"] = None

    estado["eventos_concluidos"] = []

    estado["eventos_programados_pendentes"] = []

    estado["inicio_eventos"] = agora

    estado["proximo_evento_aleatorio"] = (
        agora + random.randint(
            INTERVALO_MINIMO,
            INTERVALO_MAXIMO
        )
    )

    estado["registros_diario_eventos"] = []


# REGISTRAR UM EVENTO PROGRAMADO

def registrar_evento_programado(estado, evento, atraso_ms):

    if not isinstance(evento, dict):
        return False

    if atraso_ms < 0:
        return False

    evento_novo = evento.copy()

    evento_novo["momento_ativacao"] = (
        estado["inicio_eventos"] + atraso_ms
    )

    estado["eventos_programados_pendentes"].append(
        evento_novo
    )

    return True


# ADICIONAR EVENTO À FILA

def adicionar_evento(estado, evento):

    if not isinstance(evento, dict):
        return False

    if evento.get("cenario") not in CENARIOS_VALIDOS:
        return False

    if not evento.get("nome"):
        return False

    if not evento.get("mensagem"):
        return False

    evento_novo = evento.copy()

    evento_novo.setdefault("categoria", "acontecimento")

    evento_novo.setdefault("importante", False)

    evento_novo.setdefault("exige_acao", False)

    evento_novo.setdefault("prazo", None)

    evento_novo.setdefault("efeitos_sucesso", {})

    evento_novo.setdefault("efeitos_falha", {})

    estado["fila_eventos"].append(evento_novo)

    return True


# SORTEAR UM EVENTO ALEATÓRIO

def sortear_evento():

    if not EVENTOS_ALEATORIOS:
        return None

    eventos_validos = [
        evento
        for evento in EVENTOS_ALEATORIOS
        if evento.get("peso", 1) > 0
    ]

    if not eventos_validos:
        return None

    pesos = [
        evento.get("peso", 1)
        for evento in eventos_validos
    ]

    evento = random.choices(
        eventos_validos,
        weights=pesos,
        k=1
    )[0]

    return evento.copy()


# APLICAR CONSEQUÊNCIAS

def aplicar_consequencias(estado, efeitos):

    atributos_validos = [
        "energia",
        "sanidade",
        "exposicao",
        "vitalidade",
        "iluminacao_farol"
    ]

    for atributo, quantidade in efeitos.items():

        if atributo not in atributos_validos:
            continue

        valor_atual = estado.get(atributo)

        if valor_atual is None:
            continue

        novo_valor = valor_atual + quantidade

        estado[atributo] = max(
            0,
            min(100, novo_valor)
        )


# REGISTRAR EVENTO IMPORTANTE NO DIÁRIO

def registrar_no_diario(estado, evento):

    if not evento.get("importante", False):
        return

    registro = {
        "nome": evento["nome"],
        "mensagem": evento["mensagem"],
        "categoria": evento["categoria"]
    }

    estado["registros_diario_eventos"].append(registro)


# INICIAR UM EVENTO

def iniciar_evento(estado, evento, agora):

    evento["inicio"] = agora

    prazo = evento.get("prazo")

    if prazo is not None:

        evento["limite"] = agora + prazo

    else:

        evento["limite"] = None

    estado["evento_ativo"] = evento

    adicionar_notificacao(
        estado,
        evento["mensagem"],
        categoria=evento["categoria"],
        importante=evento["importante"]
    )

    if not evento["exige_acao"]:

        registrar_no_diario(
            estado,
            evento
        )

        estado["eventos_concluidos"].append(
            evento["nome"]
        )

        estado["evento_ativo"] = None


# FINALIZAR EVENTO

def finalizar_evento(estado, sucesso=True):

    evento = estado.get("evento_ativo")

    if evento is None:
        return False

    if sucesso:

        efeitos = evento["efeitos_sucesso"]

    else:

        efeitos = evento["efeitos_falha"]

    aplicar_consequencias(
        estado,
        efeitos
    )

    registrar_no_diario(
        estado,
        evento
    )

    estado["eventos_concluidos"].append(
        evento["nome"]
    )

    estado["evento_ativo"] = None

    return True


# RESOLVER EVENTO

def resolver_evento(estado):

    evento = estado.get("evento_ativo")

    if evento is None:
        return False

    if not evento["exige_acao"]:
        return False

    return finalizar_evento(
        estado,
        sucesso=True
    )


# ATUALIZAR SISTEMA DE EVENTOS

def atualizar_eventos(estado, agora, cenario_atual):

    # VERIFICAR EVENTOS PROGRAMADOS

    for evento in estado["eventos_programados_pendentes"][:]:

        if agora >= evento["momento_ativacao"]:

            adicionar_evento(
                estado,
                evento
            )

            estado["eventos_programados_pendentes"].remove(
                evento
            )

    # VERIFICAR EVENTOS ALEATÓRIOS

    if (
        agora >= estado["proximo_evento_aleatorio"]
        and not estado["evento_ativo"]
        and not estado["fila_eventos"]
    ):

        evento = sortear_evento()

        if evento is not None:

            adicionar_evento(
                estado,
                evento
            )

        estado["proximo_evento_aleatorio"] = (
            agora + random.randint(
                INTERVALO_MINIMO,
                INTERVALO_MAXIMO
            )
        )

    # VERIFICAR EVENTO ATIVO

    evento = estado.get("evento_ativo")

    if evento is not None:

        limite = evento.get("limite")

        if limite is not None and agora >= limite:

            finalizar_evento(
                estado,
                sucesso=False
            )

        return

    # INICIAR PRÓXIMO EVENTO COMPATÍVEL COM O CENÁRIO

    for evento in estado["fila_eventos"]:

        if evento["cenario"] == cenario_atual:

            estado["fila_eventos"].remove(evento)

            iniciar_evento(
                estado,
                evento,
                agora
            )

            break
