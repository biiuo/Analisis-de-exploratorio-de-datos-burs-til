class GestorErrores:
    EXITO = 0

    # VALIDACIONES DE FECHA 
    ERR_FECHA_FORMATO  = -1   # No cumple YYYY-MM-DD
    ERR_FECHA_RANGO    = -2   # Mes/día fuera de rango o año < 1900
    ERR_FECHA_DUPLICADA = -3  # Ya existe ese día en la BD

    # VALIDACIONES DE PRECIO 
    ERR_PRECIO_TIPO    = -10  # No es un decimal
    ERR_PRECIO_RANGO   = -11  # <= 0 o > 10.000
    ERR_ADJCLOSE_MAYOR = -12  # Adj_Close > Close (financieramente imposible)

    # VALIDACIONES DE VOLUMEN 
    ERR_VOLUMEN_TIPO   = -20  # No es entero
    ERR_VOLUMEN_RANGO  = -21  # < 0 o > 100.000.000

    #  VALIDACIONES OHLC 
    ERR_OHLC_HIGH_LOW  = -30  # High < Low  → bloquea inserción
    ERR_OHLC_VARIACION = -31  # Variación diaria > 20%  → aviso

    #  BÚSQUEDA / CRUD 
    ERR_REGISTRO_NO_ENCONTRADO = -40

    _mensajes = {
        EXITO: "Operación realizada con éxito.",

        # Fecha
        ERR_FECHA_FORMATO:   "Error: la fecha debe tener formato YYYY-MM-DD.",
        ERR_FECHA_RANGO:     "Error: fecha imposible (año >= 1900, mes 1-12, día 1-31).",
        ERR_FECHA_DUPLICADA: "Error: ya existe un registro para esa fecha.",

        # Precio
        ERR_PRECIO_TIPO:    "Error: el precio debe ser un número decimal.",
        ERR_PRECIO_RANGO:   "Error: el precio debe ser > 0 y <= 10.000.",
        ERR_ADJCLOSE_MAYOR: "Error: Adj_Close no puede ser mayor que Close.",

        # Volumen
        ERR_VOLUMEN_TIPO:  "Error: el volumen debe ser un número entero.",
        ERR_VOLUMEN_RANGO: "Error: el volumen debe estar entre 0 y 100.000.000.",

        # OHLC
        ERR_OHLC_HIGH_LOW:  "INVÁLIDO: High no puede ser menor que Low.",
        ERR_OHLC_VARIACION: "Aviso: variación diaria > 20% (revisa los valores).",

        # CRUD
        ERR_REGISTRO_NO_ENCONTRADO: "Error: registro no encontrado en la base de datos.",
    }

    @staticmethod
    def getMensaje(iCodigo):
        return GestorErrores._mensajes.get(iCodigo, "Error desconocido.")
