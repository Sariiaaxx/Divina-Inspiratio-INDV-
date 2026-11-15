"""Router: elige la vista según la ruta y el rol del usuario logueado."""
import flet as ft

from vista.login_vista import LoginVista
from vista.admin_vista import AdminVista
from vista.autoridad_vista import AutoridadVista
from vista.propietario_vista import PropietarioVista
from vista.vecino_vista import VecinoVista

VISTAS_POR_ROL = {
    "admin": AdminVista,
    "autoridad": AutoridadVista,
    "propietario": PropietarioVista,
    "vecino": VecinoVista,
}


class AppRouter:
    def __init__(self, page: ft.Page):
        self.page = page
        self.auth = None
        self.crud = None

    def registrar_controladores(self, auth, crud):
        self.auth = auth
        self.crud = crud

    def navegar(self, ruta: str):
        usuario = self.auth.usuario_actual if self.auth else None
        if ruta != "login" and not usuario:
            ruta = "login"  # protege los dashboards
        if ruta == "dashboard":
            ruta = usuario.get("rol", "vecino")

        if ruta == "login":
            vista = LoginVista(self.page, self.auth)
        else:
            vista = VISTAS_POR_ROL.get(ruta, VecinoVista)(self.page, self.auth, self.crud)

        self.page.controls.clear()
        self.page.add(vista.construir())
        self.page.update()