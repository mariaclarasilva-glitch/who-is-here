import random

import pygame


# SISTEMA DE APARIÇÕES DOS FANTASMAS


def atualizar_aparicoes(estado):

    dia = estado["dia_atual"]

    # NÃO PERMITIR OUTRA APARIÇÃO SE JÁ EXISTIR UM FANTASMA NA PORTA

    if estado.get("fantasma_na_porta") is not None:
        return

    # DEPOIS QUE O BEN ENTRA NO FAROL, NINGUÉM MAIS APARECE

    if estado.get("ben_no_farol", False):
        return

    # EVITAR MAIS DE UMA VERIFICAÇÃO NO MESMO DIA

    if estado.get("dia_verificacao_fantasmas") == dia:
        return

    estado["dia_verificacao_fantasmas"] = dia

    # FINAL DO JOGO: BEN NO 5º DIA (>= PARA NÃO PERDER O EVENTO)
    # O BEN SÓ APARECE QUANDO ANABELLE E ROSABELLA NÃO ESTÃO NO FAROL,
    # PARA NÃO ATRAPALHAR O COMBATE. SE ELAS AINDA ESTIVEREM,
    # ELE ESPERA E APARECE NO DIA EM QUE O FAROL ESTIVER LIVRE.

    if (
        dia >= 565
        and not estado.get("ben_apareceu", False)
    ):

        if (
            estado.get("anabelle_no_farol", False)
            or estado.get("rosabella_no_farol", False)
        ):
            return

        estado["fantasma_na_porta"] = "ben"
        estado["ben_apareceu"] = True

        # GARANTIR ÁGUA BENTA PARA O COMBATE

        quantidades = estado.setdefault("quantidades_itens", {})
        quantidades["Água benta"] = max(
            quantidades.get("Água benta", 0), 3
        )

        return

    # EVENTO CANÔNICO DE ROSABELLA

    if (
        dia == 562
        and not estado.get("rosabella_apareceu", False)
    ):

        estado["fantasma_na_porta"] = "rosabella"
        estado["rosabella_apareceu"] = True

        return

    # APARIÇÃO ALEATÓRIA DE ANABELLE DURANTE A MARÉ ALTA

    if 562 < dia < 565:

        chance_anabelle = 20

        if random.randint(1, 100) <= chance_anabelle:

            estado["fantasma_na_porta"] = "anabelle"


# APLICAR ALTERAÇÕES NOS ATRIBUTOS

def alterar_atributo(estado, atributo, quantidade):

    valor_atual = estado.get(atributo)

    if valor_atual is None:
        return

    estado[atributo] = max(
        0,
        min(100, valor_atual + quantidade)
    )


# INICIAR CONTATO COM UM FANTASMA

def aplicar_efeitos_contato(estado):

    alterar_atributo(estado, "sanidade", -5)

    alterar_atributo(estado, "exposicao", 10)


# EXPULSAR O FANTASMA

def aplicar_efeito_expulsar(estado):

    alterar_atributo(estado, "sanidade", -15)


# PERMITIR A ENTRADA DO FANTASMA

def aplicar_efeito_deixar_entrar(estado, fantasma=None):

    alterar_atributo(estado, "exposicao", 10)

    # O BEN ENTRA COMO "BEM" E SE REVELA "MAL" NO FAROL

    if fantasma == "ben":
        estado["ben_no_farol"] = True
        estado["ben_entrada_ms"] = pygame.time.get_ticks()