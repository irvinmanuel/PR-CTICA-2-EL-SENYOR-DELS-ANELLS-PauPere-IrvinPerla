import numpy as np
import random

SIZE = 12
MAX_BRONZE=6
MAX_SILVER=3
MAX_GOLD=1
barrera5_count = 0
MAX_BARRERA5 = 2
bronze_count = 0
silver_count = 0
gold_count = 0

direcciones = [
    (-1, 0),  # arriba
    (1, 0),   # abajo
    (0, -1),  # izquierda
    (0, 1),  
    (-1, -1), 
    (-1, 1),  
    (1, -1),  
    (1, 1)    
]

typerBerrier = [5, 4, 3, 3, 3]
board = np.empty((SIZE, SIZE), dtype=str)
#creamos el tablero y lo llenamos de casillas vacias representadas por "⬛"
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

#colocamos las barreras de forma aleatoria, asegurándonos de que no se superpongan ni salgan del tablero
for barrier_size in typerBerrier:

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

            barrera5_count += 1
            break
x = random.randint(0, SIZE - 1)
y = random.randint(0, SIZE - 1)
while board[x][y] != "⬛":
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)

board[x][y] = "🧘"


print(board)
print(f"Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count}")