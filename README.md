# ?? Smart Color Sorting Robotic Arm

Sistema de visión por computadora y robótica que detecta objetos por color con una cámara y los clasifica usando un brazo robótico controlado por Arduino.

## ?? Tecnologías

- Python 3
- Arduino IDE
- Visual Studio Code

## ?? Estructura del proyecto

```text
ClasificacionDeColores
¦
+-- arduino/
¦   +-- brazo_robotico.ino
¦
+-- python/
¦   +-- camara.py
¦   +-- detectar_colores.py
¦   +-- main.py
¦   +-- movimientos.py
¦   +-- serial_arduino.py
¦
+-- imagenes/
+-- README.md
```

## ?? Instalación

1. Abre una terminal en el proyecto.
2. Instala las dependencias:

```bash
pip install opencv-python numpy pyserial
```

## ?? Cómo probar cada fase

### Fase 1: Ver la cámara

```bash
python python/camara.py
```

Presiona `q` para cerrar la ventana.

### Fase 2 y 3: Detectar colores y ver coordenadas

```bash
python python/detectar_colores.py
```

Verás círculos, el nombre del color y las coordenadas `X,Y` en la pantalla.

### Fase 4: Enviar comando al ESP32 por serial

1. Conecta el ESP32 a tu computadora y abre el puerto correcto.
2. Ejecuta:

```bash
python python/serial_arduino.py COM3
```

Reemplaza `COM3` por el puerto de tu ESP32.

### Fase de integración (opcional)

```bash
python python/main.py COM3
```

Esto captura la cámara, detecta el color y envía el primer color detectado al Arduino.

## ?? Nota de Arduino

Abre `arduino/brazo_robotico.ino` en el Arduino IDE y sube el sketch a tu ESP32. El código escucha comandos seriales `ROJO`, `VERDE` y `AZUL`.
