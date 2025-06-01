import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def contar_dedos(hand_landmarks):
    dedos_extendidos = 0
    dedos = [
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP),
    ]
    for tip, base in dedos:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            dedos_extendidos += 1

    pulgar_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    pulgar_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    muñeca = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    if pulgar_tip.x < pulgar_mcp.x:
        if pulgar_tip.x < muñeca.x:
            dedos_extendidos += 1
    else:
        if pulgar_tip.x > muñeca.x:
            dedos_extendidos += 1

    return dedos_extendidos

def gesture_hands_recognition():
    cap = cv2.VideoCapture(0)
    intentos = 0
    max_intentos = 3

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:

        while intentos < max_intentos:
            print(f"🖐️ Intento {intentos + 1}/3: Esperando mano...")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resultados = hands.process(rgb)

                if resultados.multi_hand_landmarks:
                    print("✅ Mano detectada. Iniciando cuenta regresiva...")
                    start = time.time()
                    count = 2

                    while count > 0:
                        ret, frame = cap.read()
                        frame = cv2.flip(frame, 1)
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        resultados_temp = hands.process(rgb)

                        if resultados_temp.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(frame, resultados_temp.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

                        elapsed = time.time() - start
                        if elapsed >= 1:
                            count -= 1
                            start = time.time()

                        cv2.putText(frame, f"{count+1}", (250, 200), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 6)
                        cv2.imshow("Contando...", frame)
                        if cv2.waitKey(1) & 0xFF == 27:
                            cap.release()
                            cv2.destroyAllWindows()
                            return False

                    # Captura final
                    ret, frame = cap.read()
                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    resultados = hands.process(rgb)

                    if resultados.multi_hand_landmarks:
                        hand_landmarks = resultados.multi_hand_landmarks[0]
                        dedos = contar_dedos(hand_landmarks)
                        print(f"✋ Número de dedos levantados: {dedos}")
                        cap.release()
                        cv2.destroyAllWindows()
                        return dedos
                    else:
                        print("❌ No se detectó la mano en la captura final.")
                        break

                cv2.imshow("Esperando mano...", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return False

            intentos += 1

        print("⛔ No se pudo detectar correctamente una mano después de 3 intentos.")
        cap.release()
        cv2.destroyAllWindows()
        return False

if __name__ == "__main__":
    resultado = gesture_hands_recognition()
    if resultado is False:
        print("😔 No se pudo reconocer un gesto válido.")
    else:
        print(f"🎉 Gesto reconocido: {resultado} dedos levantados.")
