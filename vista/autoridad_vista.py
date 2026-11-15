"""Dashboard de la Autoridad: monitoriza todos los locales y puede cerrarlos temporalmente."""
import flet as ft

from vista import componentes_vista as c
from vista.base_vista import PanelBase


class AutoridadVista(PanelBase):
    SECCIONES = [("dashboard", ft.Icons.DASHBOARD, "Dashboard"),
                 ("bares", ft.Icons.STOREFRONT, "Bares")]

    def render(self, clave):
        if clave == "dashboard":
            return ("Dashboard", "Resumen general de la calle",
                    [self.bloque_stats(), self.bloque_sensores()])
        tabla = self.tabla_bares(self.crud.listar_bares(), self.acciones_cierre)
        return ("Locales de la calle", "Cierre temporal por inspección o protocolo de seguridad",
                [c.tarjeta(ft.Column([c.encabezado("Todos los locales"), tabla], spacing=12))])