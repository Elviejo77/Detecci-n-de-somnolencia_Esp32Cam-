#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// Modelo de cámara
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Pines extra
#define PIN_LED_BLANCO 4     // LED soldado a la cámara
#define PIN_BUZZER     14    // Buzzer pasivo (Low Level Trigger)
#define PIN_IR         12    // Módulo infrarrojo (opcional)
#define PIN_BOTON      13    // Botón físico

// WiFi
const char *ssid = "POCO X3 Pro";
const char *password = "88888222";

// Servidor web
WebServer server(80);

void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // 🔧 Configuración de la cámara
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;

  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;     // 📏 640x480
  config.jpeg_quality = 15;              // 🌟 calidad media
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.fb_count = psramFound() ? 2 : 1;
  config.grab_mode = CAMERA_GRAB_LATEST;

  // Inicializa la cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Error inicializando la cámara: 0x%x\n", err);
    return;
  }

  // Ajustes del sensor
  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }

  s->set_framesize(s, FRAMESIZE_VGA);   // Fuerza resolución VGA
  s->set_quality(s, 15);                // Fuerza calidad 15

  // 🧰 Configuración de pines
  pinMode(PIN_LED_BLANCO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_IR, OUTPUT);
  pinMode(PIN_BOTON, INPUT_PULLUP);

  digitalWrite(PIN_LED_BLANCO, LOW);
  digitalWrite(PIN_BUZZER, LOW);
  digitalWrite(PIN_IR, HIGH);  // Mantener sensor IR activo (si se conecta)

  // 🌐 Conexión WiFi
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi conectado");

  // Inicia el servidor MJPEG
  startCameraServer();

  // Endpoints HTTP para controlar alerta desde Python
  server.on("/alerta/on", []() {
    digitalWrite(PIN_LED_BLANCO, HIGH);
    digitalWrite(PIN_BUZZER, HIGH);
    server.send(200, "text/plain", "🚨 Alerta activada");
  });

  server.on("/alerta/off", []() {
    digitalWrite(PIN_LED_BLANCO, LOW);
    digitalWrite(PIN_BUZZER, LOW);
    server.send(200, "text/plain", "✅ Alerta desactivada");
  });

  server.begin();
  Serial.println("✅ Servidor HTTP iniciado");
  Serial.print("🌐 Cámara lista: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/ y /stream");
}

void loop() {
  server.handleClient();
  delay(10);
}
