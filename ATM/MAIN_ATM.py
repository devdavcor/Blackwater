import os
import random
import time
import math

import cv2
import face_recognition
import mediapipe as mp
import numpy as np
import pandas as pd

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

from enum import global_enum_repr
from pathlib import Path

import tkinter as tk
from tkinter import Tk, messagebox
from PIL import Image, ImageTk

from Code.Classes.ATM import ATM
from Code.Classes.Login import Login
from Code.Classes.Window import Window
from Code.Classes.clasificator_real_time import *

# ---------- Funciones Auxiliares ----------
atm = None
administrator = None
password = None
alert = None

import random
from tkinter import messagebox

def try_login():
    global atm, administrator, password, alert
    admin = server_app.user.get()
    password = server_app.password.get()

    result = login_instance.start_login(admin, password)
    if not result:
        messagebox.showerror("Login", "User or password incorrect.")
        return False

    administrator = admin
    atm = ATM('192.168.0.253', 11000)
    atm.start()

    messagebox.showerror ( "Login", "See the camera to validate your face." )
    var_1 = validate_face()
    if not var_1:
        messagebox.showerror("Login", "Authentication failed. Please try again.")
        return False

    var_2 = capture_and_classify()
    if var_2 is False:
        messagebox.showerror ( "Login", "Validate your hand gesture." )
        alert = detectar_mano_abierta()
    else:
        aux = random.choice([True, False])
        if aux:
            messagebox.showerror ( "Login", "Validate your hand gesture." )
            alert = detectar_mano_abierta ()

    messagebox.showinfo("Login", f"Welcome, {administrator}!")
    main_window.withdraw()
    open_menu_window()
    atm.send_alert(administrator)
    return True


'''
def try_login():
    global atm, administrator, password, alert  # Aquí le dices que usarás la variable global
    admin = server_app.user.get()
    password = server_app.password.get()
    result = login_instance.start_login(admin, password)

    if result:
        administrator = admin
        atm = ATM('192.168.0.253', 11000)  # Crear la instancia aquí
        atm.start ()
        var_1 = validate_face()
        if var_1:
            var_2 = capture_and_classify()
            if var_2 == False:
                alert = detectar_mano_abierta()
            else:
                if random.choice([True, False]):
                    alert = detectar_mano_abierta ()
                else:
                    alert = True
        else:
            messagebox.showerror ( "Login", "Authenticaition failed. Please try again." )
            try_login ()

        if var_1:
            messagebox.showinfo("Login", f"Welcome, {result}!")
            main_window.withdraw()
            open_menu_window()
            atm.send_alert(administrator)
        else:
            messagebox.showerror ( "Login", "Authenticaition failed. Please try again." )
            try_login()
    else:
        messagebox.showerror("Login", "User or password incorrect.")
'''


