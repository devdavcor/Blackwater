import cv2
import mediapipe as mp
import os

# Rutas
carpeta_imagenes = r"C:\Users\devdavcor\Documents\desarrollo\facemesh\AF07"
carpeta_2 = r"C:\Users\devdavcor\Documents\desarrollo\facemesh\AF07 iris"

# Inicializar Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,  # Necesario para incluir iris (478 puntos)
    min_detection_confidence=0.5
)

# Drawing specs
mp_drawing = mp.solutions.drawing_utils
color_punto = (0, 255, 0)
color_linea = (0, 0, 255)

# Índices de los centros del iris izquierdo y derecho según MediaPipe
IDX_IRIS_IZQ = 468
IDX_IRIS_DER = 473

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
                num_puntos = len(puntos)
                print(f"{filename}: Se detectaron {num_puntos} puntos faciales.")

                # Obtener coordenadas del iris izquierdo y derecho
                h, w, _ = imagen.shape
                p_izq = puntos[IDX_IRIS_IZQ]
                p_der = puntos[IDX_IRIS_DER]
                x_izq, y_izq = int(p_izq.x * w), int(p_izq.y * h)
                x_der, y_der = int(p_der.x * w), int(p_der.y * h)

                # Dibujar puntos
                cv2.circle(imagen, (x_izq, y_izq), 2, color_punto, -1)
                cv2.circle(imagen, (x_der, y_der), 2, color_punto, -1)

                # Dibujar línea entre iris
                cv2.line(imagen, (x_izq, y_izq), (x_der, y_der), color_linea, 1)

            # Guardar con sufijo "_iris"
            nombre_salida = filename.replace(".JPG", "_iris.JPG")
            cv2.imwrite(os.path.join(carpeta_2, nombre_salida), imagen)
            print(f"Procesada y guardada: {nombre_salida}")
        else:
            print(f"No se detectaron rostros en: {filename}")
