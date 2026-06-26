"""
P2 - Programa Principal de Pruebas del Modelo OOP BMW
=====================================================
Pone a prueba cada una de las capacidades del GestorSistema,
simulando un entorno de operación real y mostrando los resultados
de cada acción en pantalla.

Funcionalidades probadas:
  1. Alta con control de duplicados
  2. Baja con notificación de resultado
  3. Consulta por clave de identidad
  4. Segmentación por rango de valores
  5. Listado completo de registros
  6. Persistencia automática (volcado y reconstrucción)

Asignatura: Fundamentos de Sistemas de Información
Grado: Ingeniería Informática en Sistemas de Información
"""

import re
from registro_bmw import RegistroBmw
from gestor_errores import GestorErrores
from gestor_sistema import GestorSistema

# Patrón regex para validar formato de fecha desde consola
S_PATRON_FECHA = r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'


# ============================================================
# FUNCIONES AUXILIARES DE ENTRADA CON VALIDACIÓN
# ============================================================
def pedir_fecha(sMensaje="Fecha (YYYY-MM-DD): "):
    """Solicita una fecha por consola y valida su formato con regex."""
    while True:
        sValor = input(sMensaje).strip()
        if re.match(S_PATRON_FECHA, sValor):
            return sValor
        print("Formato incorrecto. Usa YYYY-MM-DD (ej: 2024-01-15).")


def pedir_float(sMensaje, sNombre):
    """Solicita un valor decimal por consola con validación."""
    while True:
        sValor = input(sMensaje).strip()
        try:
            fValor = float(sValor)
            if fValor < 0:
                print(f"Error: {sNombre} debe ser >= 0.")
                continue
            return fValor
        except ValueError:
            print(f"Error: {sNombre} debe ser un número decimal válido.")


def pedir_entero(sMensaje, sNombre):
    """Solicita un valor entero por consola con validación."""
    while True:
        sValor = input(sMensaje).strip()
        try:
            iValor = int(sValor)
            if iValor < 0:
                print(f"Error: {sNombre} debe ser >= 0.")
                continue
            return iValor
        except ValueError:
            print(f"Error: {sNombre} debe ser un número entero válido.")


# ============================================================
# SUBMENÚS DEL PROGRAMA
# ============================================================
def submenu_alta(oSistema):
    """
    Alta de un nuevo registro con validación completa.
    Si la entidad es genuinamente nueva -> confirma con 'OK'.
    Si el identificador ya existe -> notifica 'DUPLICADO'.
    """
    print("\n--- ALTA DE REGISTRO ---")

    sDate = pedir_fecha()
    fAdjClose = pedir_float("Adj_Close: ", "Adj_Close")
    fClose = pedir_float("Close: ", "Close")
    fHigh = pedir_float("High: ", "High")
    fLow = pedir_float("Low: ", "Low")
    fOpen = pedir_float("Open: ", "Open")
    iVolume = pedir_entero("Volume: ", "Volume")

    # Validación lógica de negocio: High >= Low
    if fHigh < fLow:
        print(GestorErrores.getMensaje(GestorErrores.ERR_HIGH_MENOR_LOW))
        return

    # Crear el objeto RegistroBmw (la validación ocurre en los setters)
    oRegistro = RegistroBmw(sDate, fAdjClose, fClose, fHigh, fLow, fOpen, iVolume)

    # Comprobar errores de validación del objeto
    if not oRegistro.esValido():
        print("Errores de validación detectados:")
        for iErr in oRegistro.getErrores():
            print(f"  -> {GestorErrores.getMensaje(iErr)}")
        return

    # Intentar el alta en el gestor
    iResultado = oSistema.alta_registro(oRegistro)
    print(f"Resultado: {GestorErrores.getMensaje(iResultado)}")


def submenu_baja(oSistema):
    """
    Baja de un registro por su clave de identidad (fecha).
    Informa si fue exitosa ('OK') o si no se localizó ('NO LOCALIZADO').
    """
    print("\n--- BAJA DE REGISTRO ---")
    sClave = input("Fecha del registro a eliminar (YYYY-MM-DD): ").strip()

    iResultado = oSistema.baja_registro(sClave)
    print(f"Resultado: {GestorErrores.getMensaje(iResultado)}")


def submenu_consulta(oSistema):
    """Consulta un registro específico por su clave de identidad."""
    print("\n--- CONSULTA POR CLAVE ---")
    sClave = input("Fecha del registro (YYYY-MM-DD): ").strip()

    oRegistro = oSistema.consulta_por_clave(sClave)
    if oRegistro:
        print(f"\nRegistro encontrado:")
        print(f"  {oRegistro}")
    else:
        print(f"No se encontró ningún registro con la fecha '{sClave}'.")


