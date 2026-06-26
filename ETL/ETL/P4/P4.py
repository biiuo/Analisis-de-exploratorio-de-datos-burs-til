# =============================================================================
# PROBLEMA 4 - PARADIGMA FUNCIONAL DECLARATIVO
# =============================================================================
# Dataset: BMW Stock Data (12_bmw_data.csv)
# Columnas: Date, Adj_Close, Close, High, Low, Open, Volume
#
# RESTRICCIONES DEL ENUNCIADO:
#   - Prohibido usar bucles (for, while) o variables de estado temporales
#   - Todo debe resolverse con funciones de orden superior (map, filter, reduce)
#   - Fábricas de predicados (funciones que generan funciones)
#   - Reducción compleja a estructura jerárquica
#   - Comprensiones avanzadas multinivel
# =============================================================================

import csv
from functools import reduce
from datetime import datetime

# =============================================================================
# SECCIÓN 1: CARGA INMUTABLE DEL DATASET (sin bucles)
# =============================================================================
# Leemos el CSV y lo convertimos a una tupla de diccionarios inmutables.
# Usamos map() para transformar cada fila cruda en un diccionario tipado.

def cargar_dataset(sRuta):
    """
    Carga el CSV y devuelve una tupla inmutable de diccionarios.
    Cada diccionario representa un registro bursátil de BMW.
    Se usa map() en lugar de bucles para la transformación.
    """
    with open(sRuta, newline='', encoding='utf-8') as oFichero:
        oLector = csv.reader(oFichero)
        lCabecera = next(oLector)  # Extraemos la cabecera
        lFilas = list(oLector)     # Leemos todas las filas restantes

    # Función de transformación: convierte una fila cruda en un dict tipado
    def _transformar_fila(lFila):
        return {
            "sDate":      lFila[0],
            "fAdjClose":  round(float(lFila[1]), 4),
            "fClose":     round(float(lFila[2]), 4),
            "fHigh":      round(float(lFila[3]), 4),
            "fLow":       round(float(lFila[4]), 4),
            "fOpen":      round(float(lFila[5]), 4),
            "iVolume":    int(lFila[6])
        }

    # map() aplica la transformación a cada fila sin usar bucle
    return tuple(map(_transformar_fila, lFilas))


# =============================================================================
# SECCIÓN 2: FÁBRICAS DE PREDICADOS (funciones que generan funciones)
# =============================================================================
# Permiten crear filtros dinámicos sin alterar el núcleo del sistema.
# El usuario define condiciones en tiempo de ejecución.

def fabrica_filtro_rango(sCampo, fMinimo, fMaximo):
    """
    Fábrica de predicados: genera una función lambda que filtra registros
    cuyo campo numérico esté dentro del rango [fMinimo, fMaximo].
    
    Ejemplo de uso:
        fnFiltro = fabrica_filtro_rango("fClose", 50.0, 80.0)
        lResultado = list(filter(fnFiltro, tDataset))
    """
    return lambda dRegistro: fMinimo <= dRegistro[sCampo] <= fMaximo


def fabrica_filtro_anio(iAnio):
    """
    Fábrica de predicados: genera un filtro por año extraído de la fecha.
    Devuelve una función que retorna True si el registro pertenece a iAnio.
    """
    sAnio = str(iAnio)
    return lambda dRegistro: dRegistro["sDate"].startswith(sAnio)


def fabrica_filtro_volumen_minimo(iUmbral):
    """
    Fábrica de predicados: filtra registros con volumen >= iUmbral.
    Útil para descartar días de baja liquidez bursátil.
    """
    return lambda dRegistro: dRegistro["iVolume"] >= iUmbral


def fabrica_filtro_volatilidad_minima(fUmbral):
    """
    Fábrica de predicados: filtra días donde la diferencia High-Low
    (volatilidad intradía) supere un umbral dado.
    """
    return lambda dRegistro: (dRegistro["fHigh"] - dRegistro["fLow"]) >= fUmbral


# =============================================================================
# SECCIÓN 3: CADENA DE FUNCIONES DE ORDEN SUPERIOR (filter -> map -> reduce)
# =============================================================================
# Pipeline funcional: el resultado de filter alimenta a map, y este a reduce.
# Toda la lógica se expresa como composición de funciones, sin variables de estado.

