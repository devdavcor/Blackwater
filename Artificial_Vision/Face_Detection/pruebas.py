import cv2
import face_recognition
import time
import numpy as np
import pandas as pd
import os

INFO_PATH = "info.parquet"

def guardar_vector(user, vector_128):
    vector_128 = vector_128.astype(np.float32)  # Garantizar tipo
    nuevo = pd.DataFrame([{"user": user, "vector": vector_128.tolist()}])

    if os.path.exists(INFO_PATH):
        df = pd.read_parquet(INFO_PATH)
        df = pd.concat([df, nuevo], ignore_index=True)
    else:
        df = nuevo

    df.to_parquet(INFO_PATH, index=False)
    print(f"✅ Vector guardado para usuario '{user}' en {INFO_PATH}")

def capturar_vector(user):
    cap = cv2.VideoCapture(0)
    intentos = 0
    max_intentos = 3
    tiempo_conteo = 3  # segundos de cuenta regresiva
    conteo = None
    tiempo_inicio = None

    while intentos < max_intentos:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al capturar imagen.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rostros = face_recognition.face_locations(rgb_frame)

        if len(rostros) > 0:
            if conteo is None:
                conteo = tiempo_conteo
                tiempo_inicio = time.time()

            tiempo_pasado = time.time() - tiempo_inicio
            tiempo_restante = max(0, int(conteo - tiempo_pasado))

            cv2.putText(frame, f"Captura en: {tiempo_restante}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            if tiempo_restante == 0:
                encoding = face_recognition.face_encodings(rgb_frame, [rostros[0]])

                if encoding:
                    guardar_vector(user, encoding[0])
                    cv2.imwrite(f"{user}_captura.png", frame)
                    break
                else:
                    print("❌ No se pudo obtener el vector facial.")
                    intentos += 1

                conteo = None
                tiempo_inicio = None
        else:
            conteo = None
            tiempo_inicio = None

        cv2.imshow("Captura facial con conteo regresivo", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            print("❌ Cancelado por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if intentos >= max_intentos:
        print("⚠️ Se agotaron los intentos para capturar el rostro.")

if __name__ == "__main__":
    usuario = input("🔹 Ingresa el nombre de usuario: ").strip()
    if usuario:
        capturar_vector(usuario)
    else:
        print("❌ Nombre de usuario no válido.")
