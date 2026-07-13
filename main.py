import sys
import pandas as pd
import questionary
from src.ui.console import console, mostrar_cabecera, mostrar_exito, mostrar_error, mostrar_advertencia
from src.ui.menus import (
    menu_principal, menu_tipo_extraccion,
    seleccionar_tabla_origen, seleccionar_columnas,
    ingresar_sql_custom, menu_configurar_transformaciones,
    seleccionar_tabla_destino, menu_mapeo_columnas,
    menu_seleccionar_llave
)
from src.database.connection import obtener_conexion_oltp, obtener_conexion_olap
from src.database.queries import (
    listar_tablas_origen, listar_columnas_tabla,
    listar_tablas_destino, listar_columnas_obligatorias_destino
)
from src.extractor.extractor import extraer_datos_por_tabla, extraer_datos_por_sql
from src.transformer.transformer import (
    rows_to_dataframe, clasificar_columnas,
    aplicar_transformacion
)
from src.loader.loader import cargar_datos_incrementales


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
        mostrar_advertencia("No se pudo conectar a la base de datos de destino.")


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
        console.print("\n[bold]Columnas detectadas en la consulta:[/bold]")
        for i, col in enumerate(columnas, 1):
            console.print(f"  {i}. {col}")
        input("\nPresione Enter para continuar...")
        return columnas, filas
    except (RuntimeError, ValueError):
        mostrar_error("Extraccion", "No se pudo ejecutar la consulta SQL ingresada.")
        input("\nPresione Enter para volver...")
        return None, None


def flujo_transformacion(columnas, filas):
    mostrar_cabecera()
    df = rows_to_dataframe(columnas, filas)
    clasificacion = clasificar_columnas(df)

    console.print("\n[bold]Columnas disponibles y sus tipos detectados:[/bold]")
    for tipo, cols in clasificacion.items():
        if cols:
            console.print(f"  [cyan]{tipo}[/cyan]: {', '.join(cols)}")
    console.print()

    configs = menu_configurar_transformaciones(df, clasificacion)
    if not configs:
        mostrar_advertencia("No se configuraron transformaciones. Los datos quedan sin cambios.")
        return df

    for cfg in configs:
        col = cfg['columna']
        tipo = cfg['tipo']
        valor = cfg.get('valor')
        try:
            df = aplicar_transformacion(df, col, tipo, valor)
            mostrar_exito(f"Transformacion '{tipo}' aplicada a columna '{col}'.")
        except Exception:
            mostrar_error("Transformacion", f"Error al aplicar transformacion a la columna '{col}'.")

    mostrar_exito(f"Todas las transformaciones aplicadas correctamente a {len(configs)} columna(s).")
    input("\nPresione Enter para continuar...")
    return df


def flujo_carga(df):
    conexion_olap = obtener_conexion_olap()
    if not conexion_olap:
        input("\nPresione Enter para volver...")
        return

    try:
        tablas = listar_tablas_destino(conexion_olap)
        if not tablas:
            mostrar_error("Carga", "No se encontraron tablas en la base de datos de destino.")
            return

        while True:
            tabla = seleccionar_tabla_destino(tablas)
            if tabla == "volver":
                return

            columnas_destino_con_tipo = listar_columnas_tabla(conexion_olap, tabla)
            columnas_destino = [c[0] for c in columnas_destino_con_tipo]

            mostrar_cabecera()
            print(f"Mapeando columnas hacia {tabla}...\n")
            mapeo = menu_mapeo_columnas(df.columns.tolist(), columnas_destino)

            if not mapeo:
                mostrar_advertencia("Debe mapear al menos una columna para continuar.")
                continue

            columnas_obligatorias = listar_columnas_obligatorias_destino(conexion_olap, tabla)
            columnas_mapeadas_destino = list(mapeo.values())
            faltantes = [c for c in columnas_obligatorias if c not in columnas_mapeadas_destino]

            if faltantes:
                mostrar_cabecera()
                console.print(f"\n[bold yellow]Columnas obligatorias no mapeadas en '{tabla}':[/bold yellow]")
                for col in faltantes:
                    console.print(f"  [yellow]- {col}[/yellow]")
                console.print("\nEstas columnas son requeridas por la base de datos de destino.")
                continuar = questionary.confirm(
                    "Desea continuar de todas formas? (la insercion podria fallar)",
                    default=False
                ).ask()
                if not continuar:
                    continue

            df_mapeado = df[list(mapeo.keys())].rename(columns=mapeo)

            columnas_mapeadas = list(df_mapeado.columns)
            llave = menu_seleccionar_llave(columnas_mapeadas)

            try:
                registros_insertados, error = cargar_datos_incrementales(
                    conexion_olap, df_mapeado, tabla, llave
                )
                if error:
                    mostrar_error("Carga", error)
                elif registros_insertados == 0:
                    mostrar_exito("Carga incremental completada. No hay registros nuevos para insertar.")
                else:
                    mostrar_exito(
                        f"Carga incremental completada. "
                        f"Se insertaron {registros_insertados} registro(s) nuevo(s) en '{tabla}'."
                    )
                input("\nPresione Enter para volver...")
                return
            except RuntimeError:
                mostrar_error("Carga", "Error durante la insercion de datos en la tabla destino.")
                input("\nPresione Enter para volver...")
                return
    finally:
        conexion_olap.close()


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
                    df_transformado = flujo_transformacion(columnas, filas)
                    flujo_carga(df_transformado)
            elif tipo == "sql_custom":
                columnas, filas = flujo_extraccion_por_sql(conexion)
                if columnas is not None:
                    df_transformado = flujo_transformacion(columnas, filas)
                    flujo_carga(df_transformado)
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
