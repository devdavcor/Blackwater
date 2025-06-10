import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir a RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Procesar la imagen
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Obtener todas las coordenadas x, y normalizadas
            h, w, _ = frame.shape
            x_list = [int(landmark.x * w) for landmark in hand_landmarks.landmark]
            y_list = [int(landmark.y * h) for landmark in hand_landmarks.landmark]

            # Calcular el rectángulo que encierra toda la mano
            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)

            # Dibujar un rectángulo verde
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    cv2.imshow("Hands detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Esc para salir
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
hands.close()
