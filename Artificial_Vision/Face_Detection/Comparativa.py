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


def capturar_vector_en_tiempo_real():
    cap = cv2.VideoCapture(0)
    tiempo_inicio = time.time()
    vector_resultado = None

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
            vector_resultado = encodings[0]
            mensaje = "✅ Rostro capturado"
            break  # salimos con el primer rostro detectado

        # Mostrar mensaje en la ventana
        cv2.putText(frame, mensaje, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0) if "capturado" in mensaje else (0, 0, 255), 3)

        cv2.imshow("Captura de rostro", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir manualmente
            break

        if time.time() - tiempo_inicio > 5:  # máximo 5 segundos
            break

    cap.release()
    cv2.destroyAllWindows()
    return vector_resultado

import cv2
import face_recognition
import numpy as np
import time

def processing_biometrics(user):
    cap = cv2.VideoCapture(0)
    tiempo_inicio = time.time()
    vector_resultado = None

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
            vector_resultado = encodings[0]
            mensaje = "✅ Rostro capturado"
            break  # salimos con el primer rostro detectado

        # Mostrar mensaje en la ventana
        cv2.putText(frame, mensaje, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (0, 255, 0) if "capturado" in mensaje else (0, 0, 255), 3)

        cv2.imshow("Captura de rostro", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir manualmente
            break

        if time.time() - tiempo_inicio > 5:  # máximo 5 segundos
            break

    cap.release()
    cv2.destroyAllWindows()

    # Si se capturó un rostro, procesamos el envío
    if vector_resultado is not None:
        vector_str = ','.join([str(v) for v in vector_resultado])
        petition = f"UPDATE_BIOMETRICS|{user}|{vector_str}"
        #response = self.send_command_to_a(petition)
        print(petition)
    '''
        parts = response.split('|')
        if len(parts) >= 2:
            print(response)
            return parts[-1]
        else:
            return "ERROR|Invalid response format"
    else:
        print("❌ No se capturó ningún rostro.")
        return "ERROR|No face captured"
    '''

if __name__ == "__main__":
    '''
    usuario = input("🔹 Ingresa el nombre de usuario a verificar: ").strip()
    if usuario:
        coincide = comparar_en_tiempo_real(usuario)
        print(f"\nResultado final: {'✅ Coincide' if coincide else '❌ No coincide'}")
    else:
        print("❌ Nombre de usuario no válido.")
    '''
    print(f"El vector es {capturar_vector_en_tiempo_real()}")

    processing_biometrics ( 'administrator' )