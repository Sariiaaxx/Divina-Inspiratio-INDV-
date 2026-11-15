"""Modelo de códigos de invitación de un solo uso (registros/codigos.json)."""
import secrets
from datetime import datetime

from modelo.gestor_modelo import GestorModelo

PREFIJOS = {"autoridad": "AUT", "propietario": "PRO"}
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin caracteres ambiguos


def _bloque(n=4) -> str:
    return "".join(secrets.choice(ALFABETO) for _ in range(n))


class CodigosModel:
    def __init__(self, gestor: GestorModelo = None):
        self.gestor = gestor or GestorModelo("codigos.json")

    @staticmethod
    def _norm(codigo: str) -> str:
        return (codigo or "").strip().upper()

    def listar(self) -> list:
        return list(reversed(self.gestor.leer()))  # más recientes primero

    def generar(self, rol: str) -> dict:
        if rol not in PREFIJOS:
            raise ValueError("Solo se generan códigos para Autoridad y Propietario.")
        codigos = self.gestor.leer()
        existentes = {c["codigo"] for c in codigos}
        while True:
            codigo = f"{PREFIJOS[rol]}-{_bloque()}-{_bloque()}"
            if codigo not in existentes:
                break
        registro = {"codigo": codigo, "rol": rol, "usado": False,
                    "creado": datetime.now().isoformat(timespec="seconds"),
                    "usado_por": None, "usado_en": None}
        codigos.append(registro)
        self.gestor.guardar(codigos)
        return registro

    def validar(self, codigo: str, rol: str) -> bool:
        codigo = self._norm(codigo)
        return any(c["codigo"] == codigo and c["rol"] == rol and not c["usado"]
                   for c in self.gestor.leer())

    def consumir(self, codigo: str, correo: str) -> bool:
        codigo = self._norm(codigo)
        codigos = self.gestor.leer()
        for c in codigos:
            if c["codigo"] == codigo and not c["usado"]:
                c.update(usado=True, usado_por=correo.strip().lower(),
                         usado_en=datetime.now().isoformat(timespec="seconds"))
                self.gestor.guardar(codigos)
                return True
        return False