def logs():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Logs",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16)
    )

    def close_window() :
        # Cierra la ventana actual sin afectar otras ventanas
        server_app_menu.root.destroy ()
        # 'server_app_menu.root' es la ventana donde se encuentra el botón "Back"

    # Creación del botón Back
    server_app_menu.create_button (
        text="Back",
        command=close_window,  # Llama a la función close_window para cerrar solo la ventana actual
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#d94e4e",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )


def logout() :
    # Mostrar un popup de confirmación
    response = messagebox.askyesno ( "Precaution!", "Are you sure you want to log out? All process will be stop." )

    if response :  # Si el usuario selecciona "Yes"
        main_window.quit ()  # Usa el nombre de la ventana principal, en este caso 'login_window'
        main_window.destroy ()  # Destruye la ventana completamente

# ---------- Funciones para mostrar las ventanas ----------

# ---------- Función para crear la ventana de Menu
def open_menu_window():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Select an option.",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16)
    )

    server_app_menu.create_button(
        text="Check Balance",
        command=chek_balance,
        row=9,
        column=8,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Deposit Cash",
        command=deposit_cash_button,
        row=9,
        column=2,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Change NIP",
        command=change_nip_button,
        row=14,
        column=8,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Withdraw Cash",
        command=withdraw_cash_button,
        row=9,
        column=14,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    '''
    server_app_menu.create_button (
        text="Prueba identidad",
        command=validate_face,
        row=14,
        column=14,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Open Close",
        command=detectar_mano_abierta,
        row=19,
        column=14,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )
    '''
    server_app_menu.create_button (
        text="Log Out",
        command=logout,
        row=22,
        column=17,
        columnspan=1,
        rowspan=1,
        bg="#d94e4e",
        fg="#0D2626",
        font=("Arial", 14)
    )

    menu_window.mainloop()

def chek_balance():
    balance_info = atm.check_balance(administrator)
    parts = balance_info.split ( "|" )
    if len ( parts ) >= 3 :
        messagebox.showinfo ( "Balance", f"Your Balance is ${parts[2]}" )
    else :
        messagebox.showinfo ( "Balance", f"Error" )

def deposit_cash_button():
    global administrator
    amount = float(100)
    result = atm.deposit_cash(administrator, amount)
    parts = result.split ( "|" )
    if len ( parts ) >= 3 :
        messagebox.showinfo ( "Deposit Cash", f"Your deposit was: {parts[2]}" )
    else :
        messagebox.showinfo ( "Balance", f"Error" )

def withdraw_cash_button():
    global administrator
    amount = float(100)
    result = atm.withdraw_cash(administrator, amount)
    parts = result.split ( "|" )
    if len ( parts ) >= 3 :
        messagebox.showinfo ( "Deposit Cash", f"Your withdraw was: {parts[2]}" )
    else :
        messagebox.showinfo ( "Balance", f"Error" )

def validate_face():
    global administrator
    UMBRAL_SIMILITUD = 0.6
    face_db = atm.get_biometrics(administrator)  # debe devolver una lista de 128 floats
    face_captured = capture_face_vector()        # ya definida antes

    if face_db is None or face_captured is None:
        print("❌ No se pudo obtener el vector facial.")
        return False

    # Convertimos a arrays de numpy
    face_db = np.array(face_db)
    face_captured = np.array(face_captured)

    # Calculamos la distancia facial usando face_recognition
    distancia = face_recognition.face_distance([face_db], face_captured)[0]
    coincide = distancia < UMBRAL_SIMILITUD
    mensaje = f"{'✅ Coincide' if coincide else '❌ No coincide'} ({distancia:.2f})"
    print(mensaje)

    return coincide


def capture_face_vector(timeout=5):
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
            break

        # Mostrar mensaje en pantalla
        cv2.putText(frame, mensaje, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (0, 255, 0) if "capturado" in mensaje else (0, 0, 255), 3)

        cv2.imshow("Captura de rostro", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
            break

        if time.time() - tiempo_inicio > 5:  # máximo 5 segundos
            break

    cap.release()
    cv2.destroyAllWindows()

    return vector_resultado

mp_hands = mp.solutions.hands



def detectar_mano_abierta():
    mp_hands = mp.solutions.hands

    def distancia(p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands:

        mano_detectada = False
        tiempo_inicio = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                if not mano_detectada:
                    mano_detectada = True
                    tiempo_inicio = time.time()
                    print("Mano detectada, esperando 2 segundos...")

                elif time.time() - tiempo_inicio >= 2:
                    hand_landmarks = results.multi_hand_landmarks[0]

                    punta = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    base = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                    muñeca = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

                    dist_punta = distancia(punta, muñeca)
                    dist_base = distancia(base, muñeca)

                    cap.release()
                    cv2.destroyAllWindows()
                    if dist_punta > dist_base * 1.3:
                        print('abierta')
                    else:
                        print('cerrada')
                    return dist_punta > dist_base * 1.3  # True si está abierta, False si cerrada

            cv2.imshow("Detectando mano", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()
    return None  # No se detectó mano




# ---------- Función para crear la ventana de login

def create_login_window():
    # Instrucciones
    server_app.create_label(
        text="Please, enter your credentials below.",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app.create_label(
        text="User:",
        row=9,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app.user = server_app.create_entry(row=9, column=9, columnspan=4)

    # Espacio para el password
    server_app.create_label(
        text="Password:",
        row=12,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app.password = server_app.create_entry(row=12, column=9, columnspan=4, show_text=False)

    # Espacio para el botón
    server_app.create_button(
        text="Login",
        command=try_login,
        row=15,
        column=8,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

# ---------- Configuración de la DB ----------

def get_parquet_path():
    base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

parquet_path = get_parquet_path()
login_instance = Login(parquet_path)

def change_nip_button():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="Please, introduce the new NIP to update.",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16)
    )

    server_app_menu.create_label (
        text="New Password:",
        row=11,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#F25CBE",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.password = server_app_menu.create_entry ( row=11, column=10, columnspan=4 )

    # Espacio para el botón
    server_app_menu.create_button (
        text="Update",
        # command=lambda : branch_server.update_name ( server_app_menu.user.get (), server_app_menu.name.get ()),
        command=lambda : update_password (password),
        row=17,
        column=8,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    def close_window() :
        # Cierra la ventana actual sin afectar otras ventanas
        server_app_menu.root.destroy ()
        # 'server_app_menu.root' es la ventana donde se encuentra el botón "Back"

    # Creación del botón Back
    server_app_menu.create_button (
        text="Back",
        command=close_window,  # Llama a la función close_window para cerrar solo la ventana actual
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#d94e4e",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )


def update_password(password):
    global administrator
    result = atm.update_password(administrator, password)
    if result == False:
        messagebox.showinfo ( "Update Password", f"Error. Try again." )
    if result == True:
        messagebox.showinfo ( "Update Password", f"The password was updated." )
    print("Start Server")

if __name__ == "__main__":
    main_window = Tk()
    server_app = Window(main_window)
    # Crear la ventana de login
    create_login_window()

    # Mantener el ciclo principal abierto
    main_window.mainloop()
