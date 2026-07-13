import questionary
from src.ui.console import console

PUNTERO = "\u00bb "
CHECK_MARCADO = "\u2611 "
CHECK_VACIO = "\u2610 "

estilo_moderno = questionary.Style([
    ('qmark', 'fg:#00ffff bold'),
    ('question', 'bold'),
    ('pointer', 'fg:#00ffff bold'),
    ('highlighted', 'fg:#00ffff bold'),
    ('selected', 'fg:#ffffff'),
    ('instruction', 'fg:#888888 italic'),
])


def menu_principal() -> str:
    opcion = questionary.select(
        "Seleccione una opcion para continuar:",
        choices=[
            questionary.Choice("1. Iniciar Proceso ETL (Tabla o SQL Query)", value="etl"),
            questionary.Choice("2. Probar Conexiones de Base de Datos", value="probar_db"),
            questionary.Choice("3. Salir", value="salir")
        ],
        style=estilo_moderno,
        pointer=PUNTERO
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
        style=estilo_moderno,
        pointer=PUNTERO
    ).ask()
    return opcion


def seleccionar_tabla_origen(tablas: list) -> str:
    opcion = questionary.select(
        "Seleccione la tabla de origen para extraer los datos:",
        choices=[questionary.Choice(t, value=t) for t in tablas] + [
            questionary.Choice("<-- Volver", value="volver")
        ],
        style=estilo_moderno,
        pointer=PUNTERO
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
        choices=choices,
        style=estilo_moderno,
        pointer=PUNTERO
    ).ask()
    return seleccionadas if seleccionadas else []


def menu_preguntar_si_transformar():
    return questionary.confirm(
        "Desea aplicar una transformacion a alguna columna?",
        default=True,
        style=estilo_moderno,
        qmark="?"
    ).ask()


def menu_seleccionar_columna(columnas):
    seleccion = questionary.select(
        "Seleccione la columna que desea transformar:",
        choices=[questionary.Choice(c, value=c) for c in columnas],
        style=estilo_moderno,
        pointer=PUNTERO
    ).ask()
    return seleccion


def _determinar_tipo_columna(columna, clasificacion):
    for tipo, cols in clasificacion.items():
        if columna in cols:
            return tipo
    return 'otros'


def _menu_concatenar_entre_columnas(columna, todas_columnas):
    otras = [c for c in todas_columnas if c != columna]
    if not otras:
        console.print("[yellow]No hay otras columnas disponibles para concatenar.[/yellow]")
        return None

    otra_col = questionary.select(
        f"Seleccione la columna con la que desea concatenar '{columna}':",
        choices=[questionary.Choice(c, value=c) for c in otras],
        style=estilo_moderno,
        pointer=PUNTERO
    ).ask()

    separador = questionary.select(
        "Seleccione el separador entre ambas columnas:",
        choices=[
            questionary.Choice("Espacio (' ')", value=" "),
            questionary.Choice("Guion ('-')", value="-"),
            questionary.Choice("Coma (', ')", value=", "),
            questionary.Choice("Sin separador", value=""),
            questionary.Choice("Personalizado", value="personalizado")
        ],
        style=estilo_moderno,
        pointer=PUNTERO
    ).ask()

    if separador == "personalizado":
        separador = questionary.text(
            "Ingrese el separador personalizado:",
            style=estilo_moderno
        ).ask() or ""

    nueva_col = questionary.text(
        "Ingrese el nombre (Alias) de la nueva columna resultante:",
        default=f"{columna}_{otra_col}",
        style=estilo_moderno
    ).ask()

    if not nueva_col:
        nueva_col = f"{columna}_{otra_col}"

    return {
        'columna': columna,
        'tipo': 'concatenar_columna',
        'valor': {
            'otra_columna': otra_col,
            'separador': separador,
            'nueva_columna': nueva_col
        }
    }


