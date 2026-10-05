"""Aplicación principal SAINT REPAIRS.

La clase App,,, coordina la ventana principal; cada módulo funcional vive en su
propio mixin para mantener el proyecto escalable y fácil de mantener.
"""

import tkinter as tk
from tkinter import ttk

from .common import *
from .ui_base import UiBaseMixin
from .dashboard import DashboardMixin
from .clients import ClientsMixin
from .equipment import EquipmentMixin
from .orders import OrdersMixin
from .inventory import InventoryMixin
from .services import ServicesMixin
from .budgets import BudgetsMixin
from .payments import PaymentsMixin
from .deliveries import DeliveriesMixin
from .guarantees import GuaranteesMixin
from .users import UsersMixin
from .reports import ReportsMixin


class App(tk.Tk, UiBaseMixin, DashboardMixin, ClientsMixin, EquipmentMixin, OrdersMixin, InventoryMixin, ServicesMixin, BudgetsMixin, PaymentsMixin, DeliveriesMixin, GuaranteesMixin, UsersMixin, ReportsMixin):
    def __init__(self, user_id=1, user_name="Administrador"):
        super().__init__()
        self.current_user_id = user_id
        self.current_user_name = user_name
        self._active_module_window = None
        self.title(APP_TITLE)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        width = min(1500, max(1180, int(sw * 0.94)))
        height = min(900, max(700, int(sh * 0.90)))
        self.geometry(f"{width}x{height}+{max(0,(sw-width)//2)}+{max(0,(sh-height)//2)}")
        self.minsize(1180, 700)
        self.resizable(True, True)
        self.configure(bg=BG)
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure_styles()
        self.create_layout()
        self.show_dashboard()
