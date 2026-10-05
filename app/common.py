"""Dependencias compartidas de la interfaz SAINT REPAIRS."""

import csv
import os
import sqlite3
import tkinter as tk
import urllib.parse
import webbrowser
from datetime import datetime, date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from database.database import get_connection

APP_TITLE = "SAINT REPAIRS | Taller de Reparación de Electrónica"
BG = "#F4F7FB"
SIDEBAR = "#061A33"
BLUE = "#1769E0"
TEXT = "#172033"
MUTED = "#65748B"
GREEN = "#2EAF72"
ORANGE = "#F28C28"
PURPLE = "#7757D8"
RED = "#D94C4C"
WHITE = "#FFFFFF"

ESTADOS = [
    "En diagnostico", "Esperando presupuesto", "Presupuesto enviado",
    "Aprobado", "En reparacion", "Esperando repuesto",
    "Listo para entregar", "Entregado", "Cancelado"
]
PRIORIDADES = ["Normal", "Alta", "Urgente"]
ROLES = ["Administrador", "Tecnico", "Recepcion"]
TIPOS_EQUIPO = ["Celular", "Notebook", "PC", "Tablet", "Consola", "TV", "Audio", "Otro"]
METODOS_PAGO = ["Efectivo", "Transferencia", "Tarjeta", "Mercado Pago"]
ESTADOS_PRESUPUESTO = ["Pendiente", "Enviado", "Aprobado", "Rechazado", "Vencido"]
