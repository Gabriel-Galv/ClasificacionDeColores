import cv2


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara. Prueba con index 1 o revisa la conexión.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error leyendo el frame de la cámara.")
            break

        cv2.imshow('Camara - Smart Arm', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