def pipeline_analisis_anual(tDataset, iAnio, fVolatilidadMin):
    """
    Cadena funcional completa: SEGMENTACIÓN -> TRANSFORMACIÓN -> CONSOLIDACIÓN.
    
    1. filter(): selecciona registros del año indicado con volatilidad mínima
    2. map(): transforma cada registro en una tupla enriquecida con métricas derivadas
    3. reduce(): consolida todo en un diccionario resumen jerárquico
    
    No se usan bucles ni variables de estado intermedias.
    """

    # --- PASO 1: SEGMENTACIÓN (composición de dos filtros) ---
    # Combinamos dos fábricas de predicados en un solo filtro compuesto
    fnFiltroAnio = fabrica_filtro_anio(iAnio)
    fnFiltroVolatilidad = fabrica_filtro_volatilidad_minima(fVolatilidadMin)

    # Filtro compuesto: ambas condiciones deben cumplirse simultáneamente
    tFiltrado = tuple(filter(
        lambda dReg: fnFiltroAnio(dReg) and fnFiltroVolatilidad(dReg),
        tDataset
    ))

    # Si no hay datos tras el filtrado, devolvemos estructura vacía
    if len(tFiltrado) == 0:
        return {"iAnio": iAnio, "iRegistros": 0, "sMensaje": "Sin datos para estos criterios"}

    # --- PASO 2: TRANSFORMACIÓN (map) ---
    # Enriquecemos cada registro con campos derivados calculados al vuelo
    tTransformado = tuple(map(
        lambda dReg: {
            **dReg,  # Spread del registro original (inmutabilidad)
            "fVolatilidad":    round(dReg["fHigh"] - dReg["fLow"], 4),
            "fRendimiento":    round(((dReg["fClose"] - dReg["fOpen"]) / dReg["fOpen"]) * 100, 4),
            "sMes":            dReg["sDate"][5:7]  # Extraemos el mes de la fecha
        },
        tFiltrado
    ))

    # --- PASO 3: CONSOLIDACIÓN (reduce) ---
    # Reducción compleja: construimos una estructura jerárquica de reporte
    # El acumulador es un diccionario que se enriquece con cada registro procesado
    dReporte = reduce(
        lambda dAcc, dReg: {
            "iAnio":               iAnio,
            "iRegistros":          dAcc["iRegistros"] + 1,
            "fSumaClose":          dAcc["fSumaClose"] + dReg["fClose"],
            "fSumaVolatilidad":    dAcc["fSumaVolatilidad"] + dReg["fVolatilidad"],
            "fSumaRendimiento":    dAcc["fSumaRendimiento"] + dReg["fRendimiento"],
            "fMaxHigh":            max(dAcc["fMaxHigh"], dReg["fHigh"]),
            "fMinLow":             min(dAcc["fMinLow"], dReg["fLow"]),
            "iSumaVolumen":        dAcc["iSumaVolumen"] + dReg["iVolume"],
            "fMaxVolatilidad":     max(dAcc["fMaxVolatilidad"], dReg["fVolatilidad"]),
            "sFechaMasVolatil":    dReg["sDate"] if dReg["fVolatilidad"] > dAcc["fMaxVolatilidad"] else dAcc["sFechaMasVolatil"],
            # Acumulamos registros por mes para el desglose jerárquico
            "dMeses":              {
                **dAcc["dMeses"],
                dReg["sMes"]: {
                    "iDias":           dAcc["dMeses"].get(dReg["sMes"], {}).get("iDias", 0) + 1,
                    "fSumaClose":      dAcc["dMeses"].get(dReg["sMes"], {}).get("fSumaClose", 0.0) + dReg["fClose"],
                    "fSumaVolatilidad": dAcc["dMeses"].get(dReg["sMes"], {}).get("fSumaVolatilidad", 0.0) + dReg["fVolatilidad"],
                }
            }
        },
        tTransformado,
        # Valor inicial del acumulador (semilla del reduce)
        {
            "iAnio": iAnio, "iRegistros": 0,
            "fSumaClose": 0.0, "fSumaVolatilidad": 0.0, "fSumaRendimiento": 0.0,
            "fMaxHigh": 0.0, "fMinLow": float('inf'), "iSumaVolumen": 0,
            "fMaxVolatilidad": 0.0, "sFechaMasVolatil": "",
            "dMeses": {}
        }
    )

    # --- PASO 4: POST-PROCESADO FUNCIONAL (sin bucles) ---
    # Calculamos medias a partir de las sumas acumuladas por el reduce
    iN = dReporte["iRegistros"]
    dReporte["fMediaClose"]       = round(dReporte["fSumaClose"] / iN, 4)
    dReporte["fMediaVolatilidad"] = round(dReporte["fSumaVolatilidad"] / iN, 4)
    dReporte["fMediaRendimiento"] = round(dReporte["fSumaRendimiento"] / iN, 4)

    # Enriquecemos cada mes con su media usando comprensión de diccionario (sin bucle)
    dReporte["dMeses"] = {
        sMes: {
            **dDatos,
            "fMediaClose":       round(dDatos["fSumaClose"] / dDatos["iDias"], 4),
            "fMediaVolatilidad": round(dDatos["fSumaVolatilidad"] / dDatos["iDias"], 4)
        }
        for sMes, dDatos in dReporte["dMeses"].items()
    }

    return dReporte


