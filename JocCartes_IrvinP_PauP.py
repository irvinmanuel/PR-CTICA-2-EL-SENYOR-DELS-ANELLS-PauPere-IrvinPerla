#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import random
import time

from games import Game, minmax_decision

OR = "Or"
PLATA = "Plata"
BRONZE = "Bronze"

JERARQUIA = {BRONZE: 1, PLATA: 2, OR: 3}
JERARQUIA_NOM = {1: BRONZE, 2: PLATA, 3: OR}

TOTAL_OR = 1
TOTAL_PLATA = 3
TOTAL_BRONZE = 6

COMPOSICIO = [OR] * TOTAL_OR + [PLATA] * TOTAL_PLATA + [BRONZE] * TOTAL_BRONZE

MAX_PASOS_MINMAX = 6


def nou_estat_inicial():
    def baralla():
        b = COMPOSICIO[:]
        random.shuffle(b)
        return tuple(b)

    return {
        "baralla_J": baralla(),
        "baralla_M": baralla(),
        "descoberta_J": None,
        "descoberta_M": None,
        "reserva_J": None,
        "reserva_M": None,
        "alliberades_J": (),
        "alliberades_M": (),
        "bloqueig_J": 0,
        "bloqueig_M": 0,
        "bloqueo_usado_J": False,
        "bloqueo_usado_M": False,
        "pasos": 0,
        "torn": "J",
    }


def _key(estat, camp, qui):
    return estat[f"{camp}_{qui}"]


def _contar_alliberadas(estat, qui):
    alliberades = _key(estat, "alliberades", qui)
    return {
        BRONZE: alliberades.count(BRONZE),
        PLATA: alliberades.count(PLATA),
        OR: alliberades.count(OR),
    }


def _proximo_alliberable(estat, qui):
    compt = _contar_alliberadas(estat, qui)
    if compt[BRONZE] < TOTAL_BRONZE:
        return BRONZE
    if compt[PLATA] < TOTAL_PLATA:
        return PLATA
    if compt[OR] < TOTAL_OR:
        return OR
    return None


def _pot_alliberar(estat, qui, carta):
    return carta == _proximo_alliberable(estat, qui)


def _ha_guanyat(estat, qui):
    return OR in _key(estat, "alliberades", qui)


def _barreja_determinista(baralla, seed_text):
    digest = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)
    rng = random.Random(seed)
    b = list(baralla)
    rng.shuffle(b)
    return tuple(b)


