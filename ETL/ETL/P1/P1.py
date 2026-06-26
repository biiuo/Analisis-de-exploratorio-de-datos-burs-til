"""
P1 - Núcleo de Gestión de Información del Dataset BMW
=====================================================
Organiza los registros del dataset de cotizaciones bursátiles de BMW
en un diccionario con clave compuesta (Date + Open) para acceso
instantáneo y sin colisiones. Incluye: Alta con validación rigurosa
(expresiones regulares), Consulta, Baja, y Reporte Visual con tabla
de anchura automática.

Asignatura: Fundamentos de Sistemas de Información
Grado: Ingeniería Informática en Sistemas de Información
"""

import re
import os
import pandas as pd

# ============================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================
# Ruta al fichero del dataset (relativa al directorio del script)
S_DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
S_FICHERO_DATASET = os.path.join(S_DIRECTORIO_BASE, '12_bmw_data.csv')

# Patrones de validación con expresiones regulares
# Patrón para fecha YYYY-MM-DD (solo formato, luego se valida lógicamente)
S_PATRON_FECHA = r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'

# Patrón para valores numéricos decimales (positivos, con punto decimal)
S_PATRON_DECIMAL = r'^[0-9]+(\.[0-9]+)?$'

# Patrón para valores enteros positivos
S_PATRON_ENTERO = r'^[0-9]+$'

# Diccionario principal en memoria: clave compuesta -> registro completo
dRegistros = {}


# ============================================================
# FUNCIONES DE VALIDACIÓN (Expresiones Regulares)
# ============================================================
def validar_fecha(sValor):
    """
    Valida que la fecha tenga formato YYYY-MM-DD usando expresión regular.
    Retorna tupla (bValido, sMensaje).
    """
    if not isinstance(sValor, str) or len(sValor.strip()) == 0:
        return False, "Error: La fecha no puede estar vacía y debe ser texto."
    
    sValor = sValor.strip()
    if not re.match(S_PATRON_FECHA, sValor):
        return False, "Error: Formato de fecha inválido. Usa YYYY-MM-DD (ej: 2024-01-15)."
    
    # Validación lógica adicional: comprobar que el día es válido para el mes
    try:
        pd.Timestamp(sValor)
    except ValueError:
        return False, "Error: La fecha introducida no existe (ej: 2024-02-30 no es válida)."
    
    return True, ""


def validar_decimal_positivo(sValor, sNombreCampo):
    """
    Valida que el valor sea un número decimal >= 0 usando regex.
    Retorna tupla (bValido, sMensaje).
    """
    if not isinstance(sValor, str) or len(sValor.strip()) == 0:
        return False, f"Error: {sNombreCampo} no puede estar vacío."
    
    sValor = sValor.strip()
    if not re.match(S_PATRON_DECIMAL, sValor):
        return False, f"Error: {sNombreCampo} debe ser un número decimal válido (ej: 18.25)."
    
    return True, ""


def validar_entero_positivo(sValor, sNombreCampo):
    """
    Valida que el valor sea un número entero >= 0 usando regex.
    Retorna tupla (bValido, sMensaje).
    """
    if not isinstance(sValor, str) or len(sValor.strip()) == 0:
        return False, f"Error: {sNombreCampo} no puede estar vacío."
    
    sValor = sValor.strip()
    if not re.match(S_PATRON_ENTERO, sValor):
        return False, f"Error: {sNombreCampo} debe ser un número entero válido (ej: 767000)."
    
    return True, ""


# ============================================================
# FUNCIÓN DE CLAVE COMPUESTA
# ============================================================
def generar_clave_compuesta(sDate, sOpen):
    """
    Genera la clave compuesta del registro combinando Date + Open.
    Esto asegura que no existan colisiones de información incluso
    si se registrasen dos entradas con la misma fecha pero distinto precio.
    Ejemplo: '1996-11-08_18.21' 
    """
    return f"{sDate}_{sOpen}"


