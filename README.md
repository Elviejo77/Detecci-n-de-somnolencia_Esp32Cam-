# 🛡️ Detector de Somnolencia con ESP32-CAM, Python y MediaPipe

Este proyecto implementa un sistema de **detección de somnolencia en tiempo real** utilizando visión artificial con **MediaPipe y Python**, combinado con un microcontrolador **ESP32-CAM** que activa señales de alerta mediante un **LED** y un **buzzer**.

---

## 🎯 Objetivo

Diseñar un sistema de bajo costo capaz de detectar signos de somnolencia (como parpadeos frecuentes o prolongados) en personas, especialmente conductores o trabajadores, y generar alertas inmediatas para prevenir accidentes.

---

## ⚙️ Tecnologías y Herramientas

- 📷 **ESP32-CAM (AI Thinker)** para captura y streaming de video (MJPEG)
- 🧠 **MediaPipe Face Mesh** para detección facial y análisis ocular
- 🐍 **Python 3** con OpenCV para procesar el video
- 🌐 **Flask / WebServer** para controlar remotamente el ESP32
- 🛠️ **Arduino IDE** para programar el ESP32-CAM
- 💻 Visual Studio Code para correr el código Python

---

## 🔌 Componentes Utilizados

| Componente               | Función                                      |
|--------------------------|----------------------------------------------|
| ESP32-CAM (AI Thinker)   | Captura video y activa alertas               |
| Buzzer pasivo (Low Trigger) | Alarma sonora en caso de somnolencia    |
| LED blanco (GPIO 4)      | Alarma visual                               |
| Botón físico (GPIO 13)   | Reinicio manual del conteo de parpadeos     |
| Fuente USB 5V            | Alimentación                                |

---

## 🧠 Lógica de Funcionamiento

1. El ESP32-CAM transmite video vía IP (`http://<IP>:81/stream`).
2. Python con MediaPipe procesa el stream, detecta el rostro y calcula el EAR (Eye Aspect Ratio).
3. Si se detecta somnolencia (múltiples parpadeos o cierre ocular prolongado):
   - Se activa el buzzer y el LED remotamente vía comandos HTTP.
4. Al presionar la barra espaciadora o el botón físico, se reinicia el conteo y se apagan las alertas.

---

## 🛠️ Instrucciones de Uso

### 1. Cargar el código al ESP32-CAM

- Usa el Arduino IDE y selecciona la tarjeta **AI Thinker ESP32-CAM**
- Asegúrate de usar los siguientes ajustes:
  - Flash Mode: QIO
  - Partition Scheme: Huge APP (3MB)
- Conecta el ESP32-CAM al puerto serial (ej. COM6) y sube el código.

### 2. Conexión del Hardware

| Módulo     | GPIO  | Descripción               |
|------------|-------|---------------------------|
| LED        | 4     | LED blanco                |
| Buzzer     | 14    | Módulo buzzer (Low Trigger) |
| Botón      | 13    | Pulsador físico para reset |

### 3. Corre el Script Python

- Asegúrate de tener Python 3.7+
- Instala dependencias:

```bash
pip install opencv-python mediapipe requests numpy

Corre el archivo detector_somnolencia.py en Visual Studio Code (Run Current File in Interactive Window)

El sistema mostrará el conteo de parpadeos y activará la alerta al detectar somnolencia
