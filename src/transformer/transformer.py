import pandas as pd


def rows_to_dataframe(columnas, filas):
    data = [tuple(row) for row in filas]
    return pd.DataFrame(data, columns=columnas)


def clasificar_columnas(df):
    texto = []
    fecha = []
    otros = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            fecha.append(col)
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            texto.append(col)
        else:
            otros.append(col)
    return {'texto': texto, 'fecha': fecha, 'otros': otros}


def obtener_tipo_columna(columna, clasificacion):
    for tipo, cols in clasificacion.items():
        if columna in cols:
            return tipo
    return 'otros'


def aplicar_transformacion(df, columna, tipo, valor_extra=None):
    if tipo == 'mayuscula':
        df[columna] = df[columna].astype(str).str.upper()
    elif tipo == 'minuscula':
        df[columna] = df[columna].astype(str).str.lower()
    elif tipo == 'concatenar':
        valor_str = str(valor_extra) if valor_extra is not None else ""
        df[columna] = df[columna].astype(str) + valor_str
    elif tipo == 'extraer_fecha':
        df[columna] = pd.to_datetime(df[columna], errors='coerce')
        if valor_extra == 'year':
            df[columna] = df[columna].dt.year
        elif valor_extra == 'month':
            df[columna] = df[columna].dt.month
        elif valor_extra == 'day':
            df[columna] = df[columna].dt.day
        elif valor_extra == 'hour':
            df[columna] = df[columna].dt.hour
    return df
