"""
GestorErrores - Gestión centralizada de códigos de error
=========================================================
Define todas las constantes de error y sus mensajes descriptivos
para la validación de los registros de cotizaciones BMW.
Sigue el patrón del profesor: constantes estáticas + diccionario de mensajes.
"""


class GestorErrores:
    # --- CÓDIGO DE ÉXITO ---
    EXITO = 0

    # --- ERRORES DE FECHA (Date) ---
    ERR_DATE_TIPO = -1
    ERR_DATE_VACIO = -2
    ERR_DATE_FORMATO = -3

    # --- ERRORES DE ADJ_CLOSE ---
    ERR_ADJCLOSE_TIPO = -10
    ERR_ADJCLOSE_RANGO = -11

    # --- ERRORES DE CLOSE ---
    ERR_CLOSE_TIPO = -20
    ERR_CLOSE_RANGO = -21

    # --- ERRORES DE HIGH ---
    ERR_HIGH_TIPO = -30
    ERR_HIGH_RANGO = -31

    # --- ERRORES DE LOW ---
    ERR_LOW_TIPO = -40
    ERR_LOW_RANGO = -41

    # --- ERRORES DE OPEN ---
    ERR_OPEN_TIPO = -50
    ERR_OPEN_RANGO = -51

    # --- ERRORES DE VOLUME ---
    ERR_VOLUME_TIPO = -60
    ERR_VOLUME_RANGO = -61

    # --- ERRORES DE LÓGICA DE NEGOCIO ---
    ERR_HIGH_MENOR_LOW = -70

    # --- ERRORES DEL GESTOR (CRUD) ---
    ERR_DUPLICADO = -80
    ERR_NO_LOCALIZADO = -81

    # --- DICCIONARIO DE MENSAJES ---
    _mensajes = {
        EXITO: "Operación realizada con éxito.",

        # Date
        ERR_DATE_TIPO: "Error: Date debe ser string.",
        ERR_DATE_VACIO: "Error: Date no puede estar vacío.",
        ERR_DATE_FORMATO: "Error: Date debe tener formato YYYY-MM-DD.",

        # Adj_Close
        ERR_ADJCLOSE_TIPO: "Error: Adj_Close debe ser numérico (int o float).",
        ERR_ADJCLOSE_RANGO: "Error: Adj_Close debe ser >= 0.",

        # Close
        ERR_CLOSE_TIPO: "Error: Close debe ser numérico (int o float).",
        ERR_CLOSE_RANGO: "Error: Close debe ser >= 0.",

        # High
        ERR_HIGH_TIPO: "Error: High debe ser numérico (int o float).",
        ERR_HIGH_RANGO: "Error: High debe ser >= 0.",

        # Low
        ERR_LOW_TIPO: "Error: Low debe ser numérico (int o float).",
        ERR_LOW_RANGO: "Error: Low debe ser >= 0.",

        # Open
        ERR_OPEN_TIPO: "Error: Open debe ser numérico (int o float).",
        ERR_OPEN_RANGO: "Error: Open debe ser >= 0.",

        # Volume
        ERR_VOLUME_TIPO: "Error: Volume debe ser entero (int).",
        ERR_VOLUME_RANGO: "Error: Volume debe ser >= 0.",

        # Lógica de negocio
        ERR_HIGH_MENOR_LOW: "Error: High no puede ser menor que Low.",

        # CRUD
        ERR_DUPLICADO: "DUPLICADO: Ya existe un registro con esa clave.",
        ERR_NO_LOCALIZADO: "NO LOCALIZADO: No existe un registro con esa clave."
    }

    @staticmethod
    def getMensaje(iCodigo):
        """Devuelve el mensaje descriptivo asociado a un código de error."""
        return GestorErrores._mensajes.get(iCodigo, "Error desconocido.")
