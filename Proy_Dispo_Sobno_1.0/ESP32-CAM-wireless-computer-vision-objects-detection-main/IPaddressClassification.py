import cv2
import mediapipe as mp
import urllib.request
import numpy as np
import time
import requests  # Para activar/desactivar alerta en el ESP32

# 📷 URL del stream MJPEG de tu ESP32-CAM
stream_url = 'http://192.168.19.139:81/stream'

# 🌐 URLs para controlar el LED y buzzer del ESP32
URL_ALERTA_ON = 'http://192.168.19.139/alerta/on'
URL_ALERTA_OFF = 'http://192.168.19.139/alerta/off'

# 🧠 Inicializar MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# 📏 Índices de los ojos en Face Mesh
OJOS = {
    "izquierdo": [33, 160, 158, 133, 153, 144],
    "derecho": [362, 385, 387, 263, 373, 380]
}

def distancia_relativa(ojos, landmarks, w, h):
    def punto(idx):
        x = int(landmarks[idx].x * w)
        y = int(landmarks[idx].y * h)
        return x, y

    vertical_1 = np.linalg.norm(np.array(punto(ojos[1])) - np.array(punto(ojos[5])))
    vertical_2 = np.linalg.norm(np.array(punto(ojos[2])) - np.array(punto(ojos[4])))
    horizontal = np.linalg.norm(np.array(punto(ojos[0])) - np.array(punto(ojos[3])))
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear

# 🎛 Umbral y contador de parpadeos
UMBRAL_EAR = 0.25
UMBRAL_PARPADEOS = 7
parpadeos = 0
ojos_cerrados_anterior = False
tiempo_cierre = None
TIEMPO_CIERRE_UMBRAL = 0.6
alerta_activada = False

# 🖼 Inicializar captura de stream MJPEG desde ESP32-CAM
stream = urllib.request.urlopen(stream_url)
bytes_data = b''

cv2.namedWindow("MediaPipe - Detección de Somnolencia", cv2.WINDOW_AUTOSIZE)

while True:
    try:
        bytes_data += stream.read(1024)
        a = bytes_data.find(b'\xff\xd8')  # JPEG start
        b = bytes_data.find(b'\xff\xd9')  # JPEG end
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            img = cv2.flip(img, 1)
            h, w, _ = img.shape
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            result = face_mesh.process(rgb)

            ojos_detectados = False
            if result.multi_face_landmarks:
                for face_landmarks in result.multi_face_landmarks:
                    ear_izq = distancia_relativa(OJOS["izquierdo"], face_landmarks.landmark, w, h)
                    ear_der = distancia_relativa(OJOS["derecho"], face_landmarks.landmark, w, h)
                    ear_avg = (ear_izq + ear_der) / 2.0

                    if ear_avg < UMBRAL_EAR:
                        if not ojos_cerrados_anterior:
                            tiempo_cierre = time.time()
                        ojos_cerrados_anterior = True
                    else:
                        if ojos_cerrados_anterior and tiempo_cierre:
                            duracion = time.time() - tiempo_cierre
                            if duracion > TIEMPO_CIERRE_UMBRAL:
                                parpadeos += 1
                                print(f"Parpadeo #{parpadeos}")
                            tiempo_cierre = None
                        ojos_cerrados_anterior = False

                    ojos_detectados = True

            # 📊 Mostrar resultados
            cv2.putText(img, f"Parpadeos: {parpadeos}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            if parpadeos >= UMBRAL_PARPADEOS:
                cv2.putText(img, "ALERTA: SOMNOLENCIA DETECTADA", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

                if not alerta_activada:
                    try:
                        requests.get(URL_ALERTA_ON)
                        print("🚨 Alerta activada en ESP32")
                        alerta_activada = True
                    except:
                        print("⚠️ Error activando alerta en ESP32")

            cv2.imshow("MediaPipe - Detección de Somnolencia", img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # ESPACIO para reiniciar
            parpadeos = 0
            alerta_activada = False
            print("🔄 Contador reiniciado.")
            try:
                requests.get(URL_ALERTA_OFF)
                print("💤 LED y Buzzer apagados desde ESP32")
            except:
                print("⚠️ Error apagando alerta en ESP32")

    except Exception as e:
        print("⚠️ Error al leer stream:", e)
        continue

cv2.destroyAllWindows()
