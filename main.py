import sys
from src.ui.console import mostrar_cabecera, mostrar_exito, mostrar_error, mostrar_advertencia
from src.ui.menus import (
    menu_principal, menu_tipo_extraccion,
    seleccionar_tabla_origen, seleccionar_columnas,
    ingresar_sql_custom
)
from src.database.connection import obtener_conexion_oltp, obtener_conexion_olap
from src.database.queries import listar_tablas_origen, listar_columnas_tabla
from src.extractor.extractor import extraer_datos_por_tabla, extraer_datos_por_sql


def ejecutar_prueba_conexiones():
    mostrar_cabecera()
    print("Probando conexiones...\n")

    conn_oltp = obtener_conexion_oltp()
    if conn_oltp:
        mostrar_exito("Conexion a base de datos de origen establecida correctamente.")
        conn_oltp.close()

    conn_olap = obtener_conexion_olap()
    if conn_olap:
        mostrar_exito("Conexion a base de datos de destino establecida correctamente.")
        conn_olap.close()
    else:
        mostrar_advertencia("No se pudo conectar a la base de datos de destino. Esto es normal si aun no ha sido configurada.")


def flujo_extraccion_por_tabla(conexion):
    tablas = listar_tablas_origen(conexion)
    if not tablas:
        mostrar_error("Extraccion", "No se encontraron tablas disponibles en la base de datos de origen.")
        input("\nPresione Enter para volver...")
        return None, None

    while True:
        tabla = seleccionar_tabla_origen(tablas)
        if tabla == "volver":
            return None, None

        columnas_con_tipo = listar_columnas_tabla(conexion, tabla)
        if not columnas_con_tipo:
            mostrar_advertencia(f"La tabla {tabla} no tiene columnas disponibles.")
            continue

        campos = seleccionar_columnas(columnas_con_tipo)
        if not campos:
            mostrar_advertencia("Debe seleccionar al menos un campo.")
            continue

        mostrar_cabecera()
        print(f"Extrayendo datos de {tabla}...")
        try:
            columnas, filas = extraer_datos_por_tabla(conexion, tabla, campos)
            mostrar_exito(f"Extraccion completada: {len(filas)} registros obtenidos de {len(columnas)} columna(s).")
            input("\nPresione Enter para continuar...")
            return columnas, filas
        except RuntimeError:
            mostrar_error("Extraccion", "No se pudieron extraer los datos de la tabla seleccionada.")
            input("\nPresione Enter para volver...")
            return None, None


def flujo_extraccion_por_sql(conexion):
    mostrar_cabecera()
    consulta = ingresar_sql_custom()
    if not consulta:
        mostrar_advertencia("No se ingreso ninguna consulta.")
        input("\nPresione Enter para volver...")
        return None, None

    try:
        columnas, filas = extraer_datos_por_sql(conexion, consulta)
        mostrar_exito(f"Extraccion completada: {len(filas)} registros obtenidos de {len(columnas)} columna(s).")
        mostrar_cabecera()
        print(f"\nColumnas detectadas en la consulta:")
        for i, col in enumerate(columnas, 1):
            print(f"  {i}. {col}")
        input("\nPresione Enter para continuar...")
        return columnas, filas
    except (RuntimeError, ValueError):
        mostrar_error("Extraccion", "No se pudo ejecutar la consulta SQL ingresada.")
        input("\nPresione Enter para volver...")
        return None, None


def iniciar_flujo_etl():
    conexion = obtener_conexion_oltp()
    if not conexion:
        input("\nPresione Enter para volver al menu principal...")
        return

    try:
        while True:
            mostrar_cabecera()
            tipo = menu_tipo_extraccion()

            if tipo == "volver":
                break
            elif tipo == "tabla":
                columnas, filas = flujo_extraccion_por_tabla(conexion)
                if columnas is not None:
                    print("\n[Fase Futura] Los datos extraidos estan listos para la etapa de transformacion...")
                    input("\nPresione Enter para volver...")
            elif tipo == "sql_custom":
                columnas, filas = flujo_extraccion_por_sql(conexion)
                if columnas is not None:
                    print("\n[Fase Futura] Los datos extraidos estan listos para la etapa de transformacion...")
                    input("\nPresione Enter para volver...")
    finally:
        conexion.close()


def main():
    try:
        while True:
            mostrar_cabecera()
            opcion = menu_principal()

            if opcion == "salir":
                mostrar_cabecera()
                print("\nGracias por usar el sistema ETL! Saliendo...\n")
                sys.exit(0)

            elif opcion == "probar_db":
                ejecutar_prueba_conexiones()
                input("\nPresione Enter para volver al menu principal...")

            elif opcion == "etl":
                iniciar_flujo_etl()

    except KeyboardInterrupt:
        print("\n\nEjecucion cancelada por el usuario. Saliendo del sistema ETL...\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
