# ventanas_multiples.py
import tkinter as tk
from tkinter import BOTH, END, Text, ttk
import json
from tkinter import messagebox
from tkinter import filedialog

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(20))
        self.parent = parent    # guardamos una referencia de la ventana ppal
        parent.title("Recetario de cocina")
        parent.geometry("1500x600+100+100")
        self.grid(sticky=(tk.N, tk.S, tk.E, tk.W))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.resizable(False, False)

        columns = ('nombre_receta', 'tiempo_preparacion', 'tiempo_coccion', 'fecha_creacion', 'editar', 'eliminar')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        # define headings
        self.tree.heading('nombre_receta', text='Nombre')
        self.tree.heading('tiempo_preparacion', text='Tiempo prep.')
        self.tree.heading('tiempo_coccion', text='Tiempo cocc.')
        self.tree.heading('fecha_creacion', text='Fecha')
        self.tree.heading('editar', text='Editar')
        self.tree.heading('eliminar', text='Eliminar')
       
        self.get_elemento_lista()
        
        # vincular la doble clic a la función editar_receta
        self.tree.bind('<Double-Button-1>', self.editar_receta)
        
        # vincular la doble clic a la función editar_receta
        self.tree.bind('<Double-Button-1>', self.eliminar_receta)
        
        self.tree.grid(row=0, column=0, sticky='nsew')

        ttk.Button(self, text="Nueva Receta", command=self.abrir_ventana).grid()
    
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
        values = self.tree.item(self.tree.selection())['values']
        # abrir la ventana para editar la receta
        toplevel = tk.Toplevel(self.parent)
        Editar(toplevel, self, item_id, values).grid()
    
    def eliminar_receta(self, event):
        item_id = self.tree.identify_row(event.y)
        if self.tree.selection():
            # obtener el nombre de la receta seleccionada
            nombre_receta = str(self.tree.item(self.tree.selection())['values'][0])
            with open("recetas.json", 'r') as archivo:
                recetas = json.load(archivo)
                recetas = [receta for receta in recetas if receta["nombre"] != nombre_receta]
                with open("recetas.json", 'w') as archivo:
                    json.dump(recetas, archivo, indent=4)
                # actualizar la tabla
                self.tree.delete(item_id)
                self.get_elemento_lista()
                messagebox.showinfo("Éxito", f"La receta '{nombre_receta}' ha sido eliminada con éxito.")
        else:
            messagebox.showerror("Error", f"No se ha seleccionado ninguna receta para eliminar.")


#class My_treeview(ttk.Treeview):
#    def __init__(self, parent):
#        super().__init__(parent)

class Editar(ttk.Frame):
    def __init__(self, parent, app, item_id, values):
        super().__init__(parent, padding=(20))
        self.parent = parent    # guardamos una referencia de la ventana ppal
        self.app = app          # guardamos una referencia a la clase App
        self.item_id = item_id  # guardamos el ID de la fila a editar
        self.values = values    # guardamos los valores de la fila a editar
        parent.title("Editar receta")
        parent.geometry("400x300+200+200")
        parent.resizable(False, False)

        ttk.Label(self, text="Nombre:").grid(row=0, column=0, sticky='w')
        self.nombre_var = tk.StringVar(value=self.values[0])
        ttk.Entry(self, textvariable=self.nombre_var).grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(self, text="Tiempo de preparación:").grid(row=1, column=0, sticky='w')
        self.tiempo_preparacion_var = tk.StringVar(value=self.values[1])
        ttk.Entry(self, textvariable=self.tiempo_preparacion_var).grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(self, text="Tiempo de cocción:").grid(row=2, column=0, sticky='w')
        self.tiempo_coccion_var = tk.StringVar(value=self.values[2])
        ttk.Entry(self, textvariable=self.tiempo_coccion_var).grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(self, text="Guardar cambios", command=self.guardar_cambios).grid(row=3, column=0, columnspan=2, pady=10)

    def guardar_cambios(self):
        # obtener los nuevos valores
        nombre = self.nombre_var.get()
        tiempo_preparacion = self.tiempo_preparacion_var.get()
        tiempo_coccion = self.tiempo_coccion_var.get()

        # actualizar los valores en la lista
        with open("recetas.json", 'r') as archivo:
            recetas = json.load(archivo)
        # buscar la receta por su nombre y actualizar sus valores
        for receta in recetas:
            if receta['nombre'] == self.item_id:
                receta['nombre'] = nombre
                receta['tiempo_preparacion'] = tiempo_preparacion
                receta['tiempo_coccion'] = tiempo_coccion
                break
        with open("recetas.json", 'w') as archivo:
            json.dump(recetas, archivo)

        # actualizar los valores en el treeview
        self.app.get_elemento_lista()

        # cerrar la ventana
        self.parent.destroy()

