import pyodbc
from config import OLTP_CONN_STRING, OLAP_CONN_STRING


def _conectar(conn_string, nombre_bd):
    try:
        conexion = pyodbc.connect(conn_string)
        return conexion
    except pyodbc.Error as e:
        sqlstate = e.args[0] if e.args else None
        if sqlstate == 'IM002':
            print(f"\n[Error de Conexion] No se pudo encontrar el controlador de base de datos necesario.\n")
        else:
            print(f"\n[Fallo de conexion en {nombre_bd}]: No se pudo conectar a la base de datos.\n")
        return None


def obtener_conexion_oltp():
    return _conectar(OLTP_CONN_STRING, "Origen (OLTP)")


def obtener_conexion_olap():
    return _conectar(OLAP_CONN_STRING, "Destino (OLAP/DW)")
