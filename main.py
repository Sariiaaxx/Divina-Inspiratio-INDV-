"""Punto de entrada de Divine Inspiratio."""
import flet as ft

from modelo.usuarios_modelo import UsuariosModel
from modelo.codigos_modelo import CodigosModel
from modelo.bares_modelo import BaresModelo
from controlador.app_router import AppRouter
from controlador.autentificacion_controlador import AutentificacionControlador
from controlador.crud_bares_controlador import CrudBaresControlador


def main(page: ft.Page):
    page.title = "Divine Inspiratio"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#101117"
    page.padding = 0

    usuarios = UsuariosModel()   # crea registros/ y al Admin Supremo si faltan
    codigos = CodigosModel()
    bares = BaresModelo()

    router = AppRouter(page)
    auth = AutentificacionControlador(usuarios, codigos, bares, router)
    crud = CrudBaresControlador(bares, usuarios, lambda: auth.usuario_actual)
    router.registrar_controladores(auth, crud)

    router.navegar("login")


if __name__ == "__main__":
    # Flet 1.0+ usa ft.run; las versiones anteriores, ft.app
    (getattr(ft, "run", None) or ft.app)(main)