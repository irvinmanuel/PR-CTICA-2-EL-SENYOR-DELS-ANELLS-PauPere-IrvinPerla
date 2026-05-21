import tablero
import keyboard


def main():
    print("Bienvenido al juego del Señor de los Anillos")
    print("Usa las flechas para mover al jugador (🧘) y recoge las monedas (🥉, 🥈, 🥇)")
    print("#########REGLAS DEL JUEGO#########")
    print("1. Mueve al jugador con las flechas del teclado.")
    print("2. Recoge las monedas en el orden correcto para desbloquear nuevas áreas.")
    print("3. Si presionas 'e', se mostrará el mejor camino para recoger todas las monedas.")
    print("4. Si presionas 'q', se mostrará el siguiente mejor movimiento que puedes hacer.")
    print("5. Presiona 'esc' para salir del juego.")
    print("para iniciar presiona la letra 'z'")

    keyboard.wait("z")
    board = tablero.crear_tablero()
    

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "flecha izquierda":
                tablero.mover_jugador(board, tablero.find_player_position(board), (0, -1))  # Mover a la izquierda
                print("Flecha izquierda presionada")
            elif event.name == "flecha derecha":
                tablero.mover_jugador(board, tablero.find_player_position(board), (0, 1))  # Mover a la derecha
                print("Flecha derecha presionada")
            elif event.name == "flecha arriba":
                tablero.mover_jugador(board, tablero.find_player_position(board), (-1, 0))  # Mover hacia arriba
                print("Flecha arriba presionada")
            elif event.name == "flecha abajo":
                tablero.mover_jugador(board, tablero.find_player_position(board), (1, 0))  # Mover hacia abajo
                print("Flecha abajo presionada")

            elif event.name == "q":
                camino = tablero.buscar_mejor_camino(board)
                pitar = tablero.pintar_camino(board, camino,True)
                print("Algoritmo de búsqueda ejecutado")
            elif event.name == "e":
                camino = tablero.buscar_mejor_camino(board)
                pitar = tablero.pintar_camino(board, camino,False)
                print("Algoritmo de búsqueda ejecutado sin mostrar el camino")
            
            elif event.name == "esc":
                break



if __name__ == "__main__":
    main()
