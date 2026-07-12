from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def mostrar_cabecera():
    console.clear()
    titulo = Text("SISTEMA ETL - BASES DE DATOS II", style="bold cyan")
    subtitulo = Text("Data Warehouse Loader para AdventureWorks2019", style="italic white")

    contenido = Text.assemble(titulo, "\n", subtitulo)
    console.print(Panel(contenido, border_style="cyan", expand=False))


def mostrar_exito(mensaje: str):
    console.print(Panel(f"[bold green]\u2713[/bold green] {mensaje}", border_style="green", expand=False))


def mostrar_error(fase: str, mensaje: str = ""):
    if mensaje:
        contenido = f"[bold red]Fallo en: {fase}[/bold red]\n{mensaje}"
    else:
        contenido = f"[bold red]Fallo en: {fase}[/bold red]"
    console.print(Panel(contenido, title="[bold red]ERROR DETECTADO[/bold red]", border_style="red", expand=False))


def mostrar_advertencia(mensaje: str):
    console.print(f"[bold yellow]\u00a1[/bold yellow] {mensaje}")
