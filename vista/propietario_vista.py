"""Dashboard del Propietario: alta y gestión de su único local."""
import flet as ft

from vista import componentes_vista as c
from vista.base_vista import PanelBase

NUM = ft.KeyboardType.NUMBER


class PropietarioVista(PanelBase):
    SECCIONES = [("local", ft.Icons.STOREFRONT, "Mi local"),
                 ("estadisticas", ft.Icons.BAR_CHART, "Estadísticas")]

    def render(self, clave):
        bar = self.crud.mi_local()
        if clave == "estadisticas":
            if bar is None:
                return ("Estadísticas", "Datos de tu local",
                        [c.tarjeta(ft.Text("Primero da de alta tu local en «Mi local».", color=c.SUAVE))])
            return ("Estadísticas", f"Sensores y aforo de {bar['nombre']}",
                    [self.bloque_stats(), self.bloque_sensores()])
        if bar is None:
            return ("Da de alta tu local", "Solo puedes tener un local en la calle", [self._formulario()])
        return ("Mi local", "Gestiona tu local", [self._gestion(bar)])

    # ---------- alta ----------
    def _formulario(self):
        nombre = c.campo("Nombre del local")
        cap = c.campo("Capacidad de aforo", keyboard_type=NUM)
        num = c.campo("Número en la calle (1-5)", keyboard_type=NUM)
        ape = c.campo("Apertura (HH:MM)", "18:00", expand=True)
        cie = c.campo("Cierre (HH:MM)", "02:00", expand=True)
        ocupados = self.crud.numeros_ocupados()
        ayuda = ("Números ocupados: " + ", ".join(map(str, ocupados))) if ocupados \
            else "Todos los números están libres."

        def crear(e):
            ok, msg = self.crud.crear_local(nombre.value, cap.value, num.value, ape.value, cie.value)
            if ok:
                c.notificar(self.page, msg)
                self.refrescar()
            else:  # incluye "número ocupado": alerta en SnackBar
                c.notificar(self.page, msg, error=True)

        return c.tarjeta(ft.Column([
            c.encabezado("Datos del local", "Se publicará en la vista de los vecinos"),
            nombre, cap, num, ft.Text(ayuda, size=12, color=c.SUAVE),
            ft.Row([ape, cie], spacing=12),
            ft.Row([c.boton("Crear local", crear, icono=ft.Icons.ADD)])], spacing=14, width=480))

    # ---------- gestión ----------
    def _gestion(self, b):
        abierto = b["estado"] == c.ABIERTO
        detalle = ft.Row([self._dato("Nº en la calle", b["numero"]),
                          self._dato("Aforo máximo", b["capacidad"]),
                          self._dato("Horario", f"{b['apertura']} – {b['cierre']}")], spacing=40, wrap=True)
        aforo = ft.Row([
            c.boton("−", lambda e: self.ejecutar(self.crud.ajustar_aforo(b["id"], -1)), "neutro", pequeno=True),
            ft.Text(f"{b['aforo_actual']} / {b['capacidad']} personas", size=16,
                    weight=ft.FontWeight.BOLD, color=c.TEXTO),
            c.boton("+", lambda e: self.ejecutar(self.crud.ajustar_aforo(b["id"], 1)), "neutro", pequeno=True),
        ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER) if abierto else \
            ft.Text("El aforo no se registra mientras el local está cerrado.", size=13, color=c.SUAVE)

        if abierto:
            cierre = c.boton("Cerrar temporalmente", lambda e: self.ejecutar(
                self.crud.cerrar_temporal(b["id"])), "suave", icono=ft.Icons.LOCK_CLOCK)
        else:
            cierre = c.boton("Reabrir local", lambda e: self.ejecutar(
                self.crud.abrir(b["id"])), "suave", icono=ft.Icons.LOCK_OPEN)
        definitivo = c.boton("Cerrar definitivamente", lambda e: c.confirmar(
            self.page, "Cerrar definitivamente",
            "Se eliminará tu local y su número quedará libre para otro propietario. "
            "Esta acción no se puede deshacer.",
            lambda: self.ejecutar(self.crud.cerrar_permanente(b["id"])), "Cerrar definitivamente"),
            "peligro", icono=ft.Icons.DELETE)
        return c.tarjeta(ft.Column([
            ft.Row([ft.Text(b["nombre"], size=22, weight=ft.FontWeight.BOLD, color=c.TEXTO),
                    c.chip_estado(b)], spacing=14),
            detalle, ft.Divider(color=c.BORDE),
            ft.Text("Aforo actual", size=12, weight=ft.FontWeight.BOLD, color=c.SUAVE),
            aforo, c.barra_aforo(b["aforo_actual"], b["capacidad"], 320) if abierto else ft.Container(),
            ft.Text("Hasta integrar los sensores, el aforo se registra a mano.", size=11, color=c.SUAVE),
            ft.Divider(color=c.BORDE),
            ft.Row([c.boton("Editar local", lambda e: self._editar(b), "neutro", icono=ft.Icons.EDIT),
                    cierre, definitivo], spacing=10, wrap=True)], spacing=14))

    @staticmethod
    def _dato(etiqueta, valor):
        return ft.Column([ft.Text(etiqueta, size=12, color=c.SUAVE),
                          ft.Text(str(valor), size=16, weight=ft.FontWeight.BOLD, color=c.TEXTO)], spacing=2)

    def _editar(self, b):
        nombre = c.campo("Nombre", b["nombre"])
        cap = c.campo("Capacidad", str(b["capacidad"]), keyboard_type=NUM)
        ape = c.campo("Apertura (HH:MM)", b["apertura"], expand=True)
        cie = c.campo("Cierre (HH:MM)", b["cierre"], expand=True)
        error = ft.Text("", size=12, color=c.ERROR)

        def guardar(dlg):
            ok, msg = self.crud.editar_local(b["id"], nombre.value, cap.value, ape.value, cie.value)
            if ok:
                c.cerrar_dialogo(self.page, dlg)
                c.notificar(self.page, msg)
                self.refrescar()
            else:
                error.value = msg
                self.page.update()

        c.dialogo(self.page, "Editar local",
                  ft.Column([nombre, cap, ft.Row([ape, cie], spacing=10), error],
                            tight=True, width=380, spacing=12), "Guardar", guardar)