def _menu_transformacion_columna(columna, tipo, todas_columnas=None):
    if tipo == 'fecha':
        seleccion = questionary.select(
            f"Transformacion para columna de fecha '{columna}':",
            choices=[
                questionary.Choice("Extraer solo el a\u00f1o", value="year"),
                questionary.Choice("Extraer solo el mes", value="month"),
                questionary.Choice("Extraer solo el dia", value="day"),
                questionary.Choice("Extraer solo la hora", value="hour"),
                questionary.Choice("Saltar esta columna", value="saltar")
            ],
            style=estilo_moderno,
            pointer=PUNTERO
        ).ask()
        if seleccion and seleccion != "saltar":
            return {'columna': columna, 'tipo': 'extraer_fecha', 'valor': seleccion}
    elif tipo == 'texto':
        seleccion = questionary.select(
            f"Transformacion para columna de texto '{columna}':",
            choices=[
                questionary.Choice("Convertir a mayuscula", value="mayuscula"),
                questionary.Choice("Convertir a minuscula", value="minuscula"),
                questionary.Choice("Concatenar con otra columna", value="concatenar_columna"),
                questionary.Choice("Concatenar con texto estatico", value="concatenar"),
                questionary.Choice("Saltar esta columna", value="saltar")
            ],
            style=estilo_moderno,
            pointer=PUNTERO
        ).ask()
        if seleccion == "concatenar_columna":
            if todas_columnas:
                return _menu_concatenar_entre_columnas(columna, todas_columnas)
            return None
        elif seleccion == "concatenar":
            valor = questionary.text(
                f"Ingrese el texto estatico a concatenar al final del campo '{columna}':",
                style=estilo_moderno
            ).ask()
            if valor is not None:
                return {'columna': columna, 'tipo': 'concatenar', 'valor': valor}
        elif seleccion and seleccion != "saltar":
            return {'columna': columna, 'tipo': seleccion}
    else:
        seleccion = questionary.select(
            f"Transformacion para columna '{columna}':",
            choices=[
                questionary.Choice("Concatenar con otra columna", value="concatenar_columna"),
                questionary.Choice("Concatenar con texto estatico", value="concatenar"),
                questionary.Choice("Saltar esta columna", value="saltar")
            ],
            style=estilo_moderno,
            pointer=PUNTERO
        ).ask()
        if seleccion == "concatenar_columna":
            if todas_columnas:
                return _menu_concatenar_entre_columnas(columna, todas_columnas)
            return None
        elif seleccion == "concatenar":
            valor = questionary.text(
                f"Ingrese el texto estatico a concatenar al final del campo '{columna}':",
                style=estilo_moderno
            ).ask()
            if valor is not None:
                return {'columna': columna, 'tipo': 'concatenar', 'valor': valor}
    return None


def seleccionar_tabla_destino(tablas: list) -> str:
    opcion = questionary.select(
        "Seleccione la tabla de destino en el Data Warehouse (OLAP):",
        choices=[questionary.Choice(t, value=t) for t in tablas] + [
            questionary.Choice("<-- Volver", value="volver")
        ],
        style=estilo_moderno,
        pointer=PUNTERO
    ).ask()
    return opcion


def menu_mapeo_columnas(cols_origen: list, cols_destino: list) -> dict:
    mapeo = {}
    for col_origen in cols_origen:
        opciones = [questionary.Choice(f"{c}", value=c) for c in cols_destino]
        opciones.append(questionary.Choice("No mapear esta columna", value=None))
        seleccion = questionary.select(
            f"Seleccione la columna de destino para '{col_origen}':",
            choices=opciones,
            style=estilo_moderno,
            pointer=PUNTERO
        ).ask()
        if seleccion is not None:
            mapeo[col_origen] = seleccion
    return mapeo


def menu_seleccionar_llave(columnas: list) -> str:
    seleccion = questionary.select(
        "Seleccione la columna que actuara como Llave de Negocio para la carga incremental:",
        choices=[questionary.Choice(c, value=c) for c in columnas],
        style=estilo_moderno,
        pointer=PUNTERO
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