class JocSenyorAnells(Game):

    def __init__(self, estat_inicial, usar_limite=False, max_pasos=MAX_PASOS_MINMAX):
        self.initial = estat_inicial
        self.usar_limite = usar_limite
        self.max_pasos = max_pasos
        self.base_pasos = 0

    def actions(self, state):
        qui = state["torn"]
        descoberta = _key(state, "descoberta", qui)
        reserva = _key(state, "reserva", qui)
        baralla = _key(state, "baralla", qui)
        accions = []

        if not descoberta:
            if baralla:
                accions.append("DESCOBRIR")
            return accions

        if _pot_alliberar(state, qui, descoberta):
            accions.append("ALLIBERAR_DESCOBERTA")

        if reserva is None:
            accions.append("RESERVAR")

        if reserva and _pot_alliberar(state, qui, reserva):
            accions.append("ALLIBERAR_RESERVA")

        accions.append("RETORNAR_BARREJAR")

        if not _key(state, "bloqueo_usado", qui):
            accions.append("BLOQUEJAR_OPONENT")

        return accions

    def result(self, state, move):
        e = {k: v for k, v in state.items()}
        e["pasos"] = e.get("pasos", 0) + 1
        qui = e["torn"]
        opon = "M" if qui == "J" else "J"

        if move == "DESCOBRIR":
            baralla = list(_key(e, "baralla", qui))
            carta = baralla.pop(0)
            e[f"baralla_{qui}"] = tuple(baralla)
            e[f"descoberta_{qui}"] = carta

        elif move == "ALLIBERAR_DESCOBERTA":
            carta = _key(e, "descoberta", qui)
            e[f"alliberades_{qui}"] = _key(e, "alliberades", qui) + (carta,)
            e[f"descoberta_{qui}"] = None
            e["torn"] = opon

        elif move == "RESERVAR":
            carta = _key(e, "descoberta", qui)
            e[f"reserva_{qui}"] = carta
            e[f"descoberta_{qui}"] = None
            e["torn"] = opon

        elif move == "ALLIBERAR_RESERVA":
            carta = _key(e, "reserva", qui)
            e[f"alliberades_{qui}"] = _key(e, "alliberades", qui) + (carta,)
            e[f"reserva_{qui}"] = None
            e["torn"] = opon

        elif move == "RETORNAR_BARREJAR":
            carta = _key(e, "descoberta", qui)
            baralla = list(_key(e, "baralla", qui)) + [carta]
            seed_text = f"{qui}|{e['pasos']}|{','.join(baralla)}|{carta}"
            e[f"baralla_{qui}"] = _barreja_determinista(baralla, seed_text)
            e[f"descoberta_{qui}"] = None
            e["torn"] = opon

        elif move == "BLOQUEJAR_OPONENT":
            e[f"bloqueig_{opon}"] = _key(e, "bloqueig", opon) + 1
            e[f"bloqueo_usado_{qui}"] = True
            e["torn"] = opon

        return e

    def utility(self, state, player):
        if _ha_guanyat(state, "M"):
            return 1000
        if _ha_guanyat(state, "J"):
            return -1000

        score_M = sum(JERARQUIA[c] * 10 for c in state["alliberades_M"])
        score_J = sum(JERARQUIA[c] * 10 for c in state["alliberades_J"])

        prox_M = _proximo_alliberable(state, "M")
        prox_J = _proximo_alliberable(state, "J")

        if state["descoberta_M"] and prox_M and state["descoberta_M"] == prox_M:
            score_M += 5
        if state["reserva_M"] and prox_M and state["reserva_M"] == prox_M:
            score_M += 8
        if state["descoberta_J"] and prox_J and state["descoberta_J"] == prox_J:
            score_J += 5
        if state["reserva_J"] and prox_J and state["reserva_J"] == prox_J:
            score_J += 8

        score_M -= state["bloqueig_M"] * 6
        score_J -= state["bloqueig_J"] * 6

        score_M += (10 - len(state["baralla_M"])) * 1
        score_J += (10 - len(state["baralla_J"])) * 1

        diferencia = score_M - score_J
        return diferencia if player == "M" else -diferencia

    def terminal_test(self, state):
        if _ha_guanyat(state, "J") or _ha_guanyat(state, "M"):
            return True
        if self.usar_limite and (state.get("pasos", 0) - self.base_pasos) >= self.max_pasos:
            return True
        return False

    def to_move(self, state):
        return state["torn"]


SEP = "=" * 62

NOM_ACCIO = {
    "DESCOBRIR": "Descobreix una carta de la baralla",
    "ALLIBERAR_DESCOBERTA": "Allibera la carta descoberta",
    "RESERVAR": "Reserva la carta descoberta",
    "ALLIBERAR_RESERVA": "Allibera la carta reservada",
    "RETORNAR_BARREJAR": "Retorna la descoberta i barreja",
    "BLOQUEJAR_OPONENT": "Bloqueja un torn a l'oponent",
}


def mostrar_estat(estat):
    print(f"\n{SEP}")
    print("JOC DE CARTES - EL SENYOR DELS ANELLS")
    print(SEP)
    for qui, nom in [("J", "JUGADOR"), ("M", "MAQUINA")]:
        d = estat[f"descoberta_{qui}"]
        r = estat[f"reserva_{qui}"]
        a = estat[f"alliberades_{qui}"]
        bl = estat[f"bloqueig_{qui}"]
        pr = _proximo_alliberable(estat, qui)
        print(f"\n  {nom}")
        print(f"  Baralla: {len(estat[f'baralla_{qui}'])} cartes")
        print(f"  Descoberta: {d if d else '-'}")
        print(f"  Reserva: {r if r else '-'}")
        print(f"  Alliberades: {' -> '.join(a) if a else '-'}")
        print(f"  Necessita: {pr if pr else 'Ha guanyat!'}")
        if bl:
            print(f"  Torns bloquejats: {bl}")
    print(f"\n{SEP}")


def demanar_accio(accions):
    print("\nACCIONS DISPONIBLES:")
    for i, a in enumerate(accions, 1):
        print(f"  {i}. {NOM_ACCIO.get(a, a)}")
    while True:
        try:
            op = int(input("\nTria una opcio: "))
            if 1 <= op <= len(accions):
                return accions[op - 1]
            print("  Opcio no valida, torna a intentar.")
        except ValueError:
            print("  Cal introduir un numero.")


