"""Vista de Dashboard (Actualizado para Flet 1.0+)."""
import flet as ft


class DashboardVista:
    def __init__(self, page: ft.Page, controlador):
        self.page = page
        self.controlador = controlador

    def construir(self) -> ft.Control:
        usuario = self.controlador.usuario_actual or {}
        nombre = usuario.get("nombre", "usuario")
        return ft.Container(
            expand=True, bgcolor="#101117", padding=24,
            content=ft.Column(
                [
                    ft.Row(
                        [ft.Text("Divine Inspiratio", size=20, weight=ft.FontWeight.BOLD),
                         ft.OutlinedButton(
                             content=ft.Text("Cerrar sesión"), # CORREGIDO: Uso de content
                             on_click=lambda e: self.controlador.cerrar_sesion())],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        expand=True, alignment=ft.Alignment.CENTER, # CORREGIDO A MAYÚSCULAS
                        content=ft.Column(
                            [ft.Text(f"Bienvenido, {nombre}", size=28,
                                     weight=ft.FontWeight.BOLD),
                             ft.Text("Vista de Bares · próximamente", color="#8b8fa3")],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER)),
                ],
                expand=True))