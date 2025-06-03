import cv2
import mediapipe as mp
import math
import os
import numpy as np

# Inicializa MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Pares a medir
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

# Par de referencia
reference_pair = (468, 473)

# Sufijos a analizar
suffixes = ["AFS", "ANS", "DIS", "HAS", "NES", "SAS", "SUS"]

def euclidean_distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def process_image(image_path, face_mesh):
    image = cv2.imread(image_path)
    if image is None:
        return None

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)

    if results.multi_face_landmarks:
        h, w, _ = image.shape
        for face_landmarks in results.multi_face_landmarks:
            ref_dist = euclidean_distance(
                face_landmarks.landmark[reference_pair[0]],
                face_landmarks.landmark[reference_pair[1]],
                w, h
            )
            ratios = []
            for p1, p2 in measurement_pairs:
                dist = euclidean_distance(
                    face_landmarks.landmark[p1],
                    face_landmarks.landmark[p2],
                    w, h
                )
                ratio = dist / ref_dist if ref_dist != 0 else 0
                ratios.append(round(ratio, 4))
            return ratios
    return None

def main():
    folder_path = r'C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\impress'

    avg_vectors = []  # Guardar vector promedio de cada grupo

    with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
    ) as face_mesh:

        for suffix in suffixes:
            print(f"\n--- Procesando grupo: {suffix} ---")
            image_files = [f for f in os.listdir(folder_path) if f.endswith(suffix + ".JPG")]
            group_ratios = []

            for filename in image_files:
                full_path = os.path.join(folder_path, filename)
                ratios = process_image(full_path, face_mesh)

                if ratios:
                    group_ratios.append(ratios)
                else:
                    print(f"{filename}: [NO LANDMARKS DETECTED]")

            if not group_ratios:
                print(f"[!] Grupo {suffix}: sin imágenes válidas.")
                continue

            # Calcular promedio de ratios para este grupo
            num_ratios = len(group_ratios[0])
            averages = [round(sum(r[i] for r in group_ratios) / len(group_ratios), 4) for i in range(num_ratios)]

            print(f"[{suffix}] Vector promedio: {averages}")

            avg_vectors.append(averages)

    # Convertir a numpy array y guardar
    avg_vectors_np = np.array(avg_vectors)
    print(f"\nVectores promedio por grupo guardados: {avg_vectors_np.shape}")

    np.save("average_vectors.npy", avg_vectors_np)
    print(avg_vectors_np)

if __name__ == "__main__":
    main()
