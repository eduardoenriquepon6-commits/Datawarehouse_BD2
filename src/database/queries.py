import pyodbc


def listar_tablas_origen(conexion: pyodbc.Connection):
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    cursor = conexion.cursor()
    cursor.execute(query)
    tablas = [f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}" for row in cursor.fetchall()]
    cursor.close()
    return tablas


def listar_columnas_tabla(conexion: pyodbc.Connection, tabla_completa: str):
    esquema, tabla = tabla_completa.split(".")
    query = """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """
    cursor = conexion.cursor()
    cursor.execute(query, (esquema, tabla))
    columnas = [(row.COLUMN_NAME, row.DATA_TYPE) for row in cursor.fetchall()]
    cursor.close()
    return columnas


def extraer_por_tabla(conexion: pyodbc.Connection, tabla_completa: str, campos: list):
    columnas_str = ", ".join([f"[{c}]" for c in campos])
    query = f"SELECT {columnas_str} FROM {tabla_completa}"
    try:
        cursor = conexion.cursor()
        cursor.execute(query)
        columnas_reales = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        cursor.close()
        return columnas_reales, filas
    except pyodbc.Error:
        raise RuntimeError("Fallo en la extraccion por tabla") from None


def ejecutar_sql_custom(conexion: pyodbc.Connection, consulta_sql: str):
    consulta_limpia = consulta_sql.strip()
    if not consulta_limpia.upper().startswith("SELECT") and not consulta_limpia.upper().startswith("WITH"):
        raise ValueError("La consulta debe comenzar con SELECT o WITH.")
    try:
        cursor = conexion.cursor()
        cursor.execute(consulta_limpia)
        columnas_reales = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        cursor.close()
        return columnas_reales, filas
    except pyodbc.Error:
        raise RuntimeError("Fallo en la extraccion por SQL custom") from None


def listar_tablas_destino(conexion: pyodbc.Connection):
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    cursor = conexion.cursor()
    cursor.execute(query)
    tablas = [f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}" for row in cursor.fetchall()]
    cursor.close()
    return tablas
