PRAGMA foreign_keys = ON;

-- SAINT REPAIRS - MODELO DEFINITIVO SIMPLIFICADO
-- 15 TABLAS - alineado con DER definitivo

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    documento TEXT,
    fecha_alta DATE,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS equipos (
    id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    numero_serie TEXT,
    imei TEXT,
    color TEXT,
    clave_dispositivo TEXT,
    accesorios_entregados TEXT,
    estado_fisico TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'Tecnico',
    activo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ordenes_trabajo (
    id_orden INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_equipo INTEGER NOT NULL,
    id_tecnico INTEGER,
    fecha_ingreso DATE NOT NULL,
    fecha_estimada DATETIME,
    fecha_finalizacion DATETIME,
    problema_informado TEXT NOT NULL,
    diagnostico TEXT,
    solucion TEXT,
    estado TEXT NOT NULL DEFAULT 'En diagnostico',
    prioridad TEXT NOT NULL DEFAULT 'Normal',
    costo_final REAL DEFAULT 0,
    observaciones TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (id_tecnico) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS historial_estados (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL,
    id_usuario INTEGER,
    estado_anterior TEXT,
    estado_nuevo TEXT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comentario TEXT,
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS servicios (
    id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio_base REAL NOT NULL DEFAULT 0,
    tiempo_estimado INTEGER
);

CREATE TABLE IF NOT EXISTS servicios_orden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL,
    id_servicio INTEGER NOT NULL,
    precio REAL NOT NULL DEFAULT 0,
    cantidad INTEGER NOT NULL DEFAULT 1,
    subtotal REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio)
);

CREATE TABLE IF NOT EXISTS presupuestos (
    id_presupuesto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL,
    fecha DATE NOT NULL,
    subtotal REAL NOT NULL DEFAULT 0,
    descuento REAL NOT NULL DEFAULT 0,
    total REAL NOT NULL DEFAULT 0,
    estado TEXT NOT NULL DEFAULT 'Pendiente',
    fecha_vencimiento DATE,
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden)
);

CREATE TABLE IF NOT EXISTS detalle_presupuesto (
    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    id_presupuesto INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario REAL NOT NULL DEFAULT 0,
    subtotal REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (id_presupuesto) REFERENCES presupuestos(id_presupuesto)
);

CREATE TABLE IF NOT EXISTS pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL,
    fecha DATE NOT NULL,
    monto REAL NOT NULL,
    metodo_pago TEXT NOT NULL,
    tipo TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden)
);

CREATE TABLE IF NOT EXISTS entregas (
    id_entrega INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL UNIQUE,
    fecha DATETIME NOT NULL,
    recibido_por TEXT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden)
);

CREATE TABLE IF NOT EXISTS garantias (
    id_garantia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL UNIQUE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    condiciones TEXT,
    estado TEXT NOT NULL DEFAULT 'Activa',
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden)
);

CREATE TABLE IF NOT EXISTS insumos (
    id_insumo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    codigo TEXT UNIQUE,
    categoria TEXT,
    marca TEXT,
    modelo_compatible TEXT,
    costo REAL NOT NULL DEFAULT 0,
    precio_venta REAL NOT NULL DEFAULT 0,
    stock INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 0,
    ubicacion TEXT,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS insumos_orden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_orden INTEGER NOT NULL,
    id_insumo INTEGER NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario REAL NOT NULL DEFAULT 0,
    subtotal REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo),
    UNIQUE (id_orden, id_insumo)
);

CREATE TABLE IF NOT EXISTS movimientos_insumos (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_insumo INTEGER NOT NULL,
    id_orden INTEGER,
    id_usuario INTEGER,
    tipo TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo),
    FOREIGN KEY (id_orden) REFERENCES ordenes_trabajo(id_orden),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE INDEX IF NOT EXISTS idx_equipos_cliente ON equipos(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ordenes_cliente ON ordenes_trabajo(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ordenes_equipo ON ordenes_trabajo(id_equipo);
CREATE INDEX IF NOT EXISTS idx_ordenes_tecnico ON ordenes_trabajo(id_tecnico);
CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes_trabajo(estado);
CREATE INDEX IF NOT EXISTS idx_historial_orden ON historial_estados(id_orden);
CREATE INDEX IF NOT EXISTS idx_ordenes_fecha_estimada ON ordenes_trabajo(fecha_estimada);
CREATE INDEX IF NOT EXISTS idx_entregas_fecha ON entregas(fecha);
CREATE INDEX IF NOT EXISTS idx_servicios_orden_orden ON servicios_orden(id_orden);
CREATE INDEX IF NOT EXISTS idx_presupuestos_orden ON presupuestos(id_orden);
CREATE INDEX IF NOT EXISTS idx_detalle_presupuesto ON detalle_presupuesto(id_presupuesto);
CREATE INDEX IF NOT EXISTS idx_pagos_orden ON pagos(id_orden);
CREATE INDEX IF NOT EXISTS idx_entregas_orden ON entregas(id_orden);
CREATE INDEX IF NOT EXISTS idx_garantias_fecha_fin ON garantias(fecha_fin);
CREATE INDEX IF NOT EXISTS idx_insumos_orden ON insumos_orden(id_orden);
CREATE INDEX IF NOT EXISTS idx_movimientos_insumo ON movimientos_insumos(id_insumo);
CREATE INDEX IF NOT EXISTS idx_movimientos_orden ON movimientos_insumos(id_orden);