class Alta(ttk.Frame):
    def __init__(self, parent, marco):
        super().__init__(parent, padding=(20))
        self.parent = parent
        self.marco = marco
        parent.title("Nueva Receta")
        parent.geometry("500x300+180+100")
        self.grid(sticky=(tk.N, tk.S, tk.E, tk.W))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.resizable(False, False)

        self.nombre_receta = tk.StringVar()
        self.tiempo_preparacion = tk.StringVar()
        self.tiempo_coccion = tk.StringVar()
        self.fecha_creacion = tk.StringVar()
        self.ingredientes = tk.StringVar()
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

        # ttk.Label(self, text="Ingredientes:").grid(row=5, column=1)
        # ttk.Entry(self, textvariable=self.ingredientes).grid(row=5, column=2)

        ttk.Label(self, text="Preparación:").grid(row=6, column=1)
        self.preparacion_text = tk.Text(self, height=5)
        self.preparacion_text.grid(row=6, column=2)

        
        # ttk.Label(self, text="Imagen:").grid(row=7, column=1)
        # ttk.Button(self, text="Seleccionar imagen", command=self.cargar_imagen).grid(row=7, column=2)

        ttk.Button(self, text="Guardar", command=self.guardar_receta).grid(row=10, column=1)
        ttk.Button(self, text="Cerrar", command=parent.destroy).grid(row=10, column=2)
        


    def cargar_imagen(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.imagen = filepath
            print(f"Imagen seleccionada: {self.imagen}")

    def guardar_receta(self):
        recetas = Receta()
        recetas.set_nombre(self.nombre_receta.get())
        recetas.set_tiempo_preparacion(self.tiempo_preparacion.get())
        recetas.set_tiempo_coccion(self.tiempo_coccion.get())
        recetas.set_fecha_creacion(self.fecha_creacion.get())
        recetas.set_ingredientes(self.ingredientes.get())
        # Obtener el contenido del Text
        pasos_str = self.preparacion_text.get("1.0", "end-1c")
        # Convertir el contenido del Text a una lista de python
        pasos_list = [paso.strip() for paso in pasos_str.split('\n') if paso.strip()]
        print(pasos_list)
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
        
        # nombres_recetas = [r['nombre'] for r in recetas]
        # if self.nombre in nombres_recetas:
        #     messagebox.showerror("Error", f"Ya existe una receta con el nombre {self.nombre}")
        #     return False
        
        receta = {}
        receta["nombre"] = self.nombre
        receta["tiempo_preparacion"] = self.tiempo_preparacion
        receta["tiempo_coccion"] = self.tiempo_coccion
        receta["fecha_creacion"] = self.fecha_creacion
        receta["pasos"] = self.pasos
        receta["ingredientes"] = self.ingredientes
        receta["imagenes"] = [self.imagenes]
        recetas.append(receta)
        
        with open("recetas.json", 'w') as archivo:
            json.dump(recetas, archivo)
        return True

class Ingrediente:
    def __init__(self, nombre, unidad_de_medida, cantidad):
        self.nombre = nombre
        self.unidad_de_medida = unidad_de_medida
        self.cantidad = cantidad

root = tk.Tk()
App(root).grid()
root.mainloop()