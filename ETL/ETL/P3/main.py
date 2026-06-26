

import sqlite3
from gestorbd import (CSV_PATH, DB_PATH, crear_esquema, crear_triggers, cargar_datos,
                      insertar_registro, buscar_registro, actualizar_registro,
                      eliminar_registro, mostrar_registros,
                      consulta_cte_sobre_media, consulta_window_functions,
                      modificacion_masiva, ver_auditoria)
import os


# ─────────────────────────────────────────────
# SUBMENÚS
# ─────────────────────────────────────────────
def submenu_crud(con: sqlite3.Connection) -> None:
    # Menú: Insertar, Buscar, Actualizar, Eliminar, Mostrar registros
    print("\n--- MÓDULO CRUD ---")
    print("1. Insertar | 2. Buscar | 3. Actualizar | 4. Eliminar | 5. Mostrar registros")
    sOpc = input("Opción: ").strip()

    if   sOpc == "1": insertar_registro(con)
    elif sOpc == "2": buscar_registro(con)
    elif sOpc == "3": actualizar_registro(con)
    elif sOpc == "4": eliminar_registro(con)
    elif sOpc == "5": mostrar_registros(con)
    else: print("  ⚠  Opción no válida.")


def submenu_analitica(con: sqlite3.Connection) -> None:
    # CTE (media anual) + Window Functions (volumen) + Modif. masiva
    print("\n--- MÓDULO ANALÍTICA ---")
    print("1. CTE: cierres sobre la media anual")
    print("2. Window Function: volumen acumulado por año")
    print("3. Modificación masiva (+2% Close días > 10M volumen)")
    sOpc = input("Opción: ").strip()

    if   sOpc == "1": consulta_cte_sobre_media(con)
    elif sOpc == "2": consulta_window_functions(con)
    elif sOpc == "3": modificacion_masiva(con)
    else: print("  ⚠  Opción no válida.")


# ─────────────────────────────────────────────
# MENÚ PRINCIPAL
# ─────────────────────────────────────────────
def main() -> None:
    # Sistema: verifica CSV → conecta BD → crea esquema → menú interactivo
    print("=" * 60)
    print("  PROBLEMA 3 – Base de datos relacional BMW")
    print("=" * 60)

    #  Validar que existe el archivo CSV con datos
    # Si no existe, terminar sin crear BD (evita BD vacía)
    if not os.path.exists(CSV_PATH):
        print(f"  ✖  Error: Archivo CSV '{CSV_PATH}' no encontrado.")
        print("  Verifica que exista BMW_Data.csv en la ruta correcta.")
        return

    try:
        # Conectar con validación de FK
        con = sqlite3.connect(DB_PATH)
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        
        # Crear esquema (4 tablas) si no existe
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Cotizacion'")
            if not cur.fetchone():
                crear_esquema(cur)
                crear_triggers(cur)
                cargar_datos(con)
                con.commit()
        except sqlite3.DatabaseError:
            crear_esquema(cur)
            crear_triggers(cur)
            con.commit()

        # Verificar BD
        try:
            total = con.execute("SELECT COUNT(*) FROM Cotizacion").fetchone()[0]
            print(f"  ✔  BD conectada ({total} registros).")
        except sqlite3.OperationalError:
            print("  ✖  Error: No se pudo acceder a la base de datos.")
            con.close()
            return

        # Menú principal
        sOpcion = ""
        while sOpcion != "0":
            print("\n" + "=" * 45)
            print("  SISTEMA BMW — SQLite Edition")
            print("=" * 45)
            print("1. Módulo CRUD        (Insertar/Buscar/Actualizar/Eliminar)")
            print("2. Módulo Analítica   (CTE + Window Function + Modif. masiva)")
            print("3. Ver Auditoría")
            print("0. Salir")

            sOpcion = input("Selecciona un módulo: ").strip()

            try:
                match sOpcion:
                    case "1": submenu_crud(con)
                    case "2": submenu_analitica(con)
                    case "3":
                        # Ver auditoría: últimas N operaciones registradas automáticamente
                        n = input("  ¿Cuántas entradas mostrar? (defecto 8): ").strip()
                        ver_auditoria(con, int(n) if n.isdigit() else 8)
                    case "0":
                        print("Saliendo… ¡Hasta pronto!")
                    case _:
                        print("Opción no válida.")
            except Exception as e:
                # Atrapar errores durante la operación (ej: división por cero en input)
                print(f"  ✖  Error durante la operación: {e}")

        #Cerrar conexión
        con.close()
        
    except sqlite3.DatabaseError as e:
        # Error específico de BD (corrupción, acceso denegado, etc)
        print(f"  ✖  Error de base de datos: {e}")
    except Exception as e:
        # Cualquier otro error no previsto
        print(f"  ✖  Error inesperado: {e}")


if __name__ == "__main__":
    main()
