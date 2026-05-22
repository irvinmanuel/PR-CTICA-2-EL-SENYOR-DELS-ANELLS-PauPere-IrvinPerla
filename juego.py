import tablero
import keyboard


def main():
    print("Bienvenido al juego del Señor de los Anillos")
    print("Usa las flechas para mover al jugador (🧘) y recoge las monedas (🥉, 🥈, 🥇)")
    print("#########REGLAS DEL JUEGO#########")
    print("1. Mueve al jugador con las flechas del teclado.")
    print("2. Recoge las monedas en el orden correcto para desbloquear nuevas áreas.")
    print("3. Si presionas 'e', se mostrará el mejor camino (pulsa otra vez para ocultarlo).")
    print("4. Si presionas 'q', se activará el modo de asistencia (pistas automáticas).")
    print("5. Presiona 'esc' para salir del juego.")
    print("para iniciar presiona la letra 'z'")

    keyboard.wait("z")
    board = tablero.crear_tablero()
    nueva_posicion = tablero.find_player_position(board)
    
    pista_activa = False
    pista_coordenada = None  
    camino_activo = False

    def actualizar_pista():
        nonlocal pista_coordenada
        camino = tablero.buscar_mejor_camino(board)
        tablero.pintar_camino(board, camino, solo_siguiente=True)
        pista_coordenada = camino[0] if camino else None

    def limpiar_pista():
        nonlocal pista_coordenada
        tablero.pintar_camino(board, [], solo_siguiente=True)
        pista_coordenada = None

    def mostrar_camino_completo():
        camino = tablero.buscar_mejor_camino(board)
        tablero.pintar_camino(board, camino, solo_siguiente=False, limpiar=False)

    def limpiar_camino_completo():
        tablero.pintar_camino(board, [], solo_siguiente=False, limpiar=True)

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            movido = False
            
            if event.name == "flecha izquierda":
                nueva_posicion = tablero.mover_jugador(board, nueva_posicion, (0, -1))
                movido = True
                print("Flecha izquierda presionada")
            elif event.name == "flecha derecha":
                nueva_posicion = tablero.mover_jugador(board, nueva_posicion, (0, 1))
                movido = True
                print("Flecha derecha presionada")
            elif event.name == "flecha arriba":
                nueva_posicion = tablero.mover_jugador(board, nueva_posicion, (-1, 0))
                movido = True
                print("Flecha arriba presionada")
            elif event.name == "flecha abajo":
                nueva_posicion = tablero.mover_jugador(board, nueva_posicion, (1, 0))
                movido = True
                print("Flecha abajo presionada")

            if movido:
                if pista_activa:
                    actualizar_pista()
                else:
                    pista_coordenada = None

            elif event.name == "q":
                if camino_activo:
                    limpiar_camino_completo()
                    camino_activo = False
                if pista_activa:
                    # Desactivar el modo asistencia y limpiar cuadro azul
                    limpiar_pista()
                    pista_activa = False
                    print("Asistencia desactivada.")
                else:
                    # Activar el modo asistencia
                    actualizar_pista()
                    pista_activa = True
                    print("Asistencia activada: Las pistas aparecerán automáticamente al avanzar.")

            elif event.name == "e":
                if pista_activa:
                    limpiar_pista()
                    pista_activa = False
                if camino_activo:
                    limpiar_camino_completo()
                    camino_activo = False
                    print("Camino completo desactivado.")
                else:
                    mostrar_camino_completo()
                    camino_activo = True
                    print("Mostrando camino completo.")
            
            if nueva_posicion == (1000, 1000) or nueva_posicion == (-1000, -1000) or event.name == "esc":
                break

if __name__ == "__main__":
    main()