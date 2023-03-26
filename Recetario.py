# ventanas_multiples.py
import os
import shutil
import tkinter as tk
from tkinter import BOTH, END, Text, ttk
import json
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk


class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(20))
        self.parent = parent    # guardamos una referencia de la ventana ppal
        parent.title("Recetario de cocina")
        parent.geometry("1500x600+100+100")
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.resizable(False, False)

        # Crear un frame para contener los widgets
        self.widget_frame = ttk.Frame(parent, padding=(20))
        self.widget_frame.place(relx=0.5, rely=0.5, anchor="center")

        columns = ('nombre_receta', 'tiempo_preparacion', 'tiempo_coccion', 'fecha_creacion', 'editar', 'eliminar')
        self.tree = ttk.Treeview(self.widget_frame, columns=columns, show='headings')
        # define headings
        self.tree.heading('nombre_receta', text='Nombre')
        self.tree.heading('tiempo_preparacion', text='Tiempo prep.')
        self.tree.heading('tiempo_coccion', text='Tiempo cocc.')
        self.tree.heading('fecha_creacion', text='Fecha')
        
        
        self.tree.heading('editar', text='Editar')
        self.tree.heading('eliminar', text='Eliminar')
        

        self.get_elemento_lista()
        
        #vincular la doble clic a la función editar_receta - DERECHO
        self.tree.bind('<Double-Button-1>', self.editar_receta)

        #vincular la doble clic a la función editar_receta - IZQUIERDO
        self.tree.bind('<Double-Button-3>', self.eliminar_receta)

        self.tree.grid(row=0, column=0, sticky='nsew')

        ttk.Button(self.widget_frame, text="Nueva Receta", command=self.abrir_ventana).grid()

        # Configurar la transparencia del frame
        self.widget_frame.configure(style='Transparent.TFrame')
        self.widget_frame.bind('<Configure>', lambda e: self.widget_frame.configure(style='Transparent.TFrame'))

        # Configurar la transparencia de los widgets
        ttk.Style().configure('Transparent.TFrame', background='rgba(0, 0, 0, 0.0)')
        ttk.Style().configure('Transparent.TLabel', background='rgba(0, 0, 0, 0.0)')
        ttk.Style().configure('Transparent.TButton', background='rgba(0, 0, 0, 0.0)')
    
    def abrir_ventana(self):
        # creamos la ventana Alta
        # como padre indicamos la ventana principal
        toplevel = tk.Toplevel(self.parent)
        # agregamos el frame (Alta) a la ventana (toplevel)
        Alta(toplevel, self).grid()

    def get_elemento_lista(self):
        #add data to the treeview
        self.tree.delete(*self.tree.get_children())
        #leemos los datos
        with open("recetas.json", 'r') as archivo:
            try:
                recetas = json.load(archivo)
            except ValueError:
                recetas = []
        lista_recetas = []
        #generamos los datos
        for receta in recetas:
            lista_recetas.append((receta["nombre"], receta["tiempo_preparacion"], receta["tiempo_coccion"], receta["fecha_creacion"]))
        #add data to the treeview
        for receta in lista_recetas:
            #self.tree.insert('', tk.END, values=receta)
            self.tree.insert('', tk.END, values=receta + ("Editar", "Eliminar",))
            
    def get_elemento_lista2(self):
        # Obtener los nombres de las recetas existentes en el Treeview
        nombres_existentes = set()
        for item in self.tree.get_children():
            nombre = self.tree.item(item)["values"][0]
            nombres_existentes.add(nombre)
            
        # Leer los datos del archivo recetas.json
        with open("recetas.json", 'r') as archivo:
            try:
                recetas = json.load(archivo)
            except ValueError:
                recetas = []
        
        # Agregar nuevas recetas al Treeview si no existen ya
        for receta in recetas:
            nombre = receta["nombre"]
            if nombre not in nombres_existentes:
                self.tree.insert('', tk.END, values=(nombre, receta["tiempo_preparacion"], receta["tiempo_coccion"], receta["fecha_creacion"], "Editar", "Eliminar"))
                nombres_existentes.add(nombre)

    
    def editar_receta(self, event):
        # obtener el nombre de la receta seleccionada
        item_id = self.tree.item(self.tree.selection())['values'][0]
        # obtener los valores de la fila seleccionada
        with open('recetas.json') as f:
            recetas = json.load(f)
        receta_seleccionada = next((r for r in recetas if r['nombre'] == item_id), None)
        # abrir la ventana para editar la receta
        toplevel = tk.Toplevel(self.parent)
        Editar(toplevel, self, item_id, receta_seleccionada).grid()
    
    def eliminar_receta(self, event):
        item_id = self.tree.identify_row(event.y)
        if self.tree.selection():
            # obtener el nombre de la receta seleccionada
            nombre_receta = str(self.tree.item(self.tree.selection())['values'][0])
            with open("recetas.json", 'r') as archivo:
                recetas = json.load(archivo)
                recetas = [receta for receta in recetas if receta["nombre"] != nombre_receta]
                with open("recetas.json", 'w') as archivo:
                    json.dump(recetas, archivo, indent=4, sort_keys=True)
                # actualizar la tabla
                self.tree.delete(item_id)
                self.get_elemento_lista()
                messagebox.showinfo("Éxito", f"La receta '{nombre_receta}' ha sido eliminada con éxito.")
        else:
            messagebox.showerror("Error", f"No se ha seleccionado ninguna receta para eliminar.")

