import cv2
import numpy as np
import serial
import time
import sys

# ===========================================================
# CONFIGURACIÓN DEL PUERTO SERIAL
# ===========================================================
if len(sys.argv) > 1:
    PUERTO = sys.argv[1]
else:
    PUERTO = 'COM3'  # Cambia según tu puerto

try:
    arduino = serial.Serial(PUERTO, 115200, timeout=1)
    time.sleep(2)  # Esperar a que el ESP32 inicie
    print(f"Conectado a {PUERTO}")
except:
    print(f"Error: No se pudo conectar a {PUERTO}")
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
    arduino.write((color + '\n').encode())
    print(f"Enviado: {color}")
    
    # Esperar hasta que Arduino diga "LISTO"
    while True:
        if arduino.in_waiting > 0:
            linea = arduino.readline().decode().strip()
            if linea == "LISTO":
                print("Brazo listo para siguiente objeto")
                break
            elif linea:
                print(f"Arduino: {linea}")

# ===========================================================
# INICIALIZAR CÁMARA
# ===========================================================
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara")
    arduino.close()
    sys.exit(1)

print("Sistema listo. Coloca una bolita de color ROJO o AZUL")
print("Presiona 'q' para salir")

color_anterior = ""
ultimo_envio = 0
RETARDO_ENTRE_ENVIOS = 5  # Segundos entre detecciones

# ===========================================================
# BUCLE PRINCIPAL
# ===========================================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer la cámara")
        break
    
    # Redimensionar para hacer más rápido
    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Crear máscaras para cada color
    mask_rojo1 = cv2.inRange(hsv, rojo_bajo1, rojo_alto1)
    mask_rojo2 = cv2.inRange(hsv, rojo_bajo2, rojo_alto2)
    mask_rojo = cv2.bitwise_or(mask_rojo1, mask_rojo2)
    mask_azul = cv2.inRange(hsv, azul_bajo, azul_alto)
    
    # Detectar objetos ROJOS
    contornos_rojo, _ = cv2.findContours(mask_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_azul, _ = cv2.findContours(mask_azul, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    color_detectado = ""
    cx, cy = 0, 0
    
    # Buscar el contorno más grande (ROJO)
    if contornos_rojo:
        contorno = max(contornos_rojo, key=cv2.contourArea)
        area = cv2.contourArea(contorno)
        if area > 500:  # Filtrar ruido
            momento = cv2.moments(contorno)
            if momento["m00"] != 0:
                cx = int(momento["m10"] / momento["m00"])
                cy = int(momento["m01"] / momento["m00"])
                color_detectado = "ROJO"
                cv2.drawContours(frame, [contorno], -1, (0, 0, 255), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
    
    # Buscar el contorno más grande (AZUL)
    if contornos_azul and color_detectado == "":
        contorno = max(contornos_azul, key=cv2.contourArea)
        area = cv2.contourArea(contorno)
        if area > 500:
            momento = cv2.moments(contorno)
            if momento["m00"] != 0:
                cx = int(momento["m10"] / momento["m00"])
                cy = int(momento["m01"] / momento["m00"])
                color_detectado = "AZUL"
                cv2.drawContours(frame, [contorno], -1, (255, 0, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
    
    # Mostrar información en pantalla
    if color_detectado != "":
        cv2.putText(frame, f"Color: {color_detectado}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"X:{cx} Y:{cy}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Enviar comando al Arduino (solo si cambió el color y pasó el tiempo)
        tiempo_actual = time.time()
        if color_detectado != color_anterior and (tiempo_actual - ultimo_envio > RETARDO_ENTRE_ENVIOS):
            enviar_comando(color_detectado)
            color_anterior = color_detectado
            ultimo_envio = tiempo_actual
    else:
        cv2.putText(frame, "Esperando objeto...", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    
    # Mostrar video
    cv2.imshow('Clasificador por Color - Smart Arm', frame)
    
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