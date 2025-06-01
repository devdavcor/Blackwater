import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Función para contar dedos extendidos
def contar_dedos(hand_landmarks):
    dedos_extendidos = 0

    # Dedos índice, medio, anular, meñique
    dedos = [
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP),
    ]

    for tip, base in dedos:
        punta = hand_landmarks.landmark[tip]
        base_dedo = hand_landmarks.landmark[base]
        if punta.y < base_dedo.y:  # punta "más arriba" que base
            dedos_extendidos += 1

    # Pulgar - comparación horizontal (x)
    pulgar_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    pulgar_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    muñeca = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # Determinar mano derecha o izquierda para pulgar
    if pulgar_tip.x < pulgar_mcp.x:  # mano derecha (espejo)
        if pulgar_tip.x < muñeca.x:
            dedos_extendidos += 1
    else:  # mano izquierda
        if pulgar_tip.x > muñeca.x:
            dedos_extendidos += 1

    return dedos_extendidos

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
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    dedos = contar_dedos(hand_landmarks)

                    x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * frame.shape[1])
                    y = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * frame.shape[0]) - 20
                    cv2.putText(frame, f"Dedos: {dedos}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (201, 78, 217), 2)

            cv2.imshow("Detección de manos - Contar dedos", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
