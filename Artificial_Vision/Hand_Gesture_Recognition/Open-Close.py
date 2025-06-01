import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Función para calcular distancia euclidiana entre dos puntos
def distancia(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Función para determinar si la mano está abierta o cerrada
def mano_abierta_o_cerrada(hand_landmarks):
    # Vamos a comparar la distancia entre la punta del dedo medio y la muñeca
    # con la distancia entre la base del dedo medio y la muñeca
    # Esto es un método simple para detectar si la mano está abierta o cerrada

    punta_dedo_medio = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    base_dedo_medio = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    muñeca = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    dist_punta_muñeca = distancia(punta_dedo_medio, muñeca)
    dist_base_muñeca = distancia(base_dedo_medio, muñeca)

    # Si la punta está mucho más lejos que la base, asumimos mano abierta
    if dist_punta_muñeca > dist_base_muñeca * 1.3:
        return "Abierta"
    else:
        return "Cerrada"

def main():
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            resultados = hands.process(rgb)

            if resultados.multi_hand_landmarks:
                for hand_landmarks in resultados.multi_hand_landmarks:
                    # Dibujar la malla
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    estado_mano = mano_abierta_o_cerrada(hand_landmarks)

                    # Mostrar el estado en pantalla
                    x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * frame.shape[1])
                    y = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * frame.shape[0]) - 20
                    cv2.putText(frame, f"Mano {estado_mano}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow("Detección de manos", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
