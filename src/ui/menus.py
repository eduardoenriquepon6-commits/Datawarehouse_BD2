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
