"""Modelo de locales (registros/bares.json): CRUD."""
import re
import secrets

from modelo.gestor_modelo import GestorModelo

ABIERTO = "abierto"
TEMPORAL = "cerrado_temporal"
PERMANENTE = "cerrado_permanente"
NUMEROS = (1, 2, 3, 4, 5)
RE_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class NumeroOcupado(ValueError):
    """El número de la calle ya lo usa otro local."""


class BaresModelo:
    def __init__(self, gestor: GestorModelo = None):
        self.gestor = gestor or GestorModelo("bares.json")

    # ---------- lectura ----------
    def listar_todos(self) -> list:
        return sorted(self.gestor.leer(), key=lambda b: b.get("numero", 0))

    def listar_activos(self) -> list:
        """Locales que ocupan un hueco en la calle (no cerrados definitivamente)."""
        return [b for b in self.listar_todos() if b.get("estado") != PERMANENTE]

    def obtener(self, bar_id: str):
        return next((b for b in self.gestor.leer() if b.get("id") == bar_id), None)

    def por_propietario(self, uid: str):
        return next((b for b in self.listar_activos() if b.get("propietario_id") == uid), None)

    def numeros_ocupados(self) -> list:
        return sorted(b["numero"] for b in self.listar_activos())

    # ---------- validación ----------
    @staticmethod
    def _entero(valor, campo):
        try:
            return int(str(valor).strip())
        except ValueError:
            raise ValueError(f"{campo} debe ser un número entero.")

    def _validar(self, nombre, capacidad, apertura, cierre):
        nombre = (nombre or "").strip()
        if not 2 <= len(nombre) <= 40:
            raise ValueError("El nombre debe tener entre 2 y 40 caracteres.")
        capacidad = self._entero(capacidad, "La capacidad")
        if not 1 <= capacidad <= 5000:
            raise ValueError("La capacidad debe estar entre 1 y 5000 personas.")
        apertura, cierre = (apertura or "").strip(), (cierre or "").strip()
        if not (RE_HORA.match(apertura) and RE_HORA.match(cierre)):
            raise ValueError("Los horarios deben tener formato HH:MM (por ejemplo 18:00).")
        return nombre, capacidad, apertura, cierre

    # ---------- escritura ----------
    def crear(self, nombre, capacidad, numero, propietario_id, apertura="18:00", cierre="02:00"):
        nombre, capacidad, apertura, cierre = self._validar(nombre, capacidad, apertura, cierre)
        numero = self._entero(numero, "El número de calle")
        if numero not in NUMEROS:
            raise ValueError("El número de calle debe estar entre 1 y 5.")
        if self.por_propietario(propietario_id):
            raise ValueError("Ya tienes un local dado de alta. Solo se permite uno por propietario.")
        if numero in self.numeros_ocupados():
            raise NumeroOcupado(f"El número {numero} de la calle ya está ocupado.")
        bares = self.gestor.leer()
        bar = {"id": secrets.token_hex(6), "nombre": nombre, "capacidad": capacidad,
               "numero": numero, "estado": ABIERTO, "cerrado_por": None,
               "propietario_id": propietario_id, "apertura": apertura,
               "cierre": cierre, "aforo_actual": 0}
        bares.append(bar)
        self.gestor.guardar(bares)
        return bar

    def _modificar(self, bar_id, cambio):
        bares = self.gestor.leer()
        for b in bares:
            if b.get("id") == bar_id:
                cambio(b)
                self.gestor.guardar(bares)
                return b
        raise ValueError("El local no existe.")

    def actualizar(self, bar_id, nombre, capacidad, apertura, cierre):
        nombre, capacidad, apertura, cierre = self._validar(nombre, capacidad, apertura, cierre)

        def cambio(b):
            b.update(nombre=nombre, capacidad=capacidad, apertura=apertura, cierre=cierre)
            b["aforo_actual"] = min(b.get("aforo_actual", 0), capacidad)
        return self._modificar(bar_id, cambio)

    def ajustar_aforo(self, bar_id, delta):
        def cambio(b):
            if b["estado"] != ABIERTO:
                raise ValueError("El local está cerrado.")
            b["aforo_actual"] = max(0, min(b["capacidad"], b.get("aforo_actual", 0) + delta))
        return self._modificar(bar_id, cambio)

    def cambiar_estado(self, bar_id, estado, cerrado_por=None):
        def cambio(b):
            b["estado"] = estado
            b["cerrado_por"] = None if estado == ABIERTO else cerrado_por
            if estado != ABIERTO:
                b["aforo_actual"] = 0
        return self._modificar(bar_id, cambio)

    def eliminar(self, bar_id) -> bool:
        bares = self.gestor.leer()
        restantes = [b for b in bares if b.get("id") != bar_id]
        if len(restantes) == len(bares):
            return False
        self.gestor.guardar(restantes)
        return True

    def eliminar_de_propietario(self, uid) -> int:
        bares = self.gestor.leer()
        restantes = [b for b in bares if b.get("propietario_id") != uid]
        if len(restantes) != len(bares):
            self.gestor.guardar(restantes)
        return len(bares) - len(restantes)