import tkinter as tk
from PIL import Image, ImageTk
import random
import os

class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("Corona Banking Central Server")
        self.root.configure(bg="white")
        self.center_window(self.root, 1000, 600)
        self.root.resizable(False, False)

        # Obtener la ruta del archivo Python para generar rutas relativas
        self.base_path = os.path.dirname(os.path.abspath(__file__))


        # Intentar cambiar el icono
        try:
            #icon_path = os.path.join(self.base_path, "..", "..", "graphics", "resources", "icon.png")
            icon_path = os.path.abspath ( os.path.join ( self.base_path, "..", "..", "Resources", "Graphics","icon.png"))
            image = Image.open(os.path.abspath(icon_path))  # Abrimos la imagen con PIL
            self.icon = ImageTk.PhotoImage(image)  # Convertimos la imagen a un formato compatible
            self.root.iconphoto(False, self.icon)  # Establecemos el icono de la ventana
        except Exception as e:
            print(f"Error al establecer el icono: {e}")
            # Si ocurre un error, intentamos establecer un icono por defecto o no hacer nada
            try:
                self.root.iconphoto(False, None)  # No establecer el icono si falla
            except Exception as e2:
                print(f"Error al intentar quitar el icono: {e2}")

        # Añadir fondo
        self.add_background()

        # Configurar celdas de la cuadrícula
        self.configure_grid(rows=24, columns=20)

        # Crear ventana emergente
        self.create_popup_window()

        self.create_label(
            text="Corona Banking Branch Server",  # El texto a mostrar
            row=3,  # Fila en la que estará
            column=0,  # Columna en la que estará
            columnspan=20,  # Cuántas columnas ocupará
            rowspan=1,  # Cuántas filas ocupará
            bg="#bf0413",  # Color de fondo
            fg="white",  # Color de texto
            font=("Arial", 18, "bold")  # Tipo y tamaño de fuente
        )

    def center_window(self, window, width, height):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def add_background(self):
        # Generar un número aleatorio entre 1 y 10 (inclusive)
        random_number = random.randint(1, 10)
        #image_path = os.path.join(self.base_path, "..","Resources", "Graphics", f"f_sc_{random_number}.jpg")
        image_path = os.path.abspath(os.path.join(self.base_path, "..", "..", "Resources", "Graphics", f"f_sc_{random_number}.jpg"))

        # Usamos el número aleatorio
        image = Image.open(image_path)
        self.background_img = ImageTk.PhotoImage(image)  # Mantener la referencia a la imagen
        self.background_label = tk.Label(self.root, image=self.background_img)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Aseguramos que se mantenga

    def configure_grid(self, rows, columns):
        for r in range(rows):
            self.root.grid_rowconfigure(r, weight=1)
        for c in range(columns):
            self.root.grid_columnconfigure(c, weight=1)

    def create_popup_window(self):
        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.withdraw()

    def show_window(self):
        self.popup_window.deiconify()

    def hide_window(self):
        self.popup_window.withdraw()

    def create_button(self, text, command, row, column, columnspan=1, rowspan=1,
                      bg="gray", fg="black", font=("Arial", 12)):
        button = tk.Button(self.root, text=text, command=command, bg=bg, fg=fg, font=font)
        button.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan,
                    sticky="nsew", padx=2, pady=2)

    def create_entry(self, row, column, columnspan=1, rowspan=1, show_text=True):
        entry = tk.Entry(self.root, bg="white", fg="black", font=("Arial", 12))
        if not show_text:
            entry.config(show="*")
        entry.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky="nsew", padx=2, pady=2)
        return entry

    def create_label(self, text, row, column, columnspan=1, rowspan=1,
                     bg="white", fg="black", font=("Arial", 12), anchor="center"):
        label = tk.Label(self.root, text=text, bg=bg, fg=fg, font=font, anchor=anchor)
        label.grid(row=row, column=column, columnspan=columnspan,
                   rowspan=rowspan, sticky="nsew", padx=2, pady=2)


# Crear la instancia de la clase y usar el método
if __name__ == "__main__":
    root = tk.Tk()
    app = Window(root)  # Ahora la clase se llama Window
    root.mainloop()  # Correcta indentación
