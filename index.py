import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import simpledialog
import pandas as pd
from encabezados import obtener_vista_previa  # Importar la función
from concatColumnas import usar_una_columna_para_nombre, concatenar_dos_columnas
from seleccionarCols import detectar_columna_telefonos, seleccionar_columnas, detectar_columna_emails

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cargador de Archivos Excel")
        self.root.geometry("700x500")
        
        # Variables
        self.archivo = None  # Ruta del archivo seleccionado
        self.df = None       # DataFrame cargado
        
        # Botón para cargar archivo
        self.cargar_btn = tk.Button(root, text="Cargar Archivo Excel o CSV", command=self.cargar_archivo, width=30)
        self.cargar_btn.pack(pady=20)
        
        # Etiqueta para mostrar el archivo seleccionado
        self.archivo_lbl = tk.Label(root, text="No se ha seleccionado ningún archivo", wraplength=400)
        self.archivo_lbl.pack(pady=10)
        
        # Botón para continuar (deshabilitado hasta que se cargue un archivo)
        self.continuar_btn = tk.Button(root, text="Vista Previa", command=self.preparar_trabajo, state="disabled", width=20)
        self.continuar_btn.pack(pady=10)
        
        self.seleccionar_columnas_btn = tk.Button(
            root, 
            text="Seleccionar Columnas", 
            command=self.seleccionar_columnas_con_checkboxes, 
            state="disabled",  # Se habilita después de cargar un archivo
            width=20
        )
        self.seleccionar_columnas_btn.pack(pady=5)
                
        # Botón para usar una columna como 'name'
        self.usar_una_columna_btn = tk.Button(root, text="Usar Una Columna", command=self.seleccionar_columna_para_nombre,state="disabled", width=20)
        self.usar_una_columna_btn.pack(pady=5)

        # Botón para concatenar dos columnas
        self.concatenar_columnas_btn = tk.Button(root, text="Concatenar Columnas", command=self.concatenar_columnas_para_nombre, state="disabled", width=20)
        self.concatenar_columnas_btn.pack(pady=5)

        # Tabla para mostrar la vista previa
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

    def cargar_archivo(self):
        # Seleccionar archivo
        self.archivo = filedialog.askopenfilename(
            title="Seleccionar Archivo",
            filetypes=[("Archivos Excel y CSV", "*.xlsx *.xls *.csv")]
        )
        if self.archivo:
            self.archivo_lbl.config(text=f"Archivo seleccionado:\n{self.archivo}")
            self.continuar_btn.config(state="normal")  # Habilitar el botón de continuar
            self.usar_una_columna_btn.config(state="normal")  # Botón "Usar Una Columna"
            self.concatenar_columnas_btn.config(state="normal")  # Botón "Concatenar Columnas"
            self.seleccionar_columnas_btn.config(state="normal")  # Botón "Usar Una Columna"

        else:
            self.archivo_lbl.config(text="No se seleccionó ningún archivo.")
    
    def preparar_trabajo(self):
        if self.archivo:
            encabezados, vista_previa = obtener_vista_previa(self.archivo)
            if vista_previa is not None:
                if encabezados:
                    messagebox.showinfo("Encabezados Detectados", "Se detectaron encabezados automáticamente.")
                else:
                    messagebox.showinfo("Encabezados Asignados", "No se detectaron encabezados claros. Se asignaron nombres genéricos.")
                
                # Asignar los datos cargados a self.df
                self.df = vista_previa.copy()
                self.mostrar_vista_previa(vista_previa)
            else:
                messagebox.showerror("Error", "No se pudo procesar el archivo.")
        else:
            messagebox.showwarning("Advertencia", "No hay archivo cargado.")
    
    def mostrar_vista_previa(self, df):
        # Limpiar cualquier contenido previo en la tabla
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        
        # Configurar encabezados
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        
        # Agregar filas
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def actualizar_vista_previa(self):
        if self.df is not None:
            self.mostrar_vista_previa(self.df)
        else:
            messagebox.showerror("Error", "No se pudo actualizar la vista previa porque no hay datos cargados.")

    def seleccionar_columna_para_nombre(self):
        if self.df is not None:
            # Obtener lista de columnas
            columnas = list(self.df.columns)
            
            # Crear una ventana para que el usuario seleccione una columna
            columna = self.seleccionar_opcion("Selecciona una columna para 'name':", columnas)
            
            if columna:
                # Llamar a la función para usar una columna
                self.df = usar_una_columna_para_nombre(self.df, columna)
                self.actualizar_vista_previa()
        else:
            messagebox.showerror("Error", "No hay datos cargados.")

    def concatenar_columnas_para_nombre(self):
        if self.df is not None:
            # Obtener lista de columnas
            columnas = list(self.df.columns)
            
            # Crear ventanas para seleccionar las dos columnas
            columna1 = self.seleccionar_opcion("Selecciona la primera columna:", columnas)
            columna2 = self.seleccionar_opcion("Selecciona la segunda columna:", columnas)
            
            if columna1 and columna2:
                # Llamar a la función para concatenar columnas
                self.df = concatenar_dos_columnas(self.df, columna1, columna2)
                
                # Eliminar únicamente las columnas seleccionadas
                self.df.drop(columns=[columna1, columna2], inplace=True)
                
                # Actualizar la vista previa
                self.actualizar_vista_previa()
                
                # Mensaje informativo
                messagebox.showinfo("Éxito", f"Las columnas '{columna1}' y '{columna2}' fueron concatenadas y eliminadas. La nueva columna 'name' ha sido añadida.")
        else:
            messagebox.showerror("Error", "No hay datos cargados.")

    def seleccionar_opcion(self, mensaje, opciones):
        """
        Abre una ventana emergente para que el usuario seleccione una opción de una lista de opciones.
        :param mensaje: Mensaje para mostrar en la ventana.
        :param opciones: Lista de opciones disponibles.
        :return: Opción seleccionada o None si el usuario cancela.
        """
        ventana = tk.Toplevel(self.root)  # Crear una nueva ventana emergente
        ventana.title("Seleccionar Opción")
        ventana.geometry("300x150")
        
        # Etiqueta con el mensaje
        etiqueta = tk.Label(ventana, text=mensaje, wraplength=250)
        etiqueta.pack(pady=10)
        
        # Combobox con las opciones
        seleccion = tk.StringVar()
        combo = ttk.Combobox(ventana, textvariable=seleccion, values=opciones, state="readonly")
        combo.pack(pady=10)
        combo.set(opciones[0])  # Seleccionar la primera opción por defecto
        
        # Variable para guardar la selección
        seleccion_confirmada = {"opcion": None}

        # Botón para confirmar la selección
        def confirmar():
            seleccion_confirmada["opcion"] = combo.get()
            ventana.destroy()  # Cerrar la ventana

        boton_confirmar = tk.Button(ventana, text="Confirmar", command=confirmar)
        boton_confirmar.pack(pady=10)
        
        # Esperar a que se cierre la ventana antes de continuar
        ventana.transient(self.root)
        ventana.grab_set()
        self.root.wait_window(ventana)
        
        return seleccion_confirmada["opcion"]
    
    def seleccionar_columnas_con_checkboxes(self):
        if self.df is not None:
            # Crear una ventana emergente
            ventana_seleccion = tk.Toplevel(self.root)
            ventana_seleccion.title("Seleccionar Columnas")
            ventana_seleccion.geometry("300x400")
            
            # Frame contenedor con canvas y scrollbar
            frame_scroll = tk.Frame(ventana_seleccion)
            frame_scroll.pack(fill=tk.BOTH, expand=True)
            
            canvas = tk.Canvas(frame_scroll)
            scrollbar = tk.Scrollbar(frame_scroll, orient=tk.VERTICAL, command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar y canvas
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Frame interno para checkboxes
            frame_checkboxes = tk.Frame(canvas)
            canvas.create_window((0, 0), window=frame_checkboxes, anchor="nw")
            
            # Lista de variables para checkboxes
            variables_checkboxes = {}
            for columna in self.df.columns:
                var = tk.BooleanVar(value=True)  # Por defecto, todas seleccionadas
                chk = tk.Checkbutton(frame_checkboxes, text=columna, variable=var)
                chk.pack(anchor="w", padx=10, pady=5)
                variables_checkboxes[columna] = var
            
            # Ajustar la región del canvas al contenido del frame interno
            def actualizar_scrollregion(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            frame_checkboxes.bind("<Configure>", actualizar_scrollregion)
            
            # Botón para confirmar la selección
            def confirmar_seleccion():
                # Obtener las columnas seleccionadas
                columnas_seleccionadas = [col for col, var in variables_checkboxes.items() if var.get()]
                if not columnas_seleccionadas:
                    messagebox.showerror("Error", "Debe seleccionar al menos una columna.")
                    return
                
                # Aplicar la selección: eliminar las columnas no seleccionadas
                self.df = seleccionar_columnas(self.df, columnas_seleccionadas)
                if self.df is not None:
                    # Detectar y renombrar la columna de teléfonos
                    self.df = detectar_columna_telefonos(self.df)
                    # Detectar y renombrar la columna de correos electrónicos
                    self.df = detectar_columna_emails(self.df)
                    
                    # Crear columnas faltantes si no existen
                    if 'phone' not in self.df.columns:
                        self.df['phone'] = "No hay telefono"
                    if 'email' not in self.df.columns:
                        self.df['email'] = "No hay email"
                    
                    # Reorganizar las columnas en el orden deseado
                    columnas_deseadas = ['name', 'phone', 'email']
                    columnas_restantes = [col for col in self.df.columns if col not in columnas_deseadas]
                    columnas_reorganizadas = columnas_deseadas + columnas_restantes
                    self.df = self.df[[col for col in columnas_reorganizadas if col in self.df.columns]]
                    
                    # Cerrar la ventana de selección
                    ventana_seleccion.destroy()
                    
                    # Actualizar la vista previa en la interfaz
                    self.actualizar_vista_previa()
                else:
                    messagebox.showerror("Error", "No se pudo seleccionar las columnas.")
            
            # Botón para confirmar selección
            btn_confirmar = tk.Button(ventana_seleccion, text="Confirmar", command=confirmar_seleccion)
            btn_confirmar.pack(pady=10)
        else:
            messagebox.showerror("Error", "No hay datos cargados.")

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
