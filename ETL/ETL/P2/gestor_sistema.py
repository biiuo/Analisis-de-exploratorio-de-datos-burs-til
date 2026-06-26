"""
GestorSistema - Custodio Inteligente de la Información BMW
==========================================================
Unidad central de administración de datos que gestiona los registros
de cotizaciones BMW. Se encarga de:
  - Altas con control de duplicados
  - Bajas con notificación de resultado
  - Segmentación por rango de valores
  - Persistencia bidireccional (volcado y reconstrucción desde fichero)
  - Detección automática de dataset modificado en ejecuciones anteriores

Sigue el patrón del profesor: diccionarios en memoria, Pandas para I/O,
guardado automático tras cada operación CRUD.
"""

import os
import pandas as pd
from registro_bmw import RegistroBmw
from gestor_errores import GestorErrores


class GestorSistema:
    def __init__(self):
        # Diccionario principal en memoria (clave: sDate -> objeto RegistroBmw)
        self.dRegistros = {}

        # Rutas de ficheros
        sDirBase = os.path.dirname(os.path.abspath(__file__))
        self.sFicheroOriginal = os.path.join(sDirBase, '12_bmw_data.csv')
        self.sFicheroModificado = os.path.join(sDirBase, 'dataset_modificado.csv')

        # Carga inteligente al iniciar el sistema
        self._cargar_datos_inteligente()

    # ============================================================
    # CARGA INTELIGENTE: Detecta si existe un dataset modificado
    # ============================================================
    def _cargar_datos_inteligente(self):
        """
        Comprueba si el dataset ya ha sufrido algún tipo de cambio previo
        con alguna ejecución anterior (si existe el fichero modificado).
        - Si existe 'dataset_modificado.csv' -> carga desde él
        - En caso contrario -> carga el dataset original completo
        """
        if os.path.exists(self.sFicheroModificado):
            print("Detectado dataset modificado de una ejecución anterior.")
            print(f"Cargando desde: {self.sFicheroModificado}")
            self._cargar_desde_csv(self.sFicheroModificado)
        else:
            print("No se detectaron cambios previos. Cargando dataset original.")
            print(f"Cargando desde: {self.sFicheroOriginal}")
            self._cargar_desde_csv(self.sFicheroOriginal)

    def _cargar_desde_csv(self, sFichero):
        """
        Reconstruye toda la estructura de objetos a partir de un fichero CSV.
        Usa Pandas para la lectura y crea objetos RegistroBmw validados.
        """
        if not os.path.exists(sFichero):
            print(f"Error: No se encontró el fichero '{sFichero}'.")
            self._inicializar_fichero_vacio()
            return

        try:
            dfDatos = pd.read_csv(sFichero)

            iCargados = 0
            iErrores = 0
            for _, dFila in dfDatos.iterrows():
                oRegistro = RegistroBmw(
                    sDate=str(dFila['Date']).strip(),
                    fAdjClose=float(dFila['Adj_Close']),
                    fClose=float(dFila['Close']),
                    fHigh=float(dFila['High']),
                    fLow=float(dFila['Low']),
                    fOpen=float(dFila['Open']),
                    iVolume=int(dFila['Volume'])
                )

                # Solo insertamos registros que pasen la validación
                if oRegistro.esValido():
                    self.dRegistros[oRegistro.sDate] = oRegistro
                    iCargados += 1
                else:
                    iErrores += 1

            print(f"Carga completada: {iCargados} registros válidos.")
            if iErrores > 0:
                print(f"  (Se descartaron {iErrores} registros con errores de validación)")

        except Exception as e:
            print(f"Error crítico durante la carga: {e}")

    def _inicializar_fichero_vacio(self):
        """Crea un fichero CSV vacío con cabeceras usando Pandas."""
        dfVacio = pd.DataFrame(columns=["Date", "Adj_Close", "Close", "High", "Low", "Open", "Volume"])
        dfVacio.to_csv(self.sFicheroModificado, index=False)
        print("Fichero vacío inicializado con cabeceras.")

    # ============================================================
    # PERSISTENCIA: Volcado a soporte físico externo (Pandas)
    # ============================================================
    def guardar_datos(self):
        """
        Vuelca todo el contenido del administrador al fichero CSV modificado.
        Usa Pandas para la escritura, garantizando formato consistente.
        """
        lDatos = [{
            "Date": oReg.sDate,
            "Adj_Close": oReg.fAdjClose,
            "Close": oReg.fClose,
            "High": oReg.fHigh,
            "Low": oReg.fLow,
            "Open": oReg.fOpen,
            "Volume": oReg.iVolume
        } for oReg in self.dRegistros.values()]

        dfExportar = pd.DataFrame(lDatos)

        # Ordenamos por fecha antes de guardar para mantener coherencia
        dfExportar = dfExportar.sort_values(by="Date").reset_index(drop=True)
        dfExportar.to_csv(self.sFicheroModificado, index=False)

    # ============================================================
    # CRUD: ALTA (Control de duplicados)
    # ============================================================
    def alta_registro(self, oRegistro):
        """
        Incorpora una nueva entidad al sistema.
        Actúa como filtro infranqueable contra la redundancia:
        - Si el identificador ya existe -> devuelve ERR_DUPLICADO
        - Si es genuinamente nueva -> confirma con EXITO
        """
        if oRegistro.sDate in self.dRegistros:
            return GestorErrores.ERR_DUPLICADO

        self.dRegistros[oRegistro.sDate] = oRegistro
        self.guardar_datos()
        return GestorErrores.EXITO

    # ============================================================
    # CRUD: BAJA (Localización y eliminación)
    # ============================================================
    def baja_registro(self, sClave):
        """
        Localiza y elimina una entidad basándose en su clave de identidad.
        - Si la operación es exitosa -> devuelve EXITO ("OK")
        - Si no existe -> notifica ERR_NO_LOCALIZADO ("NO LOCALIZADO")
        """
        if sClave not in self.dRegistros:
            return GestorErrores.ERR_NO_LOCALIZADO

        del self.dRegistros[sClave]
        self.guardar_datos()
        return GestorErrores.EXITO

    # ============================================================
    # CONSULTA: Segmentación por rango (dos umbrales)
    # ============================================================
    def consulta_por_rango(self, sCampo, valor1_inicial1, valor2_final2):
        """
        Función de segmentación: el usuario define dos umbrales
        (valor1_inicial1 y valor2_final2) para un campo determinado.
        El software rastrear toda la colección y devuelve un conjunto
        exclusivo con las entidades dentro de ese intervalo.
        
        Parámetros:
            sCampo           -- Nombre del atributo a filtrar
            valor1_inicial1  -- Umbral inferior del rango
            valor2_final2    -- Umbral superior del rango
        
        Retorna:
            Lista de objetos RegistroBmw dentro del rango especificado.
        """
        lResultado = []

        for oRegistro in self.dRegistros.values():
            # Obtenemos el valor del campo solicitado del objeto
            valorCampo = getattr(oRegistro, sCampo, None)

            if valorCampo is None:
                continue

            # Comparamos si el valor está dentro del intervalo [inicial, final]
            if valor1_inicial1 <= valorCampo <= valor2_final2:
                lResultado.append(oRegistro)

        return lResultado

    # ============================================================
    # CONSULTA: Búsqueda por clave
    # ============================================================
    def consulta_por_clave(self, sClave):
        """Localiza un registro específico por su clave de identidad (fecha)."""
        return self.dRegistros.get(sClave, None)

    # ============================================================
    # LISTADO COMPLETO
    # ============================================================
    def listar_todos(self):
        """Devuelve todos los registros ordenados por fecha."""
        return sorted(self.dRegistros.values(), key=lambda r: r.sDate)
