import cv2
import json
import numpy as np

OUT_FILE = 'hsv_calibration.json'

current_hsv = None


def mouse_callback(event, x, y, flags, param):
    global current_hsv
    if event == cv2.EVENT_LBUTTONDOWN:
        frame = param['frame']
        if frame is None:
            return
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[y, x]
        current_hsv = (int(h), int(s), int(v))
        print(f"HSV clicado: H={h} S={s} V={v}")


def build_range(hsv, dh=5, min_s=80, min_v=80):
    h, s, v = hsv
    low_h = max(0, h - dh)
    high_h = min(179, h + dh)
    low = [low_h, min_s, min_v]
    high = [high_h, 255, 255]
    return low, high


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('No se pudo abrir la cámara')
        return

    cv2.namedWindow('Selector HSV')
    param = {'frame': None}
    cv2.setMouseCallback('Selector HSV', mouse_callback, param)

    print('Clica sobre la bolita para leer HSV. Presiona s para guardar último HSV clicado. q para salir.')

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        param['frame'] = frame
        display = frame.copy()

        if current_hsv is not None:
            h, s, v = current_hsv
            low, high = build_range(current_hsv)
            cv2.putText(display, f'H={h} S={s} V={v}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(display, f'Rango H:{low[0]}-{high[0]} S>={low[1]} V>={low[2]}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow('Selector HSV', display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s') and current_hsv is not None:
            low, high = build_range(current_hsv)
            data = {'low': low, 'high': high}
            with open(OUT_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print(f'Guardado rango en {OUT_FILE}: {data}')

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