# ============================================================
# CARGA INICIAL DEL DATASET CON PANDAS
# ============================================================
def cargar_dataset():
    """
    Lee el fichero CSV con Pandas y vuelca cada fila al diccionario
    en memoria usando la clave compuesta (Date + Open).
    """
    global dRegistros

    if not os.path.exists(S_FICHERO_DATASET):
        print(f"Error: No se encontró el fichero '{S_FICHERO_DATASET}'.")
        return False

    try:
        dfDatos = pd.read_csv(S_FICHERO_DATASET)
        
        for _, dFila in dfDatos.iterrows():
            sDate = str(dFila['Date']).strip()
            fOpen = float(dFila['Open'])

            # Generamos la clave compuesta (Date + Open)
            sClave = generar_clave_compuesta(sDate, str(fOpen))

            dRegistros[sClave] = {
                'Date':      sDate,
                'Adj_Close': round(float(dFila['Adj_Close']), 6),
                'Close':     round(float(dFila['Close']), 2),
                'High':      round(float(dFila['High']), 2),
                'Low':       round(float(dFila['Low']), 2),
                'Open':      round(fOpen, 2),
                'Volume':    int(dFila['Volume'])
            }
        
        print(f"Dataset cargado correctamente: {len(dRegistros)} registros en memoria.")
        return True

    except Exception as e:
        print(f"Error crítico al cargar el dataset: {e}")
        return False


# ============================================================
# OPERACIONES CRUD
# ============================================================
def alta_registro():
    """
    Alta de un nuevo registro con validación rigurosa de cada campo.
    Si la clave compuesta ya existe, se rechaza la inserción.
    """
    print("\n--- ALTA DE NUEVO REGISTRO ---")

    # 1. Validación de la fecha (parte de la clave compuesta)
    sDate = input("Fecha (YYYY-MM-DD): ").strip()
    bValido, sMensaje = validar_fecha(sDate)
    if not bValido:
        print(sMensaje)
        return

    # 2. Validación de Adj_Close
    sAdjClose = input("Adj_Close: ").strip()
    bValido, sMensaje = validar_decimal_positivo(sAdjClose, "Adj_Close")
    if not bValido:
        print(sMensaje)
        return

    # 3. Validación de Close
    sClose = input("Close: ").strip()
    bValido, sMensaje = validar_decimal_positivo(sClose, "Close")
    if not bValido:
        print(sMensaje)
        return

    # 4. Validación de High
    sHigh = input("High: ").strip()
    bValido, sMensaje = validar_decimal_positivo(sHigh, "High")
    if not bValido:
        print(sMensaje)
        return

    # 5. Validación de Low
    sLow = input("Low: ").strip()
    bValido, sMensaje = validar_decimal_positivo(sLow, "Low")
    if not bValido:
        print(sMensaje)
        return

    # 6. Validación lógica cruzada: High >= Low (regla de negocio bursátil)
    if float(sHigh) < float(sLow):
        print("Error: El valor 'High' no puede ser inferior al valor 'Low'.")
        return

    # 7. Validación de Open
    sOpen = input("Open: ").strip()
    bValido, sMensaje = validar_decimal_positivo(sOpen, "Open")
    if not bValido:
        print(sMensaje)
        return

    # 8. Validación de Volume
    sVolume = input("Volume: ").strip()
    bValido, sMensaje = validar_entero_positivo(sVolume, "Volume")
    if not bValido:
        print(sMensaje)
        return

    # 9. Generar clave compuesta y comprobar duplicados
    sClave = generar_clave_compuesta(sDate, sOpen)
    if sClave in dRegistros:
        print(f"Error: Ya existe un registro con la clave compuesta '{sClave}'. Inserción rechazada.")
        return

    # 10. Inserción exitosa en el diccionario
    dRegistros[sClave] = {
        'Date':      sDate,
        'Adj_Close': round(float(sAdjClose), 6),
        'Close':     round(float(sClose), 2),
        'High':      round(float(sHigh), 2),
        'Low':       round(float(sLow), 2),
        'Open':      round(float(sOpen), 2),
        'Volume':    int(sVolume)
    }

    print(f"Registro con clave '{sClave}' creado correctamente.")


def consulta_registro():
    """
    Localiza un registro específico por su clave compuesta (Date + Open).
    Muestra todos los detalles del registro encontrado.
    """
    print("\n--- CONSULTA DE REGISTRO ---")
    sDate = input("Fecha del registro (YYYY-MM-DD): ").strip()
    sOpen = input("Open del registro: ").strip()
    sClave = generar_clave_compuesta(sDate, sOpen)

    dRegistro = dRegistros.get(sClave)
    if dRegistro:
        print(f"\nRegistro encontrado (Clave: {sClave}):")
        print("-" * 35)
        for sCampo, valor in dRegistro.items():
            print(f"  {sCampo:<12} : {valor}")
    else:
        print(f"No se encontró ningún registro con la clave '{sClave}'.")


