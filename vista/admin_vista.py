"""Dashboard del Admin Supremo."""
import flet as ft

from vista import componentes_vista as c
from vista.base_vista import PanelBase


class AdminVista(PanelBase):
    SECCIONES = [("dashboard", ft.Icons.DASHBOARD, "Dashboard"),
                 ("bares", ft.Icons.STOREFRONT, "Bares"),
                 ("usuarios", ft.Icons.GROUP, "Usuarios"),
                 ("codigos", ft.Icons.VPN_KEY, "Códigos")]

    def render(self, clave):
        return getattr(self, f"_{clave}")()

    # ---------- secciones ----------
    def _dashboard(self):
        n_usuarios = c.stat("USUARIOS", len(self.auth.listar_usuarios()), "cuentas registradas")
        return ("Dashboard", "Resumen general de toda la calle",
                [self.bloque_stats([n_usuarios]), self.bloque_sensores()])

    def _bares(self):
        tabla = self.tabla_bares(self.crud.listar_bares(),
                                 lambda b: self.acciones_cierre(b, definitivo=True))
        return ("Gestión de locales", "Cierra locales de forma temporal o permanente",
                [c.tarjeta(ft.Column([c.encabezado("Locales de la calle"), tabla], spacing=12))])

    def _usuarios(self):
        pesos = [2.4, 2.6, 1.4, 1.4, 1.6]
        filas = [c.fila(["Nombre", "Correo electrónico", "Rol", "Alta", "Acciones"], pesos, True)]
        for u in self.auth.listar_usuarios():
            nombre = ft.Row([c.avatar(u["nombre"]), ft.Text(u["nombre"], size=13, color=c.TEXTO,
                             weight=ft.FontWeight.BOLD)], spacing=10)
            accion = (ft.Text("—", color=c.SUAVE) if u["rol"] == "admin" or u["id"] == self.usuario.get("id")
                      else c.boton("Dar de baja", lambda e, u=u: self._baja(u), "peligro", pequeno=True))
            filas.append(c.fila([nombre, ft.Text(u["correo"], size=13, color=c.SUAVE),
                                 c.chip(c.ETIQUETA_ROL[u["rol"]], c.TONO_ROL[u["rol"]]),
                                 u.get("creado", "")[:10], accion], pesos))
        return ("Gestión de usuarios", "Da de baja cuentas de cualquier rol",
                [c.tarjeta(ft.Column([c.encabezado("Todos los usuarios",
                 "Al dar de baja a un propietario, su local se elimina y su número queda libre."),
                 ft.Column(filas, spacing=0)], spacing=12))])

    def _codigos(self):
        acciones = ft.Row([c.boton("Código Autoridad", lambda e: self._generar("autoridad"),
                                   icono=ft.Icons.ADD),
                           c.boton("Código Propietario", lambda e: self._generar("propietario"),
                                   icono=ft.Icons.ADD)], spacing=10)
        pesos = [2.6, 1.4, 1.4, 2.6]
        filas = [c.fila(["Código", "Tipo", "Estado", "Usado por"], pesos, True)]
        for k in self.auth.listar_codigos():
            filas.append(c.fila([
                ft.Text(k["codigo"], size=13, weight=ft.FontWeight.BOLD, color=c.TEXTO, selectable=True),
                c.chip(c.ETIQUETA_ROL[k["rol"]], c.TONO_ROL[k["rol"]]),
                c.chip("Usado", "gris") if k["usado"] else c.chip("Disponible", "verde"),
                k.get("usado_por") or "—"], pesos))
        if len(filas) == 1:
            filas.append(ft.Container(padding=24, content=ft.Text(
                "Aún no has generado códigos.", color=c.SUAVE)))
        return ("Códigos de registro", "Invitaciones de un solo uso para Autoridad y Propietario",
                [c.tarjeta(ft.Column([c.encabezado("Códigos generados", None, acciones),
                                      ft.Column(filas, spacing=0)], spacing=12))])

    # ---------- acciones ----------
    def _baja(self, u):
        c.confirmar(self.page, "Dar de baja",
                    f"¿Eliminar la cuenta de «{u['nombre']}» ({c.ETIQUETA_ROL[u['rol']]})? "
                    "Esta acción no se puede deshacer.",
                    lambda: self.ejecutar(self.auth.eliminar_usuario(u["id"])), "Dar de baja")

    def _generar(self, rol):
        ok, resultado = self.auth.generar_codigo(rol)
        if not ok:
            return c.notificar(self.page, resultado, error=True)
        self.refrescar()
        c.abrir_dialogo(self.page, ft.AlertDialog(
            bgcolor=c.PANEL, title=ft.Text("Código generado", color=c.TEXTO),
            content=ft.Column([
                ft.Text(f"Entrega este código a la persona invitada ({c.ETIQUETA_ROL[rol]}). "
                        "Solo se puede usar una vez.", color=c.SUAVE),
                ft.Text(resultado, size=24, weight=ft.FontWeight.BOLD, color=c.ACENTO, selectable=True)],
                tight=True, width=360)))