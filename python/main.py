import sys
import time

import cv2

from detectar_colores import dibujar_resultados, encontrar_colores
from serial_arduino import abrir_puerto, enviar_comando


def main():
    puerto = None
    if len(sys.argv) >= 2:
        puerto = abrir_puerto(sys.argv[1])

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('No se pudo abrir la cámara. Prueba con index 1 o revisa la conexión.')
        return

    ultimo_color = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print('No se pudo leer el frame de la cámara.')
            break

        resultados = encontrar_colores(frame)
        frame = dibujar_resultados(frame, resultados)

        if puerto and resultados:
            color = resultados[0]['nombre']
            if color != ultimo_color:
                enviar_comando(puerto, color)
                ultimo_color = color
        elif not resultados:
            ultimo_color = None

        cv2.imshow('Brazo Color - Integración', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if puerto:
        puerto.close()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
