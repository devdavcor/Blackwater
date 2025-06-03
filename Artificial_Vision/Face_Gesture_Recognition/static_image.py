import cv2
import mediapipe as mp
import math

# Inicializa MediaPipe Face Mesh con la malla de 478 puntos
mp_face_mesh = mp.solutions.face_mesh

# Puntos de interés
points_to_draw = [4, 468, 473, 57, 287, 107, 336, 105, 334, 13, 14, 346, 111]

# Líneas de interés con sus colores
lines_to_draw = {
    (13, 14): (0, 255, 0),
    (4, 14): (0, 255, 0),
    (57, 287): (0, 255, 0),
    (105, 111): (0, 255, 0),
    (334, 346): (0, 255, 0),
    (468, 105): (0, 255, 0),
    (473, 334): (0, 255, 0),
    (107, 336): (0, 255, 0),
    (468, 473): (0, 0, 255)  # Línea de referencia
}

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

def draw_selected_points_and_lines(image, landmarks, points, lines, radius=2):
    h, w, _ = image.shape

    # Dibuja puntos
    for idx in points:
        lm = landmarks[idx]
        x, y = int(lm.x * w), int(lm.y * h)
        cv2.circle(image, (x, y), radius, (0, 255, 0), -1)
        cv2.putText(image, str(idx), (x + 4, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

    # Dibuja líneas
    for (start_idx, end_idx), color in lines.items():
        start_lm = landmarks[start_idx]
        end_lm = landmarks[end_idx]
        x1, y1 = int(start_lm.x * w), int(start_lm.y * h)
        x2, y2 = int(end_lm.x * w), int(end_lm.y * h)
        cv2.line(image, (x1, y1), (x2, y2), color, 2)

def main():
    image_path = r'C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\impress\AF01NES.JPG'
    image = cv2.imread(image_path)
    if image is None:
        print("No se pudo cargar la imagen.")
        return

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = image.shape

                # Dibuja puntos y líneas
                draw_selected_points_and_lines(image, face_landmarks.landmark, points_to_draw, lines_to_draw)

                # Calcula distancia de referencia
                ref_dist = euclidean_distance(
                    face_landmarks.landmark[reference_pair[0]],
                    face_landmarks.landmark[reference_pair[1]],
                    w, h
                )

                # Calcula y guarda proporciones
                ratios = []
                for p1, p2 in measurement_pairs:
                    dist = euclidean_distance(
                        face_landmarks.landmark[p1],
                        face_landmarks.landmark[p2],
                        w, h
                    )
                    ratio = dist / ref_dist if ref_dist != 0 else 0
                    ratios.append(round(ratio, 4))  # 4 decimales para más claridad

                print("Ratios normalizados respecto a (468, 473):")
                print(ratios)

        cv2.imshow("Face Mesh - Selected Points and Lines", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
