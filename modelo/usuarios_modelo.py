"""Modelo de usuarios (registros/usuarios.json) con roles."""
import hashlib
import hmac
import secrets
from datetime import datetime

from modelo.gestor_modelo import GestorModelo, ErrorAlmacenamiento

ROLES = ("admin", "autoridad", "propietario", "vecino")
ITERACIONES = 200_000

# Admin Supremo preestablecido (cambia la contraseña tras el primer acceso).
ADMIN_NOMBRE = "Admin Supremo"
ADMIN_CORREO = "admin@divineinspiratio.com"
ADMIN_PASSWORD = "Admin2026!"


class UsuarioExistente(Exception):
    """Ya hay un usuario con ese correo."""


class UsuariosModel:
    def __init__(self, gestor: GestorModelo = None):
        self.gestor = gestor or GestorModelo("usuarios.json")
        self._asegurar_admin()

    # ---------- utilidades ----------
    @staticmethod
    def _hash(password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), ITERACIONES).hex()

    @staticmethod
    def _normalizar(correo: str) -> str:
        return correo.strip().lower()

    def _nuevo(self, nombre, correo, password, rol) -> dict:
        salt = secrets.token_hex(16)
        return {
            "id": secrets.token_hex(8),
            "nombre": nombre.strip(),
            "correo": self._normalizar(correo),
            "salt": salt,
            "password_hash": self._hash(password, salt),
            "rol": rol,
            "creado": datetime.now().isoformat(timespec="seconds"),
        }

    def _asegurar_admin(self):
        try:
            usuarios = self.gestor.leer()
        except ErrorAlmacenamiento:
            usuarios = self.gestor.leer()  # tras el reinicio queda vacío
        cambios = False
        for u in usuarios:  # migración: roles de la Fase 1 -> vecino
            if u.get("rol") not in ROLES:
                u["rol"] = "vecino"
                cambios = True
        if not any(u.get("rol") == "admin" for u in usuarios):
            usuarios.append(self._nuevo(ADMIN_NOMBRE, ADMIN_CORREO, ADMIN_PASSWORD, "admin"))
            cambios = True
        if cambios:
            self.gestor.guardar(usuarios)

    def _leer(self) -> list:
        try:
            return self.gestor.leer()
        except ErrorAlmacenamiento:
            try:
                self._asegurar_admin()  # restaura al Admin si el archivo se reinició
            except ErrorAlmacenamiento:
                pass
            raise

    # ---------- operaciones ----------
    def listar(self) -> list:
        return self._leer()

    def buscar_por_correo(self, correo: str):
        correo = self._normalizar(correo)
        return next((u for u in self._leer() if u.get("correo") == correo), None)

    def registrar(self, nombre: str, correo: str, password: str, rol: str = "vecino") -> dict:
        if rol not in ROLES or rol == "admin":
            raise ValueError("Rol no permitido en el registro.")
        usuarios = self._leer()
        if any(u.get("correo") == self._normalizar(correo) for u in usuarios):
            raise UsuarioExistente(correo)
        usuario = self._nuevo(nombre, correo, password, rol)
        usuarios.append(usuario)
        self.gestor.guardar(usuarios)
        return usuario

    def eliminar(self, uid: str):
        """Elimina y devuelve el usuario, o None si no existe."""
        usuarios = self._leer()
        for i, u in enumerate(usuarios):
            if u.get("id") == uid:
                borrado = usuarios.pop(i)
                self.gestor.guardar(usuarios)
                return borrado
        return None

    def validar_credenciales(self, correo: str, password: str):
        usuario = self.buscar_por_correo(correo)
        if not usuario:
            return None
        try:
            calculado = self._hash(password, usuario["salt"])
        except (KeyError, ValueError):
            return None
        return usuario if hmac.compare_digest(usuario.get("password_hash", ""), calculado) else None