"""Router: cambia la vista mostrada en la página de Flet."""
import flet as ft

from vista.login_vista import LoginVista
from vista.dashboard_vista import DashboardVista


class AppRouter:
    def __init__(self, page: ft.Page):
        self.page = page
        self.auth = None

    def registrar_autenticacion(self, auth):
        self.auth = auth

    def navegar(self, ruta: str):
        if ruta == "dashboard" and not (self.auth and self.auth.usuario_actual):
            ruta = "login"  # protege el dashboard
        if ruta == "dashboard":
            vista = DashboardVista(self.page, self.auth)
        else:
            vista = LoginVista(self.page, self.auth)
        self.page.controls.clear()
        self.page.add(vista.construir())
        self.page.update()