def baja_registro():
    """
    Elimina un registro del diccionario por su clave compuesta.
    No deja residuos en el sistema.
    """
    print("\n--- BAJA DE REGISTRO ---")
    sDate = input("Fecha del registro a eliminar (YYYY-MM-DD): ").strip()
    sOpen = input("Open del registro a eliminar: ").strip()
    sClave = generar_clave_compuesta(sDate, sOpen)

    if sClave in dRegistros:
        del dRegistros[sClave]
        print(f"Registro con clave '{sClave}' eliminado sin residuos.")
    else:
        print(f"No se encontró ningún registro con la clave '{sClave}'.")


# ============================================================
# REPORTE VISUAL CON TABLA ALINEADA AUTOMÁTICAMENTE
# ============================================================
def reporte_visual():
    """
    Genera un reporte visual completo presentado como tabla perfectamente
    alineada. El software calcula automáticamente el ancho de cada columna
    para que la lectura sea profesional y clara.
    """
    print("\n--- REPORTE VISUAL COMPLETO ---")

    if not dRegistros:
        print("No hay registros en el sistema.")
        return

    # Columnas del reporte
    lColumnas = ['Date', 'Adj_Close', 'Close', 'High', 'Low', 'Open', 'Volume']

    # Convertimos los valores del diccionario a una lista ordenada por fecha
    lRegistros = sorted(dRegistros.values(), key=lambda r: r['Date'])

    # Cálculo automático del ancho de cada columna
    # Se toma el máximo entre la cabecera y todos los datos de esa columna
    dAnchos = {}
    for sCol in lColumnas:
        iAnchoCabecera = len(sCol)
        iAnchoMaxDato = max(len(str(dReg[sCol])) for dReg in lRegistros)
        dAnchos[sCol] = max(iAnchoCabecera, iAnchoMaxDato) + 2  # +2 de padding

    # Línea separadora calculada dinámicamente
    sSeparador = "+" + "+".join("-" * dAnchos[c] for c in lColumnas) + "+"

    # Impresión de la cabecera
    print(sSeparador)
    sCabecera = "|" + "|".join(sCol.center(dAnchos[sCol]) for sCol in lColumnas) + "|"
    print(sCabecera)
    print(sSeparador)

    # Impresión de cada fila de datos
    for dReg in lRegistros:
        sFila = "|"
        for sCol in lColumnas:
            sValor = str(dReg[sCol])
            if sCol == 'Date':
                sFila += sValor.center(dAnchos[sCol]) + "|"
            else:
                # Números alineados a la derecha para lectura profesional
                sFila += sValor.rjust(dAnchos[sCol] - 1) + " |"
        print(sFila)

    # Pie del reporte
    print(sSeparador)
    print(f"\nTotal de registros mostrados: {len(lRegistros)}")


# ============================================================
# MENÚ PRINCIPAL
# ============================================================
def main():
    """Punto de entrada con menú de navegación por consola constante."""

    # Carga inicial del dataset completo
    if not cargar_dataset():
        print("No se pudo iniciar el sistema. Verifique el fichero 'dataset.csv'.")
        return

    sOpcion = ""
    while sOpcion != "0":
        print("\n" + "=" * 50)
        print("    GESTIÓN DE COTIZACIONES BMW - PROBLEMA 1")
        print("=" * 50)
        print("1. Alta de Registro (con validación)")
        print("2. Consulta de Registro (por clave)")
        print("3. Baja de Registro (eliminación limpia)")
        print("4. Reporte Visual (tabla alineada)")
        print("0. Salir")

        sOpcion = input("\nSeleccione una opción: ").strip()

        match sOpcion:
            case "1":
                alta_registro()
            case "2":
                consulta_registro()
            case "3":
                baja_registro()
            case "4":
                reporte_visual()
            case "0":
                print("\nSaliendo del sistema. ¡Hasta pronto!")
            case _:
                print("Opción no válida. Inténtelo de nuevo.")


if __name__ == "__main__":
    main()
