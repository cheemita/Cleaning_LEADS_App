import pandas as pd

def obtener_vista_previa(archivo):
    """
    Carga el archivo Excel o CSV, detecta si tiene encabezados,
    y devuelve una vista previa del DataFrame.
    Si no hay encabezados, asigna nombres genéricos a las columnas.
    """
    try:
        # Cargar archivo según la extensión
        if archivo.endswith(".csv"):
            df = pd.read_csv(archivo, header=None)  # Cargar sin asumir encabezados
        else:
            df = pd.read_excel(archivo, header=None)

        # Verificar si la primera fila puede ser los encabezados
        if df.iloc[0].nunique() == df.shape[1]:  # Valores únicos en la primera fila
            encabezados_detectados = True
            df.columns = df.iloc[0]  # Usar la primera fila como encabezados
            df = df[1:]  # Eliminar la fila usada como encabezados
        else:
            encabezados_detectados = False
            df.columns = [f"Column{i}" for i in range(1, len(df.columns) + 1)]  # Asignar nombres genéricos

        # Vista previa: primeras 5 filas
        vista_previa = df.head()

        return encabezados_detectados, vista_previa

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return None, None
