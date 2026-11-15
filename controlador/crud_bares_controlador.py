"""Controlador CRUD de locales: aplica los permisos de cada rol."""
from modelo.gestor_modelo import ErrorAlmacenamiento
from modelo.bares_modelo import (
    BaresModelo, ABIERTO, TEMPORAL, PERMANENTE, NUMEROS, NumeroOcupado)
from modelo.usuarios_modelo import UsuariosModel

__all__ = ["CrudBaresControlador", "ABIERTO", "TEMPORAL", "PERMANENTE", "NUMEROS"]

RANGO = {"propietario": 1, "autoridad": 2, "admin": 3}


class CrudBaresControlador:
    def __init__(self, bares: BaresModelo, usuarios: UsuariosModel, sesion):
        self.bares = bares
        self.usuarios = usuarios
        self._sesion = sesion  # función que devuelve el usuario logueado

    @property
    def usuario(self):
        return self._sesion() or {}

    @property
    def rol(self):
        return self.usuario.get("rol")

    # ---------- lectura ----------
    def estado_calle(self):
        """Lista de (numero, local|None) para los 5 huecos de la calle."""
        try:
            activos = {b["numero"]: b for b in self.bares.listar_activos()}
        except ErrorAlmacenamiento:
            activos = {}
        return [(n, activos.get(n)) for n in NUMEROS]

    def numeros_ocupados(self):
        try:
            return self.bares.numeros_ocupados()
        except ErrorAlmacenamiento:
            return []

    def mi_local(self):
        if self.rol != "propietario":
            return None
        try:
            return self.bares.por_propietario(self.usuario.get("id"))
        except ErrorAlmacenamiento:
            return None

    def listar_bares(self):
        """Locales con nombre del propietario. Solo Admin (todos) y Autoridad (activos)."""
        if self.rol not in ("admin", "autoridad"):
            return []
        try:
            lista = self.bares.listar_todos() if self.rol == "admin" else self.bares.listar_activos()
            nombres = {u["id"]: u["nombre"] for u in self.usuarios.listar()}
        except ErrorAlmacenamiento:
            return []
        return [dict(b, propietario_nombre=nombres.get(b.get("propietario_id"), "—"))
                for b in lista]

    def estadisticas(self):
        if self.rol in ("admin", "autoridad"):
            try:
                bares = self.bares.listar_activos()
            except ErrorAlmacenamiento:
                bares = []
        elif self.rol == "propietario":
            bares = [b for b in [self.mi_local()] if b]
        else:
            bares = []
        abiertos = [b for b in bares if b["estado"] == ABIERTO]
        aforo = sum(b["aforo_actual"] for b in abiertos)
        capacidad = sum(b["capacidad"] for b in abiertos)
        return {"total": len(bares), "abiertos": len(abiertos),
                "cerrados": len(bares) - len(abiertos), "aforo": aforo,
                "capacidad": capacidad,
                "ocupacion": round(100 * aforo / capacidad) if capacidad else 0}

    # ---------- permisos ----------
    def _ejecutar(self, accion, mensaje_ok):
        try:
            accion()
        except NumeroOcupado as e:
            return False, str(e)
        except (ValueError, ErrorAlmacenamiento) as e:
            return False, str(e)
        return True, mensaje_ok

    def _es_suyo(self, bar):
        return bar["propietario_id"] == self.usuario.get("id")

    def _bar(self, bar_id):
        bar = self.bares.obtener(bar_id)
        if bar is None or bar["estado"] == PERMANENTE:
            raise ValueError("El local no existe.")
        return bar

    def _comprobar_gestion(self, bar):
        if self.rol in ("admin", "autoridad"):
            return
        if self.rol == "propietario" and self._es_suyo(bar):
            return
        raise ValueError("No tienes permiso sobre este local.")

    # ---------- acciones ----------
    def crear_local(self, nombre, capacidad, numero, apertura, cierre):
        def accion():
            if self.rol != "propietario":
                raise ValueError("Solo los propietarios pueden dar de alta un local.")
            self.bares.crear(nombre, capacidad, numero, self.usuario["id"], apertura, cierre)
        return self._ejecutar(accion, "Local creado correctamente.")

    def editar_local(self, bar_id, nombre, capacidad, apertura, cierre):
        def accion():
            bar = self._bar(bar_id)
            if not (self.rol == "propietario" and self._es_suyo(bar)):
                raise ValueError("Solo el propietario puede editar su local.")
            self.bares.actualizar(bar_id, nombre, capacidad, apertura, cierre)
        return self._ejecutar(accion, "Local actualizado.")

    def ajustar_aforo(self, bar_id, delta):
        """Entrada/salida manual (sustituye al sensor hasta integrarlo)."""
        def accion():
            bar = self._bar(bar_id)
            if not (self.rol == "propietario" and self._es_suyo(bar)):
                raise ValueError("Solo el propietario puede registrar el aforo.")
            self.bares.ajustar_aforo(bar_id, delta)
        return self._ejecutar(accion, "Aforo actualizado.")

    def cerrar_temporal(self, bar_id):
        def accion():
            bar = self._bar(bar_id)
            self._comprobar_gestion(bar)
            self.bares.cambiar_estado(bar_id, TEMPORAL, cerrado_por=self.rol)
        return self._ejecutar(accion, "Local cerrado temporalmente.")

    def abrir(self, bar_id):
        def accion():
            bar = self._bar(bar_id)
            self._comprobar_gestion(bar)
            quien = bar.get("cerrado_por") or "propietario"
            if RANGO[self.rol] < RANGO[quien]:
                nombre = {"autoridad": "la Autoridad", "admin": "el Admin Supremo"}[quien]
                raise ValueError(f"Este local lo cerró {nombre}; solo puede reabrirlo esa figura o una superior.")
            self.bares.cambiar_estado(bar_id, ABIERTO)
        return self._ejecutar(accion, "Local abierto de nuevo.")

    def cerrar_permanente(self, bar_id):
        def accion():
            bar = self._bar(bar_id)
            if self.rol == "admin":
                self.bares.cambiar_estado(bar_id, PERMANENTE, cerrado_por="admin")
            elif self.rol == "propietario" and self._es_suyo(bar):
                self.bares.eliminar(bar_id)  # libera el hueco de la calle
            else:
                raise ValueError("No tienes permiso para cerrar este local definitivamente.")
        return self._ejecutar(accion, "Local cerrado definitivamente. El número de calle queda libre.")