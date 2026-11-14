"""Vista de inicio de sesión y registro (Actualizado para Flet 1.0+)."""
import flet as ft

BG = "#101117"
BG_CIRCULO = "#161b2b"
TARJETA = "#1b1e2a"
CAMPO = "#12141c"
BORDE = "#2f3342"
ACENTO = "#7c9bff"
TEXTO = "#ffffff"
TEXTO_SUAVE = "#8b8fa3"
ERROR = "#ff7b7b"


class LoginVista:
    def __init__(self, page: ft.Page, controlador):
        self.page = page
        self.controlador = controlador
        self.modo = "login"  # "login" | "registro"

        def campo(hint, password=False):
            return ft.TextField(
                hint_text=hint, password=password, can_reveal_password=password,
                bgcolor=CAMPO, border_color=BORDE, focused_border_color=ACENTO,
                border_radius=10, color=TEXTO,
                hint_style=ft.TextStyle(color=TEXTO_SUAVE),
                content_padding=14,
                on_submit=self._enviar,
            )

        self.nombre = campo("Tu nombre")
        self.correo = campo("nombre@ejemplo.com")
        self.password = campo("••••••••••", password=True)
        self.confirmar = campo("Repite la contraseña", password=True)

        self.titulo = ft.Text(size=26, weight=ft.FontWeight.BOLD, color=TEXTO,
                              text_align=ft.TextAlign.CENTER)
        self.subtitulo = ft.Text(size=14, color=TEXTO_SUAVE,
                                 text_align=ft.TextAlign.CENTER)
        self.mensaje = ft.Text("", size=13, color=ERROR, visible=False,
                               text_align=ft.TextAlign.CENTER)

        self.texto_boton = ft.Text("Iniciar sesión", weight=ft.FontWeight.BOLD, size=15, color="#0f1220")
        self.boton = ft.Container(
            width=356, height=48, on_click=self._enviar,
            bgcolor=ACENTO, border_radius=10,
            alignment=ft.Alignment.CENTER,  # CORREGIDO A MAYÚSCULAS
            content=self.texto_boton
        )

        self.texto_cambio = ft.Text(size=13, color=TEXTO_SUAVE)
        self.texto_enlace_cambio = ft.Text("Regístrate", color=TEXTO_SUAVE)

        self.enlace_cambio = ft.TextButton(
            content=self.texto_enlace_cambio,
            on_click=self._cambiar_modo,
            style=ft.ButtonStyle(padding=0)
        )
        self.enlace_olvido = ft.TextButton(
            content=ft.Text("¿Olvidaste tu contraseña?", color=ACENTO),
            on_click=self._olvido,
            style=ft.ButtonStyle(padding=0)
        )

        self.bloque_nombre = self._con_etiqueta("Nombre", self.nombre)
        self.bloque_confirmar = self._con_etiqueta("Confirmar contraseña", self.confirmar)
        self.fila_olvido = ft.Row([self.enlace_olvido], alignment=ft.MainAxisAlignment.END)

        self._aplicar_modo()

    @staticmethod
    def _con_etiqueta(texto, control):
        return ft.Column(
            [ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=TEXTO), control],
            spacing=8)

    def construir(self) -> ft.Control:
        logo = ft.Column(
            [
                ft.Text("Divine\nInspiratio", size=30, weight=ft.FontWeight.BOLD,
                        color=TEXTO, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=ft.Text("SENSOR MONITORING", size=11, weight=ft.FontWeight.BOLD, color=ACENTO),
                    bgcolor="#222a47", border_radius=20,
                    padding=ft.Padding.only(left=12, right=12, top=5, bottom=5)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

        tarjeta = ft.Container(
            width=420, bgcolor=TARJETA, border=ft.Border.all(1, BORDE),
            border_radius=22, padding=32,
            content=ft.Column(
                [
                    self.titulo, self.subtitulo,
                    ft.Container(height=8),
                    self.bloque_nombre,
                    self._con_etiqueta("Correo electrónico", self.correo),
                    self._con_etiqueta("Contraseña", self.password),
                    self.bloque_confirmar,
                    self.fila_olvido,
                    self.mensaje,
                    self.boton,
                    ft.Row([self.texto_cambio, self.enlace_cambio],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                ],
                spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER))

        centro = ft.Column(
            [
                logo, ft.Container(height=12), tarjeta, ft.Container(height=8),
                ft.Text("Prototipo visual · Datos de ejemplo", size=11, color=TEXTO_SUAVE),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)

        return ft.Container(
            expand=True, bgcolor=BG,
            content=ft.Stack(
                [
                    ft.Container(width=420, height=420, border_radius=210,
                                 bgcolor=BG_CIRCULO, right=-120, top=-170),
                    ft.Container(width=380, height=380, border_radius=190,
                                 bgcolor=BG_CIRCULO, left=-170, bottom=-190),
                    ft.Container(content=centro, alignment=ft.Alignment.CENTER, # CORREGIDO A MAYÚSCULAS
                                 padding=20, left=0, right=0, top=0, bottom=0),
                ],
                expand=True))

    def _aplicar_modo(self):
        login = self.modo == "login"
        self.titulo.value = "Bienvenido de nuevo" if login else "Crea tu cuenta"
        self.subtitulo.value = ("Accede a tu panel de monitorización" if login
                                else "Regístrate para monitorizar tus sensores")

        self.texto_boton.value = "Iniciar sesión" if login else "Crear cuenta"
        self.texto_cambio.value = "¿No tienes cuenta?" if login else "¿Ya tienes cuenta?"
        self.texto_enlace_cambio.value = "Regístrate" if login else "Inicia sesión"

        self.bloque_nombre.visible = not login
        self.bloque_confirmar.visible = not login
        self.fila_olvido.visible = login
        self._mostrar_mensaje("")

    def _mostrar_mensaje(self, texto, error=True):
        self.mensaje.value = texto
        self.mensaje.color = ERROR if error else TEXTO_SUAVE
        self.mensaje.visible = bool(texto)

    def _cambiar_modo(self, e):
        self.modo = "registro" if self.modo == "login" else "login"
        self._aplicar_modo()
        self.page.update()

    def _olvido(self, e):
        self._mostrar_mensaje(
            "La recuperación de contraseña estará disponible próximamente.", error=False)
        self.page.update()

    def _enviar(self, e):
        if self.modo == "login":
            ok, msg = self.controlador.iniciar_sesion(
                self.correo.value or "", self.password.value or "")
        else:
            ok, msg = self.controlador.registrar(
                self.nombre.value or "", self.correo.value or "",
                self.password.value or "", self.confirmar.value or "")
        if not ok:
            self._mostrar_mensaje(msg)
            self.page.update()