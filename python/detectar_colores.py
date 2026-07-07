import cv2
import numpy as np

from movimientos import obtener_centroid

RANGOS = {
    'ROJO': [((0, 100, 100), (10, 255, 255)), ((160, 100, 100), (179, 255, 255))],
    'VERDE': [((40, 100, 100), (80, 255, 255))],
    'AZUL': [((100, 100, 100), (140, 255, 255))],
}
COLORES_BGR = {
    'ROJO': (0, 0, 255),
    'VERDE': (0, 255, 0),
    'AZUL': (255, 0, 0),
}


def obtener_mascara(hsv, limites):
    mascara = None
    for bajo, alto in limites:
        m = cv2.inRange(hsv, np.array(bajo), np.array(alto))
        mascara = m if mascara is None else cv2.bitwise_or(mascara, m)
    return mascara


def obtener_contorno_mas_grande(mascara, min_area=500):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None
    contorno = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(contorno) < min_area:
        return None
    return contorno


def encontrar_colores(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    resultados = []

    for nombre, limites in RANGOS.items():
        mascara = obtener_mascara(hsv, limites)
        contorno = obtener_contorno_mas_grande(mascara)
        if contorno is None:
            continue

        centro = obtener_centroid(contorno)
        if centro is None:
            continue

        radio = int(cv2.minEnclosingCircle(contorno)[1])
        resultados.append({
            'nombre': nombre,
            'centro': centro,
            'radio': radio,
            'contorno': contorno,
        })

    return resultados


def dibujar_resultados(frame, resultados):
    for dato in resultados:
        nombre = dato['nombre']
        cx, cy = dato['centro']
        radio = dato['radio']
        color = COLORES_BGR[nombre]

        cv2.circle(frame, (cx, cy), radio + 10, color, 2)
        cv2.putText(frame, nombre, (cx - 40, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f'X:{cx} Y:{cy}', (cx - 40, cy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return frame


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('No se pudo abrir la cámara. Prueba con index 1 o revisa la conexión.')
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print('No se pudo leer el frame de la cámara.')
            break

        resultados = encontrar_colores(frame)
        frame = dibujar_resultados(frame, resultados)

        cv2.imshow('Detección de colores', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
