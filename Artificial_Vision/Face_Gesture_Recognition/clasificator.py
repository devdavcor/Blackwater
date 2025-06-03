import os
import cv2
import mediapipe as mp
import numpy as np
import math

# Carpeta con imágenes a clasificar
image_folder = r"C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\impress"

# Archivo con los vectores promedio (uno por clase)
vectors_path = "average_vectors.npy"  # <-- usa el archivo que guardaste con los 7 vectores promedio

# Etiquetas de clase en orden
class_labels = ["AFS", "ANS", "DIS", "HAS", "NES", "SAS", "SUS"]

# Carga los vectores promedio
all_vectors = np.load(vectors_path)
print(f"Vectores cargados: {all_vectors.shape[0]}")  # Debe ser 7
print(f"Cantidad de clases: {len(class_labels)}")

if all_vectors.shape[0] != len(class_labels):
    raise ValueError("La cantidad de vectores no coincide con la cantidad de clases. "
                     "Verifica que 'average_vectors.npy' tenga 7 vectores, uno por clase.")

# Inicializa MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Pares de puntos para mediciones
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

def process_image_vector(image_path, face_mesh):
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
    return None

def main():
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")]

    if not image_files:
        print("No se encontraron imágenes para procesar.")
        return

    # Contadores para evaluación
    total_per_class = {label: 0 for label in class_labels}
    correct_per_class = {label: 0 for label in class_labels}
    no_face_count = 0

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:

        for filename in image_files:
            # Extraer etiqueta real de los últimos 3 caracteres antes de la extensión
            true_label = os.path.splitext(filename)[0][-3:].upper()

            # Validar que la etiqueta real esté en las clases conocidas
            if true_label not in class_labels:
                print(f"{filename} | Etiqueta real '{true_label}' no reconocida. Se omite.")
                continue

            total_per_class[true_label] += 1

            full_path = os.path.join(image_folder, filename)
            current_vector = process_image_vector(full_path, face_mesh)

            if current_vector is not None:
                distances = np.linalg.norm(all_vectors - current_vector, axis=1)
                min_index = np.argmin(distances)
                predicted_class = class_labels[min_index]

                if predicted_class == true_label:
                    correct_per_class[true_label] += 1

                print(f"{filename} | Real: {true_label} | Predicción: {predicted_class} | Distancia mínima: {distances[min_index]:.5f}")
            else:
                no_face_count += 1
                print(f"{filename} | [NO SE DETECTÓ ROSTRO]")

    # Mostrar resultados finales
    print("\n--- Resumen de precisión por clase ---")
    for label in class_labels:
        total = total_per_class[label]
        correct = correct_per_class[label]
        if total > 0:
            accuracy = correct / total * 100
            print(f"{label}: {correct}/{total} correctos - Precisión: {accuracy:.2f}%")
        else:
            print(f"{label}: No hay imágenes para evaluar")

    print(f"\nImágenes sin rostro detectado: {no_face_count}")

if __name__ == "__main__":
    main()