def submenu_segmentacion(oSistema):
    """
    Segmentación por rango: el usuario define dos umbrales para un campo
    y el sistema devuelve las entidades dentro de ese intervalo.
    """
    print("\n--- SEGMENTACIÓN POR RANGO ---")
    print("Campos disponibles: fAdjClose, fClose, fHigh, fLow, fOpen, iVolume")

    sCampo = input("Campo a filtrar: ").strip()

    # Validar que el campo existe en RegistroBmw
    lCamposValidos = ['fAdjClose', 'fClose', 'fHigh', 'fLow', 'fOpen', 'iVolume']
    if sCampo not in lCamposValidos:
        print(f"Error: Campo '{sCampo}' no válido.")
        return

    # Solicitar los dos umbrales del rango
    if sCampo == 'iVolume':
        valor1_inicial1 = pedir_entero("Valor inicial del rango: ", "Umbral inferior")
        valor2_final2 = pedir_entero("Valor final del rango: ", "Umbral superior")
    else:
        valor1_inicial1 = pedir_float("Valor inicial del rango: ", "Umbral inferior")
        valor2_final2 = pedir_float("Valor final del rango: ", "Umbral superior")

    # Validar coherencia del rango
    if valor1_inicial1 > valor2_final2:
        print("Error: El valor inicial no puede ser mayor que el valor final.")
        return

    # Ejecutar la segmentación
    lResultados = oSistema.consulta_por_rango(sCampo, valor1_inicial1, valor2_final2)

    if lResultados:
        print(f"\nRegistros con '{sCampo}' entre {valor1_inicial1} y {valor2_final2}:")
        print(f"  Total encontrados: {len(lResultados)}\n")
        # Mostramos los primeros 20 para no saturar la consola
        for i, oReg in enumerate(lResultados[:20]):
            print(f"  {oReg}")
        if len(lResultados) > 20:
            print(f"\n  ... y {len(lResultados) - 20} registros más.")
    else:
        print("No se encontraron registros en el rango especificado.")


def submenu_listar(oSistema):
    """Lista todos los registros del sistema ordenados por fecha."""
    print("\n--- LISTADO COMPLETO ---")

    lRegistros = oSistema.listar_todos()
    if not lRegistros:
        print("No hay registros en el sistema.")
        return

    print(f"Total de registros: {len(lRegistros)}\n")

    # Mostrar los primeros 20 con opción de ver más
    iMostrar = 20
    for i, oReg in enumerate(lRegistros[:iMostrar]):
        print(f"  {oReg}")

    if len(lRegistros) > iMostrar:
        print(f"\n  Mostrando {iMostrar} de {len(lRegistros)} registros.")
        sVer = input("  ¿Desea ver todos? (Si/No): ").strip().lower()
        if sVer == 'si':
            for oReg in lRegistros[iMostrar:]:
                print(f"  {oReg}")


# ============================================================
# MENÚ PRINCIPAL
# ============================================================
def main():
    """
    Programa principal que pone a prueba cada una de las capacidades
    del GestorSistema, simulando un entorno de operación real.
    """

    # Inicialización del sistema (carga inteligente automática)
    print("=" * 55)
    print("  INICIALIZANDO SISTEMA DE GESTIÓN BMW - PROBLEMA 2")
    print("=" * 55)
    oSistema = GestorSistema()

    sOpcion = ""
    while sOpcion != "0":
        print("\n" + "=" * 55)
        print("    ADMINISTRADOR DE COTIZACIONES BMW - PROBLEMA 2")
        print("=" * 55)
        print("1. Alta de Registro (control de duplicados)")
        print("2. Baja de Registro (por clave de identidad)")
        print("3. Consulta por Clave")
        print("4. Segmentación por Rango de Valores")
        print("5. Listado Completo de Registros")
        print("0. Salir (estado guardado automáticamente)")

        sOpcion = input("\nSeleccione una opción: ").strip()

        match sOpcion:
            case "1":
                submenu_alta(oSistema)
            case "2":
                submenu_baja(oSistema)
            case "3":
                submenu_consulta(oSistema)
            case "4":
                submenu_segmentacion(oSistema)
            case "5":
                submenu_listar(oSistema)
            case "0":
                print("\nEstado guardado. ¡Hasta pronto!")
            case _:
                print("Opción no válida. Inténtelo de nuevo.")


if __name__ == "__main__":
    main()
