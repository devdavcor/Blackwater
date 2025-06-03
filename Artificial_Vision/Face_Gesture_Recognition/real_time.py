import cv2
import mediapipe as mp
import numpy as np
import math

# Archivo con los vectores promedio (uno por clase)
vectors_path = "average_vectors.npy"  # Asegúrate de tener este archivo en el directorio actual

# Etiquetas de clase en orden
class_labels = ["AFS", "ANS", "DIS", "HAS", "NES", "SAS", "SUS"]

# Carga los vectores promedio
all_vectors = np.load(vectors_path)
if all_vectors.shape[0] != len(class_labels):
    raise ValueError("La cantidad de vectores no coincide con la cantidad de clases.")

# Inicializa MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Pares de puntos para mediciones (igual que en tu versión offline)
measurement_pairs = [
    (13, 14),
    (4, 14),
    (57, 287),
    (105, 111),
    (334, 346),
    (468, 105),
    (473, 334),
    (107, 336),
]

# Par de referencia para normalizar distancias
reference_pair = (468, 473)

def euclidean_distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_face_vector(face_landmarks, w, h):
    ref_dist = euclidean_distance(
        face_landmarks.landmark[reference_pair[0]],
        face_landmarks.landmark[reference_pair[1]],
        w, h
    )
    if ref_dist == 0:
        return None

    ratios = []
    for p1, p2 in measurement_pairs:
        dist = euclidean_distance(
            face_landmarks.landmark[p1],
            face_landmarks.landmark[p2],
            w, h
        )
        ratio = dist / ref_dist
        ratios.append(round(ratio, 4))
    return np.array(ratios)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("No se pudo leer el frame")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                h, w, _ = frame.shape
                face_landmarks = results.multi_face_landmarks[0]

                vector = get_face_vector(face_landmarks, w, h)

                if vector is not None:
                    # Calcula distancia con vectores promedio
                    distances = np.linalg.norm(all_vectors - vector, axis=1)
                    min_index = np.argmin(distances)
                    predicted_class = class_labels[min_index]
                    confidence = 1 - distances[min_index]  # Solo para dar una idea

                    # Mostrar resultado en la imagen
                    cv2.putText(frame, f"Emocion: {predicted_class} ({confidence:.2f})",
                                (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2, cv2.LINE_AA)
                else:
                    cv2.putText(frame, "No se pudo calcular vector",
                                (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, "Rostro no detectado",
                            (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.imshow("Reconocimiento de Emociones", frame)

            key = cv2.waitKey(1)
            if key == 27:  # ESC para salir
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
