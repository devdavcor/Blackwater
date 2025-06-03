import cv2
import mediapipe as mp
import math
import os

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
    (107, 336)
]

# Par de referencia
reference_pair = (468, 473)

def euclidean_distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def process_image(image_path, face_mesh):
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] No se pudo cargar la imagen: {image_path}")
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

def euclidean_distance_between_lists(list1, list2):
    return round(math.sqrt(sum((a - b) ** 2 for a, b in zip(list1, list2))), 4)

def main():
    folder_path = r'C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\impress'
    image_files = [f for f in os.listdir(folder_path) if f.endswith("NES.JPG")]

    if not image_files:
        print("No se encontraron imágenes que terminen en 'NES.JPG'")
        return

    all_ratios = []
    filenames = []

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:

        for filename in image_files:
            full_path = os.path.join(folder_path, filename)
            ratios = process_image(full_path, face_mesh)

            if ratios:
                print(f"{filename}: {ratios}")
                all_ratios.append(ratios)
                filenames.append(filename)
            else:
                print(f"{filename}: [NO LANDMARKS DETECTED]")

    if not all_ratios:
        print("No se pudieron calcular distancias porque no se detectaron landmarks en ninguna imagen.")
        return

    # Calcular promedio
    num_ratios = len(all_ratios[0])
    averages = [round(sum(r[i] for r in all_ratios) / len(all_ratios), 4) for i in range(num_ratios)]

    print("\n--- PROMEDIO DE RATIOS ---")
    print(averages)

    # Calcular distancias a la media
    print("\n--- DISTANCIAS A LA MEDIA ---")
    distances = []
    for name, ratios in zip(filenames, all_ratios):
        dist = euclidean_distance_between_lists(ratios, averages)
        distances.append(dist)
        print(f"{name}: {dist}")

    print("\n--- RESUMEN DE DISTANCIAS ---")
    print(f"Distancia mínima : {min(distances)}")
    print(f"Distancia máxima : {max(distances)}")
    print(f"Distancia promedio: {round(sum(distances)/len(distances), 4)}")

if __name__ == "__main__":
    main()
