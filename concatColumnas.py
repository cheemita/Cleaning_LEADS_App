import pandas as pd

def usar_una_columna_para_nombre(df, columna):
    """
    Selecciona una columna para usarla como 'name'.
    Renombra esa columna como 'name' y devuelve el DataFrame modificado.
    
    :param df: DataFrame a modificar.
    :param columna: Nombre de la columna a usar como 'name'.
    :return: DataFrame modificado.
    """
    try:
        # Verificar si la columna existe
        if columna not in df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el archivo.")
        
        # Renombrar la columna
        df = df.rename(columns={columna: "name"})
        return df
    except Exception as e:
        print(f"Error al procesar la columna: {e}")
        return None


def concatenar_dos_columnas(df, columna1, columna2):
    """
    Concatena dos columnas para crear una nueva columna llamada 'name'.
    Devuelve el DataFrame modificado.

    :param df: DataFrame a modificar.
    :param columna1: Nombre de la primera columna.
    :param columna2: Nombre de la segunda columna.
    :return: DataFrame modificado.
    """
    try:
        # Verificar si ambas columnas existen
        if columna1 not in df.columns or columna2 not in df.columns:
            raise ValueError(f"Una o ambas columnas seleccionadas no existen: {columna1}, {columna2}")
        
        # Concatenar las dos columnas con un espacio en medio
        df["name"] = df[columna1].astype(str) + " " + df[columna2].astype(str)
        return df
    except Exception as e:
        print(f"Error al concatenar columnas: {e}")
        return None
