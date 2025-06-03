import cv2
import mediapipe as mp
import os

# Rutas
carpeta_imagenes = r"C:\Users\devdavcor\Documents\desarrollo\facemesh\AF07"
carpeta_2 = r"C:\Users\devdavcor\Documents\desarrollo\facemesh\AF07 nariz"

# Inicializar Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# Drawing specs
color_punto = (255, 0, 0)
color_linea = (0, 0, 255)
color_texto = (0, 255, 0)

# Índices clave
IDX_IRIS_IZQ = 468  # A
IDX_IRIS_DER = 473  # B
IDX_NARIZ = 1       # C

# Iterar sobre las imágenes
for filename in os.listdir(carpeta_imagenes):
    if filename.endswith('S.JPG'):
        path_imagen = os.path.join(carpeta_imagenes, filename)
        imagen = cv2.imread(path_imagen)
        if imagen is None:
            print(f"No se pudo leer la imagen: {filename}")
            continue

        # Convertir a RGB
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        resultados = face_mesh.process(imagen_rgb)

        if resultados.multi_face_landmarks:
            for face_landmarks in resultados.multi_face_landmarks:
                puntos = face_landmarks.landmark
                h, w, _ = imagen.shape

                # Obtener coordenadas
                def obtener_punto(idx):
                    p = puntos[idx]
                    return int(p.x * w), int(p.y * h)

                x_izq, y_izq = obtener_punto(IDX_IRIS_IZQ)
                x_der, y_der = obtener_punto(IDX_IRIS_DER)
                x_nariz, y_nariz = obtener_punto(IDX_NARIZ)

                # Dibujar puntos
                cv2.circle(imagen, (x_izq, y_izq), 3, color_punto, -1)
                cv2.circle(imagen, (x_der, y_der), 3, color_punto, -1)
                cv2.circle(imagen, (x_nariz, y_nariz), 3, color_punto, -1)

                # Dibujar etiquetas
                cv2.putText(imagen, 'A', (x_izq + 5, y_izq - 5), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color_texto, 1)
                cv2.putText(imagen, 'B', (x_der + 5, y_der - 5), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color_texto, 1)
                cv2.putText(imagen, 'C', (x_nariz + 5, y_nariz - 5), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color_texto, 1)

                # Dibujar líneas
                cv2.line(imagen, (x_izq, y_izq), (x_der, y_der), color_linea, 1)
                cv2.line(imagen, (x_izq, y_izq), (x_nariz, y_nariz), color_linea, 1)
                cv2.line(imagen, (x_der, y_der), (x_nariz, y_nariz), color_linea, 1)

            # Guardar con sufijo
            nombre_salida = filename.replace(".JPG", "_iris_nariz_etiquetas.JPG")
            cv2.imwrite(os.path.join(carpeta_2, nombre_salida), imagen)
            print(f"Procesada y guardada: {nombre_salida}")
        else:
            print(f"No se detectaron rostros en: {filename}")
