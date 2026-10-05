from pathlib import Path
import sqlite3
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'database' / 'saint_repairs.db'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def _schema_is_current(conn):
    """Comprueba que la base existente sea compatible con el DER definitivo de 15 tablas.

    CREATE TABLE IF NOT EXISTS no modifica tablas antiguas. Por eso, si el usuario
    ya tenía una base de una versión anterior, primero detectamos el esquema viejo
    para evitar errores como: sqlite3.OperationalError: no such column: fecha.
    """
    required = {
        "clientes": {"id_cliente", "nombre", "apellido", "telefono", "email", "direccion", "documento", "fecha_alta", "observaciones"},
        "equipos": {"id_equipo", "id_cliente", "tipo", "marca", "modelo", "numero_serie", "imei", "color", "clave_dispositivo", "accesorios_entregados", "estado_fisico", "observaciones"},
        "usuarios": {"id_usuario", "nombre", "usuario", "contrasena_hash", "rol", "activo"},
        "ordenes_trabajo": {"id_orden", "id_cliente", "id_equipo", "id_tecnico", "fecha_ingreso", "fecha_estimada", "fecha_finalizacion", "problema_informado", "diagnostico", "solucion", "estado", "prioridad", "costo_final", "observaciones"},
        "historial_estados": {"id_historial", "id_orden", "id_usuario", "estado_anterior", "estado_nuevo", "fecha", "comentario"},
        "servicios": {"id_servicio", "nombre", "descripcion", "precio_base", "tiempo_estimado"},
        "servicios_orden": {"id", "id_orden", "id_servicio", "precio", "cantidad", "subtotal"},
        "presupuestos": {"id_presupuesto", "id_orden", "fecha", "subtotal", "descuento", "total", "estado", "fecha_vencimiento"},
        "detalle_presupuesto": {"id_detalle", "id_presupuesto", "descripcion", "cantidad", "precio_unitario", "subtotal"},
        "pagos": {"id_pago", "id_orden", "fecha", "monto", "metodo_pago", "tipo", "observaciones"},
        "entregas": {"id_entrega", "id_orden", "fecha", "recibido_por", "observaciones"},
        "garantias": {"id_garantia", "id_orden", "fecha_inicio", "fecha_fin", "condiciones", "estado"},
        "insumos": {"id_insumo", "nombre", "codigo", "categoria", "marca", "modelo_compatible", "costo", "precio_venta", "stock", "stock_minimo", "ubicacion", "observaciones"},
        "insumos_orden": {"id", "id_orden", "id_insumo", "cantidad", "precio_unitario", "subtotal"},
        "movimientos_insumos": {"id_movimiento", "id_insumo", "id_orden", "id_usuario", "tipo", "cantidad", "fecha", "motivo", "observaciones"},
    }

    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not set(required).issubset(tables):
        return False

    for table, expected in required.items():
        columns = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        if not expected.issubset(columns):
            return False
    return True


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # IMPORTANTE: el programa puede venir de una versión anterior con tablas
    # diferentes. SQLite no actualiza una tabla existente mediante CREATE TABLE
    # IF NOT EXISTS y los índices del esquema nuevo pueden fallar (por ejemplo,
    # "no such column: fecha"). Detectamos ese caso y hacemos una copia de
    # seguridad antes de crear la base definitiva.
    if DB_PATH.exists():
        check_conn = sqlite3.connect(DB_PATH)
        try:
            current = _schema_is_current(check_conn)
        finally:
            check_conn.close()

        if not current:
            backup = DB_PATH.with_name(DB_PATH.stem + "_backup_esquema_anterior.db")
            # Si ya existe una copia, generamos una numerada para no perderla.
            n = 1
            candidate = backup
            while candidate.exists():
                candidate = DB_PATH.with_name(DB_PATH.stem + f"_backup_esquema_anterior_{n}.db")
                n += 1
            DB_PATH.replace(candidate)

    with get_connection() as conn:
        schema = (BASE_DIR / 'database' / 'schema.sql').read_text(encoding='utf-8')
        conn.executescript(schema)
        seed(conn)


def seed(conn):
    # Usuario inicial. El rol es un atributo simple, no una tabla relacionada.
    conn.execute(
        """INSERT OR IGNORE INTO usuarios(nombre,usuario,contrasena_hash,rol,activo)
           VALUES (?,?,?,?,1)""",
        ('Administrador', 'admin', 'admin', 'Administrador')
    )

    servicios = [
        ('Diagnóstico', 'Diagnóstico general del equipo', 15000, 60),
        ('Cambio de pantalla', 'Reemplazo de display', 45000, 120),
        ('Limpieza interna', 'Limpieza y mantenimiento', 20000, 90),
        ('Cambio de batería', 'Reemplazo de batería', 25000, 60),
        ('Reparación de placa', 'Reparación electrónica', 60000, 240),
    ]
    for item in servicios:
        conn.execute(
            'INSERT OR IGNORE INTO servicios(nombre,descripcion,precio_base,tiempo_estimado) VALUES (?,?,?,?)',
            item
        )

    if conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0] == 0:
        conn.execute(
            '''INSERT INTO clientes(nombre,apellido,telefono,email,direccion,documento,fecha_alta,observaciones)
               VALUES (?,?,?,?,?,?,?,?)''',
            ('Juan', 'Pérez', '11-5555-1111', 'juan@example.com', 'Calle 10 123',
             '30111222', date.today().isoformat(), 'Cliente de demostración')
        )
        cid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.execute(
            '''INSERT INTO equipos(id_cliente,tipo,marca,modelo,numero_serie,estado_fisico,observaciones)
               VALUES (?,?,?,?,?,?,?)''',
            (cid, 'Celular', 'Apple', 'iPhone 11', 'SN-IPH-001', 'Bueno', 'Equipo de demostración')
        )
        eid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.execute(
            '''INSERT INTO ordenes_trabajo
               (id_cliente,id_equipo,id_tecnico,fecha_ingreso,fecha_estimada,problema_informado,estado,prioridad,observaciones)
               VALUES (?,?,?,?,?,?,?,?,?)''',
            (cid, eid, 1, date.today().isoformat(), None, 'No carga', 'En diagnostico', 'Alta',
             'Equipo ingresado para diagnóstico')
        )
        oid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.execute(
            '''INSERT INTO historial_estados(id_orden,id_usuario,estado_nuevo,comentario)
               VALUES (?,?,?,?)''',
            (oid, 1, 'En diagnostico', 'Alta de orden')
        )

    if conn.execute('SELECT COUNT(*) FROM insumos').fetchone()[0] == 0:
        demo = [
            ('Pantalla iPhone 11', 'INS-00123', 'Pantallas', 'Genérica', 'iPhone 11', 30000, 55000, 5, 5, 'A-01', 'Display de reemplazo'),
            ('Pantalla Samsung A32', 'INS-00456', 'Pantallas', 'Genérica', 'Samsung A32', 22000, 42000, 1, 3, 'A-02', 'Display de reemplazo'),
            ('Conector USB-C', 'INS-00031', 'Conectores', 'Universal', 'USB-C', 3500, 8000, 8, 3, 'B-01', 'Conector universal'),
            ('Pasta térmica', 'INS-00044', 'Consumibles', 'Genérica', 'Notebook/PC', 2500, 5500, 12, 4, 'C-01', 'Consumible'),
        ]
        for item in demo:
            conn.execute(
                '''INSERT INTO insumos
                   (nombre,codigo,categoria,marca,modelo_compatible,costo,precio_venta,stock,stock_minimo,ubicacion,observaciones)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)''', item
            )
    conn.commit()
