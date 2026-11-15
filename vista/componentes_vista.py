"""Componentes visuales compartidos (Flet 1.0+) con el estilo del diseño."""
import flet as ft

from controlador.crud_bares_controlador import ABIERTO, TEMPORAL, PERMANENTE

BG = "#101117"
SIDEBAR = "#171a25"
PANEL = "#1b1e2a"
CAMPO = "#12141c"
BORDE = "#2f3342"
ACENTO = "#7c9bff"
TEXTO = "#ffffff"
SUAVE = "#8b8fa3"
ERROR = "#ff7b7b"
VERDE_F, VERDE_T = "#1c3a2e", "#5fdc9a"
AMBAR_F, AMBAR_T = "#3d3020", "#f0b35a"
AZUL_F = "#222a47"
ROJO_F, ROJO_T = "#3d2230", "#ff8a9a"

TONOS = {"azul": (AZUL_F, ACENTO), "verde": (VERDE_F, VERDE_T), "ambar": (AMBAR_F, AMBAR_T),
         "rojo": (ROJO_F, ROJO_T), "gris": ("#262a38", SUAVE)}
ETIQUETA_ROL = {"admin": "Admin Supremo", "autoridad": "Autoridad",
                "propietario": "Propietario", "vecino": "Vecino"}
TONO_ROL = {"admin": "rojo", "autoridad": "ambar", "propietario": "azul", "vecino": "gris"}


def pad(h=0, v=0):
    return ft.Padding(left=h, top=v, right=h, bottom=v)


# ---------- diálogos y alertas ----------
def abrir_dialogo(page, dlg):
    (page.show_dialog if hasattr(page, "show_dialog") else page.open)(dlg)


def cerrar_dialogo(page, dlg):
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    else:
        page.close(dlg)


def notificar(page, texto, error=False):
    """SnackBar de éxito (verde) o error (rojo)."""
    abrir_dialogo(page, ft.SnackBar(
        content=ft.Text(texto, color=TEXTO),
        bgcolor="#7a2e3a" if error else "#1f5a43"))


def dialogo(page, titulo, contenido, texto_ok, al_ok, texto_cancelar="Cancelar", peligro=False):
    """Diálogo modal. `al_ok` recibe el diálogo; debe cerrarlo si todo fue bien."""
    dlg = ft.AlertDialog(modal=True, bgcolor=PANEL, title=ft.Text(titulo, color=TEXTO, weight=ft.FontWeight.BOLD))
    dlg.content = contenido
    dlg.actions = [
        ft.TextButton(content=ft.Text(texto_cancelar, color=SUAVE),
                      on_click=lambda e: cerrar_dialogo(page, dlg)),
        ft.TextButton(content=ft.Text(texto_ok, color=ROJO_T if peligro else ACENTO,
                                      weight=ft.FontWeight.BOLD),
                      on_click=lambda e: al_ok(dlg)),
    ]
    abrir_dialogo(page, dlg)
    return dlg


def confirmar(page, titulo, texto, al_confirmar, texto_ok="Confirmar", peligro=True):
    def ok(dlg):
        cerrar_dialogo(page, dlg)
        al_confirmar()
    dialogo(page, titulo, ft.Text(texto, color=SUAVE, width=360), texto_ok, ok, peligro=peligro)


# ---------- elementos ----------
def chip(texto, tono="azul"):
    fondo, color = TONOS[tono]
    return ft.Container(content=ft.Text(texto, size=12, weight=ft.FontWeight.BOLD, color=color),
                        bgcolor=fondo, border_radius=20, padding=pad(12, 5))


def chip_estado(bar):
    if bar["estado"] == ABIERTO:
        return chip("Abierto", "verde")
    if bar["estado"] == TEMPORAL:
        return chip("Cerrado temporal", "ambar")
    return chip("Cerrado definitivo", "rojo")


def boton(texto, on_click, tono="primario", icono=None, pequeno=False, ancho=None):
    estilos = {"primario": (ACENTO, "#0f1220"), "suave": (AZUL_F, ACENTO),
               "peligro": (ROJO_F, ROJO_T), "neutro": ("#262a38", TEXTO)}
    fondo, color = estilos[tono]
    hijos = []
    if icono:
        hijos.append(ft.Icon(icono, size=14 if pequeno else 18, color=color))
    hijos.append(ft.Text(texto, size=12 if pequeno else 14, weight=ft.FontWeight.BOLD, color=color))
    return ft.Container(
        content=ft.Row(hijos, spacing=6, tight=ancho is None, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=fondo, border_radius=10, width=ancho, ink=True, on_click=on_click,
        padding=pad(12 if pequeno else 18, 7 if pequeno else 11))


def campo(label, valor="", **kw):
    return ft.TextField(label=label, value=valor, bgcolor=CAMPO, border_color=BORDE,
                        focused_border_color=ACENTO, border_radius=10, color=TEXTO,
                        label_style=ft.TextStyle(color=SUAVE), content_padding=14, **kw)


def tarjeta(contenido, padding=24, ancho=None):
    return ft.Container(content=contenido, bgcolor=PANEL, border=ft.Border.all(1, BORDE),
                        border_radius=18, padding=padding, width=ancho)


def encabezado(titulo, subtitulo=None, accion=None):
    textos = [ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEXTO)]
    if subtitulo:
        textos.append(ft.Text(subtitulo, size=12, color=SUAVE))
    fila = [ft.Column(textos, spacing=2, expand=True)]
    if accion:
        fila.append(accion)
    return ft.Row(fila, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def stat(titulo, valor, detalle):
    return tarjeta(ft.Column([
        ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD, color=SUAVE),
        ft.Text(str(valor), size=30, weight=ft.FontWeight.BOLD, color=TEXTO),
        ft.Text(detalle, size=12, color=SUAVE)], spacing=4), padding=20, ancho=240)


def fila(celdas, pesos, cabecera=False):
    items = []
    for celda, peso in zip(celdas, pesos):
        if isinstance(celda, str):
            celda = (ft.Text(celda, size=12, weight=ft.FontWeight.BOLD, color=SUAVE) if cabecera
                     else ft.Text(celda, size=13, color=TEXTO))
        items.append(ft.Container(content=celda, expand=max(1, round(peso * 10))))  # expand exige int
    return ft.Container(
        content=ft.Row(items, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=pad(8, 8 if cabecera else 12), border=ft.Border(bottom=ft.BorderSide(1, BORDE)))


def avatar(nombre, tam=32):
    ini = "".join(p[0] for p in (nombre or "?").split()[:2]).upper()
    return ft.Container(width=tam, height=tam, border_radius=tam / 2, bgcolor="#2c3558",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(ini, size=tam * 0.36, weight=ft.FontWeight.BOLD, color=ACENTO))


def barra_aforo(actual, capacidad, ancho=120):
    pct = actual / capacidad if capacidad else 0
    color = VERDE_T if pct < 0.7 else AMBAR_T if pct < 0.9 else ROJO_T
    return ft.ProgressBar(value=min(pct, 1), width=ancho, color=color, bgcolor="#262a38")