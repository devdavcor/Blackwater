import cv2
import face_recognition
import numpy as np
import pandas as pd
import os
import time

INFO_PATH = "info.parquet"
UMBRAL_SIMILITUD = 0.6  # entre menor, más estricta la coincidencia

def cargar_vector_usuario(user):
    if not os.path.exists(INFO_PATH):
        print("❌ El archivo info.parquet no existe.")
        return None

    df = pd.read_parquet(INFO_PATH)
    usuario = df[df["user"] == user]

    if usuario.empty:
        print(f"❌ Usuario '{user}' no encontrado.")
        return None

    vector = np.array(usuario.iloc[0]["vector"], dtype=np.float32)
    return vector

def comparar_en_tiempo_real(user):
    vector_guardado = cargar_vector_usuario(user)
    if vector_guardado is None:
        return False

    cap = cv2.VideoCapture(0)
    tiempo_inicio = time.time()
    resultado = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rostros = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, rostros)

        mensaje = "No hay rostro"

        if encodings:
            distancia = face_recognition.face_distance([vector_guardado], encodings[0])[0]
            coincide = distancia < UMBRAL_SIMILITUD
            mensaje = f"{'✅ Coincide' if coincide else '❌ No coincide'} ({distancia:.2f})"
            if coincide:
                resultado = True
                break  # podemos salir si ya se confirmó coincidencia

        # Mostrar mensaje en la ventana
        cv2.putText(frame, mensaje, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0) if "Coincide" in mensaje else (0, 0, 255), 3)

        cv2.imshow("Verificación de rostro", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir manualmente
            break

        if time.time() - tiempo_inicio > 5:  # máximo 5 segundos
            break

    cap.release()
    cv2.destroyAllWindows()
    return resultado

if __name__ == "__main__":
    usuario = input("🔹 Ingresa el nombre de usuario a verificar: ").strip()
    if usuario:
        coincide = comparar_en_tiempo_real(usuario)
        print(f"\nResultado final: {'✅ Coincide' if coincide else '❌ No coincide'}")
    else:
        print("❌ Nombre de usuario no válido.")
