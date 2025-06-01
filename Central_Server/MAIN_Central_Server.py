from tkinter import Tk, messagebox
import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import pandas as pd
from pathlib import Path

from Code.Classes.Window import Window
from Code.Classes.Login import Login
from Code.Classes.Central_Server import Central_Server
from Code.Classes.Unit import *


# ---------- Funciones Auxiliares ----------
central_server = None
administrator = None
password = None

def try_login():
    global central_server  # Aquí le dices que usarás la variable global
    admin = server_app.user.get()
    password = server_app.password.get()
    result = login_instance.start_login(admin, password)

    if result:
        global administrator
        administrator = admin
        messagebox.showinfo("Login", f"Welcome, {result}!")
        main_window.withdraw()
        central_server = Central_Server()  # Crear la instancia aquí
        open_menu_window()
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
        command=central_server.start_server,
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
        command=central_server.stop_server,
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

    server_app_menu.port = server_app_menu.create_entry(row=9, column=9, columnspan=4)

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

    server_app_menu.branches = server_app_menu.create_entry(row=12, column=9, columnspan=4, show_text=True)

    # Espacio para el botón
    server_app_menu.create_button(
        text="Reset Server",
        command=lambda: central_server.settings_server(int(server_app_menu.port.get()), int(server_app_menu.branches.get())),
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
        command=show_conexions,
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
        command=disconnect,
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
        command=show_registered_branches,
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
        command=new_branch_button,
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
        command=edit_branch_button,
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
        command=delete_branch_button,
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
def new_branch_button():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="New Branch",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label (
        text="Name:",
        row=9,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.name = server_app_menu.create_entry ( row=9, column=9, columnspan=4 )

    # Espacio para el password
    server_app_menu.create_label (
        text="Last Name:",
        row=12,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.last_name = server_app_menu.create_entry ( row=12, column=9, columnspan=4, show_text=True )

    # Espacio para el botón
    server_app_menu.create_button (
        text="New Branch",
        command=lambda : new_branch ( server_app_menu.name.get () , server_app_menu.last_name.get ()  ),
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

def edit_branch_button():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="Edit Branch",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label (
        text="User:",
        row=9,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.user = server_app_menu.create_entry ( row=9, column=10, columnspan=4 )

    server_app_menu.create_label (
        text="Name:",
        row=11,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.name = server_app_menu.create_entry ( row=11, column=10, columnspan=4 )

    # Espacio para el password
    server_app_menu.create_label (
        text="Last Name:",
        row=13,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.last_name = server_app_menu.create_entry ( row=13, column=10, columnspan=4, show_text=True )

    server_app_menu.create_label (
        text="Password:",
        row=15,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.password = server_app_menu.create_entry ( row=15, column=10, columnspan=4, show_text=True )

    # Espacio para el botón
    server_app_menu.create_button (
        text="Edit Branch",
        command=lambda : update_branch_data ( server_app_menu.user.get (), server_app_menu.name.get (), server_app_menu.last_name.get (), server_app_menu.password.get () ),
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
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )


def show_registered_branches():

    # Crear nueva ventana
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)

    server_app_menu.create_label(
        text="Registered Branches",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    def close_window():
        server_app_menu.root.destroy()

    listbox = tk.Listbox(server_app_menu.root, font=("Arial", 12), width=50)
    listbox.grid(row=10, column=6, columnspan=8, rowspan=10, padx=10, pady=10, sticky="nsew")

    # Ruta relativa al archivo Parquet
    relative_path = Path("Resources/DB/branches.parquet")

    try:
        df = pd.read_parquet(relative_path)

        if "user" in df.columns:
            for i, user in enumerate(df["user"]):
                listbox.insert(tk.END, f"{i + 1}. {user}")
        else:
            listbox.insert(tk.END, "La columna 'user' no existe en el archivo.")
    except Exception as e:
        listbox.insert(tk.END, f"Error reading branches: {e}")

    server_app_menu.create_button(
        text="Back",
        command=close_window,
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#BFA980",
        fg="#0D2626",
        font=("Arial", 14)
    )

def disconnect():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
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
    server_app_menu.create_label (
        text="Branch:",
        row=9,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.port = server_app_menu.create_entry ( row=9, column=9, columnspan=4 )

    # Espacio para el botón
    server_app_menu.create_button (
        text="Reset Server",
        command=lambda : central_server.disconnect_client ( int ( server_app_menu.port.get () )),
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

def show_conexions():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel(main_window)
    server_app_menu = Window(menu_window)

    server_app_menu.create_label(
        text="Connected Branches",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    def close_window():
        server_app_menu.root.destroy()

    # Crear el Listbox con .grid() en lugar de .pack()
    listbox = tk.Listbox(server_app_menu.root, font=("Arial", 12), width=50)
    listbox.grid(row=10, column=6, columnspan=8, rowspan=10, padx=10, pady=10, sticky="nsew")

    # Rellenar el Listbox con las conexiones
    for i, conn in enumerate(central_server.connected_users):
        listbox.insert(tk.END, f"{i + 1}. {conn}")

    # Botón para cerrar la ventana
    server_app_menu.create_button(
        text="Back",
        command=close_window,
        row=22,
        column=18,
        columnspan=1,
        rowspan=1,
        bg="#BFA980",
        fg="#0D2626",
        font=("Arial", 14)
    )

def delete_branch_button ():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="Delete User",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label (
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

    server_app_menu.user = server_app_menu.create_entry ( row=9, column=9, columnspan=4 )

    # Espacio para el botón
    server_app_menu.create_button (
        text="Delete",
        command=lambda : delete_branch ( server_app_menu.user.get ()),
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
        command=show_admin_button,
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
        command=logout,
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
        command=try_login,
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
        command=new_admin_button,
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
        command=edit_admin_button,
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
        command=delete_admin_button,
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

def show_admin_button ():
    messagebox.showinfo ( "Administrator", f"User: {administrator}" )
    return

def new_admin_button():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="New Administrator",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label (
        text="Name:",
        row=9,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.name = server_app_menu.create_entry ( row=9, column=9, columnspan=4 )

    # Espacio para el password
    server_app_menu.create_label (
        text="Last Name:",
        row=12,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.last_name = server_app_menu.create_entry ( row=12, column=9, columnspan=4, show_text=True )

    # Espacio para el botón
    server_app_menu.create_button (
        text="New Admin",
        command=lambda : new_administrator ( server_app_menu.name.get () , server_app_menu.last_name.get ()  ),
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

def edit_admin_button():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="Edit Admin",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label (
        text="User:",
        row=9,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.user = server_app_menu.create_entry ( row=9, column=10, columnspan=4 )

    server_app_menu.create_label (
        text="Name:",
        row=11,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.name = server_app_menu.create_entry ( row=11, column=10, columnspan=4 )

    # Espacio para el password
    server_app_menu.create_label (
        text="Last Name:",
        row=13,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.last_name = server_app_menu.create_entry ( row=13, column=10, columnspan=4, show_text=True )

    server_app_menu.create_label (
        text="Password:",
        row=15,
        column=7,
        columnspan=4,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.password = server_app_menu.create_entry ( row=15, column=10, columnspan=4, show_text=True )

    # Espacio para el botón
    server_app_menu.create_button (
        text="Edit Admin",
        command=lambda : update_admin_data ( server_app_menu.user.get (), server_app_menu.name.get (), server_app_menu.last_name.get (), server_app_menu.password.get () ),
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
        bg="#BFA980",  # Color del botón
        fg="#0D2626",
        font=("Arial", 14)
    )

def delete_admin_button ():
    # Crear una nueva ventana Toplevel para el menú
    menu_window = tk.Toplevel ( main_window )
    server_app_menu = Window ( menu_window )
    server_app_menu.create_label (
        text="Delete Admin",
        row=6,
        column=6,
        columnspan=8,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16)
    )

    # Espacio para usuario
    server_app_menu.create_label (
        text="Admin:",
        row=9,
        column=7,
        columnspan=3,
        rowspan=1,
        bg="#195959",
        fg="white",
        font=("Arial", 16),
        anchor="w"
    )

    server_app_menu.user = server_app_menu.create_entry ( row=9, column=9, columnspan=4 )

    # Espacio para el botón
    server_app_menu.create_button (
        text="Delete",
        command=lambda : delete_administrator ( server_app_menu.user.get ()),
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
        command=start_server,
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
        command=stop_server,
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
        command=settings,
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
        command=branches,
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

if __name__ == "__main__":
    main_window = Tk()
    server_app = Window(main_window)
    central_server = Central_Server ()
    # Crear la ventana de login
    create_login_window()

    # Mantener el ciclo principal abierto
    main_window.mainloop()
