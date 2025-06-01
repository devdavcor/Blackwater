import cv2
import face_recognition
import time
import numpy as np

def main():
    cap = cv2.VideoCapture(0)
    conteo = None
    tiempo_inicio = None
    tiempo_conteo = 3  # segundos para conteo regresivo

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detectar rostros (retorna lista de bounding boxes)
        rostros = face_recognition.face_locations(rgb_frame)

        if len(rostros) > 0:
            # Si hay al menos un rostro, iniciar conteo si no iniciado
            if conteo is None:
                conteo = tiempo_conteo
                tiempo_inicio = time.time()

            tiempo_pasado = time.time() - tiempo_inicio
            tiempo_restante = max(0, int(conteo - tiempo_pasado))

            # Mostrar el conteo regresivo en pantalla
            cv2.putText(frame, f"Captura en: {tiempo_restante}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            if tiempo_restante == 0:
                # Tomar la instantánea y obtener encoding facial
                # Solo del primer rostro detectado
                encoding = face_recognition.face_encodings(rgb_frame, [rostros[0]])

                if encoding:
                    vector_128 = encoding[0]
                    print("Vector facial de 128 puntos:")
                    print(vector_128)

                    # Guardar imagen capturada (opcional)
                    cv2.imwrite("rostro_capturado.png", frame)

                else:
                    print("❌ No se pudo obtener el vector facial.")

                # Resetear conteo para permitir nuevo reconocimiento
                conteo = None
                tiempo_inicio = None
        else:
            # Si no hay rostro, resetear conteo
            conteo = None
            tiempo_inicio = None

        cv2.imshow("Reconocimiento facial con conteo regresivo", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
