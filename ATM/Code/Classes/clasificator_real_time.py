import cv2
import mediapipe as mp
import numpy as np
import math
import time

vectors_path = r"C:\Users\devdavcor\Documents\Blackwater\ATM\Code\Classes\average_vectors.npy"
class_labels = ["AFS", "ANS", "DIS", "HAS", "NES", "SAS", "SUS"]

all_vectors = np.load(vectors_path)
if all_vectors.shape[0] != len(class_labels):
    raise ValueError("La cantidad de vectores no coincide con la cantidad de clases.")

mp_face_mesh = mp.solutions.face_mesh

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

def capture_and_classify(duration_seconds=2):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return False

    detected_emotions = set()
    start_time = time.time()

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while time.time() - start_time < duration_seconds:
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                h, w, _ = frame.shape
                face_landmarks = results.multi_face_landmarks[0]
                vector = get_face_vector(face_landmarks, w, h)

                if vector is not None:
                    distances = np.linalg.norm(all_vectors - vector, axis=1)
                    min_index = np.argmin(distances)
                    predicted_class = class_labels[min_index]
                    detected_emotions.add(predicted_class)

    cap.release()
    # Devuelve True si detecta NES o HAS en algún momento, False en caso contrario
    return any(em in detected_emotions for em in ["NES", "HAS"])
