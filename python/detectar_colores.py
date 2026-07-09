import cv2
import numpy as np

from movimientos import obtener_centroid

RANGOS = {
    'ROJO': [((0, 120, 120), (10, 255, 255)), ((160, 120, 120), (179, 255, 255))],
    'VERDE': [((40, 100, 100), (80, 255, 255))],
    'AZUL': [((95, 80, 80), (130, 255, 255))],
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
    # Morfología para limpiar ruido
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel, iterations=1)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel, iterations=1)
    return mascara


def obtener_contorno_mas_grande(mascara, min_area=1500, min_circularity=0.6):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None

    # Filtrar por area y circularidad, luego devolver el más grande válido
    candidatos = []
    for c in contornos:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        per = cv2.arcLength(c, True)
        if per == 0:
            continue
        circularity = 4 * np.pi * (area / (per * per))
        if circularity < min_circularity:
            continue
        candidatos.append((c, area))

    if not candidatos:
        return None

    contorno = max(candidatos, key=lambda x: x[1])[0]
    return contorno


def encontrar_colores(frame, min_area=1500, min_circularity=0.6):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    resultados = []

    for nombre, limites in RANGOS.items():
        mascara = obtener_mascara(hsv, limites)
        contorno = obtener_contorno_mas_grande(mascara, min_area=min_area, min_circularity=min_circularity)
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
        print('No se pudo abrir la c�mara. Prueba con index 1 o revisa la conexi�n.')
        return

    # Procesamiento en baja resolución para detección y salto de frames
    PROCESS_SIZE = (320, 240)
    FRAME_SKIP = 2  # procesar 1 de cada FRAME_SKIP+1
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print('No se pudo leer el frame de la c�mara.')
            break

        frame_idx += 1
        mostrar = frame.copy()

        if frame_idx % (FRAME_SKIP + 1) == 0:
            pequeño = cv2.resize(frame, PROCESS_SIZE)
            resultados = encontrar_colores(pequeño)

            # Mapear resultados a tamaño original
            sx = frame.shape[1] / PROCESS_SIZE[0]
            sy = frame.shape[0] / PROCESS_SIZE[1]
            for r in resultados:
                cx, cy = r['centro']
                r['centro'] = (int(cx * sx), int(cy * sy))
                r['radio'] = int(r['radio'] * (sx + sy) / 2)

            mostrar = dibujar_resultados(mostrar, resultados)

        cv2.imshow('Detecci�n de colores', mostrar)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
