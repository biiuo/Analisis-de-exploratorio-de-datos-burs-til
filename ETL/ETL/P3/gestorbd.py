import csv
import os
import sqlite3

from gestorerrores import GestorErrores
from validaciones  import (validar_fecha, validar_precio, validar_adj_close,
                            validar_volumen, validar_coherencia_ohlc, pedir_campo)

CSV_PATH = "BMW_Data.csv"
DB_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BBDD.sqlite")




# ESQUEMA
def crear_esquema(cur: sqlite3.Cursor) -> None:
    # 4 tablas en 3NF: Cotizacion (padre), Precio, Volumen, Auditoria (log)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Cotizacion (
            cot_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT    NOT NULL UNIQUE,
            adj_close REAL    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Precio (
            precio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            open      REAL    NOT NULL,
            high      REAL    NOT NULL,
            low       REAL    NOT NULL,
            close     REAL    NOT NULL,
            cot_id    INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (cot_id) REFERENCES Cotizacion(cot_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Volumen (
            vol_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            volume    INTEGER NOT NULL,
            cot_id    INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (cot_id) REFERENCES Cotizacion(cot_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Auditoria (
            aud_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            tabla      TEXT    NOT NULL,
            operacion  TEXT    NOT NULL,
            fecha_hora TEXT    NOT NULL,
            cot_id     INTEGER,
            detalle    TEXT
        )
    """)




# TRIGGERS
def crear_triggers(cur: sqlite3.Cursor) -> None:
    # 6 triggers (INSERT/UPDATE/DELETE) registran cambios automáticamente en Auditoria

    # INSERT en Precio
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_precio_insert
        AFTER INSERT ON Precio
        BEGIN
            INSERT INTO Auditoria (tabla, operacion, fecha_hora, cot_id, detalle)
            VALUES ('Precio', 'INSERT', datetime('now'), NEW.cot_id,
                'Open=' || NEW.open || ' High=' || NEW.high ||
                ' Low='  || NEW.low  || ' Close=' || NEW.close);
        END
    """)

    # UPDATE en Precio
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_precio_update
        AFTER UPDATE ON Precio
        BEGIN
            INSERT INTO Auditoria (tabla, operacion, fecha_hora, cot_id, detalle)
            VALUES ('Precio', 'UPDATE', datetime('now'), NEW.cot_id,
                'Open: '  || OLD.open  || ' -> ' || NEW.open  || ' | ' ||
                'High: '  || OLD.high  || ' -> ' || NEW.high  || ' | ' ||
                'Low: '   || OLD.low   || ' -> ' || NEW.low   || ' | ' ||
                'Close: ' || OLD.close || ' -> ' || NEW.close);
        END
    """)

    # DELETE en Precio
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_precio_delete
        AFTER DELETE ON Precio
        BEGIN
            INSERT INTO Auditoria (tabla, operacion, fecha_hora, cot_id, detalle)
            VALUES ('Precio', 'DELETE', datetime('now'), OLD.cot_id,
                'Open=' || OLD.open || ' High=' || OLD.high ||
                ' Low='  || OLD.low  || ' Close=' || OLD.close);
        END
    """)

    # INSERT en Volumen
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_volumen_insert
        AFTER INSERT ON Volumen
        BEGIN
            INSERT INTO Auditoria (tabla, operacion, fecha_hora, cot_id, detalle)
            VALUES ('Volumen', 'INSERT', datetime('now'), NEW.cot_id,
                'Volume=' || NEW.volume);
        END
    """)

    # UPDATE en Volumen
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_volumen_update
        AFTER UPDATE ON Volumen
        BEGIN
            INSERT INTO Auditoria (tabla, operacion, fecha_hora, cot_id, detalle)
            VALUES ('Volumen', 'UPDATE', datetime('now'), NEW.cot_id,
                'Volume: ' || OLD.volume || ' -> ' || NEW.volume);
        END
    """)

    # DELETE en Volumen
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_volumen_delete
        AFTER DELETE ON Volumen
        BEGIN
            INSERT INTO Auditoria (tabla, operacion, fecha_hora, cot_id, detalle)
            VALUES ('Volumen', 'DELETE', datetime('now'), OLD.cot_id,
                'Volume=' || OLD.volume);
        END
    """)



# ─────────────────────────────────────────────
# CARGA DESDE CSV
# ─────────────────────────────────────────────
def cargar_datos(con: sqlite3.Connection) -> None:
    """
    Puebla las tres tablas en orden obligatorio por las FK:
      1. Cotizacion (tabla padre, debe existir primero)
      2. Precio     (referencia cot_id)
      3. Volumen    (referencia cot_id)
    """
    cur = con.cursor()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            fecha = fila["Date"].strip()

            # 1. Cotizacion
            cur.execute(
                "INSERT OR IGNORE INTO Cotizacion (fecha, adj_close) VALUES (?,?)",
                (fecha, float(fila["Adj_Close"]))
            )
            cot_id = cur.execute(
                "SELECT cot_id FROM Cotizacion WHERE fecha=?", (fecha,)
            ).fetchone()[0]

            # 2. Precio (OHLC)
            cur.execute(
                "INSERT OR IGNORE INTO Precio (open,high,low,close,cot_id) VALUES (?,?,?,?,?)",
                (float(fila["Open"]), float(fila["High"]),
                 float(fila["Low"]),  float(fila["Close"]), cot_id)
            )

            # 3. Volumen
            cur.execute(
                "INSERT OR IGNORE INTO Volumen (volume, cot_id) VALUES (?,?)",
                (int(fila["Volume"]), cot_id)
            )
    con.commit()
    print(f"  ✔  Datos cargados desde {CSV_PATH}.")



# ─────────────────────────────────────────────
# CONSULTAS ANALÍTICAS
# ─────────────────────────────────────────────
def consulta_cte_sobre_media(con: sqlite3.Connection) -> None:
    """
    CTE: días cuyo Close supera la media anual de su propio año.
    Cruza Cotizacion + Precio en dos niveles.
    """
    sql = """
    WITH media_anual AS (
        SELECT  SUBSTR(c.fecha, 1, 4) AS anio,
                AVG(p.close)          AS media_close
        FROM    Cotizacion c
        JOIN    Precio     p ON p.cot_id = c.cot_id
        GROUP BY anio
    )
    SELECT  c.fecha,
            p.close,
            ROUND(ma.media_close, 4)           AS media,
            ROUND(p.close - ma.media_close, 4) AS desviacion
    FROM    Cotizacion  c
    JOIN    Precio      p  ON p.cot_id  = c.cot_id
    JOIN    media_anual ma ON SUBSTR(c.fecha,1,4) = ma.anio
    WHERE   p.close > ma.media_close
    ORDER BY desviacion DESC
    LIMIT 10
    """
    print("\n── CTE: Top 10 cierres por encima de la media anual ──")
    print(f"  {'Fecha':<14} {'Close':>10} {'Media':>10} {'Desviac.':>10}")
    print("  " + "-" * 46)
    for row in con.execute(sql):
        print(f"  {row[0]:<14} {row[1]:>10.4f} {row[2]:>10.4f} {row[3]:>10.4f}")


def consulta_window_functions(con: sqlite3.Connection) -> None:
    """
    Window Function: volumen acumulado histórico por año.
    Cruza las 3 tablas (Cotizacion, Precio, Volumen).
    """
    sql = """
    SELECT  SUBSTR(c.fecha,1,4)              AS anio,
            COUNT(*)                         AS sesiones,
            ROUND(AVG(p.close),4)            AS media_close,
            ROUND(MAX(p.high)-MIN(p.low),4)  AS rango_precio,
            SUM(v.volume)                    AS vol_anual,
            SUM(SUM(v.volume)) OVER (
                ORDER BY SUBSTR(c.fecha,1,4)
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )                                AS vol_acumulado
    FROM    Cotizacion c
    JOIN    Precio     p ON p.cot_id = c.cot_id
    JOIN    Volumen    v ON v.cot_id = c.cot_id
    GROUP BY anio
    ORDER BY anio DESC
    LIMIT 10
    """
    print("\n── Window Function: volumen acumulado por año ──")
    print(f"  {'Año':>4} {'Sesiones':>9} {'MediaClose':>11} "
          f"{'RangoPrecio':>12} {'VolAnual':>14} {'VolAcumulado':>14}")
    print("  " + "-" * 70)
    for row in con.execute(sql):
        print(f"  {row[0]:>4} {row[1]:>9} {row[2]:>11.4f} "
              f"{row[3]:>12.4f} {row[4]:>14,} {row[5]:>14,}")


def modificacion_masiva(con: sqlite3.Connection) -> None:
    """
    UPDATE masivo que involucra Precio y Volumen:
    Sube un 2% el Close de los días con volume > 10.000.000.
    Condición en Volumen, actualización en Precio → dos tablas relacionadas.
    Los triggers registran cada UPDATE en Auditoria automáticamente.
    """
    sql = """
        UPDATE Precio
        SET    close = ROUND(close * 1.02, 6)
        WHERE  cot_id IN (
                   SELECT cot_id FROM Volumen WHERE volume > 10000000
               )
    """
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    print(f"\n── Modificación masiva: {cur.rowcount} días con volume > 10M "
          f"actualizados (+2% en Close).")


def ver_auditoria(con: sqlite3.Connection, limite: int = 8) -> None:
    """
    Muestra los últimos registros de Auditoria agrupados por cotización:
    Precio y Volumen del mismo día aparecen juntos bajo la misma fecha,
    mostrando el cot_id (clave de Cotizacion) en lugar del aud_id interno.
    Ordenado por aud_id DESC para mostrar siempre las operaciones más recientes.
    """
    sql = """
        SELECT  a.cot_id,
                COALESCE(c.fecha, '(eliminado)') AS fecha_bolsa,
                a.operacion,
                a.fecha_hora,
                GROUP_CONCAT(a.tabla || ': ' || a.detalle, ' | ') AS detalle
        FROM    Auditoria  a
        LEFT JOIN Cotizacion c ON c.cot_id = a.cot_id
        GROUP BY a.cot_id, a.operacion, a.fecha_hora
        ORDER BY MAX(a.aud_id) DESC
        LIMIT ?
    """
    print(f"\n── Últimas {limite} operaciones de Auditoría ──")
    print(f"  {'cot_id':>7} {'Fecha bolsa':<14} {'Op':<8} {'Fecha-Hora':<22} {'Detalle'}")
    print("  " + "-" * 90)
    for row in con.execute(sql, (limite,)):
        cot_id, fecha_bolsa, op, fecha_hora, detalle = row
        print(f"  {cot_id:>7} {fecha_bolsa:<14} {op:<8} {fecha_hora:<22} {detalle}")



# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────
def insertar_registro(con: sqlite3.Connection) -> None:
    """
    Inserta un nuevo día de cotización en las tres tablas:
    Cotizacion, Precio y Volumen.
    Valida cada campo antes de insertar.
    El trigger registra el INSERT en Auditoria automáticamente.
    """
    print("\n── Insertar registro ──")

    fecha = pedir_campo(
        "Fecha (YYYY-MM-DD)", validar_fecha,
        GestorErrores.getMensaje(GestorErrores.ERR_FECHA_FORMATO))

    # Comprobar que la fecha no existe ya en la BD
    if con.execute("SELECT 1 FROM Cotizacion WHERE fecha=?", (fecha,)).fetchone():
        print(f"  ✖  {GestorErrores.getMensaje(GestorErrores.ERR_FECHA_DUPLICADA)}")
        return

    open_p = pedir_campo(
        "Open  (decimal > 0)", validar_precio,
        GestorErrores.getMensaje(GestorErrores.ERR_PRECIO_RANGO))

    high = pedir_campo(
        "High  (decimal > 0)", validar_precio,
        GestorErrores.getMensaje(GestorErrores.ERR_PRECIO_RANGO))

    low = pedir_campo(
        "Low   (decimal > 0)", validar_precio,
        GestorErrores.getMensaje(GestorErrores.ERR_PRECIO_RANGO))

    close = pedir_campo(
        "Close (decimal > 0)", validar_precio,
        GestorErrores.getMensaje(GestorErrores.ERR_PRECIO_RANGO))

    # Adj_Close se pide DESPUÉS de Close
    adj_close = float(input("  Adj_Close (decimal > 0): ").strip())

    volume = pedir_campo(
        "Volume (entero >= 0)", validar_volumen,
        GestorErrores.getMensaje(GestorErrores.ERR_VOLUMEN_RANGO))

    if int(volume) == 0:
        print("  ℹ  Aviso: Volume = 0 (día festivo o cierre parcial).")

    # Validación de coherencia OHLC
    lErroresOhlc = validar_coherencia_ohlc(open_p, high, low, close)
    bBloquear = False
    for iErr in lErroresOhlc:
        print(f"  ⚠  {GestorErrores.getMensaje(iErr)}")
        if iErr == GestorErrores.ERR_OHLC_HIGH_LOW:
            bBloquear = True

    if bBloquear:
        print("  ✖  Inserción cancelada por error crítico en precios OHLC.")
        return

    cur = con.cursor()
    try:
        # 1. Cotizacion (tabla padre)
        cur.execute(
            "INSERT INTO Cotizacion (fecha, adj_close) VALUES (?,?)",
            (fecha, adj_close)
        )
        cot_id = cur.lastrowid

        # 2. Precio (trigger dispara INSERT en Auditoria)
        cur.execute(
            "INSERT INTO Precio (open,high,low,close,cot_id) VALUES (?,?,?,?,?)",
            (open_p, high, low, close, cot_id)
        )

        # 3. Volumen (trigger dispara INSERT en Auditoria)
        cur.execute(
            "INSERT INTO Volumen (volume,cot_id) VALUES (?,?)",
            (volume, cot_id)
        )
        con.commit()
        print(f"  ✔  Registro '{fecha}' insertado (cot_id={cot_id}).")
    except sqlite3.IntegrityError as e:
        con.rollback()
        print(f"  ✖  Error: {e}")


def buscar_registro(con: sqlite3.Connection) -> None:
    """
    Busca un día por fecha y muestra sus datos de las tres tablas.
    Usa JOIN para reconstruir la fila completa.
    """
    print("\n── Buscar registro ──")
    fecha = input("  Fecha (YYYY-MM-DD): ").strip()

    sql = """
        SELECT  c.fecha, c.adj_close,
                p.open, p.high, p.low, p.close,
                v.volume
        FROM    Cotizacion c
        JOIN    Precio     p ON p.cot_id = c.cot_id
        JOIN    Volumen    v ON v.cot_id = c.cot_id
        WHERE   c.fecha = ?
    """
    row = con.execute(sql, (fecha,)).fetchone()
    if row:
        campos = ["Fecha", "Adj_Close", "Open", "High", "Low", "Close", "Volume"]
        print()
        for campo, valor in zip(campos, row):
            print(f"  {campo:<12} {valor}")
    else:
        print(f"  ✖  {GestorErrores.getMensaje(GestorErrores.ERR_REGISTRO_NO_ENCONTRADO)}")


def actualizar_registro(con: sqlite3.Connection) -> None:
    """
    Actualiza Open, High, Low, Close, Adj_Close y Volume de un día.
    Los triggers registran cada UPDATE en Auditoria automáticamente.
    """
    print("\n── Actualizar registro ──")
    fecha = input("  Fecha del registro a actualizar (YYYY-MM-DD): ").strip()

    row = con.execute(
        "SELECT cot_id FROM Cotizacion WHERE fecha=?", (fecha,)
    ).fetchone()
    if not row:
        print(f"  ✖  {GestorErrores.getMensaje(GestorErrores.ERR_REGISTRO_NO_ENCONTRADO)}")
        return

    cot_id = row[0]
    print("  (Enter para dejar el valor sin cambios)")

    # ── Campos de Precio ──
    nuevo_open   = input("  Nuevo Open      : ").strip()
    nuevo_high   = input("  Nuevo High      : ").strip()
    nuevo_low    = input("  Nuevo Low       : ").strip()
    nuevo_close  = input("  Nuevo Close     : ").strip()
    # ── Cotizacion ──
    nuevo_adj    = input("  Nuevo Adj_Close : ").strip()
    # ── Volumen ──
    nuevo_volume = input("  Nuevo Volume    : ").strip()

    # Validaciones de precio
    for val in [nuevo_open, nuevo_high, nuevo_low, nuevo_close, nuevo_adj]:
        if val and validar_precio(val) != GestorErrores.EXITO:
            print(f"  ✖  {GestorErrores.getMensaje(GestorErrores.ERR_PRECIO_RANGO)}")
            return

    # Validación de volumen
    if nuevo_volume and validar_volumen(nuevo_volume) != GestorErrores.EXITO:
        print(f"  ✖  {GestorErrores.getMensaje(GestorErrores.ERR_VOLUMEN_RANGO)}")
        return

    cur = con.cursor()
    try:
        # Actualizar Precio si se cambió algún campo OHLC
        if nuevo_open or nuevo_high or nuevo_low or nuevo_close:
            cur.execute("""
                UPDATE Precio SET
                    open  = COALESCE(NULLIF(?, ''), CAST(open  AS TEXT)),
                    high  = COALESCE(NULLIF(?, ''), CAST(high  AS TEXT)),
                    low   = COALESCE(NULLIF(?, ''), CAST(low   AS TEXT)),
                    close = COALESCE(NULLIF(?, ''), CAST(close AS TEXT))
                WHERE cot_id = ?
            """, (nuevo_open  or None,
                  nuevo_high  or None,
                  nuevo_low   or None,
                  nuevo_close or None,
                  cot_id))

        # Actualizar Adj_Close en Cotizacion
        if nuevo_adj:
            cur.execute(
                "UPDATE Cotizacion SET adj_close=? WHERE cot_id=?",
                (float(nuevo_adj), cot_id)
            )

        # Actualizar Volumen
        if nuevo_volume:
            if int(nuevo_volume) == 0:
                print("  ℹ  Aviso: Volume = 0 (día festivo o cierre parcial).")
            cur.execute(
                "UPDATE Volumen SET volume=? WHERE cot_id=?",
                (int(nuevo_volume), cot_id)
            )

        con.commit()
        print(f"  ✔  Registro '{fecha}' actualizado.")
    except Exception as e:
        con.rollback()
        print(f"  ✖  Error: {e}")


def eliminar_registro(con: sqlite3.Connection) -> None:
    """
    Elimina un día completo de las tres tablas.
    El orden importa: primero hijos (Precio, Volumen) luego padre (Cotizacion).
    Los triggers registran el DELETE en Auditoria automáticamente.
    """
    print("\n── Eliminar registro ──")
    fecha = input("  Fecha (YYYY-MM-DD): ").strip()

    row = con.execute(
        "SELECT cot_id FROM Cotizacion WHERE fecha=?", (fecha,)
    ).fetchone()
    if not row:
        print(f"  ✖  {GestorErrores.getMensaje(GestorErrores.ERR_REGISTRO_NO_ENCONTRADO)}")
        return

    cot_id = row[0]
    cur = con.cursor()
    try:
        # Borrar primero las tablas hijas (FK lo exige)
        # Los triggers trg_precio_delete y trg_volumen_delete registran en Auditoria
        cur.execute("DELETE FROM Precio    WHERE cot_id=?", (cot_id,))
        cur.execute("DELETE FROM Volumen   WHERE cot_id=?", (cot_id,))
        cur.execute("DELETE FROM Cotizacion WHERE cot_id=?", (cot_id,))
        con.commit()
        print(f"  ✔  Registro '{fecha}' eliminado de Cotizacion, Precio y Volumen.")
    except Exception as e:
        con.rollback()
        print(f"  ✖  Error: {e}")


def mostrar_registros(con: sqlite3.Connection) -> None:
    cantidad = int(input("\n  Ingrese cantidad de registros a mostrar: "))
    print(f"\n── Últimos {cantidad} registros ──")
    sql = """
        SELECT  c.fecha, c.adj_close,
                p.open, p.high, p.low, p.close,
                v.volume
        FROM    Cotizacion c
        JOIN    Precio     p ON p.cot_id = c.cot_id
        JOIN    Volumen    v ON v.cot_id = c.cot_id
        ORDER BY c.fecha DESC
        LIMIT ?
    """
    print(f"\n  {'Fecha':<14} {'Adj_Cl':>8} {'Open':>8} "
          f"{'High':>8} {'Low':>8} {'Close':>8} {'Volume':>12}")
    print("  " + "-" * 72)
    for row in con.execute(sql, (cantidad,)):
        print(f"  {row[0]:<14} {row[1]:>8.4f} {row[2]:>8.4f} "
              f"{row[3]:>8.4f} {row[4]:>8.4f} {row[5]:>8.4f} {row[6]:>12,}")