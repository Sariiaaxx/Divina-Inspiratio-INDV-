"""Modelo: lectura/escritura de usuarios en registros/usuarios.json."""
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_REGISTROS = RAIZ / "registros"
ARCHIVO_USUARIOS = DIR_REGISTROS / "usuarios.json"
ITERACIONES = 200_000


class ErrorAlmacenamiento(Exception):
    """El archivo JSON no se pudo leer o escribir."""


class UsuarioExistente(Exception):
    """Ya hay un usuario con ese correo."""


class UsuariosModelo:
    def __init__(self, archivo: Path = ARCHIVO_USUARIOS):
        self.archivo = Path(archivo)
        self._preparar_almacenamiento()

    # ---------- almacenamiento ----------
    def _preparar_almacenamiento(self):
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            if not self.archivo.exists():
                self._guardar([])
        except OSError as e:
            raise ErrorAlmacenamiento(f"No se pudo preparar 'registros/': {e}")

    def _leer(self) -> list:
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if not isinstance(datos, list):
                raise ValueError("Estructura inesperada")
            return datos
        except (json.JSONDecodeError, ValueError):
            # Archivo corrupto: se conserva una copia y se avisa.
            copia = self.archivo.with_name(
                f"usuarios.corrupto-{datetime.now():%Y%m%d%H%M%S}.json")
            try:
                os.replace(self.archivo, copia)
            except OSError:
                pass
            self._guardar([])
            raise ErrorAlmacenamiento(
                "El archivo de usuarios estaba dañado. Se guardó una copia "
                f"({copia.name}) y se creó uno nuevo. Vuelve a registrarte.")
        except OSError as e:
            raise ErrorAlmacenamiento(f"No se pudo leer usuarios.json: {e}")

    def _guardar(self, usuarios: list):
        tmp = self.archivo.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(usuarios, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.archivo)  # escritura atómica
        except OSError as e:
            raise ErrorAlmacenamiento(f"No se pudo guardar usuarios.json: {e}")

    # ---------- contraseñas ----------
    @staticmethod
    def _hash(password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), ITERACIONES).hex()

    @staticmethod
    def _normalizar(correo: str) -> str:
        return correo.strip().lower()

    # ---------- operaciones ----------
    def buscar_por_correo(self, correo: str):
        correo = self._normalizar(correo)
        for u in self._leer():
            if u.get("correo") == correo:
                return u
        return None

    def registrar(self, nombre: str, correo: str, password: str) -> dict:
        usuarios = self._leer()
        correo = self._normalizar(correo)
        if any(u.get("correo") == correo for u in usuarios):
            raise UsuarioExistente(correo)
        salt = secrets.token_hex(16)
        usuario = {
            "id": secrets.token_hex(8),
            "nombre": nombre.strip(),
            "correo": correo,
            "salt": salt,
            "password_hash": self._hash(password, salt),
            "rol": "Administrador" if not usuarios else "Usuario",
            "creado": datetime.now().isoformat(timespec="seconds"),
        }
        usuarios.append(usuario)
        self._guardar(usuarios)
        return usuario

    def validar_credenciales(self, correo: str, password: str):
        """Devuelve el usuario si las credenciales son correctas, o None."""
        usuario = self.buscar_por_correo(correo)
        if not usuario:
            return None
        try:
            calculado = self._hash(password, usuario["salt"])
        except (KeyError, ValueError):
            return None
        esperado = usuario.get("password_hash", "")
        return usuario if hmac.compare_digest(esperado, calculado) else None