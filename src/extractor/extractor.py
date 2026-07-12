import pyodbc
from src.database.queries import extraer_por_tabla, ejecutar_sql_custom


def extraer_datos_por_tabla(conexion: pyodbc.Connection, tabla: str, campos_seleccionados: list):
    columnas, filas = extraer_por_tabla(conexion, tabla, campos_seleccionados)
    return columnas, filas


def extraer_datos_por_sql(conexion: pyodbc.Connection, consulta_sql: str):
    columnas, filas = ejecutar_sql_custom(conexion, consulta_sql)
    return columnas, filas
