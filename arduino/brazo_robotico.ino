void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("ESP32 listo para recibir comandos");
  // Aquí inicializa tus servos y variables si ya los tienes configurados.
}

void loop() {
  // Si hay datos disponibles en el puerto serie, los leemos.
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    if (comando == "ROJO") {
      Serial.println("OK: Recibido ROJO");
      // Aquí puedes llamar a la rutina para mover el brazo hacia la caja roja.
    } else if (comando == "VERDE") {
      Serial.println("OK: Recibido VERDE");
      // Aquí puedes llamar a la rutina para mover el brazo hacia la caja verde.
    } else if (comando == "AZUL") {
      Serial.println("OK: Recibido AZUL");
      // Aquí puedes llamar a la rutina para mover el brazo hacia la caja azul.
    } else {
      Serial.print("COMANDO DESCONOCIDO: ");
      Serial.println(comando);
    }
  }

  // Aquí puedes mantener el control manual del brazo con el código que ya tienes.
  // Por ejemplo, leer botones o teclado y mover servos.
}
