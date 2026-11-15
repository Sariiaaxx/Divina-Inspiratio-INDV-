"""Utilidad común: lectura/escritura segura de archivos JSON en registros/."""
import json
import os
from datetime import datetime
from pathlib import Path

DIR_REGISTROS = Path(__file__).resolve().parent.parent / "registros"


class ErrorAlmacenamiento(Exception):
    """El archivo JSON no se pudo leer o escribir."""


class GestorModelo:
    def __init__(self, nombre_archivo: str, directorio=DIR_REGISTROS):
        self.archivo = Path(directorio) / nombre_archivo
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            if not self.archivo.exists():
                self.guardar([])
        except OSError as e:
            raise ErrorAlmacenamiento(f"No se pudo preparar 'registros/': {e}")

    def leer(self) -> list:
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if not isinstance(datos, list):
                raise ValueError("Estructura inesperada")
            return datos
        except (json.JSONDecodeError, ValueError):
            copia = self.archivo.with_name(
                f"{self.archivo.stem}.corrupto-{datetime.now():%Y%m%d%H%M%S}.json")
            try:
                os.replace(self.archivo, copia)
            except OSError:
                pass
            self.guardar([])
            raise ErrorAlmacenamiento(
                f"{self.archivo.name} estaba dañado. Se guardó una copia "
                f"({copia.name}) y se creó uno nuevo.")
        except OSError as e:
            raise ErrorAlmacenamiento(f"No se pudo leer {self.archivo.name}: {e}")

    def guardar(self, datos: list):
        tmp = self.archivo.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.archivo)  # escritura atómica
        except OSError as e:
            raise ErrorAlmacenamiento(f"No se pudo guardar {self.archivo.name}: {e}")