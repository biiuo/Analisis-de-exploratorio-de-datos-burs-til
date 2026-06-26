import re
from gestorerrores import GestorErrores

# ─────────────────────────────────────────────
# PATRONES
# ─────────────────────────────────────────────
PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ─────────────────────────────────────────────
# VALIDADORES INDIVIDUALES
# ─────────────────────────────────────────────
def validar_fecha(v: str) -> int:
    # Validar formato YYYY-MM-DD y rango coherente
    if not PATRON_FECHA.match(v):
        return GestorErrores.ERR_FECHA_FORMATO
    anio, mes, dia = int(v[:4]), int(v[5:7]), int(v[8:])
    if not (anio >= 1900 and 1 <= mes <= 12 and 1 <= dia <= 31):
        return GestorErrores.ERR_FECHA_RANGO
    return GestorErrores.EXITO


def validar_precio(v: str) -> int:
    # Decimal > 0 y ≤ 10.000
    try:
        p = float(v)
        if 0 < p <= 10_000:
            return GestorErrores.EXITO
        return GestorErrores.ERR_PRECIO_RANGO
    except ValueError:
        return GestorErrores.ERR_PRECIO_TIPO


def validar_adj_close(v: str, close: str = None) -> int:
    # Debe ser válido y ≤ Close (ajuste por dividendos)
    iRes = validar_precio(v)
    if iRes != GestorErrores.EXITO:
        return iRes
    if close is not None and validar_precio(close) == GestorErrores.EXITO:
        if float(v) > float(close):
            return GestorErrores.ERR_ADJCLOSE_MAYOR
    return GestorErrores.EXITO


def validar_volumen(v: str) -> int:
    # Entero ≥ 0 y ≤ 100.000.000
    try:
        vol = int(v)
        if 0 <= vol <= 100_000_000:
            return GestorErrores.EXITO
        return GestorErrores.ERR_VOLUMEN_RANGO
    except ValueError:
        return GestorErrores.ERR_VOLUMEN_TIPO


def validar_coherencia_ohlc(open_p, high, low, close) -> list:
    # High ≥ Low (crítico), variación ≤ 20% (aviso)
    lErrores = []
    o, h, l, c = float(open_p), float(high), float(low), float(close)

    if h < l:
        lErrores.append(GestorErrores.ERR_OHLC_HIGH_LOW)
   
    return lErrores


# ─────────────────────────────────────────────
# HELPER: pedir campo con reintento
# ─────────────────────────────────────────────
def pedir_campo(nombre: str, fnValidador, sError: str) -> str:
    # Pedir dato y reintentar si validación falla
    while True:
        v = input(f"  {nombre}: ").strip()
        if fnValidador(v) == GestorErrores.EXITO:
            return v
        print(f"  ⚠  {sError}. Inténtalo de nuevo.")
