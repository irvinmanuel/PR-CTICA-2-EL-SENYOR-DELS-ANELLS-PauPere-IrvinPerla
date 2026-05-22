import itertools
import numpy as np
import random
from search import Node, UndirectedGraph, GraphProblem, astar_search
#from utils import show_map

SIZE = 12
MAX_BRONZE=6
MAX_SILVER=3
MAX_GOLD=1
barrera5_count = 0
MAX_BARRERA5 = 2
puede_plata = False
puede_oro = False

bronze_count = 0
silver_count = 0    
gold_count = 0

movimientos = 0
movimientos_maximos = 0 


direcciones = [
    (-1, 0),  # arriba
    (1, 0),   # abajo
    (0, -1),  # izquierda
    (0, 1),  # derecha
    (-1, -1), 
    (-1, 1),  
    (1, -1),  
    (1, 1)    
]

typerBerrier = [5, 4, 3, 3, 3]
board = np.empty((SIZE, SIZE), dtype=str)
#creamos el tablero y lo llenamos de casillas vacias representadas por "⬛"
def crear_tablero():
    global bronze_count, silver_count, gold_count
    global movimientos_maximos, movimientos


    for i in range(SIZE):
        for j in range(SIZE):
            board[i][j] = "⬛"  

    #colocamos las monedas de bronce, plata y oro en el tablero de forma aleatoria
    for i in range(MAX_BRONZE+MAX_SILVER+MAX_GOLD):
        while True:
            x = random.randint(0, SIZE-1)
            y = random.randint(0, SIZE-1)
            if board[x][y] == "⬛":
                if bronze_count < MAX_BRONZE:
                    board[x][y] = "🥉"
                    bronze_count += 1
                elif silver_count < MAX_SILVER:
                    board[x][y] = "🥈"
                    silver_count += 1
                elif gold_count < MAX_GOLD:
                    board[x][y] = "🥇"
                    gold_count += 1
                break
    bronze_count = 0
    silver_count = 0
    gold_count = 0

    #colocamos las barreras de forma aleatoria, asegurándonos de que no se superpongan ni salgan del tablero
    for barrier_size in typerBerrier:
        global barrera5_count
        while True:

            x = random.randint(0, SIZE - 1)
            y = random.randint(0, SIZE - 1)

            dx, dy = random.choice(direcciones)

            posiciones = []
            valido = True

            for i in range(barrier_size):

                nx = x + dx * i
                ny = y + dy * i

                # comprobar límites
                if nx < 0 or nx >= SIZE or ny < 0 or ny >= SIZE:
                    valido = False
                    break

                # comprobar si está ocupado
                if board[nx][ny] != "⬛":
                    valido = False
                    break

                posiciones.append((nx, ny))

            # colocar si es válido
            if valido:

                for px, py in posiciones:
                    board[px][py] = "🧱"

                break
        


    #colocamos al jugador        
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)
    while board[x][y] != "⬛":
        x = random.randint(0, SIZE - 1)
        y = random.randint(0, SIZE - 1)

    board[x][y] = "🧘"


    print(board)
    print(f"Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count}")
    camino_optimo = buscar_mejor_camino(board)

    if camino_optimo is None:
        print("ESTE TABLERO NO TIENE SOLUCIÓN, GENERANDO UNO NUEVO...\n\n")
        return crear_tablero()
    

    coste_optimo = len(camino_optimo)

    movimientos = 0
    movimientos_maximos = coste_optimo + 5

    print(f"Coste óptimo del tablero: {coste_optimo}")
    print(f"Máximo de movimientos permitidos: {movimientos_maximos}")
    return board

def find_player_position(board):
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == "🧘":
                return (i, j)
    return None

def find_Cards(symbol, board):
    cards = []
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == symbol:
                cards.append((i, j))
    return cards


def generar_grafo(board, celdas_bloqueadas=set()):
    grafo = {}

    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == "🧱":
                continue
            if (i, j) in celdas_bloqueadas:
                continue  # esta celda no existe en este grafo

            vecinos = {}

            for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < SIZE and 0 <= nj < SIZE:
                    if puede_moverse((ni, nj), board):
                        if (ni, nj) not in celdas_bloqueadas:
                            vecinos[(ni, nj)] = 1

            grafo[(i, j)] = vecinos
    

    return UndirectedGraph(grafo)

def puede_moverse(pos, board):
    x, y = pos
    if x < 0 or x >= SIZE or y < 0 or y >= SIZE:
        return False
    if board[x][y] == "🧱":
        return False
    
    if board[x][y] == "🥈" and not puede_plata:
        return False
    if board[x][y] == "🥇" and not puede_oro:
        return False
    return True

