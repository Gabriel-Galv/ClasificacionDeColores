import sys
import time

try:
    import serial
except ImportError:
    print('Instala pyserial con: pip install pyserial')
    sys.exit(1)


def abrir_puerto(puerto_com, velocidad=115200, timeout=1):
    puerto = serial.Serial(puerto_com, velocidad, timeout=timeout)
    time.sleep(2)
    return puerto


def enviar_comando(puerto, color):
    comando = color.strip().upper()
    puerto.write((comando + '\n').encode())
    respuesta = puerto.readline().decode(errors='ignore').strip()
    print(f'Arduino dice: {respuesta}')
    return respuesta


def main():
    if len(sys.argv) < 2:
        print('Uso: python serial_arduino.py COM3')
        return

    puerto_com = sys.argv[1]
    puerto = abrir_puerto(puerto_com)
    enviar_comando(puerto, 'ROJO')
    puerto.close()


if __name__ == '__main__':
    main()