def descriure_resultat(estat_abans, estat_despres, qui, accio):
    carta_d = estat_abans.get(f"descoberta_{qui}")
    carta_r = estat_abans.get(f"reserva_{qui}")
    opon_nom = "la maquina" if qui == "J" else "el jugador"

    missatges = {
        "DESCOBRIR": lambda: f"Carta descoberta: {estat_despres[f'descoberta_{qui}']}",
        "ALLIBERAR_DESCOBERTA": lambda: f"Alliberada: {carta_d}",
        "RESERVAR": lambda: f"Reservada: {carta_d}",
        "ALLIBERAR_RESERVA": lambda: f"Reserva alliberada: {carta_r}",
        "RETORNAR_BARREJAR": lambda: f"{carta_d} retornada i baralla barrejada",
        "BLOQUEJAR_OPONENT": lambda: f"Torn bloquejat a {opon_nom}!",
    }
    fn = missatges.get(accio)
    if fn:
        try:
            print(f"  {fn()}")
        except KeyError:
            pass


def joc_principal():
    print()
    print("=" * 54)
    print("  JOC DE CARTES - EL SENYOR DELS ANELLS")
    print("  Intel·ligencia Artificial - Minmax")
    print("=" * 54)
    print("""
REGLES:
  Baralla: 1 Or, 3 Plata, 6 Bronze (10 cartes per jugador)
  Cal alliberar en ordre estricte: 6 Bronze -> 3 Plata -> 1 Or
  Guanya el primer que allibera l'Anell d'Or

  La MAQUINA utilitza minmax_decision de games.py.
    """)
    input("  Prem ENTER per comenar...")

    estat_inicial = nou_estat_inicial()
    joc = JocSenyorAnells(estat_inicial, usar_limite=False)
    joc_ai = JocSenyorAnells(estat_inicial, usar_limite=True, max_pasos=MAX_PASOS_MINMAX)
    estat = estat_inicial
    torn_num = 0

    while not joc.terminal_test(estat):
        torn_num += 1
        print(f"\n{'-'*20} TORN {torn_num} {'-'*20}")
        mostrar_estat(estat)

        qui = estat["torn"]

        if qui == "J" and estat["bloqueig_J"] > 0:
            estat = {**estat, "bloqueig_J": estat["bloqueig_J"] - 1, "torn": "M"}
            print("\nEl teu torn esta BLOQUEJAT per la maquina. Perds el torn.")
            input("  Prem ENTER per continuar...")
            continue

        if qui == "M" and estat["bloqueig_M"] > 0:
            estat = {**estat, "bloqueig_M": estat["bloqueig_M"] - 1, "torn": "J"}
            print("\nLa maquina te el torn BLOQUEJAT. Perd el seu torn.")
            time.sleep(1.0)
            continue

        if qui == "J":
            print("\nTORN DEL JUGADOR")
            accions = joc.actions(estat)
            if not accions:
                print("  No hi ha accions disponibles. Passa torn.")
                estat = {**estat, "torn": "M"}
                continue
            accio = demanar_accio(accions)

        else:
            print("\nTORN DE LA MAQUINA (cercant la millor accio amb Minimax...)")
            time.sleep(0.6)
            accions = joc.actions(estat)
            if not accions:
                print("  La maquina no te accions disponibles. Passa torn.")
                estat = {**estat, "torn": "J"}
                continue

            joc_ai.base_pasos = estat.get("pasos", 0)
            accio = minmax_decision(estat, joc_ai)

            if accio is None:
                accio = accions[0]
            print(f"  La maquina decideix: {NOM_ACCIO.get(accio, accio)}")
            time.sleep(0.4)

        estat_nou = joc.result(estat, accio)
        descriure_resultat(estat, estat_nou, qui, accio)
        estat = estat_nou

        if joc.terminal_test(estat):
            break

        if torn_num > 300:
            print("\nEl joc ha durat massa torns. Finalitzant per seguretat.")
            break

        if qui == "J":
            input("\n  Prem ENTER per continuar...")

    print(f"\n{SEP}")
    mostrar_estat(estat)
    if _ha_guanyat(estat, "J"):
        print("\nEnhorabona! Has guanyat l'Anell d'Or!")
        print("  'Un anell per governar-los a tots...'")
    elif _ha_guanyat(estat, "M"):
        print("\nLa maquina ha guanyat l'Anell d'Or.")
        print("  'Sauron triomfa... per ara.'")
    else:
        print("\nPartida finalitzada sense guanyador clar.")
    print(SEP)


if __name__ == "__main__":
    while True:
        joc_principal()
        print()
        tornar = input("Vols jugar una altra partida? (s/n): ").strip().lower()
        if tornar != "s":
            print("\nFins aviat, aventurer!")
            break
