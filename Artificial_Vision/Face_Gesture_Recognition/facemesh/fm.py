import cv2
import mediapipe as mp
import os

# Ruta de tu carpeta con imágenes
carpeta_imagenes = r"C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\Face_Gesture_Recognition\facemesh\AF07"
carpeta_2 = r"C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\Face_Gesture_Recognition\facemesh\AF07 Processed"

# Inicializar Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh (
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,  # Incluye puntos del iris (478 puntos)
    min_detection_confidence=0.5
)

# Dibujo de los puntos
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec ( thickness=1, circle_radius=1, color=(217, 132, 187) )

# Iterar sobre las imágenes
for filename in os.listdir ( carpeta_imagenes ) :
    # Solo imágenes que terminan EXACTAMENTE en 'S.JPG'
    if filename.endswith ( 'S.JPG' ) :
        path_imagen = os.path.join ( carpeta_imagenes, filename )
        imagen = cv2.imread ( path_imagen )
        cv2.imwrite ( os.path.join ( carpeta_2, filename ), imagen )

        if imagen is None :
            print ( f"No se pudo leer la imagen: {filename}" )
            continue

        # Convertir a RGB
        imagen_rgb = cv2.cvtColor ( imagen, cv2.COLOR_BGR2RGB )
        resultados = face_mesh.process ( imagen_rgb )

        if resultados.multi_face_landmarks :
            for face_landmarks in resultados.multi_face_landmarks :
                mp_drawing.draw_landmarks (
                    image=imagen,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec
                )
                # Contar los puntos detectados
                num_puntos = len ( face_landmarks.landmark )
                print ( f"{filename}: Se detectaron {num_puntos} puntos faciales." )

            # Guardar con sufijo "_mesh"
            nombre_salida = filename.replace ( ".JPG", "_mesh.JPG" )
            cv2.imwrite ( os.path.join ( carpeta_2, nombre_salida ), imagen )
            print ( f"Procesada y guardada: {nombre_salida}" )
        else :
            print ( f"No se detectaron rostros en: {filename}" )
