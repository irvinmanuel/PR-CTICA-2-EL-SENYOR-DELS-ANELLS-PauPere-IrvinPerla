#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JOC DE CARTES - EL SENYOR DELS ANELLS
Pràctica 2 - Intel·ligència Artificial
Jugador Humà vs Màquina (algoritme MINIMAX)

Jerarquia: Bronze (valor 1) --> Plata (valor 2) --> Or (valor 3)
Guanya el primer jugador que allibera la carta de l'Anell d'Or.
Condició: Per alliberar una carta, cal respectar la jerarquia
(no es pot alliberar Or si no s'ha alliberat Plata, etc.)
"""

import random
import copy
import time

# ==============================================================================
# CONSTANTS I TIPUS DE CARTES
# ==============================================================================

OR     = "Or"
PLATA  = "Plata"
BRONZE = "Bronze"

JERARQUIA = {BRONZE: 1, PLATA: 2, OR: 3}
JERARQUIA_NOM = {1: BRONZE, 2: PLATA, 3: OR}

# Símbols visuals
SIMBOL = {OR: "💍", PLATA: "🥈", BRONZE: "🥉"}

# Composició de la baralla
COMPOSICIO_BARALLA = [OR] * 1 + [PLATA] * 3 + [BRONZE] * 6  # 10 cartes


# ==============================================================================
# ESTAT DEL JOC
# ==============================================================================

class Estat:
    """
    Representa l'estat complet del joc en un moment donat.
    """
    def __init__(self):
        # Baralles
        self.baralla_jugador = []
        self.baralla_maquina  = []

        # Cartes alliberades (descobertes correctament seguint jerarquia)
        self.alliberades_jugador = []
        self.alliberades_maquina  = []

        # Carta descoberta (boca amunt, pendent de decisió)
        self.descoberta_jugador = None
        self.descoberta_maquina  = None

        # Carta reservada (a part, guardada per un torn futur)
        self.reserva_jugador = None
        self.reserva_maquina  = None

        # Torns bloquejats
        self.bloqueig_jugador = 0
        self.bloqueig_maquina  = 0

        # De qui és el torn (JUGADOR o MAQUINA)
        self.torn = "JUGADOR"

        # Resultat del joc
        self.guanyador = None

    def baralla_activa(self, qui):
        return self.baralla_jugador if qui == "JUGADOR" else self.baralla_maquina

    def alliberades(self, qui):
        return self.alliberades_jugador if qui == "JUGADOR" else self.alliberades_maquina

    def descoberta(self, qui):
        return self.descoberta_jugador if qui == "JUGADOR" else self.descoberta_maquina

    def reserva(self, qui):
        return self.reserva_jugador if qui == "JUGADOR" else self.reserva_maquina

    def set_descoberta(self, qui, carta):
        if qui == "JUGADOR":
            self.descoberta_jugador = carta
        else:
            self.descoberta_maquina = carta

    def set_reserva(self, qui, carta):
        if qui == "JUGADOR":
            self.reserva_jugador = carta
        else:
            self.reserva_maquina = carta

    def proximo_alliberable(self, qui):
        """Retorna el tipus de carta que el jugador pot alliberar a continuació."""
        alliberades = self.alliberades(qui)
        if not alliberades:
            return BRONZE  # Primer cal alliberar Bronze
        max_alliberat = max(JERARQUIA[c] for c in alliberades)
        if max_alliberat < 3:
            return JERARQUIA_NOM[max_alliberat + 1]
        return None  # Ja ha alliberat Or (ha guanyat)

    def pot_alliberar(self, qui, carta):
        """Comprova si es pot alliberar la carta respectant la jerarquia."""
        return carta == self.proximo_alliberable(qui)

    def clonar(self):
        """Crea una còpia profunda de l'estat."""
        return copy.deepcopy(self)

    def ha_guanyat(self, qui):
        """El jugador guanya si ha alliberat l'anell d'Or."""
        return OR in self.alliberades(qui)


# ==============================================================================
# INICIALITZACIÓ
# ==============================================================================

def crear_baralla():
    baralla = COMPOSICIO_BARALLA[:]
    random.shuffle(baralla)
    return baralla

def inicialitzar_joc():
    estat = Estat()
    estat.baralla_jugador = crear_baralla()
    estat.baralla_maquina  = crear_baralla()
    return estat


# ==============================================================================
# LÒGICA D'ACCIONS
# ==============================================================================

def descobrir_carta(estat, qui):
    """Descobreix la primera carta de la baralla del jugador."""
    baralla = estat.baralla_activa(qui)
    if not baralla:
        return False
    carta = baralla.pop(0)
    estat.set_descoberta(qui, carta)
    return True

def accio_alliberar_descoberta(estat, qui):
    """Allibera la carta descoberta si compleix la jerarquia."""
    carta = estat.descoberta(qui)
    if carta and estat.pot_alliberar(qui, carta):
        estat.alliberades(qui).append(carta)
        estat.set_descoberta(qui, None)
        return True
    return False

def accio_reservar(estat, qui):
    """Reserva la carta descoberta."""
    carta = estat.descoberta(qui)
    if carta and estat.reserva(qui) is None:
        estat.set_reserva(qui, carta)
        estat.set_descoberta(qui, None)
        return True
    return False

def accio_alliberar_reserva(estat, qui):
    """Allibera la carta reservada si compleix la jerarquia."""
    carta = estat.reserva(qui)
    if carta and estat.pot_alliberar(qui, carta):
        estat.alliberades(qui).append(carta)
        estat.set_reserva(qui, None)
        return True
    return False

def accio_retornar_barrejar(estat, qui):
    """Retorna la carta descoberta a la baralla i barreja."""
    carta = estat.descoberta(qui)
    if carta:
        baralla = estat.baralla_activa(qui)
        baralla.append(carta)
        random.shuffle(baralla)
        estat.set_descoberta(qui, None)
        return True
    return False

def accio_bloquejar_oponent(estat, qui):
    """Bloqueja un torn a l'oponent."""
    oponent = "MAQUINA" if qui == "JUGADOR" else "JUGADOR"
    if qui == "JUGADOR":
        estat.bloqueig_maquina += 1
    else:
        estat.bloqueig_jugador += 1
    return True

def canviar_torn(estat):
    """Canvia el torn al jugador seguent."""
    oponent = "MAQUINA" if estat.torn == "JUGADOR" else "JUGADOR"

    # Comprova si l'oponent té torns bloquejats
    if oponent == "JUGADOR" and estat.bloqueig_jugador > 0:
        estat.bloqueig_jugador -= 1
        print("⚠️  El JUGADOR té el torn BLOQUEJAT per la màquina!")
        time.sleep(1)
        # El torn segueix sent de la màquina? No, canvia però saltem
        estat.torn = oponent  # assignem però marcarem com bloquejat
    elif oponent == "MAQUINA" and estat.bloqueig_maquina > 0:
        estat.bloqueig_maquina -= 1
        print("⚠️  La MÀQUINA té el torn BLOQUEJAT pel jugador!")
        time.sleep(1)
        estat.torn = oponent
    else:
        estat.torn = oponent


# ==============================================================================
# AVALUACIÓ HEURÍSTICA PER MINIMAX
# ==============================================================================

def heuristica(estat):
    """
    Funció d'avaluació heurística.
    Positiu = favorable per a la màquina.
    Negatiu = favorable per al jugador.
    """
    # Puntuació bàsica per cartes alliberades
    score_maquina  = sum(JERARQUIA[c] * 10 for c in estat.alliberades_maquina)
    score_jugador = sum(JERARQUIA[c] * 10 for c in estat.alliberades_jugador)

    # Bonus per tenir una reserva útil
    proxim_m = estat.proximo_alliberable("MAQUINA")
    proxim_j = estat.proximo_alliberable("JUGADOR")

    if estat.reserva_maquina and proxim_m and estat.reserva_maquina == proxim_m:
        score_maquina += 8
    if estat.reserva_jugador and proxim_j and estat.reserva_jugador == proxim_j:
        score_jugador += 8

    # Bonus per tenir la descoberta útil
    if estat.descoberta_maquina and proxim_m and estat.descoberta_maquina == proxim_m:
        score_maquina += 5
    if estat.descoberta_jugador and proxim_j and estat.descoberta_jugador == proxim_j:
        score_jugador += 5

    # Penalització per torns bloquejats
    score_maquina  -= estat.bloqueig_maquina  * 6
    score_jugador -= estat.bloqueig_jugador * 6

    # Bonus per tenir menys cartes a la baralla (més aprop del final)
    score_maquina  += (10 - len(estat.baralla_maquina))  * 1
    score_jugador += (10 - len(estat.baralla_jugador)) * 1

    return score_maquina - score_jugador


# ==============================================================================
# ALGORITME MINIMAX
# ==============================================================================

MAX_PROFUNDITAT = 4  # Profunditat de recerca

def obtenir_accions_possibles(estat, qui):
    """
    Retorna una llista de noms d'accions vàlides per al jugador indicat.
    Cada acció és una cadena: 'alliberar_descoberta', 'reservar', etc.
    """
    accions = []
    descoberta = estat.descoberta(qui)
    reserva    = estat.reserva(qui)
    baralla    = estat.baralla_activa(qui)

    # Primer cal descobrir una carta si no en tenim cap de descoberta
    if not descoberta and baralla:
        accions.append("descobrir")
        return accions  # L'acció de descobrir és obligatòria primer

    if descoberta:
        # Alliberar la descoberta si és possible per jerarquia
        if estat.pot_alliberar(qui, descoberta):
            accions.append("alliberar_descoberta")
        # Reservar la descoberta (si no tenim reserva)
        if reserva is None:
            accions.append("reservar")
        # Retornar a la baralla i barrejar
        accions.append("retornar_barrejar")
        # Bloquejar un torn a l'oponent (acció sempre disponible si tenim descoberta)
        accions.append("bloquejar_oponent")

    if reserva:
        # Alliberar la reserva si és possible
        if estat.pot_alliberar(qui, reserva):
            accions.append("alliberar_reserva")

    return accions

def aplicar_accio(estat, qui, accio):
    """Aplica una acció i retorna el nou estat."""
    nou = estat.clonar()
    exito = False

    if accio == "descobrir":
        exito = descobrir_carta(nou, qui)
    elif accio == "alliberar_descoberta":
        exito = accio_alliberar_descoberta(nou, qui)
    elif accio == "reservar":
        exito = accio_reservar(nou, qui)
    elif accio == "alliberar_reserva":
        exito = accio_alliberar_reserva(nou, qui)
    elif accio == "retornar_barrejar":
        exito = accio_retornar_barrejar(nou, qui)
    elif accio == "bloquejar_oponent":
        exito = accio_bloquejar_oponent(nou, qui)
        # Hem de descobrir primer o deixar torn
        if not nou.descoberta(qui):
            descobrir_carta(nou, qui)

    # Canviar torn (excepte si es tracta de descobrir, on continuem)
    if accio != "descobrir":
        oponent = "MAQUINA" if qui == "JUGADOR" else "JUGADOR"
        nou.torn = oponent

    return nou if exito else estat.clonar()

def minimax(estat, profunditat, alfa, beta, maximitzant):
    """
    Algoritme Minimax amb poda Alfa-Beta.
    - maximitzant=True: torn de la Màquina (vol maximitzar)
    - maximitzant=False: torn del Jugador (vol minimitzar)
    """
    # Casos base
    if estat.ha_guanyat("MAQUINA"):
        return 1000 + profunditat, None
    if estat.ha_guanyat("JUGADOR"):
        return -1000 - profunditat, None
    if profunditat == 0:
        return heuristica(estat), None

    qui = "MAQUINA" if maximitzant else "JUGADOR"
    accions = obtenir_accions_possibles(estat, qui)

    if not accions:
        return heuristica(estat), None

    millor_accio = accions[0]

    if maximitzant:
        millor_valor = float('-inf')
        for accio in accions:
            nou_estat = aplicar_accio(estat, qui, accio)
            # Si l'acció és "descobrir", continuem el torn del mateix jugador
            seguent_maxim = (nou_estat.torn == "MAQUINA")
            valor, _ = minimax(nou_estat, profunditat - 1, alfa, beta, seguent_maxim)
            if valor > millor_valor:
                millor_valor = valor
                millor_accio = accio
            alfa = max(alfa, millor_valor)
            if beta <= alfa:
                break
        return millor_valor, millor_accio
    else:
        millor_valor = float('inf')
        for accio in accions:
            nou_estat = aplicar_accio(estat, qui, accio)
            seguent_maxim = (nou_estat.torn == "MAQUINA")
            valor, _ = minimax(nou_estat, profunditat - 1, alfa, beta, seguent_maxim)
            if valor < millor_valor:
                millor_valor = valor
                millor_accio = accio
            beta = min(beta, millor_valor)
            if beta <= alfa:
                break
        return millor_valor, millor_accio


# ==============================================================================
# INTERFÍCIE DE TEXT
# ==============================================================================

def separador(char="═", n=60):
    print(char * n)

def mostrar_estat(estat):
    separador()
    print("🧙  JOC DE CARTES - EL SENYOR DELS ANELLS  🧙")
    separador()

    # Jugador
    print("\n👤  JUGADOR HUMÀ")
    print(f"  Baralla:     {len(estat.baralla_jugador)} cartes")
    d = estat.descoberta_jugador
    r = estat.reserva_jugador
    print(f"  Descoberta:  {SIMBOL.get(d, '─') + ' ' + (d or '─')}")
    print(f"  Reserva:     {SIMBOL.get(r, '─') + ' ' + (r or '─')}")
    print(f"  Alliberades: {' > '.join(SIMBOL[c]+c for c in estat.alliberades_jugador) or '─'}")
    if estat.bloqueig_jugador > 0:
        print(f"  ⛔ Torns bloquejats: {estat.bloqueig_jugador}")

    print("\n🤖  MÀQUINA")
    print(f"  Baralla:     {len(estat.baralla_maquina)} cartes")
    dm = estat.descoberta_maquina
    rm = estat.reserva_maquina
    print(f"  Descoberta:  {SIMBOL.get(dm, '─') + ' ' + (dm or '─')}")
    print(f"  Reserva:     {SIMBOL.get(rm, '─') + ' ' + (rm or '─')}")
    print(f"  Alliberades: {' > '.join(SIMBOL[c]+c for c in estat.alliberades_maquina) or '─'}")
    if estat.bloqueig_maquina > 0:
        print(f"  ⛔ Torns bloquejats: {estat.bloqueig_maquina}")

    print()
    proxim_j = estat.proximo_alliberable("JUGADOR")
    proxim_m = estat.proximo_alliberable("MAQUINA")
    print(f"  🎯 Jugador necessita alliberar: {SIMBOL.get(proxim_j,'✅') + ' ' + (proxim_j or 'Ha guanyat!')}")
    print(f"  🎯 Màquina necessita alliberar: {SIMBOL.get(proxim_m,'✅') + ' ' + (proxim_m or 'Ha guanyat!')}")
    separador()

def menu_accions(accions):
    noms = {
        "descobrir":           "Descobrir carta de la baralla",
        "alliberar_descoberta":"Alliberar carta descoberta",
        "reservar":            "Reservar carta descoberta",
        "alliberar_reserva":   "Alliberar carta reservada",
        "retornar_barrejar":   "Retornar descoberta a la baralla i barrejar",
        "bloquejar_oponent":   "Bloquejar un torn a la màquina",
    }
    print("\n🃏  ACCIONS DISPONIBLES:")
    for i, a in enumerate(accions, 1):
        print(f"  {i}. {noms.get(a, a)}")
    print()

def demanar_accio(accions):
    menu_accions(accions)
    while True:
        try:
            opcio = int(input("➡️  Tria una opció: "))
            if 1 <= opcio <= len(accions):
                return accions[opcio - 1]
            print("  Opció no vàlida.")
        except ValueError:
            print("  Introdueix un número.")


# ==============================================================================
# LÒGICA DEL TORN
# ==============================================================================

NOMS_ACCIO = {
    "descobrir":           "Descobreix una carta",
    "alliberar_descoberta":"Allibera la carta descoberta",
    "reservar":            "Reserva la carta descoberta",
    "alliberar_reserva":   "Allibera la carta reservada",
    "retornar_barrejar":   "Retorna la descoberta i barreja",
    "bloquejar_oponent":   "Bloqueja un torn a l'oponent",
}

def torn_jugador(estat):
    """Gestiona el torn del jugador humà."""
    print("\n🟢  TORN DEL JUGADOR")

    # Si no tenim carta descoberta, descobrim primer
    if not estat.descoberta_jugador and estat.baralla_jugador:
        input("  Prem ENTER per descobrir una carta...")
        if descobrir_carta(estat, "JUGADOR"):
            carta = estat.descoberta_jugador
            print(f"  📤 Has descobert: {SIMBOL[carta]} {carta}")
        return  # Continuem al pròxim pas

    accions = obtenir_accions_possibles(estat, "JUGADOR")
    if not accions:
        print("  No hi ha accions disponibles.")
        canviar_torn(estat)
        return

    accio = demanar_accio(accions)
    executar_accio_i_mostrar(estat, "JUGADOR", accio)

    if not estat.ha_guanyat("JUGADOR"):
        canviar_torn(estat)

def torn_maquina(estat):
    """Gestiona el torn de la màquina amb Minimax."""
    print("\n🔴  TORN DE LA MÀQUINA (pensant...)")
    time.sleep(0.8)

    # Si no tenim carta descoberta, descobrim primer
    if not estat.descoberta_maquina and estat.baralla_maquina:
        if descobrir_carta(estat, "MAQUINA"):
            carta = estat.descoberta_maquina
            print(f"  📤 La màquina descobreix: {SIMBOL[carta]} {carta}")
        time.sleep(0.5)
        return

    accions = obtenir_accions_possibles(estat, "MAQUINA")
    if not accions:
        print("  La màquina no té accions disponibles.")
        canviar_torn(estat)
        return

    # Decisió Minimax
    _, millor_accio = minimax(estat, MAX_PROFUNDITAT, float('-inf'), float('inf'), True)
    if millor_accio is None:
        millor_accio = accions[0]

    print(f"  🤖 La màquina decideix: {NOMS_ACCIO.get(millor_accio, millor_accio)}")
    time.sleep(0.5)
    executar_accio_i_mostrar(estat, "MAQUINA", millor_accio)

    if not estat.ha_guanyat("MAQUINA"):
        canviar_torn(estat)

def executar_accio_i_mostrar(estat, qui, accio):
    """Executa l'acció sobre l'estat real i mostra el resultat."""
    if accio == "descobrir":
        descobrir_carta(estat, qui)
        carta = estat.descoberta(qui)
        print(f"  📤 Descobreix: {SIMBOL[carta]} {carta}")

    elif accio == "alliberar_descoberta":
        carta = estat.descoberta(qui)
        if accio_alliberar_descoberta(estat, qui):
            print(f"  ✅ Alliberada: {SIMBOL[carta]} {carta}")
        else:
            print(f"  ❌ No es pot alliberar {carta} (no és el torn correcte en la jerarquia)")

    elif accio == "reservar":
        carta = estat.descoberta(qui)
        if accio_reservar(estat, qui):
            print(f"  📦 Reservada: {SIMBOL[carta]} {carta}")
        else:
            print(f"  ❌ No s'ha pogut reservar")

    elif accio == "alliberar_reserva":
        carta = estat.reserva(qui)
        if accio_alliberar_reserva(estat, qui):
            print(f"  ✅ Reserva alliberada: {SIMBOL[carta]} {carta}")
        else:
            print(f"  ❌ No es pot alliberar la reserva ara")

    elif accio == "retornar_barrejar":
        carta = estat.descoberta(qui)
        if accio_retornar_barrejar(estat, qui):
            print(f"  🔀 {SIMBOL[carta]} {carta} retornada i baralla barrejada")

    elif accio == "bloquejar_oponent":
        oponent = "MAQUINA" if qui == "JUGADOR" else "JUGADOR"
        accio_bloquejar_oponent(estat, qui)
        print(f"  🚫 Torn bloquejat a {'la màquina' if oponent == 'MAQUINA' else 'el jugador'}!")
        # Descobrir carta després de bloquejar si no en tenim
        if not estat.descoberta(qui) and estat.baralla_activa(qui):
            descobrir_carta(estat, qui)
            carta = estat.descoberta(qui)
            if carta:
                print(f"  📤 Carta descoberta automàticament: {SIMBOL[carta]} {carta}")


# ==============================================================================
# BUCLE PRINCIPAL DEL JOC
# ==============================================================================

def joc_principal():
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║   💍  JOC DE CARTES - EL SENYOR DELS ANELLS  💍  ║")
    print("║         Intel·ligència Artificial - IA          ║")
    print("║              Algoritme MINIMAX                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print("📋  REGLES:")
    print("  • Cada jugador té 10 cartes: 1 Or, 3 Plata, 6 Bronze")
    print("  • Cal alliberar les cartes en ordre: Bronze → Plata → Or")
    print("  • Guanya el primer que allibera l'Anell d'Or 💍")
    print()
    print("🎮  ACCIONS PER TORN:")
    print("  1. Descobrir una carta de la baralla")
    print("  2. Alliberar la carta descoberta (si és del rang correcte)")
    print("  3. Reservar la carta descoberta (per usar-la més tard)")
    print("  4. Alliberar la carta reservada (si és del rang correcte)")
    print("  5. Retornar la descoberta i barrejar la baralla")
    print("  6. Bloquejar un torn a l'oponent")
    print()
    input("  Prem ENTER per començar el joc...")

    estat = inicialitzar_joc()
    torn_num = 0

    while not estat.guanyador:
        torn_num += 1
        print(f"\n{'─'*20} TORN {torn_num} {'─'*20}")
        mostrar_estat(estat)

        if estat.torn == "JUGADOR":
            if estat.bloqueig_jugador > 0:
                estat.bloqueig_jugador -= 1
                print("⛔  El teu torn està BLOQUEJAT! Perds aquest torn.")
                estat.torn = "MAQUINA"
                input("  Prem ENTER per continuar...")
                continue
            torn_jugador(estat)
        else:
            if estat.bloqueig_maquina > 0:
                estat.bloqueig_maquina -= 1
                print("⛔  La màquina té el torn BLOQUEJAT! Perd el seu torn.")
                estat.torn = "JUGADOR"
                time.sleep(1)
                continue
            torn_maquina(estat)

        # Comprovar guanyadors
        if estat.ha_guanyat("JUGADOR"):
            estat.guanyador = "JUGADOR"
        elif estat.ha_guanyat("MAQUINA"):
            estat.guanyador = "MAQUINA"

        # Comprovar si cap dels dos pot continuar (empat / sense cartes)
        elif not estat.baralla_jugador and not estat.descoberta_jugador and not estat.reserva_jugador:
            if not estat.baralla_maquina and not estat.descoberta_maquina and not estat.reserva_maquina:
                print("\n🤝  EMPAT! Cap jugador ha alliberat l'Anell d'Or.")
                break

        if torn_num > 200:  # Salvaguarda per evitar bucles infinits
            print("\n⚠️  El joc ha durat massa torns. Finalitzant...")
            break

        input("\n  Prem ENTER per continuar...")

    # Final del joc
    separador("═")
    mostrar_estat(estat)
    if estat.guanyador == "JUGADOR":
        print("\n🎉🎉  ENHORABONA! Has guanyat l'Anell d'Or!  🎉🎉")
        print("    'Un anell per governar-los a tots...'")
    elif estat.guanyador == "MAQUINA":
        print("\n😞  La màquina ha guanyat l'Anell d'Or.")
        print("    'Sauron triomfa... per ara.'")
    separador("═")


# ==============================================================================
# ENTRADA
# ==============================================================================

if __name__ == "__main__":
    while True:
        joc_principal()
        print()
        tornar = input("Vols jugar una altra partida? (s/n): ").strip().lower()
        if tornar != 's':
            print("\nFins aviat, aventurer! 🧙")
            break
