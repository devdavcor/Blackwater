from tkinter import Tk, messagebox
import tkinter as tk
from PIL import Image, ImageTk
import random
from Code.Classes.Window import Window
from Code.Classes.Login import Login
from Code.Classes.Central_Server import Central_Server

import os


# ---------- Funciones Auxiliares ----------
def try_login():
    admin = server_app.user.get()  # Accede a la entrada de usuario desde el objeto 'server_app'
    password = server_app.password.get()  # Accede a la entrada de contraseña desde el objeto 'server_app'
    result = login_instance.start_login(admin, password)

    if result:
        messagebox.showinfo("Login", f"Welcome, {result}!")
        main_window.withdraw ()
        open_menu_window()  # Llama a la función para abrir el siguiente menú
    else:
        messagebox.showerror("Login", "User or password incorrect.")

def start_server():
    print("Start Server")
    main_window.withdraw ()
    start_menu_window ()

def start_menu_window():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Start Server",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )
    server_app_menu.create_button(
        text="Start Server",
        command=start_server,  # Llama a la función try_login
        row=12,
        column=8,
        columnspan=4,
        rowspan=2,
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
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )


def stop_server():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Stop Server",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    def close_window() :
        # Cierra la ventana actual sin afectar otras ventanas
        server_app_menu.root.destroy ()
        # 'server_app_menu.root' es la ventana donde se encuentra el botón "Back"

    server_app_menu.create_button(
        text="Stop Server",
        command=stop_server,  # Llama a la función try_login
        row=12,
        column=8,
        columnspan=4,
        rowspan=2,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )
    # Creación del botón Back
    server_app_menu.create_button (
        text="Back",
        command=close_window,  # Llama a la función close_window para cerrar solo la ventana actual
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )

def settings():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Please, the new configuration. If you click on Start, the server will be restarted.",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label(
        text="Port:",
        row=9,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.user = server_app_menu.create_entry(row=9, column=9, columnspan=4)

    # Espacio para el password
    server_app_menu.create_label(
        text="Branches allowed:",
        row=12,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.password = server_app_menu.create_entry(row=12, column=9, columnspan=4, show_text=False)

    # Espacio para el botón
    server_app_menu.create_button(
        text="Start Server",
        command=try_login,  # Llama a la función try_login
        row=15,
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
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )

def branches():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Branches",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    def close_window() :
        # Cierra la ventana actual sin afectar otras ventanas
        server_app_menu.root.destroy ()
        # 'server_app_menu.root' es la ventana donde se encuentra el botón "Back"

    server_app_menu.create_button(
        text="Show Connected Branches",
        command=try_login,  # Llama a la función try_login
        row=9,
        column=6,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Disconnect Branch",
        command=try_login,  # Llama a la función try_login
        row=9,
        column=11,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Registered Branches",
        command=try_login,  # Llama a la función try_login
        row=12,
        column=6,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="New Branch",
        command=try_login,  # Llama a la función try_login
        row=12,
        column=11,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Edit Branch",
        command=try_login,  # Llama a la función try_login
        row=15,
        column=6,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Delete Branch",
        command=try_login,  # Llama a la función try_login
        row=15,
        column=11,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    # Creación del botón Back
    server_app_menu.create_button (
        text="Back",
        command=close_window,  # Llama a la función close_window para cerrar solo la ventana actual
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )

def admin_users():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)
    server_app_menu.create_label(
        text="Admin Users",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    def close_window() :
        # Cierra la ventana actual sin afectar otras ventanas
        server_app_menu.root.destroy ()
        # 'server_app_menu.root' es la ventana donde se encuentra el botón "Back"

    server_app_menu.create_button (
        text="Show Admin",
        command=try_login,  # Llama a la función try_login
        row=9,
        column=6,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Close Session",
        command=logout,  # Llama a la función try_login
        row=9,
        column=11,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Registered Admin",
        command=try_login,  # Llama a la función try_login
        row=12,
        column=6,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="New Admin",
        command=try_login,  # Llama a la función try_login
        row=12,
        column=11,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Edit Admin",
        command=try_login,  # Llama a la función try_login
        row=15,
        column=6,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Delete Admin",
        command=try_login,  # Llama a la función try_login
        row=15,
        column=11,
        columnspan=3,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    # Creación del botón Back
    server_app_menu.create_button (
        text="Back",
        command=close_window,  # Llama a la función close_window para cerrar solo la ventana actual
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )

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
        bg="#195959",
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
        bg="#BFA980",  # Color del botón
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
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    server_app_menu.create_button(
        text="Start Server",
        command=start_server,  # Llama a la función try_login
        row=9,
        column=2,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Stop Server",
        command=stop_server,  # Llama a la función try_login
        row=9,
        column=8,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button(
        text="Settings",
        command=settings,  # Llama a la función try_login
        row=9,
        column=14,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Branches",
        command=branches,  # Llama a la función "branches"
        row=14,
        column=2,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Admin Users",
        command=admin_users,  # Llama a la función "clients"
        row=14,
        column=8,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Logs",
        command=logs,  # Llama a la función "logs"
        row=14,
        column=14,
        columnspan=4,
        rowspan=1,
        bg="#D9CFCC",
        fg="#0D2626",
        font=("Arial", 14)
    )

    server_app_menu.create_button (
        text="Log Out",
        command=logout,  # Llama a la función logout
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )

    menu_window.mainloop()  # Mantener la ventana abierta

# ---------- Función para crear la ventana de login

def create_login_window():
    # Instrucciones
    server_app.create_label(
        text="Please, enter your credentials below.",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
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
        bg="#195959",
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
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app.password = server_app.create_entry(row=12, column=9, columnspan=4, show_text=False)

    # Espacio para el botón
    server_app.create_button(
        text="Login",
        command=try_login,  # Llama a la función try_login
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
    return os.path.join(base_path, "db", "admin.parquet")

parquet_path = get_parquet_path()
login_instance = Login(parquet_path)

if __name__ == "__main__":
    main_window = Tk()
    server_app = Window(main_window)

    # Crear la ventana de login
    create_login_window()

    # Mantener el ciclo principal abierto
    main_window.mainloop()
