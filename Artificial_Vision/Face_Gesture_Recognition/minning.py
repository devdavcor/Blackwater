import cv2
import mediapipe as mp

# Inicializa MediaPipe Face Mesh con la malla de 478 puntos
mp_face_mesh = mp.solutions.face_mesh

# Aquí pones los índices de los puntos que quieres dibujar
points_to_draw = [4, 468, 473, 57, 287, 9, 107, 336, 105, 334, 13, 14, 346, 111, 50, 280, 425, 205]

def draw_selected_points(image, landmarks, points, color=(0, 255, 0), radius=2):
    h, w, _ = image.shape
    for idx in points:
        lm = landmarks[idx]
        x, y = int(lm.x * w), int(lm.y * h)
        cv2.circle(image, (x, y), radius, color, -1)
        # Dibujar el número del punto
        cv2.putText(image, str(idx), (x + 4, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

def main():
    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,  # para los 478 puntos
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convierte la imagen BGR a RGB para MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Dibuja solo los puntos seleccionados
                    draw_selected_points(frame, face_landmarks.landmark, points_to_draw)

            cv2.imshow("Face Mesh - Selected Points", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