# =============================================================================
# SECCIÓN 4: COMPRENSIONES AVANZADAS MULTINIVEL
# =============================================================================
# Transformaciones cruzadas entre diferentes atributos en una sola línea.

def comprension_clasificacion_cruzada(tDataset):
    """
    Comprensión avanzada multinivel: clasifica cada registro cruzando
    dos dimensiones independientes (volatilidad y rendimiento) en una sola expresión.
    
    Genera una lista de tuplas (sDate, sClaseVolatilidad, sClaseRendimiento, fClose)
    combinando criterios de múltiples atributos simultáneamente.
    """
    # Comprensión que cruza volatilidad intradía con rendimiento apertura-cierre
    # Todo en una sola expresión, sin variables auxiliares ni bucles
    return [
        (
            dReg["sDate"],
            "ALTA_VOLATILIDAD" if (dReg["fHigh"] - dReg["fLow"]) > 2.0 else "BAJA_VOLATILIDAD",
            "ALCISTA" if dReg["fClose"] > dReg["fOpen"] else ("BAJISTA" if dReg["fClose"] < dReg["fOpen"] else "NEUTRO"),
            dReg["fClose"],
            dReg["iVolume"]
        )
        for dReg in tDataset
        if dReg["iVolume"] > 0  # Descartamos días sin operaciones
    ]


def comprension_resumen_decada_mes(tDataset):
    """
    Comprensión avanzada de doble nivel: genera un diccionario anidado
    {sDecada: {sMes: iConteo}} cruzando la década extraída del año
    con el mes, todo en una sola expresión multinivel.
    """
    # Primero extraemos las décadas únicas presentes (sin bucle, con set comprehension)
    setDecadas = {dReg["sDate"][:3] + "0s" for dReg in tDataset}
    setMeses = {dReg["sDate"][5:7] for dReg in tDataset}

    # Comprensión de diccionario anidada: cuenta registros por década y mes
    return {
        sDecada: {
            sMes: len([
                dReg for dReg in tDataset
                if dReg["sDate"][:3] + "0s" == sDecada and dReg["sDate"][5:7] == sMes
            ])
            for sMes in sorted(setMeses)
        }
        for sDecada in sorted(setDecadas)
    }


def comprension_top_dias_extremos(tDataset, iTopN=10):
    """
    Comprensión avanzada: identifica los N días con mayor rango intradía (High - Low)
    y cruza con la dirección del mercado, todo sin bucles.
    Usa sorted() + slicing funcional.
    """
    return sorted(
        [
            {
                "sDate":         dReg["sDate"],
                "fRango":        round(dReg["fHigh"] - dReg["fLow"], 4),
                "fClose":        dReg["fClose"],
                "sDireccion":    "ALCISTA" if dReg["fClose"] >= dReg["fOpen"] else "BAJISTA",
                "fRendimiento":  round(((dReg["fClose"] - dReg["fOpen"]) / dReg["fOpen"]) * 100, 2)
            }
            for dReg in tDataset
        ],
        key=lambda d: d["fRango"],
        reverse=True
    )[:iTopN]


# =============================================================================
# SECCIÓN 5: FUNCIONES AUXILIARES DE PRESENTACIÓN (funcional)
# =============================================================================

