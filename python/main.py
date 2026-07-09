import cv2
import numpy as np
import serial
import time
import sys

from detectar_colores import encontrar_colores, dibujar_resultados

# ===========================================================
# CONFIGURACIÓN DEL PUERTO SERIAL
# ===========================================================
if len(sys.argv) > 1:
    PUERTO = sys.argv[1]
else:
    PUERTO = 'COM3'  # Cambia según tu puerto

# Opcional: índice de cámara como segundo argumento
CAM_IDX = None
if len(sys.argv) > 2:
    try:
        CAM_IDX = int(sys.argv[2])
    except Exception:
        CAM_IDX = None

try:
    arduino = serial.Serial(PUERTO, 115200, timeout=0.1)
    time.sleep(2)  # Esperar a que el ESP32 inicie
    print(f"Conectado a {PUERTO}")
except Exception as e:
    print(f"Error: No se pudo conectar a {PUERTO}: {e}")
    print("Verifica el puerto y cierra el monitor serial de Arduino")
    sys.exit(1)

# ===========================================================
# CONFIGURACIÓN DE COLORES (RANGOS HSV)
# ===========================================================
# Rojo (dos rangos porque el rojo está en los extremos)
rojo_bajo1 = np.array([0, 100, 100])
rojo_alto1 = np.array([10, 255, 255])
rojo_bajo2 = np.array([160, 100, 100])
rojo_alto2 = np.array([180, 255, 255])

# Azul
azul_bajo = np.array([100, 100, 100])
azul_alto = np.array([140, 255, 255])

# ===========================================================
# FUNCIÓN PARA ENVIAR COMANDO AL ARDUINO
# ===========================================================
def enviar_comando(color):
    try:
        arduino.write((color + '\n').encode())
        print(f"Enviado: {color}")
    except Exception as e:
        print(f"Error enviando comando: {e}")

# ===========================================================
# INICIALIZAR CÁMARA
# ===========================================================
def find_camera_index(max_index=5):
    # Try multiple backends commonly available on Windows
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    for backend in backends:
        for i in range(0, max_index + 1):
            try:
                cap_test = cv2.VideoCapture(i + cv2.CAP_DSHOW if backend == cv2.CAP_DSHOW else i, backend)
            except Exception:
                # fallback to simple index open
                cap_test = cv2.VideoCapture(i)

            opened = cap_test.isOpened()
            print(f"Probing camera index {i} with backend {backend}: opened={opened}")
            if not opened:
                cap_test.release()
                continue
            # Try to grab a frame
            ret, _ = cap_test.read()
            cap_test.release()
            if ret:
                print(f"Found camera at index {i} using backend {backend}")
                return i
    return None


if CAM_IDX is not None:
    # For Windows prefer DirectShow when an explicit index is provided
    try:
        cap = cv2.VideoCapture(CAM_IDX, cv2.CAP_DSHOW)
    except Exception:
        cap = cv2.VideoCapture(CAM_IDX)
    used_idx = CAM_IDX
else:
    auto_idx = find_camera_index(5)
    if auto_idx is None:
        print("Error: No se pudo encontrar ninguna cámara disponible (probados índices 0-5).")
        print("Prueba ejecutar 'python -c ""import cv2; print(cv2.VideoCapture(i).isOpened())""' o cambia el índice de la cámara en los argumentos.")
        arduino.close()
        sys.exit(1)
    cap = cv2.VideoCapture(auto_idx)
    used_idx = auto_idx

if not cap.isOpened():
    print(f"Error: No se pudo abrir la cámara en el índice {used_idx}")
    arduino.close()
    sys.exit(1)

print(f"Cámara abierta en índice {used_idx}")

print("Sistema listo. Coloca una bolita de color ROJO o AZUL")
print("Presiona 'q' para salir")

color_anterior = ""
ultimo_envio = 0
RETARDO_ENTRE_ENVIOS = 5  # Segundos entre detecciones
waiting_for_arduino = False

# Procesamiento en baja resolución y salto de frames
PROCESS_SIZE = (320, 240)
FRAME_SKIP = 2
frame_idx = 0

# ===========================================================
# BUCLE PRINCIPAL
# ===========================================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer la cámara")
        break

    frame_idx += 1
    mostrar = cv2.resize(frame, (640, 480))

    color_detectado = ""
    cx, cy = 0, 0

    # Procesar solo 1 de cada FRAME_SKIP+1 en baja resolución
    if frame_idx % (FRAME_SKIP + 1) == 0:
        pequeño = cv2.resize(frame, PROCESS_SIZE)
        resultados = encontrar_colores(pequeño, min_area=1500, min_circularity=0.55)

        # Si hay resultados, escoger el primero por prioridad (ROJO antes que AZUL)
        if resultados:
            # Ordenar para prioridad conocida
            nombres = [r['nombre'] for r in resultados]
            elegido = None
            if 'ROJO' in nombres:
                elegido = next(r for r in resultados if r['nombre'] == 'ROJO')
            else:
                elegido = resultados[0]

            # Mapear centro a tamaño de `mostrar`
            sx = mostrar.shape[1] / pequeño.shape[1]
            sy = mostrar.shape[0] / pequeño.shape[0]
            cx_small, cy_small = elegido['centro']
            cx = int(cx_small * sx)
            cy = int(cy_small * sy)
            color_detectado = elegido['nombre']
            # Dibujar en la imagen mostrada
            mostrar = dibujar_resultados(mostrar, [{
                'nombre': elegido['nombre'],
                'centro': (cx, cy),
                'radio': int(elegido['radio'] * ((sx + sy) / 2)),
                'contorno': elegido['contorno']
            }])

    # Mostrar información en pantalla
    if color_detectado != "":
        cv2.putText(mostrar, f"Color: {color_detectado}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(mostrar, f"X:{cx} Y:{cy}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        # Enviar comando al Arduino (solo si cambió el color y pasó el tiempo y Arduino está listo)
        tiempo_actual = time.time()
        if not waiting_for_arduino and color_detectado != color_anterior and (tiempo_actual - ultimo_envio > RETARDO_ENTRE_ENVIOS):
            enviar_comando(color_detectado)
            waiting_for_arduino = True
            color_anterior = color_detectado
            ultimo_envio = tiempo_actual
    else:
        cv2.putText(mostrar, "Esperando objeto...", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

    # Leer respuesta del Arduino sin bloquear
    try:
        if arduino.in_waiting > 0:
            linea = arduino.readline().decode(errors='ignore').strip()
            if linea:
                print(f"Arduino: {linea}")
                if linea == 'LISTO':
                    waiting_for_arduino = False
    except Exception:
        pass

    # Mostrar video
    cv2.imshow('Clasificador por Color - Smart Arm', mostrar)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===========================================================
# LIMPIEZA FINAL
# ===========================================================
cap.release()
cv2.destroyAllWindows()
arduino.close()
print("Sistema cerrado correctamente")