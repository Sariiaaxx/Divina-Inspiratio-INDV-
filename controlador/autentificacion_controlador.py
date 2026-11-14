"""Controlador: conecta la vista de login con el modelo de usuarios."""
import re

from modelo.usuarios_modelo import (
    UsuariosModelo, ErrorAlmacenamiento, UsuarioExistente)

RE_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8


class AutentificacionControlador:
    def __init__(self, modelo: UsuariosModelo, router):
        self.modelo = modelo
        self.router = router
        self.usuario_actual = None

    def iniciar_sesion(self, correo: str, password: str):
        """Devuelve (ok, mensaje). Si ok, navega al dashboard."""
        if not correo.strip() or not password:
            return False, "Introduce tu correo y tu contraseña."
        if not RE_CORREO.match(correo.strip()):
            return False, "El correo electrónico no es válido."
        try:
            usuario = self.modelo.validar_credenciales(correo, password)
        except ErrorAlmacenamiento as e:
            return False, str(e)
        if usuario is None:
            return False, "Correo o contraseña incorrectos."
        self.usuario_actual = usuario
        self.router.navegar("dashboard")
        return True, ""

    def registrar(self, nombre: str, correo: str, password: str, confirmar: str):
        """Devuelve (ok, mensaje). Si ok, inicia sesión automáticamente."""
        if not nombre.strip():
            return False, "Introduce tu nombre."
        if not RE_CORREO.match(correo.strip()):
            return False, "El correo electrónico no es válido."
        if len(password) < MIN_PASSWORD:
            return False, f"La contraseña necesita al menos {MIN_PASSWORD} caracteres."
        if password != confirmar:
            return False, "Las contraseñas no coinciden."
        try:
            self.modelo.registrar(nombre, correo, password)
        except UsuarioExistente:
            return False, "Ya existe una cuenta con ese correo."
        except ErrorAlmacenamiento as e:
            return False, str(e)
        return self.iniciar_sesion(correo, password)

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.router.navegar("login")