import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import simpledialog
import pandas as pd
import sys
import os
import requests
import json
from encabezados import obtener_vista_previa  # Importar la función
from concatColumnas import usar_una_columna_para_nombre, concatenar_dos_columnas
from seleccionarCols import detectar_columna_telefonos, seleccionar_columnas, detectar_columna_emails

# Verificar si se ejecuta en modo headless
HEADLESS_MODE = '--headless' in sys.argv or os.getenv('CLEANING_HEADLESS') == '1'

# Verificar si se pasó un archivo como argumento
archivo_precargado = None
for arg in sys.argv[1:]:
    if arg != '--headless' and not arg.startswith('-'):
        archivo_precargado = arg
        break

if archivo_precargado:
    print(f"📂 Archivo precargado: {archivo_precargado}")

def ejecutar_headless():
    """Ejecutar en modo headless (sin GUI) para servidores"""
    print("🖥️ Ejecutando en modo headless (sin GUI)")
    
    if archivo_precargado and os.path.exists(archivo_precargado):
        print(f"📊 Procesando archivo: {archivo_precargado}")
        try:
            # Procesar archivo sin GUI
            encabezados, vista_previa = obtener_vista_previa(archivo_precargado)
            if vista_previa is not None:
                print(f"✅ Archivo procesado correctamente. Filas: {len(vista_previa)}, Columnas: {len(vista_previa.columns)}")
                
                # Detectar columnas automáticamente
                phone_col = detectar_columna_telefonos(vista_previa)
                email_col = detectar_columna_emails(vista_previa)
                
                if phone_col:
                    print(f"📞 Columna detectada para teléfonos: {phone_col}")
                if email_col:
                    print(f"📧 Columna detectada para correos electrónicos: {email_col}")
                
                print("✅ Procesamiento headless completado")
                return 0
            else:
                print("❌ Error al procesar el archivo")
                return 1
        except Exception as e:
            print(f"❌ Error en modo headless: {e}")
            return 1
    else:
        print("ℹ️ Modo headless iniciado, esperando archivos para procesar...")
        print("💡 Para procesar un archivo, reinicie con: python index.py --headless ruta/al/archivo.xlsx")
        return 0

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cargador de Archivos Excel")
        self.root.geometry("700x500")
        
        # Variables
        self.archivo = archivo_precargado  # Ruta del archivo precargado
        self.df_completo = None       # DataFrame completo con todos los datos
        self.df = None       # DataFrame para vista previa (primeras filas)

        # Crear primero toda la interfaz antes de cargar el archivo precargado
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

        # Nuevo botón para subir datos a la base de datos
        self.subir_bd_btn = tk.Button(root, text="📤 Subir a Base de Datos", command=self.subir_a_base_datos, state="disabled", width=25, bg="#28a745", fg="white", font=("Arial", 10, "bold"))
        self.subir_bd_btn.pack(pady=10)

        # Tabla para mostrar la vista previa
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        # AHORA sí cargar el archivo precargado (después de crear toda la interfaz)
        if self.archivo:
            self.cargar_archivo_precargado()

    def cargar_archivo(self):
        # Seleccionar archivo
        self.archivo = filedialog.askopenfilename(
            title="Seleccionar Archivo",
            filetypes=[("Archivos Excel y CSV", "*.xlsx *.xls *.csv")]
        )
        if self.archivo:
            self.archivo_lbl.config(text=f"Archivo seleccionado: {os.path.basename(self.archivo)}")
            self.continuar_btn.config(state="normal")  # Habilitar el botón de continuar
            self.usar_una_columna_btn.config(state="normal")  # Botón "Usar Una Columna"
            self.concatenar_columnas_btn.config(state="normal")  # Botón "Concatenar Columnas"
            self.seleccionar_columnas_btn.config(state="normal")  # Botón "Usar Una Columna"
            self.subir_bd_btn.config(state="normal")  # Habilitar botón de subir a BD

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
                
                # Cargar el archivo completo (no solo vista previa)
                if self.archivo.endswith(".csv"):
                    df_completo = pd.read_csv(self.archivo)
                else:
                    df_completo = pd.read_excel(self.archivo)
                
                # Si no había encabezados detectados, usar nombres genéricos
                if not encabezados:
                    df_completo.columns = [f"Column{i}" for i in range(1, len(df_completo.columns) + 1)]
                
                # Almacenar el DataFrame completo
                self.df_completo = df_completo.copy()
                
                # Reorganizar columnas automáticamente
                self.df_completo = self.reorganizar_columnas_bd(self.df_completo)
                
                # Para la vista previa, usar solo las primeras filas
                self.df = self.df_completo.head()
                self.mostrar_vista_previa(self.df)
                
                # Actualizar título con el número total de registros
                self.root.title(f"Cargador de Archivos Excel - {os.path.basename(self.archivo)} ({len(self.df_completo)} registros)")
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
        if self.df_completo is not None:
            # Actualizar la vista previa con las primeras filas del DataFrame completo
            self.df = self.df_completo.head()
            self.mostrar_vista_previa(self.df)
            # Actualizar título con el número total de registros
            self.root.title(f"Cargador de Archivos Excel - {os.path.basename(self.archivo)} ({len(self.df_completo)} registros)")
        else:
            messagebox.showerror("Error", "No se pudo actualizar la vista previa porque no hay datos cargados.")

    def seleccionar_columna_para_nombre(self):
        if self.df_completo is not None:
            # Obtener lista de columnas
            columnas = list(self.df_completo.columns)
            
            # Crear una ventana para que el usuario seleccione una columna
            columna = self.seleccionar_opcion("Selecciona una columna para 'name':", columnas)
            
            if columna:
                # Llamar a la función para usar una columna
                self.df_completo = usar_una_columna_para_nombre(self.df_completo, columna)
                
                # Reorganizar columnas automáticamente
                self.df_completo = self.reorganizar_columnas_bd(self.df_completo)
                
                self.actualizar_vista_previa()
        else:
            messagebox.showerror("Error", "No hay datos cargados.")

    def concatenar_columnas_para_nombre(self):
        if self.df_completo is not None:
            # Obtener lista de columnas
            columnas = list(self.df_completo.columns)
            
            # Crear ventanas para seleccionar las dos columnas
            columna1 = self.seleccionar_opcion("Selecciona la primera columna:", columnas)
            columna2 = self.seleccionar_opcion("Selecciona la segunda columna:", columnas)
            
            if columna1 and columna2:
                # Llamar a la función para concatenar columnas
                self.df_completo = concatenar_dos_columnas(self.df_completo, columna1, columna2)
                
                # Eliminar únicamente las columnas seleccionadas
                self.df_completo.drop(columns=[columna1, columna2], inplace=True)
                
                # Reorganizar columnas automáticamente
                self.df_completo = self.reorganizar_columnas_bd(self.df_completo)
                
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
        if self.df_completo is not None:
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
            for columna in self.df_completo.columns:
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
                self.df_completo = seleccionar_columnas(self.df_completo, columnas_seleccionadas)
                if self.df_completo is not None:
                    # Detectar y renombrar la columna de teléfonos
                    self.df_completo = detectar_columna_telefonos(self.df_completo)
                    # Detectar y renombrar la columna de correos electrónicos
                    self.df_completo = detectar_columna_emails(self.df_completo)
                    
                    # Reorganizar columnas automáticamente
                    self.df_completo = self.reorganizar_columnas_bd(self.df_completo)
                    
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

    def cargar_archivo_precargado(self):
        """Carga automáticamente el archivo precargado y prepara la interfaz"""
        try:
            print(f"🔄 Cargando archivo precargado: {self.archivo}")
            self.archivo_lbl.config(text=f"Archivo precargado: {os.path.basename(self.archivo)}")
            
            # Cargar y procesar el archivo COMPLETO
            encabezados, vista_previa = obtener_vista_previa(self.archivo)
            if vista_previa is not None:
                # Cargar el archivo completo (no solo vista previa)
                if self.archivo.endswith(".csv"):
                    df_completo = pd.read_csv(self.archivo)
                else:
                    df_completo = pd.read_excel(self.archivo)
                
                # Si no había encabezados detectados, usar nombres genéricos
                if not encabezados:
                    df_completo.columns = [f"Column{i}" for i in range(1, len(df_completo.columns) + 1)]
                
                # Almacenar el DataFrame completo
                self.df_completo = df_completo.copy()
                
                # Detectar automáticamente columnas de teléfonos y emails en el DataFrame completo
                self.df_completo = detectar_columna_telefonos(self.df_completo)
                self.df_completo = detectar_columna_emails(self.df_completo)
                
                # Reorganizar columnas automáticamente
                self.df_completo = self.reorganizar_columnas_bd(self.df_completo)
                
                # Para la vista previa, usar solo las primeras filas
                self.df = self.df_completo.head()
                
                # Mostrar vista previa
                self.mostrar_vista_previa(self.df)
                
                # Habilitar todos los botones para trabajar con los datos
                self.continuar_btn.config(state="normal")
                self.seleccionar_columnas_btn.config(state="normal")
                self.usar_una_columna_btn.config(state="normal")
                self.concatenar_columnas_btn.config(state="normal")
                self.subir_bd_btn.config(state="normal")  # Habilitar botón de subir a BD
                
                print(f"✅ Archivo precargado cargado correctamente.")
                print(f"📊 Total de filas: {len(self.df_completo)}, Columnas: {len(self.df_completo.columns)}")
                print(f"📋 Columnas disponibles: {list(self.df_completo.columns)}")
                
                # Actualizar el título de la ventana para mostrar el archivo y total de registros
                self.root.title(f"Cargador de Archivos Excel - {os.path.basename(self.archivo)} ({len(self.df_completo)} registros)")
                
            else:
                print("❌ Error al cargar el archivo precargado.")
                self.archivo_lbl.config(text="❌ Error al cargar el archivo precargado")
                
        except Exception as e:
            print(f"❌ Error al cargar archivo precargado: {e}")
            self.archivo_lbl.config(text=f"❌ Error: {str(e)}")

    def reorganizar_columnas_bd(self, df):
        """
        Reorganiza las columnas del DataFrame en el orden requerido para la base de datos:
        1. name (obligatoria)
        2. email 
        3. phone (obligatoria)
        4. Otras columnas restantes
        """
        try:
            # Definir el orden prioritario de columnas
            orden_prioritario = ['name', 'email', 'phone']
            
            # Obtener columnas actuales
            columnas_actuales = list(df.columns)
            
            # Crear lista de columnas en el orden correcto
            columnas_ordenadas = []
            
            # Agregar columnas prioritarias si existen
            for col in orden_prioritario:
                if col in columnas_actuales:
                    columnas_ordenadas.append(col)
            
            # Agregar las demás columnas
            for col in columnas_actuales:
                if col not in orden_prioritario:
                    columnas_ordenadas.append(col)
            
            # Reorganizar el DataFrame
            df_reorganizado = df[columnas_ordenadas]
            
            print(f"📋 Columnas reorganizadas: {list(df_reorganizado.columns)}")
            return df_reorganizado
            
        except Exception as e:
            print(f"❌ Error al reorganizar columnas: {e}")
            return df

    def organizar_para_bd(self, df):
        """
        Organiza el DataFrame según el esquema de la base de datos:
        Columnas requeridas: name, email, phone, status, notes, seccion
        """
        try:
            df_organizado = pd.DataFrame()
            
            # 1. Columna 'name' (obligatoria)
            if 'name' in df.columns:
                df_organizado['name'] = df['name']
            else:
                # Si no hay columna name, intentar crear una de otras columnas disponibles
                posibles_names = [col for col in df.columns if any(word in col.lower() for word in ['name', 'nombre', 'full', 'complete'])]
                if posibles_names:
                    df_organizado['name'] = df[posibles_names[0]]
                else:
                    df_organizado['name'] = 'Nombre no especificado'
            
            # 2. Columna 'email' 
            df_organizado['email'] = df['email'] if 'email' in df.columns else 'No hay email'
            
            # 3. Columna 'phone' (obligatoria para identificar duplicados)
            if 'phone' in df.columns:
                df_organizado['phone'] = df['phone']
            else:
                raise ValueError("❌ No se encontró columna 'phone'. Esta columna es obligatoria.")
            
            # 4. Columna 'status' (por defecto será 'nuevo')
            df_organizado['status'] = 'nuevo'
            
            # 5. Columna 'notes' (combinar información extra si existe)
            notas_cols = [col for col in df.columns if col not in ['name', 'email', 'phone']]
            if notas_cols:
                # Combinar columnas extra como notas
                notas_parts = []
                for col in notas_cols[:3]:  # Limitar a 3 columnas extras para evitar notas muy largas
                    if not df[col].isna().all():  # Solo si la columna tiene datos
                        notas_parts.append(f"{col}: " + df[col].astype(str))
                
                if notas_parts:
                    df_organizado['notes'] = '; '.join(notas_parts)
                else:
                    df_organizado['notes'] = 'Datos importados desde Excel'
            else:
                df_organizado['notes'] = 'Datos importados desde Excel'
            
            # 6. Columna 'seccion' (por defecto será 1, después se puede dividir)
            df_organizado['seccion'] = 1
            
            # Limpiar datos
            df_organizado = df_organizado.dropna(subset=['phone'])  # Eliminar registros sin teléfono
            df_organizado = df_organizado[df_organizado['phone'] != '']  # Eliminar teléfonos vacíos
            
            print(f"✅ Datos organizados para BD: {len(df_organizado)} registros")
            print(f"📋 Columnas finales: {list(df_organizado.columns)}")
            
            return df_organizado
            
        except Exception as e:
            print(f"❌ Error al organizar datos: {e}")
            return None
    
    def subir_a_base_datos(self):
        """
        Organiza los datos actuales y los sube a la base de datos
        """
        if self.df_completo is None:
            messagebox.showerror("Error", "No hay datos cargados para subir.")
            return
        
        try:
            # Organizar datos según esquema de BD
            df_organizado = self.organizar_para_bd(self.df_completo.copy())
            
            if df_organizado is None or len(df_organizado) == 0:
                messagebox.showerror("Error", "No se pudieron organizar los datos o no hay registros válidos.")
                return
            
            # Mostrar resumen antes de subir
            respuesta = messagebox.askyesno(
                "Confirmar subida", 
                f"¿Estás seguro de subir {len(df_organizado)} registros a la base de datos?\n\n"
                f"Columnas: {', '.join(df_organizado.columns)}\n"
                f"Primeros teléfonos: {', '.join(df_organizado['phone'].head(3).tolist())}"
            )
            
            if not respuesta:
                return
            
            # Convertir DataFrame a lista de diccionarios con limpieza de tipos
            registros_raw = df_organizado.to_dict('records')
            
            # Limpiar y validar cada registro - SOLO name, email, phone
            registros = []
            for i, record in enumerate(registros_raw):
                try:
                    # SOLO los 3 campos filtrados que quieres
                    clean_record = {
                        'name': str(record.get('name', '')).strip(),
                        'email': str(record.get('email', '')).strip(),
                        'phone': str(record.get('phone', '')).strip()
                    }
                    
                    # Validar que el teléfono tenga exactamente 10 dígitos
                    if not clean_record['phone'] or not clean_record['phone'].isdigit() or len(clean_record['phone']) != 10:
                        print(f"⚠️ Registro {i+1} omitido - teléfono inválido: '{clean_record['phone']}'")
                        continue
                    
                    # Validar que tenga nombre
                    if not clean_record['name']:
                        print(f"⚠️ Registro {i+1} omitido - sin nombre")
                        continue
                    
                    registros.append(clean_record)
                    
                except Exception as e:
                    print(f"⚠️ Error al procesar registro {i+1}: {e}")
                    continue
            
            if len(registros) == 0:
                messagebox.showerror("Error", "No hay registros válidos para subir después de la validación.")
                return
            
            print(f"📋 Registros válidos después de limpieza: {len(registros)} de {len(registros_raw)}")
            
            # Mostrar muestra de los primeros registros para debug
            if len(registros) > 0:
                print(f"📄 Muestra del primer registro: {registros[0]}")
            
            # Configurar URL del backend (ajustar según tu configuración)
            backend_url = "http://localhost:3001"  # Cambiar si es necesario
            endpoint = f"{backend_url}/cleaning/bulk-insert"
            
            # Envío por lotes para evitar payloads demasiado grandes
            batch_size = 1000  # Procesar 1000 registros por lote
            total_registros = len(registros)  # Usar registros validados, no los raw
            total_inserted = 0
            total_duplicates = 0
            total_errors = 0
            
            print(f"📤 Enviando {total_registros} registros al backend en lotes de {batch_size}...")
            
            for i in range(0, total_registros, batch_size):
                batch = registros[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_registros + batch_size - 1) // batch_size
                
                print(f"📦 Enviando lote {batch_num}/{total_batches} ({len(batch)} registros)...")
                
                try:
                    response = requests.post(
                        endpoint,
                        json={
                            "contacts": batch,
                            "check_duplicates": True,  # Verificar duplicados por teléfono
                            "source": "cleaning_app"
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        total_inserted += result.get('inserted', 0)
                        total_duplicates += result.get('duplicates_skipped', 0)
                        total_errors += result.get('errors', 0)
                        print(f"✅ Lote {batch_num} procesado: +{result.get('inserted', 0)} nuevos, {result.get('duplicates_skipped', 0)} duplicados")
                    else:
                        error_msg = f"Error {response.status_code}: {response.text}"
                        print(f"❌ Error en lote {batch_num}: {error_msg}")
                        total_errors += len(batch)
                        
                except Exception as e:
                    print(f"❌ Excepción en lote {batch_num}: {str(e)}")
                    total_errors += len(batch)
            
            # Mostrar resumen final
            messagebox.showinfo(
                "¡Proceso Completado!", 
                f"✅ Procesamiento completado!\n\n"
                f"📊 Total registros procesados: {total_registros}\n"
                f"➕ Nuevos registros insertados: {total_inserted}\n"
                f"🔄 Duplicados evitados: {total_duplicates}\n"
                f"❌ Errores: {total_errors}\n\n"
                f"📦 Lotes enviados: {total_batches}"
            )
            print(f"✅ Proceso completo: {total_inserted} nuevos, {total_duplicates} duplicados, {total_errors} errores")
            
            # Notificar al backend que el procesamiento terminó y cerrar aplicación automáticamente
            try:
                print("🔄 Notificando al backend que el procesamiento terminó...")
                response = requests.post(
                    "http://localhost:3001/cleaning/processing-completed",
                    json={
                        "totalRecords": total_registros,
                        "newRecords": total_inserted,
                        "duplicates": total_duplicates,
                        "errors": total_errors
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Backend notificado exitosamente")
                    if result.get('shouldRedirect'):
                        print("🔄 Cerrando aplicación automáticamente...")
                        # Cerrar la aplicación automáticamente
                        self.root.quit()
                        return
                else:
                    print(f"⚠️ Error notificando al backend: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ No se pudo notificar al backend: {e}")
                # Continuar normalmente si no se puede notificar
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de conexión", "❌ No se pudo conectar al backend.\nVerifica que el servidor esté ejecutándose en http://localhost:3001")
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", "❌ La subida tardó demasiado tiempo.\nIntenta con menos registros.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error inesperado:\n{str(e)}")
            print(f"❌ Error en subir_a_base_datos: {e}")

# Ejecutar la aplicación
if __name__ == "__main__":
    if HEADLESS_MODE:
        # Ejecutar en modo headless (sin GUI)
        exit_code = ejecutar_headless()
        sys.exit(exit_code)
    else:
        # Ejecutar con GUI (modo normal)
        root = tk.Tk()
        app = App(root)
        root.mainloop()
