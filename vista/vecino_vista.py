"""Dashboard del Vecino: vista de solo lectura de la calle."""
from datetime import datetime

import flet as ft

from vista import componentes_vista as c
from vista.base_vista import PanelBase


class VecinoVista(PanelBase):
    SECCIONES = [("calle", ft.Icons.STOREFRONT, "La calle")]

    def render(self, clave):
        pesos = [0.6, 2.2, 1.7, 2.2, 1.6]
        filas = [c.fila(["Nº", "Local", "Estado", "Aforo disponible", "Horario"], pesos, True)]
        for numero, b in self.crud.estado_calle():
            if b is None:
                filas.append(c.fila([str(numero), ft.Text("Sin local", color=c.SUAVE),
                                     c.chip("Libre", "gris"), "—", "—"], pesos))
                continue
            if b["estado"] == c.ABIERTO:
                libres = b["capacidad"] - b["aforo_actual"]
                aforo = ft.Column([
                    ft.Text(f"{libres} libres de {b['capacidad']}", size=13, color=c.TEXTO),
                    c.barra_aforo(b["aforo_actual"], b["capacidad"], 140)], spacing=4)
            else:
                aforo = ft.Text("—", color=c.SUAVE)
            filas.append(c.fila([str(numero),
                                 ft.Text(b["nombre"], size=13, weight=ft.FontWeight.BOLD, color=c.TEXTO),
                                 c.chip_estado(b), aforo, f"{b['apertura']} – {b['cierre']}"], pesos))
        actualizar = c.boton("Actualizar", lambda e: self.refrescar(),
                             "suave", icono=ft.Icons.REFRESH)
        pie = ft.Text(f"Última actualización: {datetime.now():%H:%M:%S}", size=12, color=c.SUAVE)
        return ("La calle", "Qué locales están abiertos y cuánto aforo queda",
                [c.tarjeta(ft.Column([c.encabezado("Estado de los locales",
                 "Vista de solo lectura", actualizar), ft.Column(filas, spacing=0), pie], spacing=12))])