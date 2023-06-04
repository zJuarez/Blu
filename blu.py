import sys
import tkinter as tk
from PIL import Image, ImageTk
from MaquinaVirtual import MaquinaVirtual
from myparser import MyParser
from console import console

class BluUI:
    def __init__(self, root, data):
        self.root = root
        self.root.title("Blu UI")
        self.create_icons()
        self.create_frames()
        dim = self.create_widgets()
        self.width = dim[0]
        self.height = dim[1]
        self.my_parser = MyParser(dim[0], dim[1], self.canvas)
        self.data = data
        self.input = None
        self.start = 0
        self.mv = None
        self.read = None

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

    def get_dims(self):
        return (self.width, self.height)

    def create_widgets(self):
        # Create a Frame to hold the custom buttons
        # create_header()

        """Crea los widgets para la interfaz de usuario."""
        # Frame para el canvas
        self.canvas_frame = tk.Frame(self.root, bd=0, relief=tk.SUNKEN)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        width = root.winfo_screenwidth() 
        height = root.winfo_screenheight() 

        canvas_width = width * 13/23
        canvas_height = height * 9/13

        # Crear encabezado del canvas con botón de borrar
        canvas_header = tk.Frame(self.canvas_frame, padx=10, pady=5, bg="#F2F2F2")
        canvas_header.pack(side="top", fill="x")

        canvas_header_label = tk.Label(canvas_header, text="Canvas " + str(int(canvas_width)) + "x" + str(int(canvas_height)), font=("Calibri", 14, "bold"))
        canvas_header_label.pack(side="left", anchor="center")

        clear_button = tk.Button(canvas_header, image=self.clear_icon, command=self.clear_canvas, bd=0, bg="#F2F2F2", activebackground="#F2F2F2")
        clear_button.image = self.clear_icon
        clear_button.pack(side="right", padx=(0, 10), pady=5)

        # Configure the compound option to display both text and image
        clear_button.config(compound=tk.LEFT)


        # Canvas
        self.canvas = tk.Canvas(self.canvas_frame, width=canvas_width, height=canvas_height, bd=0, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.margin_frame_h = tk.Frame(self.root, width = width *1/23, height = height, bg= "#A9CBD9")
        self.margin_frame_h.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame para el cuadro de texto de código y el cuadro de texto de resultados
        self.text_frame = tk.Frame(self.root, bd=0, relief=tk.RAISED, bg="#AFABAB")
        self.text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Crear encabezado del cuadro de texto del código con botón de compilar
        code_header = tk.Frame(self.text_frame, padx=10, pady=5, bg="#AFABAB")
        code_header.pack(side="top", fill=tk.BOTH)

        compile_button = tk.Label(code_header, image=self.compile_icon , bg="#AFABAB")
        compile_button.image = self.compile_icon
        compile_button.pack(side="right")
        compile_button.bind("<Button-1>", lambda event: self.compile_code(canvas_width, canvas_height))
        compile_button.bind("<Enter>", lambda event: compile_button.config(cursor="hand2"))
        compile_button.bind("<Leave>", lambda event: compile_button.config(cursor=""))
        

        # Cuadro de texto de código
        self.code_text_frame = tk.Frame(self.text_frame, bd=0, padx=10, pady=10, height = height*6/13, bg="#D0CECE")
        self.code_text_frame.pack(fill = tk.X)
        self.code_text_frame.pack_propagate(False)  # Disable automatic resizing of the

        self.code_text = tk.Text(self.code_text_frame, bd=0, bg="#D0CECE")
        self.code_text.pack()
        self.code_text.configure(font = ("Consolas", 16))
        self.code_text_frame.pack_propagate(False)  # Disable automatic resizing of the
        self.code_text.insert("1.0", data)

        self.margin_frame_v = tk.Frame(self.text_frame, height = height*0.6/13, bg= "#A9CBD9")
        self.margin_frame_v.pack(fill=tk.X, expand=True)

        # Header para el cuadro de texto de resultados
        self.result_header = tk.Label(self.text_frame, text=" ", font=("Arial", 16, "bold"), bg="#AFABAB")
        self.result_header.pack(padx=10, pady=5)

        def process_input(event):
            user_input = self.result_text.get("end-1c linestart", "end-1c lineend")
            try:
                self.mv.read_add(self.read[1], self.read[2], user_input)
            except Exception as e:
                logs = e
                self.canvas.delete("all")
                self.result_text.insert(self.result_text.index("end"), logs)
            # print("User input:", user_input)
            self.compile_code_rest(canvas_width, canvas_height, self.read[3])

        # Cuadro de texto de resultados
        self.result_text = tk.Text(self.text_frame, bd=0, bg="#D0CECE")
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.configure(font = ("Consolas", 13))
        self.result_text.bind("<Return>", process_input)
        return (canvas_width, canvas_height)
    
    

    def create_frames(self):
        """Crea los marcos para los widgets."""
        self.canvas_frame = tk.Frame(self.root, bd=0, relief=tk.SUNKEN, bg = "#F2F2F2")
        self.text_frame = tk.Frame(self.root, bd=0, relief=tk.SUNKEN)

    def create_icons(self):
        """Crea los iconos para los botones."""
        self.clear_image = Image.open("ui/clear.png")
        self.clear_image = self.clear_image.resize((24, 24), Image.LANCZOS)
        self.clear_icon = ImageTk.PhotoImage(self.clear_image)

        self.compile_image = Image.open("ui/compile.png")
        self.compile_image = self.compile_image.resize((24, 24), Image.LANCZOS)
        self.compile_icon = ImageTk.PhotoImage(self.compile_image)

        self.minimize_icon = Image.open("ui/minimize.png")
        self.minimize_icon = self.minimize_icon.resize((24, 24), Image.LANCZOS)
        self.minimize_icon = ImageTk.PhotoImage(self.minimize_icon)

        self.close_icon = Image.open("ui/close.png")
        self.close_icon = self.close_icon.resize((24, 24), Image.LANCZOS)
        self.close_icon = ImageTk.PhotoImage(self.close_icon)

    def clear_canvas(self):
        self.canvas.delete("all")

    def clear_code(self):
        self.code_text.delete("1.0", "end")

    def compile_code_rest(self,cw,ch, pc):
        read = "" 
        try :
            read = self.mv.execute(start=pc)
            if isinstance(read, tuple):
                    self.read = read
        except Exception as e:
            self.result_text.insert(self.result_text.index("end"), e)
            self.canvas.delete("all")

    def compile_code(self, cw, ch):
        code = self.code_text.get("1.0", "end")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0",console)
        self.result_text.configure(state="normal")
        parser = self.my_parser.parse(code)

        if parser[0] == "ERROR":
            self.result_text.insert(self.result_text.index("end"), parser[1])
        else:
            self.mv = MaquinaVirtual(parser[0], parser[1], parser[2], self.width, self.height, self.canvas, self.result_text)
            read = ""        
            try :
                read = self.mv.execute()
                # read
                if isinstance(read, tuple):
                        self.read = read
            except Exception as e:
                self.result_text.insert(self.result_text.index("end"), e)
                self.canvas.delete("all")


if __name__ == "__main__":
    root = tk.Tk()
    files = sys.argv[1:] if len(sys.argv) > 1 else ["square.blu"]
    data = ''' PRINT "HELLO WORLD"'''
    for fileName in files:
        with open("examples/" + fileName) as file:
            data = file.read()
    blu_editor = BluUI(root, data)
    # Make the window take up the full screen
    root.state("zoomed")
    w = blu_editor.get_dims()[0]
    h = blu_editor.get_dims()[1]
    root.config(padx=w/23, pady=h/13, bg="")
    root.configure(bg="#A9CBD9")


    root.mainloop()