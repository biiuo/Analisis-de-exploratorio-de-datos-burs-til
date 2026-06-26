"""
RegistroBmw - Entidad de Cotización Bursátil de BMW
====================================================
Representa un registro individual del dataset de cotizaciones de BMW.
Cada atributo se valida rigurosamente en su setter mediante properties.
La clave de identidad es la fecha (sDate), que identifica de forma
única cada sesión bursátil.
Sigue el patrón del profesor: properties con validación + lista de errores.
"""

import re
from gestor_errores import GestorErrores

# Patrón regex para validar formato de fecha YYYY-MM-DD
S_PATRON_FECHA = r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'


class RegistroBmw:
    def __init__(self, sDate, fAdjClose, fClose, fHigh, fLow, fOpen, iVolume):
        self._lErrores = []

        # Inicialización de atributos privados con valores por defecto
        self._sDate = ""
        self._fAdjClose = 0.0
        self._fClose = 0.0
        self._fHigh = 0.0
        self._fLow = 0.0
        self._fOpen = 0.0
        self._iVolume = 0

        # Asignación mediante setters (dispara las validaciones)
        self.sDate = sDate
        self.fAdjClose = fAdjClose
        self.fClose = fClose
        self.fHigh = fHigh
        self.fLow = fLow
        self.fOpen = fOpen
        self.iVolume = iVolume

    # =====================
    # PROPERTY: sDate
    # =====================
    @property
    def sDate(self):
        return self._sDate

    @sDate.setter
    def sDate(self, val):
        if not isinstance(val, str):
            self._lErrores.append(GestorErrores.ERR_DATE_TIPO)
        elif len(val.strip()) == 0:
            self._lErrores.append(GestorErrores.ERR_DATE_VACIO)
        elif not re.match(S_PATRON_FECHA, val.strip()):
            self._lErrores.append(GestorErrores.ERR_DATE_FORMATO)
        else:
            self._sDate = val.strip()

    # =====================
    # PROPERTY: fAdjClose
    # =====================
    @property
    def fAdjClose(self):
        return self._fAdjClose

    @fAdjClose.setter
    def fAdjClose(self, val):
        if not isinstance(val, (int, float)):
            self._lErrores.append(GestorErrores.ERR_ADJCLOSE_TIPO)
        elif val < 0:
            self._lErrores.append(GestorErrores.ERR_ADJCLOSE_RANGO)
        else:
            self._fAdjClose = float(val)

    # =====================
    # PROPERTY: fClose
    # =====================
    @property
    def fClose(self):
        return self._fClose

    @fClose.setter
    def fClose(self, val):
        if not isinstance(val, (int, float)):
            self._lErrores.append(GestorErrores.ERR_CLOSE_TIPO)
        elif val < 0:
            self._lErrores.append(GestorErrores.ERR_CLOSE_RANGO)
        else:
            self._fClose = float(val)

    # =====================
    # PROPERTY: fHigh
    # =====================
    @property
    def fHigh(self):
        return self._fHigh

    @fHigh.setter
    def fHigh(self, val):
        if not isinstance(val, (int, float)):
            self._lErrores.append(GestorErrores.ERR_HIGH_TIPO)
        elif val < 0:
            self._lErrores.append(GestorErrores.ERR_HIGH_RANGO)
        else:
            self._fHigh = float(val)

    # =====================
    # PROPERTY: fLow
    # =====================
    @property
    def fLow(self):
        return self._fLow

    @fLow.setter
    def fLow(self, val):
        if not isinstance(val, (int, float)):
            self._lErrores.append(GestorErrores.ERR_LOW_TIPO)
        elif val < 0:
            self._lErrores.append(GestorErrores.ERR_LOW_RANGO)
        else:
            self._fLow = float(val)

    # =====================
    # PROPERTY: fOpen
    # =====================
    @property
    def fOpen(self):
        return self._fOpen

    @fOpen.setter
    def fOpen(self, val):
        if not isinstance(val, (int, float)):
            self._lErrores.append(GestorErrores.ERR_OPEN_TIPO)
        elif val < 0:
            self._lErrores.append(GestorErrores.ERR_OPEN_RANGO)
        else:
            self._fOpen = float(val)

    # =====================
    # PROPERTY: iVolume
    # =====================
    @property
    def iVolume(self):
        return self._iVolume

    @iVolume.setter
    def iVolume(self, val):
        if not isinstance(val, int):
            self._lErrores.append(GestorErrores.ERR_VOLUME_TIPO)
        elif val < 0:
            self._lErrores.append(GestorErrores.ERR_VOLUME_RANGO)
        else:
            self._iVolume = val

    # =====================
    # MÉTODOS DE IGUALDAD E IDENTIDAD
    # =====================
    def __eq__(self, other):
        """Dos registros son iguales si comparten la misma fecha (clave de identidad)."""
        if isinstance(other, RegistroBmw):
            return self._sDate == other.sDate
        return False

    def __str__(self):
        """Representación legible del registro bursátil."""
        return (f"[BMW] {self._sDate} | Open: {self._fOpen:.2f} | "
                f"Close: {self._fClose:.2f} | High: {self._fHigh:.2f} | "
                f"Low: {self._fLow:.2f} | Vol: {self._iVolume}")

    # =====================
    # GESTIÓN DE ERRORES
    # =====================
    def getErrores(self):
        """Devuelve la lista de errores detectados durante la validación."""
        return self._lErrores

    def esValido(self):
        """
        Comprueba que el registro pasó todas las validaciones.
        Un registro es válido si no tiene errores y todos sus campos
        tienen valores asignados (no quedaron en sus defaults).
        """
        return (len(self._lErrores) == 0 and
                self._sDate != "" and
                self._fOpen >= 0 and
                self._iVolume >= 0)