class Editar(ttk.Frame):
    def __init__(self, parent, app, item_id, values):
        super().__init__(parent, padding=(20))
        self.parent = parent    # guardamos una referencia de la ventana ppal
        self.app = app          # guardamos una referencia a la clase App
        self.item_id = item_id  # guardamos el ID de la fila a editar
        self.values = values    # guardamos los valores de la fila a editar
        parent.title("Editar receta")
        parent.geometry("1200x700+200+200")
        parent.resizable(False, False)

        ttk.Label(self, text="Nombre:").grid(row=0, column=0, sticky='w')
        self.nombre_var = tk.StringVar(value=self.values['nombre'])
        ttk.Entry(self, textvariable=self.nombre_var).grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(self, text="Tiempo de preparación:").grid(row=1, column=0, sticky='w')
        self.tiempo_preparacion_var = tk.StringVar(value=self.values['tiempo_preparacion'])
        ttk.Entry(self, textvariable=self.tiempo_preparacion_var).grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(self, text="Tiempo de cocción:").grid(row=2, column=0, sticky='w')
        self.tiempo_coccion_var = tk.StringVar(value=self.values['tiempo_coccion'])
        ttk.Entry(self, textvariable=self.tiempo_coccion_var).grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(self, text="Fecha de creación:").grid(row=3, column=0, sticky='w')
        self.fecha_creacion_var = tk.StringVar(value=self.values['fecha_creacion'])
        ttk.Entry(self, textvariable=self.fecha_creacion_var).grid(row=3, column=1, pady=5, padx=5)
        
        self.preparacion_text = tk.Text(self, height=10, width=50)
        self.preparacion_text.insert('1.0', self.values['pasos'])
        self.preparacion_text.grid(row=4, column=1)
        ttk.Label(self, text="Preparación:").grid(row=4, column=0, sticky='w')
        
        ttk.Label(self, text="Imagen:").grid(row=5, column=0, sticky='w')
        ttk.Button(self, text="Seleccionar imagen", command=self.cargar_imagen).grid(row=5, column=1)
        
        self.image_label = ttk.Label(self)
        self.image_label.grid(row=5, column=5, padx=150, pady=10, sticky='ne')
        image_path = "img/" + self.values['imagenes'][0]
        image = Image.open(image_path)
        image = image.resize((250, 250))
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        self.current_image = photo
        #self.current_image_path = "img/" + self.values['imagenes'][0]


        # self.image_label = ttk.Label(self)
        # self.image_label.grid(row=0, column=3, padx=0, pady=0)
        # image_path = "img/" + self.values['imagenes'][0]
        # image = Image.open(image_path)
        # image = image.resize((300, 300))
        # photo = ImageTk.PhotoImage(image)
        # self.image_label.configure(image=photo)
        # self.image_label.image = photo

        ttk.Button(self, text="Guardar cambios", command=self.guardar_cambios).grid(row=6, column=0, columnspan=2, pady=10)

    def cargar_imagen(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.imagen = os.path.basename(filepath)
            destino = os.path.join('img', self.imagen)
            shutil.copy(filepath, destino)
            image = Image.open(destino)
            image = image.resize((250, 250))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            #self.current_image_path = destino
            
    def guardar_cambios(self):
        # obtener los nuevos valores
        nombre = self.nombre_var.get()
        tiempo_preparacion = self.tiempo_preparacion_var.get()
        tiempo_coccion = self.tiempo_coccion_var.get()
        fecha_creacion  = self.fecha_creacion_var.get()
        preparacion = self.preparacion_text.get('1.0', 'end-1c')
        

        # actualizar los valores en la lista
        with open("recetas.json", 'r') as archivo:
            recetas = json.load(archivo)
        # buscar la receta por su nombre y actualizar sus valores
        for receta in recetas:
            if receta['nombre'] == self.item_id:
                receta['nombre'] = nombre
                receta['tiempo_preparacion'] = tiempo_preparacion
                receta['tiempo_coccion'] = tiempo_coccion
                receta['fecha_creacion'] = fecha_creacion
                receta['pasos'] = preparacion
                # actualizar la imagen si se cambió
                if self.imagen:
                    #self.values['imagenes'][0] = self.imagen
                    # obtener los nombres de las imágenes
                    #nombre_imagen_vieja = self.values['imagenes'][0]
                    nombre_imagen_nueva = self.imagen
                    if receta['imagenes'][0] != nombre_imagen_nueva:
                        receta['imagenes'][0] = nombre_imagen_nueva
                        imagen_vieja = os.path.join('img', receta['imagenes'][0])
                        os.remove(imagen_vieja)
                break
        with open("recetas.json", 'w') as archivo:
            json.dump(recetas, archivo, indent=4, sort_keys=True)

        # actualizar los valores en el treeview
        self.app.get_elemento_lista()

        # cerrar la ventana
        self.parent.destroy()

class AltaIngrdiente(ttk.Frame):
    def __init__(self, parent, marco):
        super().__init__(parent, padding=(20))
        self.parent = parent
        self.marco = marco
        parent.title("Nueve ingrediente")
        parent.geometry("500x300+180+100")
        self.grid(sticky=(tk.N, tk.S, tk.E, tk.W))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.resizable(False, False)

        self.nombre = tk.StringVar()
        self.unidad_de_medida = tk.StringVar()
        self.cantidad = tk.StringVar()

        ttk.Label(self, text="Nombre:").grid(row=1, column=1)
        ttk.Entry(self, textvariable=self.nombre).grid(row=1, column=2)
        #
        ttk.Label(self, text="Unidad de medida:").grid(row=2, column=1)
        ttk.Entry(self, textvariable=self.unidad_de_medida).grid(row=2, column=2)
        
        ttk.Label(self, text="Cantidad:").grid(row=3, column=1)
        ttk.Entry(self, textvariable=self.cantidad).grid(row=3, column=2)

        ttk.Button(self, text="Guardar", command=self.guardar_ingrediente).grid(row=10, column=1)
        ttk.Button(self, text="Cerrar", command=parent.destroy).grid(row=10, column=2)
    
    def guardar_ingrediente(self):
        ingredientes = Ingrediente()
        ingredientes.set_nombre(self.nombre.get())
        ingredientes.set_unidad_de_medida(self.unidad_de_medida.get())
        ingredientes.set_cantidad(self.cantidad.get())
        self.marco.ingredientes.append(ingredientes)
        # Limpiar los campos de los widgets ttk.Entry
        self.nombre.set('')
        self.unidad_de_medida.set('')
        self.cantidad.set('')
        # ingredientes_str = self.ingredientes_text.get("1.0", "end-1c")

        # ingredientes_list = [paso.strip() for paso in ingredientes_str.split('\n') if paso.strip()]
        # print(ingredientes_list)
        # recetas.set_ingredientes(ingredientes_list)
        
        # recetas.guardar()

class Alta(ttk.Frame):
    def __init__(self, parent, marco):
        super().__init__(parent, padding=(20))
        self.parent = parent
        self.marco = marco
        parent.title("Nueva Receta")
        parent.geometry("800x500+180+100")
        self.grid(sticky=(tk.N, tk.S, tk.E, tk.W))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.resizable(False, False)

        self.nombre_receta = tk.StringVar()
        self.tiempo_preparacion = tk.StringVar()
        self.tiempo_coccion = tk.StringVar()
        self.fecha_creacion = tk.StringVar()
        self.ingredientes = []
        self.preparacion = tk.StringVar()
        self.imagen = None  # Atributo para guardar la imagen seleccionada

        ttk.Label(self, text="Nombre:").grid(row=1, column=1)
        ttk.Entry(self, textvariable=self.nombre_receta).grid(row=1, column=2)
        ttk.Label(self, text="Tiempo preparación:").grid(row=2, column=1)
        ttk.Entry(self, textvariable=self.tiempo_preparacion).grid(row=2, column=2)
        ttk.Label(self, text="Tiempo cocción:").grid(row=3, column=1)
        ttk.Entry(self, textvariable=self.tiempo_coccion).grid(row=3, column=2)
        ttk.Label(self, text="Fecha creación:").grid(row=4, column=1)
        ttk.Entry(self, textvariable=self.fecha_creacion).grid(row=4, column=2)

        ttk.Label(self, text="Ingredientes:").grid(row=5, column=1)
        ttk.Button(self, text="Agregar", command=self.abrir_ventana_ingrediente).grid(row=5, column=2)

        ttk.Label(self, text="Preparación:").grid(row=6, column=1)
        self.preparacion_text = tk.Text(self, height=5)
        self.preparacion_text.grid(row=6, column=2)

        
        ttk.Label(self, text="Imagen:").grid(row=7, column=1)
        ttk.Button(self, text="Seleccionar imagen", command=self.cargar_imagen).grid(row=7, column=2)

        ttk.Button(self, text="Guardar", command=self.guardar_receta).grid(row=10, column=1)
        ttk.Button(self, text="Cerrar", command=parent.destroy).grid(row=10, column=2)
   
    def abrir_ventana_ingrediente(self):
        # creamos la ventana Alta
        # como padre indicamos la ventana principal
        toplevel = tk.Toplevel(self.parent)
        # agregamos el frame (Alta) a la ventana (toplevel)
        AltaIngrdiente(toplevel, self).grid()
        
    def cargar_imagen(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.imagen = os.path.basename(filepath)
            destino = os.path.join('img', self.imagen)
            shutil.copy(filepath, destino)

    def guardar_receta(self):
        recetas = Receta()
        recetas.set_nombre(self.nombre_receta.get())
        recetas.set_tiempo_preparacion(self.tiempo_preparacion.get())
        recetas.set_tiempo_coccion(self.tiempo_coccion.get())
        recetas.set_fecha_creacion(self.fecha_creacion.get())
        #recorrer la lista de ingredientes
        ingredientes = []
        for ingrediente in self.ingredientes:
            ingrediente_dict = {"nombre": ingrediente.nombre, "unidad_medida": ingrediente.unidad_de_medida, "cantidad": ingrediente.cantidad}
            ingredientes.append(ingrediente_dict)
        recetas.set_ingredientes(ingredientes)
        # Obtener el contenido del Text
        pasos_str = self.preparacion_text.get("1.0", "end-1c")
        # Convertir el contenido del Text a una lista de python
        pasos_list = [paso.strip() for paso in pasos_str.split('\n') if paso.strip()]
        recetas.set_pasos(pasos_list)
        recetas.set_imagenes(self.imagen)
        
        render = recetas.guardar()
        
        if(render):
            self.marco.get_elemento_lista()
            self.parent.destroy()

class Receta:
    def __init__(self):
        self.nombre = ""
        self.tiempo_preparacion = ""
        self.tiempo_coccion = ""
        self.fecha_creacion = ""
        self.ingredientes = [] # lista de objetos Ingredientes
        self.pasos = [] # lista de cadenas de texto
        self.imagenes = [] # lista de imágenes
    
    def set_nombre(self, nombre):
        self.nombre = nombre
    
    def set_tiempo_preparacion(self, tiempo_preparacion):
        self.tiempo_preparacion = tiempo_preparacion

    def set_tiempo_coccion(self, tiempo_coccion):
        self.tiempo_coccion = tiempo_coccion

    def set_fecha_creacion(self, fecha_creacion):
        self.fecha_creacion = fecha_creacion
        
    def set_pasos(self, pasos):
        self.pasos = pasos
        
    def set_ingredientes(self, ingredientes):
        self.ingredientes = ingredientes
    
    def set_imagenes(self, imagenes):
        self.imagenes = imagenes

    def get_elemento_tupla(self):
        receta = ()
        receta.append(self.nombre)
        receta.append(self.tiempo_preparacion)
        receta.append(self.tiempo_coccion)
        receta.append(self.fecha_creacion)
        return receta
    
    def validar_receta_unica(self, recetas, nombre):
        # Validar que el nombre de la receta sea único
        nombres_recetas = [r['nombre'] for r in recetas]
        if nombre in nombres_recetas:
            messagebox.showerror("Error", f"Ya existe una receta con el nombre {nombre}")
            return False
    
    def guardar(self):
        with open("recetas.json", 'r') as archivo:
            try:
                recetas = json.load(archivo)
            except ValueError:
                recetas = []   
        # Validar que el nombre de la receta sea único
        self.validar_receta_unica(recetas, self.nombre)
        
        receta = {}
        receta["nombre"] = self.nombre
        receta["tiempo_preparacion"] = self.tiempo_preparacion
        receta["tiempo_coccion"] = self.tiempo_coccion
        receta["fecha_creacion"] = self.fecha_creacion
        receta["pasos"] = self.pasos
        receta["ingredientes"] = self.ingredientes
        receta["imagenes"] = [self.imagenes]
        recetas.append(receta)
        
        with open("recetas.json", "w") as archivo:
            json.dump(recetas, archivo, indent=4, sort_keys=True)
        messagebox.showinfo("Éxito", f"La receta '{self.nombre}' ha sido creada con éxito.")
        return True

class Ingrediente:
    def __init__(self):
        self.nombre = ""
        self.unidad_de_medida = ""
        self.cantidad = ""
        
    def set_nombre(self, nombre):
        self.nombre = nombre
    
    def set_unidad_de_medida(self, unidad_de_medida):
        self.unidad_de_medida = unidad_de_medida

    def set_cantidad(self, cantidad):
        self.cantidad = cantidad

root = tk.Tk()
App(root).grid()
root.mainloop()