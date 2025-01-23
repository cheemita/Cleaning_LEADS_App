import re

def seleccionar_columnas(df, columnas_a_mantener):
    """
    Mantiene únicamente las columnas seleccionadas en el DataFrame.
    :param df: DataFrame original.
    :param columnas_a_mantener: Lista de columnas que se desean mantener.
    :return: DataFrame con solo las columnas seleccionadas.
    """
    try:
        # Mantener únicamente las columnas seleccionadas
        df = df[columnas_a_mantener]
        return df
    except KeyError as e:
        print(f"Error: Una o más columnas no existen en el DataFrame: {e}")
        return None


CODIGOS_AREA_VALIDOS = {
    "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "212", "213", "214", "215", "216", "217", "218", 
    "219", "224", "225", "226", "228", "229", "231", "234", "239", "240", "242", "246", "248", "250", "251", "252", "253",
    "254", "256", "260", "262", "264", "267", "268", "269", "270", "272", "276", "279", "281", "283", "289", "301", "302",
    "303", "304", "305", "306", "307", "308", "309", "310", "312", "313", "314", "315", "316", "317", "318", "319", "320",
    "321", "323", "325", "326", "330", "331", "334", "336", "337", "339", "340", "343", "345", "346", "347", "351", "352",
    "360", "361", "364", "365", "380", "385", "386", "401", "402", "403", "404", "405", "406", "407", "408", "409", "410",
    "412", "413", "414", "415", "416", "417", "418", "419", "423", "424", "425", "430", "431", "432", "434", "435", "437",
    "438", "440", "441", "442", "443", "450", "456", "458", "463", "469", "470", "473", "475", "478", "479", "480", "481",
    "484", "501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "512", "513", "514", "515", "516", "517",
    "518", "519", "520", "530", "531", "533", "534", "539", "540", "541", "548", "551", "557", "559", "561", "562", "563",
    "564", "567", "570", "571", "573", "574", "575", "579", "580", "581", "582", "585", "586", "601", "602", "603", "604",
    "605", "606", "607", "608", "609", "610", "612", "613", "614", "615", "616", "617", "618", "619", "620", "623", "626",
    "627", "628", "629", "630", "631", "636", "639", "640", "641", "646", "647", "649", "650", "651", "657", "658", "659",
    "660", "661", "662", "664", "667", "669", "670", "671", "678", "679", "680", "681", "682", "684", "689", "701", "702",
    "703", "704", "705", "706", "707", "708", "709", "712", "713", "714", "715", "716", "717", "718", "719", "720", "721",
    "724", "725", "726", "727", "730", "731", "732", "734", "737", "740", "743", "747", "754", "757", "758", "760", "762",
    "763", "764", "765", "767", "769", "770", "771", "772", "773", "774", "775", "778", "779", "780", "781", "782", "784",
    "785", "786", "787", "801", "802", "803", "804", "805", "806", "807", "808", "809", "810", "812", "813", "814", "815",
    "816", "817", "818", "819", "820", "825", "828", "829", "830", "831", "832", "835", "843", "844", "845", "847", "848",
    "849", "850", "854", "855", "856", "857", "858", "859", "860", "862", "863", "864", "865", "867", "868", "869", "870",
    "872", "873", "876", "878", "901", "902", "903", "904", "905", "906", "907", "908", "909", "910", "912", "913", "914",
    "915", "916", "917", "918", "919", "920", "925", "927", "928", "929", "930", "931", "935", "936", "937", "938", "939",
    "940", "941", "947", "949", "951", "952", "954", "956", "959", "970", "971", "972", "973", "975", "978", "979", "980",
    "984", "985", "986", "989"
}

def detectar_columna_telefonos(df):
    """
    Detecta automáticamente la columna que contiene números de teléfono en un DataFrame.
    Si encuentra una columna válida, la renombra como 'phone'.
    Si no encuentra ninguna, crea una nueva columna 'phone' con valores predeterminados.
    También limpia la columna eliminando filas con espacios vacíos, verifica números que comiencen con '1',
    y elimina aquellos que no tengan un código de área válido después del '1'.
    Además, elimina registros con más de 10 dígitos o caracteres no numéricos.

    :param df: DataFrame a analizar.
    :return: DataFrame modificado con la columna de teléfonos renombrada o añadida como 'phone'.
    """
    def limpiar_numero(valor):
        """
        Limpia un número telefónico eliminando caracteres no numéricos.
        """
        return re.sub(r'\D', '', valor)
    
    for columna in df.columns:
        muestra = df[columna].astype(str).head(10).tolist()

        def es_posible_telefono(valor):
            """
            Valida si un valor tiene el formato de un número telefónico válido.
            """
            valor = limpiar_numero(valor)
            if len(valor) == 11 and valor.startswith('1'):  # Números de 11 dígitos que empiezan con '1'
                codigo_area = valor[1:4]
                return codigo_area in CODIGOS_AREA_VALIDOS
            return len(valor) == 10 and valor[:3] in CODIGOS_AREA_VALIDOS

        es_columna_telefonica = sum([es_posible_telefono(valor) for valor in muestra]) > (len(muestra) // 2)

        if es_columna_telefonica:
            print(f"Columna detectada para teléfonos: {columna}")
            df = df.rename(columns={columna: 'phone'})

            # Limpiar la columna phone
            df['phone'] = df['phone'].astype(str).apply(limpiar_numero)

            # Filtrar y procesar números válidos
            def procesar_numero(valor):
                """
                Procesa un número telefónico para eliminar el prefijo '1' si aplica
                y validar su formato.
                """
                if len(valor) == 11 and valor.startswith('1'):  # Números de 11 dígitos que empiezan con '1'
                    codigo_area = valor[1:4]
                    if codigo_area in CODIGOS_AREA_VALIDOS:
                        return valor[1:]  # Eliminar el '1' y usar los 10 dígitos restantes
                    return None  # Número inválido
                if len(valor) == 10 and valor[:3] in CODIGOS_AREA_VALIDOS:
                    return valor  # Número válido de 10 dígitos
                return None  # Número inválido

            # Aplicar la limpieza y filtrar valores nulos
            df['phone'] = df['phone'].apply(procesar_numero)
            df = df[df['phone'].notnull()]  # Eliminar filas con valores no válidos en 'phone'

            return df

    print("No se detectó ninguna columna con números telefónicos. Creando columna 'phone'...")
    df['phone'] = 'No hay registro'  # Crear la columna 'phone' con valores por defecto
    return df



def detectar_columna_emails(df):
    """
    Detecta automáticamente la columna que contiene direcciones de correo electrónico en un DataFrame
    verificando si contiene el símbolo '@'. Si encuentra una columna válida, la renombra como 'email'.
    Si no encuentra ninguna, crea una nueva columna 'email' con valores predeterminados.
    """
    for columna in df.columns:
        # Convertir a string y limpiar los valores
        muestra = df[columna].astype(str).str.strip().head(10).tolist()

        # Comprobar si algún valor contiene '@'
        contiene_email = any('@' in valor for valor in muestra)

        if contiene_email:
            print(f"Columna detectada para correos electrónicos: {columna}")
            df = df.rename(columns={columna: 'email'})  # Renombrar la columna como 'email'
            # Reemplazar valores NaN o vacíos por 'No hay email'
            df['email'] = df['email'].replace('', 'No hay email').fillna('No hay email')
            return df

    # Si no se detectó ninguna columna con '@', crear columna 'email' con valores predeterminados
    print("No se detectó ninguna columna con correos electrónicos. Creando columna 'email'...")
    df['email'] = 'No hay email'
    return df
