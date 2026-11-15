"""Controlador de autenticación, roles, códigos y gestión de usuarios."""
import re

from modelo.gestor_modelo import ErrorAlmacenamiento
from modelo.usuarios_modelo import UsuariosModel, UsuarioExistente
from modelo.codigos_modelo import CodigosModel
from modelo.bares_modelo import BaresModelo

RE_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8
ROLES_REGISTRO = ("vecino", "propietario", "autoridad")


class AutentificacionControlador:
    def __init__(self, usuarios: UsuariosModel, codigos: CodigosModel,
                 bares: BaresModelo, router):
        self.usuarios = usuarios
        self.codigos = codigos
        self.bares = bares
        self.router = router
        self.usuario_actual = None

    @property
    def rol(self):
        return (self.usuario_actual or {}).get("rol")

    # ---------- sesión ----------
    def iniciar_sesion(self, correo: str, password: str):
        if not correo.strip() or not password:
            return False, "Introduce tu correo y tu contraseña."
        if not RE_CORREO.match(correo.strip()):
            return False, "El correo electrónico no es válido."
        try:
            usuario = self.usuarios.validar_credenciales(correo, password)
        except ErrorAlmacenamiento as e:
            return False, str(e)
        if usuario is None:
            return False, "Correo o contraseña incorrectos."
        self.usuario_actual = usuario
        self.router.navegar("dashboard")  # el router elige la vista según el rol
        return True, ""

    def registrar(self, nombre, correo, password, confirmar, rol="vecino", codigo=""):
        if not nombre.strip():
            return False, "Introduce tu nombre."
        if not RE_CORREO.match(correo.strip()):
            return False, "El correo electrónico no es válido."
        if len(password) < MIN_PASSWORD:
            return False, f"La contraseña necesita al menos {MIN_PASSWORD} caracteres."
        if password != confirmar:
            return False, "Las contraseñas no coinciden."
        if rol not in ROLES_REGISTRO:
            return False, "Tipo de cuenta no válido."
        try:
            if rol != "vecino":
                if not codigo.strip():
                    return False, "Introduce el código de invitación."
                if not self.codigos.validar(codigo, rol):
                    return False, ("Código de registro inválido: no existe, ya se usó "
                                   "o corresponde a otro tipo de cuenta.")
            self.usuarios.registrar(nombre, correo, password, rol)
            if rol != "vecino":
                self.codigos.consumir(codigo, correo)
        except UsuarioExistente:
            return False, "Ya existe una cuenta con ese correo."
        except (ErrorAlmacenamiento, ValueError) as e:
            return False, str(e)
        return self.iniciar_sesion(correo, password)

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.router.navegar("login")

    # ---------- acciones del Admin Supremo ----------
    def _solo_admin(self):
        return None if self.rol == "admin" else (False, "Acción reservada al Admin Supremo.")

    def listar_usuarios(self):
        if self.rol != "admin":
            return []
        try:
            return self.usuarios.listar()
        except ErrorAlmacenamiento:
            return []

    def listar_codigos(self):
        if self.rol != "admin":
            return []
        try:
            return self.codigos.listar()
        except ErrorAlmacenamiento:
            return []

    def generar_codigo(self, rol: str):
        """Devuelve (True, codigo) o (False, mensaje_error)."""
        if self._solo_admin():
            return self._solo_admin()
        try:
            return True, self.codigos.generar(rol)["codigo"]
        except (ValueError, ErrorAlmacenamiento) as e:
            return False, str(e)

    def eliminar_usuario(self, uid: str):
        if self._solo_admin():
            return self._solo_admin()
        if uid == self.usuario_actual.get("id"):
            return False, "No puedes darte de baja a ti mismo."
        try:
            objetivo = next((u for u in self.usuarios.listar() if u["id"] == uid), None)
            if objetivo is None:
                return False, "El usuario ya no existe."
            if objetivo["rol"] == "admin":
                return False, "El Admin Supremo no puede darse de baja."
            self.usuarios.eliminar(uid)
            if objetivo["rol"] == "propietario":
                self.bares.eliminar_de_propietario(uid)  # libera su hueco en la calle
        except ErrorAlmacenamiento as e:
            return False, str(e)
        return True, f"Usuario «{objetivo['nombre']}» dado de baja."