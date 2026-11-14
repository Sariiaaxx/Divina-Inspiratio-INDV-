"""Punto de entrada de Divine Inspiratio."""
import flet as ft

from modelo.usuarios_modelo import UsuariosModelo
from controlador.app_router import AppRouter
from controlador.autentificacion_controlador import AutentificacionControlador


def main(page: ft.Page):
    page.title = "Divine Inspiratio"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#101117"
    page.padding = 0

    modelo = UsuariosModelo()            # Modelo
    router = AppRouter(page)            # Navegación
    auth = AutentificacionControlador(modelo, router)  # Controlador
    router.registrar_autenticacion(auth)

    router.navegar("login")


if __name__ == "__main__":
        ft.run(main)