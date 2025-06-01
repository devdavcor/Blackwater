import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def contar_dedos(hand_landmarks, hand_label):
    dedos = 0
    # Dedos (excepto pulgar)
    dedos_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]
    dedos_bases = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP,
    ]

    # Conteo dedos "verticales"
    for tip, base in zip(dedos_tips, dedos_bases):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            dedos += 1

    # Pulgar, que abre lateralmente
    pulgar_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    pulgar_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    if hand_label == "Right":
        if pulgar_tip.x < pulgar_mcp.x:
            dedos += 1
    else:  # Left
        if pulgar_tip.x > pulgar_mcp.x:
            dedos += 1

    return dedos

def main():
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        conteo = None
        tiempo_inicio = None
        tiempo_conteo = 3  # segundos para conteo regresivo

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = hands.process(rgb)

            if resultados.multi_hand_landmarks:
                # Si detecta mano, inicia conteo si no está ya iniciado
                if conteo is None:
                    conteo = tiempo_conteo
                    tiempo_inicio = time.time()

                for hand_landmarks, handedness in zip(resultados.multi_hand_landmarks, resultados.multi_handedness):
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Mostrar el conteo regresivo
                    tiempo_pasado = time.time() - tiempo_inicio
                    tiempo_restante = max(0, int(conteo - tiempo_pasado))
                    cv2.putText(frame, f"Captura en: {tiempo_restante}", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                    # Si el tiempo terminó, tomar foto y contar dedos
                    if tiempo_restante == 0:
                        dedos = contar_dedos(hand_landmarks, handedness.classification[0].label)
                        print(f"Dedos extendidos: {dedos}")
                        # Guardar la imagen (opcional)
                        cv2.imwrite("mano_capturada.png", frame)
                        # Resetear para nuevo conteo si sigue la mano
                        conteo = None
                        tiempo_inicio = None

            else:
                # No hay mano, resetear conteo
                conteo = None
                tiempo_inicio = None

            cv2.imshow("Detección de mano con conteo", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
