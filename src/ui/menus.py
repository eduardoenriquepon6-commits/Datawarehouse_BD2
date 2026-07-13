import questionary
from src.ui.console import console


def menu_principal() -> str:
    opcion = questionary.select(
        "Seleccione una opcion para continuar:",
        choices=[
            questionary.Choice("1. Iniciar Proceso ETL (Tabla o SQL Query)", value="etl"),
            questionary.Choice("2. Probar Conexiones de Base de Datos", value="probar_db"),
            questionary.Choice("3. Salir", value="salir")
        ],
        style=questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan bold'),
            ('selected', 'fg:white'),
        ])
    ).ask()

    return opcion


def menu_tipo_extraccion() -> str:
    opcion = questionary.select(
        "Seleccione el metodo de extraccion de datos (Origen):",
        choices=[
            questionary.Choice("A) Por Seleccion de Tabla", value="tabla"),
            questionary.Choice("B) Por Consulta SQL Personalizada (Custom Query)", value="sql_custom"),
            questionary.Choice("<-- Volver al menu principal", value="volver")
        ],
        style=questionary.Style([
            ('qmark', 'fg:yellow bold'),
            ('pointer', 'fg:yellow bold'),
            ('highlighted', 'fg:yellow bold'),
        ])
    ).ask()

    return opcion


def seleccionar_tabla_origen(tablas: list) -> str:
    opcion = questionary.select(
        "Seleccione la tabla de origen para extraer los datos:",
        choices=[questionary.Choice(t, value=t) for t in tablas] + [
            questionary.Choice("<-- Volver", value="volver")
        ]
    ).ask()
    return opcion


def seleccionar_columnas(columnas_con_tipo: list) -> list:
    choices = []
    for col, dtype in columnas_con_tipo:
        choices.append(
            questionary.Choice(
                f"{col} ({dtype})",
                value=col,
                checked=False
            )
        )
    seleccionadas = questionary.checkbox(
        "Seleccione los campos que desea extraer (use ESPACIO para marcar):",
        choices=choices
    ).ask()
    return seleccionadas if seleccionadas else []


def menu_configurar_transformaciones(df, clasificacion):
    todas = list(df.columns)
    if not todas:
        return []

    cols_a_transformar = questionary.checkbox(
        "Seleccione las columnas que desea transformar (ESPACIO para marcar, Enter para continuar):",
        choices=[questionary.Choice(c, value=c) for c in todas]
    ).ask()

    if not cols_a_transformar:
        return []

    configs = []
    for col in cols_a_transformar:
        tipo = _determinar_tipo_columna(col, clasificacion)
        config = _menu_transformacion_columna(col, tipo)
        if config:
            configs.append(config)
    return configs


def _determinar_tipo_columna(columna, clasificacion):
    for tipo, cols in clasificacion.items():
        if columna in cols:
            return tipo
    return 'otros'


def _menu_transformacion_columna(columna, tipo):
    if tipo == 'fecha':
        seleccion = questionary.select(
            f"Transformacion para columna de fecha '{columna}':",
            choices=[
                questionary.Choice("Extraer solo el año", value="year"),
                questionary.Choice("Extraer solo el mes", value="month"),
                questionary.Choice("Extraer solo el dia", value="day"),
                questionary.Choice("Extraer solo la hora", value="hour"),
                questionary.Choice("Saltar esta columna", value="saltar")
            ]
        ).ask()
        if seleccion and seleccion != "saltar":
            return {'columna': columna, 'tipo': 'extraer_fecha', 'valor': seleccion}
    elif tipo == 'texto':
        seleccion = questionary.select(
            f"Transformacion para columna de texto '{columna}':",
            choices=[
                questionary.Choice("Convertir a mayuscula", value="mayuscula"),
                questionary.Choice("Convertir a minuscula", value="minuscula"),
                questionary.Choice("Concatenar con texto adicional", value="concatenar"),
                questionary.Choice("Saltar esta columna", value="saltar")
            ]
        ).ask()
        if seleccion == "concatenar":
            valor = questionary.text(f"Ingrese el texto a concatenar al final del campo '{columna}':").ask()
            if valor is not None:
                return {'columna': columna, 'tipo': 'concatenar', 'valor': valor}
        elif seleccion and seleccion != "saltar":
            return {'columna': columna, 'tipo': seleccion}
    else:
        seleccion = questionary.select(
            f"Transformacion para columna '{columna}':",
            choices=[
                questionary.Choice("Concatenar con texto adicional", value="concatenar"),
                questionary.Choice("Saltar esta columna", value="saltar")
            ]
        ).ask()
        if seleccion == "concatenar":
            valor = questionary.text(f"Ingrese el texto a concatenar al final del campo '{columna}':").ask()
            if valor is not None:
                return {'columna': columna, 'tipo': 'concatenar', 'valor': valor}
    return None


def seleccionar_tabla_destino(tablas: list) -> str:
    opcion = questionary.select(
        "Seleccione la tabla de destino en el Data Warehouse (OLAP):",
        choices=[questionary.Choice(t, value=t) for t in tablas] + [
            questionary.Choice("<-- Volver", value="volver")
        ]
    ).ask()
    return opcion


def menu_mapeo_columnas(cols_origen: list, cols_destino: list) -> dict:
    mapeo = {}
    for col_origen in cols_origen:
        opciones = [questionary.Choice(f"{c}", value=c) for c in cols_destino]
        opciones.append(questionary.Choice("No mapear esta columna", value=None))
        seleccion = questionary.select(
            f"Seleccione la columna de destino para '{col_origen}':",
            choices=opciones
        ).ask()
        if seleccion is not None:
            mapeo[col_origen] = seleccion
    return mapeo


def menu_seleccionar_llave(columnas: list) -> str:
    seleccion = questionary.select(
        "Seleccione la columna que actuara como Llave de Negocio para la carga incremental:",
        choices=[questionary.Choice(c, value=c) for c in columnas]
    ).ask()
    return seleccion


def ingresar_sql_custom() -> str:
    console.print("[bold yellow]Instrucciones:[/bold yellow] Escriba o pegue su consulta SQL.")
    console.print("Para finalizar, presione [bold]Enter[/bold] dos veces seguidas.\n")
    lineas = []
    lineas_vacias = 0
    while True:
        try:
            linea = input()
        except (EOFError, KeyboardInterrupt):
            break
        if linea.strip() == "":
            lineas_vacias += 1
            if lineas_vacias >= 1:
                break
        else:
            lineas.append(linea)
            lineas_vacias = 0
    return "\n".join(lineas).strip()
