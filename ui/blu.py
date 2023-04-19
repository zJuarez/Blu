import tkinter as tk
from PIL import Image, ImageTk

class BluUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blu UI")
        self.create_icons()
        self.create_frames()
        self.create_widgets()
    
    # Define a function to minimize the application
    def minimize_app(self):
        root.iconify()

    # Define a function to close the application
    def close_app(self):
        root.destroy()

    def create_header(self):
        # Create a Frame to hold the custom buttons
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # Crear los botones de CERRAR y MINIMIZAR
        close_button = tk.Button(button_frame, image=self.close_icon, command=self.close_app)
        close_button.pack(side=tk.RIGHT)

        minimize_button = tk.Button(button_frame, image=self.minimize_icon, command=self.minimize_app)
        minimize_button.pack(side=tk.RIGHT)

    def create_widgets(self):
        # Create a Frame to hold the custom buttons
        # create_header()

        """Crea los widgets para la interfaz de usuario."""
        # Frame para el canvas
        self.canvas_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        width = root.winfo_screenwidth() 
        height = root.winfo_screenheight() 

        canvas_width = width * 13/23
        canvas_height = height * 10/13

        # Crear encabezado del canvas con botón de borrar
        canvas_header = tk.Frame(self.canvas_frame, padx=10, pady=5)
        canvas_header.pack(side="top", fill="x")
        canvas_header_label = tk.Label(canvas_header, text="Canvas (" + str(int(canvas_width)) + "x" + str(int(canvas_height)) + ")", font=("Arial", 12, "bold"))
        canvas_header_label.pack(side="top")

        clear_button = tk.Button(canvas_header, image=self.clear_icon, command=self.clear_canvas)
        clear_button.image = self.clear_icon
        clear_button.pack(side="bottom")

        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Frame para el cuadro de texto de código y el cuadro de texto de resultados
        self.text_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Crear encabezado del cuadro de texto del código con botón de compilar
        code_header = tk.Frame(self.text_frame, padx=10, pady=5)
        code_header.pack(side="top", fill="x")
        code_header_label = tk.Label(code_header, text="Código", font=("Arial", 12, "bold"))
        code_header_label.pack(side="top")

        compile_button = tk.Button(code_header, image=self.compile_icon, command=self.compile_code)
        compile_button.image = self.compile_icon
        compile_button.pack(side="bottom")

        # Cuadro de texto de código
        self.code_text = tk.Text(self.text_frame, bg="white")
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Header para el cuadro de texto de resultados
        self.result_header = tk.Label(self.text_frame, text="Results", font=("Arial", 12, "bold"))
        self.result_header.pack(padx=10, pady=10)

        # Cuadro de texto de resultados
        self.result_text = tk.Text(self.text_frame, bg="white")
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def create_frames(self):
        """Crea los marcos para los widgets."""
        self.canvas_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.text_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)

    def create_icons(self):
        """Crea los iconos para los botones."""
        self.clear_image = Image.open("ui/clear.png")
        self.clear_image = self.clear_image.resize((24, 24), Image.ANTIALIAS)
        self.clear_icon = ImageTk.PhotoImage(self.clear_image)

        self.compile_image = Image.open("ui/compile.png")
        self.compile_image = self.compile_image.resize((24, 24), Image.ANTIALIAS)
        self.compile_icon = ImageTk.PhotoImage(self.compile_image)

        self.minimize_icon = Image.open("ui/minimize.png")
        self.minimize_icon = self.minimize_icon.resize((24, 24), Image.ANTIALIAS)
        self.minimize_icon = ImageTk.PhotoImage(self.minimize_icon)

        self.close_icon = Image.open("ui/close.png")
        self.close_icon = self.close_icon.resize((24, 24), Image.ANTIALIAS)
        self.close_icon = ImageTk.PhotoImage(self.close_icon)

    def clear_canvas(self):
        self.canvas.delete("all")

    def clear_code(self):
        self.code_text.delete("1.0", "end")

    def compile_code(self):
        # TODO: Implement code compilation
        pass


if __name__ == "__main__":
    root = tk.Tk()
    blu_editor = BluUI(root)
    # Make the window take up the full screen
    root.state("zoomed")
    root.config(padx=30, pady=30, bg="")
    root.configure(bg="#A9CBD9")
    root.mainloop()