def buscar_mejor_camino(board):
    inicio = find_player_position(board)

    bronces = find_Cards("🥉", board)
    platas  = find_Cards("🥈", board)
    oros    = find_Cards("🥇", board)

    camino_completo = []
    posicion_actual = inicio

    fases = [
        (bronces, frozenset(platas) | frozenset(oros)),
        (platas,  frozenset(oros)),
        (oros,    frozenset()),
    ]

    for grupo, bloqueadas in fases:
        if not grupo:
            continue

        grafo_fase = generar_grafo(board, celdas_bloqueadas=bloqueadas)

        # Cache por fase: (origen, destino) -> path calculado
        cache = {}

        mejor_coste = float("inf")
        mejor_camino_grupo = None
        mejor_posicion_final = None

        for perm in itertools.permutations(grupo):
            posicion = posicion_actual
            camino_total = []
            coste_total = 0
            valido = True

            for moneda in perm:
                key = (posicion, moneda)

                if key not in cache:
                    problema = Tablero(board, grafo_fase, posicion, moneda)
                    sol = astar_search(problema)
                    # Guardamos el path o None si no hay solución
                    cache[key] = sol.path() if sol is not None else None

                path = cache[key]

                if path is None:
                    valido = False
                    break

                camino_total.extend(n.state for n in path[1:])
                coste_total += len(path) - 1
                posicion = moneda

            if valido and coste_total < mejor_coste:
                mejor_coste = coste_total
                mejor_camino_grupo = camino_total
                mejor_posicion_final = posicion

        if mejor_camino_grupo is None:
            return None

        camino_completo.extend(mejor_camino_grupo)
        posicion_actual = mejor_posicion_final

    return camino_completo
def pintar_camino(board, camino, solo_siguiente=False):
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == "🟦":
                board[i][j] = "⬛"  # Limpiar posición del jugador
    if solo_siguiente:
        if camino:
            i, j = camino[0]
            if board[i][j] == "⬛" :
                board[i][j] = "🟦"
    else:
        for i, j in camino:
            if board[i][j] == "⬛":

                board[i][j] = "🟦"
        
    print(board)
    return board


def mover_jugador(board, posicion_actual, direccion, ):
    global puede_plata, puede_oro, ganaste
    global bronze_count, silver_count, gold_count
    global movimientos, movimientos_maximos

   
    y, x = posicion_actual
    dy, dx = direccion
    nueva_posicion = ( y + dy, x + dx,)

    if puede_moverse(nueva_posicion, board, ):
        movimientos += 1
        print(f"Movimientos: {movimientos}/{movimientos_maximos}")  
        if board[nueva_posicion[0]][nueva_posicion[1]] == "🥉":
            print("Has recogido una moneda de bronce")
            bronze_count += 1
            if bronze_count >= MAX_BRONZE:
                puede_plata = True
        elif board[nueva_posicion[0]][nueva_posicion[1]] == "🥈":
            print("Has recogido una moneda de plata")
            silver_count += 1
            if silver_count >= MAX_SILVER:
                puede_oro = True
        elif board[nueva_posicion[0]][nueva_posicion[1]] == "🥇":
            print("🏆 Has recogido la moneda de oro")
            gold_count += 1
            ganaste = True

            print(f"Ganaste usando {movimientos} movimientos")
            print(f"Límite permitido: {movimientos_maximos}")
            return (1000,1000)  # Retorna un valor alto para indicar victoria
        board[y][x] = "⬛"  # Aseguramos que el jugador se mantenga visible
        board[nueva_posicion[0]][nueva_posicion[1]] = "🧘"


        print(board)
        print(f"Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count}")
        if movimientos >= movimientos_maximos:
            print("¡Has superado el límite de movimientos! Has perdido.")
            return (-1000, -1000)  # Retorna un valor bajo para indicar derrota
        return nueva_posicion
    
    else:

        return posicion_actual
    




################################################################
class Tablero(GraphProblem):
    def __init__(self, board, grafo, inicio, objetivo):
        super().__init__(inicio, objetivo, grafo)

    def h(self, node):
        # Distancia Manhattan como heurística admisible para grids
        x1, y1 = node.state
        x2, y2 = self.goal
        return abs(x1 - x2) + abs(y1 - y2)
def main():
    """Función principal del programa."""

    board = crear_tablero()
    print("Tablero y grafo creados correctamente")
    print(board)
    print("Grafo generado correctamente")
    camino=buscar_mejor_camino(board)
    board = pintar_camino(board, camino)
    print(board)
    """problema = Tablero(board, grafo)
    solucion = astar_search(problema)
    print("Solución encontrada:", solucion is not None)
    if solucion:
        camino = solucion.path()

        print("\n📍 Camino encontrado:\n")
        for nodo in camino:
            print(nodo.state)"""
   

    print("Tablero creado correctamente")

if __name__ == "__main__":
        main()