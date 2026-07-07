# 🤖 Smart Color Sorting Robotic Arm

Sistema de visión por computadora y robótica que detecta objetos por color mediante una cámara web y los clasifica automáticamente utilizando un brazo robótico controlado por Arduino.

## 🚀 Tecnologías

### Software
- Python 3
- Arduino IDE
- Visual Studio Code

### Librerías
- OpenCV (`opencv-python`)
- NumPy
- PySerial

> **Opcional**
>
> - Ultralytics (YOLO)

## 🛠 Hardware

- Arduino
- Brazo robótico
- Cámara Logitech HD 720p
- Laptop
- Base blanca
- Bolas de unicel pintadas (rojo, verde y azul)
- Cajas de clasificación
- Iluminación

## 📁 Estructura del proyecto

```text
Proyecto
│
├── arduino/
│   └── brazo_robotico.ino
│
├── python/
│   ├── camara.py
│   ├── detectar_colores.py
│   ├── serial_arduino.py
│   ├── movimientos.py
│   └── main.py
│
├── imagenes/
│
└── README.md
```

## ⚙️ Funcionamiento

1. La cámara captura la imagen.
2. OpenCV detecta el objeto y su color.
3. Se calculan las coordenadas del objeto.
4. Python envía el color al Arduino mediante comunicación serial.
5. Arduino ejecuta la rutina correspondiente.
6. El brazo toma el objeto y lo deposita en la caja asignada.

## 📌 Colores soportados

- 🔴 Rojo
- 🟢 Verde
- 🔵 Azul

## 🔧 Instalación

Instala las dependencias del proyecto:

```bash
pip install opencv-python numpy pyserial
```

Ejecuta el sistema:

```bash
python python/main.py
```

## 👥 Equipo

- **Arduino:** Control del brazo robótico y servomotores.
- **Visión Artificial:** Detección de colores y coordenadas con OpenCV.
- **Integración:** Comunicación serial, pruebas e integración del sistema.

---
**Proyecto académico de Robótica y Visión por Computadora.**