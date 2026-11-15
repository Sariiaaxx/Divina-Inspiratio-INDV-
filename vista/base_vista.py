"""Estructura común de los dashboards: sidebar, cabecera y bloques reutilizables."""
import flet as ft

from vista import componentes_vista as c


class PanelBase:
    SECCIONES = []  # (clave, icono, etiqueta)

    def __init__(self, page, auth, crud):
        self.page, self.auth, self.crud = page, auth, crud
        self.seccion = self.SECCIONES[0][0]
        self._titulo = ft.Text(size=26, weight=ft.FontWeight.BOLD, color=c.TEXTO)
        self._subtitulo = ft.Text(size=14, color=c.SUAVE)
        self._nav = ft.Column(spacing=6)
        self._cuerpo = ft.Column(spacing=16, expand=True, scroll=ft.ScrollMode.AUTO)

    @property
    def usuario(self):
        return self.auth.usuario_actual or {}

    def render(self, clave):
        """Devuelve (titulo, subtitulo, [controles]) de la sección."""
        raise NotImplementedError

    # ---------- navegación ----------
    def ir(self, clave):
        self.seccion = clave
        self.refrescar()

    def refrescar(self, actualizar=True):
        titulo, sub, controles = self.render(self.seccion)
        self._titulo.value, self._subtitulo.value = titulo, sub
        self._cuerpo.controls = controles
        self._nav.controls = [self._item(i, e, k == self.seccion, lambda ev, k=k: self.ir(k))
                              for k, i, e in self.SECCIONES]
        if actualizar:
            self.page.update()

    def ejecutar(self, resultado):
        """Muestra el (ok, mensaje) de un controlador y refresca si fue bien."""
        ok, msg = resultado
        c.notificar(self.page, msg, error=not ok)
        if ok:
            self.refrescar()

    # ---------- construcción ----------
    def _item(self, icono, etiqueta, activo, on_click):
        return ft.Container(
            content=ft.Row([ft.Icon(icono, size=18, color=c.ACENTO if activo else c.SUAVE),
                            ft.Text(etiqueta, size=14, color=c.TEXTO if activo else c.SUAVE,
                                    weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL)],
                           spacing=12),
            padding=c.pad(14, 12), border_radius=10, ink=True, on_click=on_click,
            bgcolor="#2a3150" if activo else None,
            border=ft.Border(left=ft.BorderSide(3, c.ACENTO)) if activo else None)

    def construir(self):
        self.refrescar(actualizar=False)
        rol = c.ETIQUETA_ROL.get(self.usuario.get("rol"), "")
        nombre = self.usuario.get("nombre", "")

        logo = ft.Column([
            ft.Text("Divine\nInspiratio", size=26, weight=ft.FontWeight.BOLD, color=c.TEXTO),
            ft.Text("MONITORIZACIÓN", size=10, weight=ft.FontWeight.BOLD, color=c.SUAVE)], spacing=4)
        perfil = ft.Row([c.avatar(nombre), ft.Column([
            ft.Text(nombre, size=13, weight=ft.FontWeight.BOLD, color=c.TEXTO),
            ft.Text(rol, size=11, color=c.SUAVE)], spacing=0)], spacing=10)
        sidebar = ft.Container(
            width=230, bgcolor=c.SIDEBAR, padding=c.pad(14, 22),
            content=ft.Column([
                logo, ft.Container(height=14), self._nav, ft.Container(expand=True),
                ft.Divider(color=c.BORDE), perfil, ft.Container(height=4),
                self._item(ft.Icons.LOGOUT, "Cerrar sesión", False,
                           lambda e: self.auth.cerrar_sesion())], expand=True))

        chip_usuario = ft.Container(
            content=ft.Row([c.avatar(nombre), ft.Column([
                ft.Text(nombre, size=12, weight=ft.FontWeight.BOLD, color=c.TEXTO),
                ft.Text(rol, size=11, color=c.SUAVE)], spacing=0)], spacing=10),
            border=ft.Border.all(1, c.BORDE), border_radius=14, padding=c.pad(12, 8), bgcolor=c.PANEL)

        cabecera = ft.Row([ft.Column([self._titulo, self._subtitulo], spacing=2, expand=True),
                           chip_usuario], vertical_alignment=ft.CrossAxisAlignment.START)
        principal = ft.Container(expand=True, padding=c.pad(28, 24),
                                 content=ft.Column([cabecera, self._cuerpo], spacing=20, expand=True))
        return ft.Container(expand=True, bgcolor=c.BG,
                            content=ft.Row([sidebar, principal], expand=True, spacing=0))

    # ---------- bloques reutilizables ----------
    def bloque_stats(self, extra=None):
        s = self.crud.estadisticas()
        tarjetas = [
            c.stat("LOCALES ABIERTOS", s["abiertos"], f"de {s['total']} locales activos"),
            c.stat("AFORO ACTUAL", s["aforo"], f"de {s['capacidad']} plazas abiertas"),
            c.stat("OCUPACIÓN", f"{s['ocupacion']} %", "de los locales abiertos"),
            c.stat("CERRADOS TEMPORALMENTE", s["cerrados"], "locales"),
        ] + (extra or [])
        return ft.Row(tarjetas, wrap=True, spacing=16, run_spacing=16)

    def bloque_sensores(self):
        return c.tarjeta(ft.Column([
            c.encabezado("Sensores", "Temperatura, humedad y calidad del aire"),
            ft.Text("Las lecturas en tiempo real se mostrarán aquí cuando se integren los "
                    "sensores (fase futura).", size=13, color=c.SUAVE)], spacing=10))

    def _aforo(self, b):
        if b["estado"] != c.ABIERTO:
            return ft.Text("—", color=c.SUAVE)
        return ft.Column([ft.Text(f"{b['aforo_actual']} / {b['capacidad']}", size=13, color=c.TEXTO),
                          c.barra_aforo(b["aforo_actual"], b["capacidad"])], spacing=4)

    def acciones_cierre(self, b, definitivo=False):
        """Botones de cierre/reapertura de un local (admin y autoridad)."""
        acc = []
        if b["estado"] == c.ABIERTO:
            acc.append(c.boton("Cerrar temporal", lambda e: self.ejecutar(
                self.crud.cerrar_temporal(b["id"])), "suave", pequeno=True))
        elif b["estado"] == c.TEMPORAL:
            acc.append(c.boton("Reabrir", lambda e: self.ejecutar(
                self.crud.abrir(b["id"])), "suave", pequeno=True))
        if definitivo and b["estado"] != c.PERMANENTE:
            acc.append(c.boton("Cerrar definitivo", lambda e: c.confirmar(
                self.page, "Cerrar definitivamente",
                f"«{b['nombre']}» quedará cerrado para siempre y su número de calle se liberará.",
                lambda: self.ejecutar(self.crud.cerrar_permanente(b["id"])), "Cerrar definitivo"),
                "peligro", pequeno=True))
        return acc

    def tabla_bares(self, bares, acciones=None):
        pesos = [0.6, 2.2, 1.8, 1.4, 1.7] + ([2.8] if acciones else [])
        cab = ["Nº", "Local", "Aforo", "Horario", "Estado"] + (["Acciones"] if acciones else [])
        filas = [c.fila(cab, pesos, cabecera=True)]
        if not bares:
            filas.append(ft.Container(padding=24, content=ft.Text(
                "Todavía no hay locales dados de alta.", color=c.SUAVE)))
        for b in bares:
            local = ft.Column([ft.Text(b["nombre"], size=13, weight=ft.FontWeight.BOLD, color=c.TEXTO),
                               ft.Text(b.get("propietario_nombre", ""), size=11, color=c.SUAVE)], spacing=2)
            celdas = [str(b["numero"]), local, self._aforo(b),
                      f"{b['apertura']} – {b['cierre']}", c.chip_estado(b)]
            if acciones:
                celdas.append(ft.Row(acciones(b), spacing=6, wrap=True))
            filas.append(c.fila(celdas, pesos))
        return ft.Column(filas, spacing=0)