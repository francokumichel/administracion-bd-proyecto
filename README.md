# SAINT REPAIRS

Sistema de escritorio para la gestión integral de un **taller de reparación de electrónica**. Permite registrar clientes y equipos, seguir el ciclo de vida de cada orden de trabajo, controlar el stock de insumos, emitir presupuestos en PDF, registrar pagos, entregas y garantías, y consultar reportes operativos.

Proyecto desarrollado en el curso **Administración de Bases de Datos**: la aplicación está construida sobre un modelo relacional de **15 tablas** (SQLite) con claves foráneas y restricciones de integridad.

---

## Tabla de contenidos

1. [Qué ofrece](#qué-ofrece)
2. [Tecnologías](#tecnologías)
3. [Requisitos](#requisitos)
4. [Instalación y ejecución](#instalación-y-ejecución)
5. [Primer acceso](#primer-acceso)
6. [Módulos del sistema](#módulos-del-sistema)
7. [Flujo de trabajo de una orden](#flujo-de-trabajo-de-una-orden)
8. [Base de datos](#base-de-datos)
9. [Estructura del proyecto](#estructura-del-proyecto)
10. [Notas y limitaciones](#notas-y-limitaciones)

---

## Qué ofrece

- **Gestión de órdenes de trabajo**: alta, edición, asignación de técnico, prioridad, fecha estimada, diagnóstico, solución e historial completo de cambios de estado.
- **Clientes y equipos**: cada cliente puede tener múltiples equipos (tipo, marca, modelo, N° de serie, IMEI, accesorios entregados, estado físico, etc.).
- **Servicios e insumos por orden**: se cargan los servicios realizados y los repuestos utilizados; el stock se descuenta y se devuelve automáticamente, dejando registro en los movimientos.
- **Inventario de insumos**: control de stock, stock mínimo, ubicación, entradas manuales y trazabilidad de movimientos.
- **Presupuestos**: editor con líneas de detalle, descuento porcentual, vencimiento y estado; generación de **PDF**; envío preparado por **WhatsApp** o **Email**.
- **Pagos, entregas y garantías**: registro de señas/pagos por método, entrega del equipo (que cierra la orden) y garantías con fecha de inicio y fin.
- **Dashboard**: órdenes en proceso, listas para entregar, esperando repuestos, ingresos del mes, alertas (insumos bajo mínimo, órdenes demoradas) y agenda próxima.
- **Reportes**: órdenes por estado, ingresos del mes, stock bajo, movimientos de insumos y exportación de órdenes a **CSV**.
- **Calendario** de fechas estimadas de entrega.
- **Usuarios** con inicio de sesión y roles (Administrador, Técnico, Recepción).

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3 |
| Interfaz gráfica | Tkinter / ttk (incluido en la biblioteca estándar) |
| Base de datos | SQLite 3 (módulo `sqlite3` de la biblioteca estándar) |
| Generación de PDF | [ReportLab](https://pypi.org/project/reportlab/) `>= 4.0` |

## Requisitos

- **Python 3.8 o superior** con soporte para Tkinter.
  - En Windows y macOS viene incluido con el instalador oficial de Python.
  - En Linux (Debian/Ubuntu) puede requerir: `sudo apt install python3-tk`.
- **pip** para instalar la dependencia de PDF.

## Instalación y ejecución

1. **Clonar el repositorio** (o descargar el código):

   ```bash
   git clone <url-del-repositorio>
   cd administracion-bd-proyecto
   ```

2. **(Opcional) Crear un entorno virtual**:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instalar las dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**:

   ```bash
   python main.py
   ```

   En Windows también se puede hacer doble clic sobre **`ejecutar.bat`**.

Al iniciar, el sistema crea automáticamente la base de datos (`database/saint_repairs.db`), aplica el esquema y carga datos iniciales de demostración. No hace falta configurar nada más.

## Primer acceso

Usuario inicial creado automáticamente:

| Usuario | Contraseña |
|---|---|
| `admin` | `admin` |

> Se recomienda crear un usuario propio y desactivar o cambiar la contraseña del administrador inicial desde el módulo **Usuarios**.

## Módulos del sistema

| Módulo | Funciones principales |
|---|---|
| **Dashboard** | Indicadores del taller, últimas órdenes, alertas y agenda. |
| **Órdenes de Trabajo** | Alta/edición/eliminación, servicios e insumos, diagnóstico, historial, cambio de estado. |
| **Clientes** | ABM de clientes con datos de contacto y documento. |
| **Equipos** | ABM de equipos asociados a un cliente. |
| **Insumos** | ABM de repuestos, entradas de stock y consulta de movimientos. |
| **Servicios** | Catálogo de servicios con precio base y tiempo estimado. |
| **Presupuestos** | Editor de presupuestos, detalle, PDF, WhatsApp, Email y cambio de estado. |
| **Pagos** | Registro de pagos (Seña / Pago / Saldo) por método de pago. |
| **Entregas** | Registro de entrega de equipos listos; marca la orden como *Entregado*. |
| **Garantías** | Alta de garantías para órdenes entregadas. |
| **Reportes** | Consultas y exportación CSV. |
| **Calendario** | Listado de órdenes por fecha estimada. |
| **Usuarios** | Alta, edición y activación/desactivación de usuarios. |

## Flujo de trabajo de una orden

Estados disponibles:

```
En diagnostico → Esperando presupuesto → Presupuesto enviado → Aprobado
→ En reparacion → Esperando repuesto → Listo para entregar → Entregado
                                                         (o Cancelado)
```

- Cada cambio de estado queda registrado en el **historial** con usuario, fecha y comentario.
- Al cambiar el estado de un **presupuesto** (Enviado, Aprobado, Rechazado) se actualiza automáticamente el estado de la orden asociada.
- Al **registrar una entrega**, la orden pasa a *Entregado* y se guarda la fecha de finalización.
- Al **eliminar una orden**, se borran sus registros asociados y los insumos consumidos **vuelven al stock**.

## Base de datos

El esquema está definido en [`database/schema.sql`](database/schema.sql) y consta de 15 tablas:

| Área | Tablas |
|---|---|
| Personas y equipos | `clientes`, `equipos`, `usuarios` |
| Órdenes | `ordenes_trabajo`, `historial_estados` |
| Servicios | `servicios`, `servicios_orden` |
| Presupuestos | `presupuestos`, `detalle_presupuesto` |
| Cobros y cierre | `pagos`, `entregas`, `garantias` |
| Inventario | `insumos`, `insumos_orden`, `movimientos_insumos` |

Características:

- **Integridad referencial** activada (`PRAGMA foreign_keys = ON`).
- Restricciones `UNIQUE` (por ejemplo, una entrega y una garantía por orden; un insumo una sola vez por orden).
- **Índices** sobre las columnas de consulta más frecuentes.
- **Detección de esquema antiguo**: si existe una base de una versión anterior, se genera automáticamente una copia de seguridad (`saint_repairs_backup_esquema_anterior.db`) y se crea la base nueva.

## Estructura del proyecto

```
.
├── main.py                 # Punto de entrada (init de BD → login → aplicación)
├── ejecutar.bat            # Acceso rápido para Windows
├── requirements.txt        # Dependencias (reportlab)
├── app/
│   ├── __init__.py
│   ├── application.py      # Ventana principal (clase App, une todos los mixins)
│   ├── common.py           # Imports, colores y constantes compartidas
│   ├── ui_base.py          # Layout, estilos, tablas y utilidades de UI
│   ├── login.py            # Pantalla de acceso
│   ├── dashboard.py        # Panel de resumen
│   ├── orders.py           # Órdenes de trabajo
│   ├── clients.py          # Clientes
│   ├── equipment.py        # Equipos
│   ├── inventory.py        # Insumos y movimientos
│   ├── services.py         # Servicios
│   ├── budgets.py          # Presupuestos, PDF, WhatsApp y Email
│   ├── payments.py         # Pagos
│   ├── deliveries.py       # Entregas
│   ├── guarantees.py       # Garantías
│   ├── reports.py          # Reportes, calendario y exportación CSV
│   └── users.py            # Usuarios
└── database/
    ├── database.py         # Conexión, inicialización, migración y datos semilla
    └── schema.sql          # Esquema de las 15 tablas
```

La interfaz sigue una arquitectura por **mixins**: cada módulo funcional es una clase independiente que `App` combina, lo que facilita mantener y extender el sistema.

## Notas y limitaciones

- Los PDF de presupuestos se guardan en `app/presupuestos_generados/`.
- El envío por **WhatsApp** abre `wa.me` con el mensaje armado; si el teléfono tiene 10 dígitos se antepone el código de país `54` (Argentina).
- El envío por **Email** abre el cliente de correo predeterminado (`mailto:`).
- Los **roles** de usuario se almacenan, pero todavía no restringen el acceso a módulos.
- Las contraseñas se guardan actualmente **en texto plano** (la columna se llama `contrasena_hash`). Para un uso real se recomienda reemplazarlo por un hash con sal (por ejemplo, `hashlib.pbkdf2_hmac` o `bcrypt`).
- La apertura automática del PDF usa `os.startfile` (Windows); en otros sistemas se abre mediante el navegador.