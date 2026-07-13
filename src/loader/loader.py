import pyodbc
import pandas as pd


def obtener_llaves_destino(conexion: pyodbc.Connection, tabla_destino: str, columna_llave: str) -> set:
    query = f"SELECT [{columna_llave}] FROM {tabla_destino}"
    try:
        cursor = conexion.cursor()
        cursor.execute(query)
        llaves = {row[0] for row in cursor.fetchall()}
        cursor.close()
        return llaves
    except pyodbc.Error:
        return set()


def cargar_datos_incrementales(
    conexion: pyodbc.Connection,
    df: pd.DataFrame,
    tabla_destino: str,
    columna_llave: str
):
    llaves_existentes = obtener_llaves_destino(conexion, tabla_destino, columna_llave)

    df_nuevos = df[~df[columna_llave].isin(llaves_existentes)]

    if df_nuevos.empty:
        return 0, None

    columnas = list(df_nuevos.columns)
    columnas_str = ", ".join([f"[{c}]" for c in columnas])
    valores_placeholders = ", ".join(["?" for _ in columnas])

    query_insert = f"INSERT INTO {tabla_destino} ({columnas_str}) VALUES ({valores_placeholders})"

    registros_a_insertar = [tuple(x) for x in df_nuevos.to_numpy()]

    cursor = conexion.cursor()
    try:
        conexion.autocommit = False
        cursor.executemany(query_insert, registros_a_insertar)
        conexion.commit()
        return len(registros_a_insertar), None
    except pyodbc.Error as e:
        conexion.rollback()
        sqlstate = e.args[0] if e.args else '00000'
        if sqlstate == '23000':
            raise RuntimeError(
                "Violacion de restriccion en la base de datos destino. "
                "Revise que todas las columnas obligatorias esten mapeadas "
                "y que no haya valores duplicados en la llave de negocio."
            ) from None
        elif sqlstate == '22001':
            raise RuntimeError(
                "El tamano de los datos excede el limite permitido en la tabla destino."
            ) from None
        else:
            raise RuntimeError("Error en la base de datos destino durante la insercion de datos.") from None
    finally:
        cursor.close()