def mostrar_reporte_anual(dReporte):
    """Presenta el reporte jerárquico generado por el pipeline funcional."""
    if dReporte.get("iRegistros", 0) == 0:
        print(f"\n  [INFO] {dReporte.get('sMensaje', 'Sin datos')}")
        return

    print(f"\n{'='*65}")
    print(f"  REPORTE FUNCIONAL - AÑO {dReporte['iAnio']}")
    print(f"{'='*65}")
    print(f"  Días analizados:        {dReporte['iRegistros']}")
    print(f"  Precio medio cierre:    {dReporte['fMediaClose']:.2f} EUR")
    print(f"  Máximo histórico:       {dReporte['fMaxHigh']:.2f} EUR")
    print(f"  Mínimo histórico:       {dReporte['fMinLow']:.2f} EUR")
    print(f"  Volatilidad media:      {dReporte['fMediaVolatilidad']:.4f} EUR")
    print(f"  Rendimiento medio:      {dReporte['fMediaRendimiento']:.4f} %")
    print(f"  Volumen total:          {dReporte['iSumaVolumen']:,}")
    print(f"  Día más volátil:        {dReporte['sFechaMasVolatil']}")

    print(f"\n  {'─'*55}")
    print(f"  DESGLOSE MENSUAL:")
    print(f"  {'─'*55}")
    print(f"  {'Mes':<6} {'Días':>6} {'Media Close':>14} {'Media Volat.':>14}")
    print(f"  {'─'*55}")

    # Presentación con map + join (sin bucle for)
    lLineas = list(map(
        lambda tItem: f"  {tItem[0]:<6} {tItem[1]['iDias']:>6} {tItem[1]['fMediaClose']:>14.2f} {tItem[1]['fMediaVolatilidad']:>14.4f}",
        sorted(dReporte["dMeses"].items())
    ))
    print("\n".join(lLineas))


def mostrar_clasificacion_cruzada(lClasificacion, iMaxFilas=15):
    """Muestra los resultados de la comprensión de clasificación cruzada."""
    print(f"\n{'='*80}")
    print(f"  CLASIFICACIÓN CRUZADA (Volatilidad x Dirección) - Primeros {iMaxFilas} registros")
    print(f"{'='*80}")
    print(f"  {'Fecha':<14} {'Volatilidad':<20} {'Dirección':<12} {'Close':>10} {'Volumen':>12}")
    print(f"  {'─'*72}")

    lLineas = list(map(
        lambda t: f"  {t[0]:<14} {t[1]:<20} {t[2]:<12} {t[3]:>10.2f} {t[4]:>12,}",
        lClasificacion[:iMaxFilas]
    ))
    print("\n".join(lLineas))


def mostrar_top_extremos(lTop):
    """Muestra el ranking de días con mayor rango intradía."""
    print(f"\n{'='*72}")
    print(f"  TOP {len(lTop)} DÍAS MÁS VOLÁTILES (Mayor rango High-Low)")
    print(f"{'='*72}")
    print(f"  {'#':>3} {'Fecha':<14} {'Rango':>8} {'Close':>10} {'Rend.%':>8} {'Dirección':<10}")
    print(f"  {'─'*60}")

    lLineas = list(map(
        lambda tItem: f"  {tItem[0]+1:>3} {tItem[1]['sDate']:<14} {tItem[1]['fRango']:>8.2f} {tItem[1]['fClose']:>10.2f} {tItem[1]['fRendimiento']:>8.2f} {tItem[1]['sDireccion']:<10}",
        enumerate(lTop)
    ))
    print("\n".join(lLineas))


def mostrar_decada_mes(dDecadaMes):
    """Muestra la matriz década x mes generada por la comprensión multinivel."""
    print(f"\n{'='*65}")
    print(f"  MATRIZ DÉCADA x MES (nº de sesiones bursátiles)")
    print(f"{'='*65}")

    # Cabecera de meses
    lMeses = sorted(next(iter(dDecadaMes.values())).keys())
    sCabecera = f"  {'Década':<10}" + "".join(map(lambda m: f"{m:>6}", lMeses))
    print(sCabecera)
    print(f"  {'─'*75}")

    lLineas = list(map(
        lambda tItem: f"  {tItem[0]:<10}" + "".join(map(lambda m: f"{tItem[1][m]:>6}", lMeses)),
        sorted(dDecadaMes.items())
    ))
    print("\n".join(lLineas))


# =============================================================================
# SECCIÓN 6: PROGRAMA PRINCIPAL
# =============================================================================

