import pyodbc
from config import OLTP_CONN_STRING, OLAP_CONN_STRING


def obtener_conexion_oltp():
    try:
        conexion = pyodbc.connect(OLTP_CONN_STRING)
        return conexion
    except pyodbc.InterfaceError:
        print("\n[Error de Conexion] No se pudo encontrar el controlador (Driver) ODBC de SQL Server.")
        print("Asegurate de tener instalado 'ODBC Driver 17 for SQL Server'.\n")
        return None
    except pyodbc.DatabaseError as e:
        print(f"\n[Fallo de conexion en Origen]: No se pudo conectar a la base de datos OLTP.")
        print(f"Detalle tecnico: {e}\n")
        return None


def obtener_conexion_olap():
    try:
        conexion = pyodbc.connect(OLAP_CONN_STRING)
        return conexion
    except pyodbc.InterfaceError:
        print("\n[Error de Conexion] No se pudo encontrar el controlador (Driver) ODBC de SQL Server.")
        print("Asegurate de tener instalado 'ODBC Driver 17 for SQL Server'.\n")
        return None
    except pyodbc.DatabaseError as e:
        print(f"\n[Fallo de conexion en Destino]: No se pudo conectar a la base de datos OLAP (DW).")
        print(f"Detalle tecnico: {e}\n")
        return None