def main():
    print("=" * 65)
    print(" PROBLEMA 4 - PARADIGMA FUNCIONAL DECLARATIVO")
    print(" Dataset: BMW Stock Data (12_bmw_data.csv)")
    print("=" * 65)

    # --- Carga inmutable del dataset ---
    sRuta = "12_bmw_data.csv"
    tDataset = cargar_dataset(sRuta)
    print(f"\n  [OK] Dataset cargado: {len(tDataset)} registros (tupla inmutable)")

    # =====================================================================
    # DEMOSTRACIÓN 1: Fábricas de predicados con filter()
    # =====================================================================
    print(f"\n{'='*65}")
    print("  DEMO 1: FÁBRICAS DE PREDICADOS")
    print(f"{'='*65}")

    # Filtro dinámico: días donde el cierre estuvo entre 90 y 120 EUR
    fnFiltroPrecio = fabrica_filtro_rango("fClose", 90.0, 120.0)
    tPrecioAlto = tuple(filter(fnFiltroPrecio, tDataset))
    print(f"\n  Filtro: Close entre 90-120 EUR -> {len(tPrecioAlto)} días encontrados")

    # Filtro dinámico: días del año 2020 con volumen >= 5 millones
    fnFiltro2020 = fabrica_filtro_anio(2020)
    fnFiltroVol = fabrica_filtro_volumen_minimo(5_000_000)
    tAltoVolumen2020 = tuple(filter(
        lambda d: fnFiltro2020(d) and fnFiltroVol(d),
        tDataset
    ))
    print(f"  Filtro: Año 2020 + Volumen >= 5M -> {len(tAltoVolumen2020)} días encontrados")

    # Mostramos 5 ejemplos del filtro compuesto (sin bucle, con map + join)
    if len(tAltoVolumen2020) > 0:
        print(f"\n  {'Fecha':<14} {'Close':>10} {'Volumen':>14}")
        print(f"  {'─'*40}")
        lEjemplos = list(map(
            lambda d: f"  {d['sDate']:<14} {d['fClose']:>10.2f} {d['iVolume']:>14,}",
            tAltoVolumen2020[:5]
        ))
        print("\n".join(lEjemplos))

    # =====================================================================
    # DEMOSTRACIÓN 2: Pipeline funcional (filter -> map -> reduce)
    # =====================================================================
    print(f"\n{'='*65}")
    print("  DEMO 2: PIPELINE FUNCIONAL (filter -> map -> reduce)")
    print(f"{'='*65}")

    # Análisis del año 2020 con volatilidad mínima de 1.0 EUR
    dReporte2020 = pipeline_analisis_anual(tDataset, 2020, 1.0)
    mostrar_reporte_anual(dReporte2020)

    # Análisis del año 2015 con volatilidad mínima de 0.5 EUR
    dReporte2015 = pipeline_analisis_anual(tDataset, 2015, 0.5)
    mostrar_reporte_anual(dReporte2015)

    # =====================================================================
    # DEMOSTRACIÓN 3: Comprensiones avanzadas multinivel
    # =====================================================================
    print(f"\n{'='*65}")
    print("  DEMO 3: COMPRENSIONES AVANZADAS MULTINIVEL")
    print(f"{'='*65}")

    # 3a. Clasificación cruzada (volatilidad x dirección)
    lClasificacion = comprension_clasificacion_cruzada(tDataset)
    mostrar_clasificacion_cruzada(lClasificacion, iMaxFilas=10)

    # Conteo funcional por categoría (sin bucles, con filter + len)
    iAlcistasAlta = len(list(filter(
        lambda t: t[1] == "ALTA_VOLATILIDAD" and t[2] == "ALCISTA", lClasificacion
    )))
    iBajistasAlta = len(list(filter(
        lambda t: t[1] == "ALTA_VOLATILIDAD" and t[2] == "BAJISTA", lClasificacion
    )))
    print(f"\n  Resumen: Alta Volatilidad + Alcista = {iAlcistasAlta} días")
    print(f"  Resumen: Alta Volatilidad + Bajista = {iBajistasAlta} días")

    # 3b. Top 10 días más volátiles
    lTop10 = comprension_top_dias_extremos(tDataset, iTopN=10)
    mostrar_top_extremos(lTop10)

    # 3c. Matriz década x mes
    dMatriz = comprension_resumen_decada_mes(tDataset)
    mostrar_decada_mes(dMatriz)

    print(f"\n{'='*65}")
    print("  [FIN] Análisis funcional completado sin bucles.")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
