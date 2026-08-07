"""
Main GUI Window Application for Mopex.
"""
import customtkinter as ctk
from database import DatabaseManager
from gui.dashboard_view import DashboardView
from gui.transactions_view import TransactionsView
from gui.budgets_view import BudgetsView
from gui.reports_view import ReportsView


# Set default appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MopexApp(ctk.CTk):
    """
    Main Application Window for Mopex PC Expense Manager.
    """
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.current_theme = "Dark"

        # Window Config
        self.title("Mopex - Desktop Expense Manager")
        self.geometry("1100x720")
        self.minsize(960, 600)

        # Configure Grid Layout (Sidebar left, Content right)
        self.grid_columnconfigure(0, weight=0)  # Sidebar width fixed
        self.grid_columnconfigure(1, weight=1)  # Main content expands
        self.grid_rowconfigure(0, weight=1)

        # ---------------- 1. Sidebar Navigation Drawer ----------------
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=("#F1F5F9", "#0F172A")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # Bottom spacer

        # Brand / Logo Header
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(24, 16), sticky="w")

        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="💎 MOPEX",
            font=("Segoe UI", 22, "bold"),
            text_color="#3B82F6"
        )
        self.logo_label.pack(side="left")

        self.tagline_label = ctk.CTkLabel(
            self.sidebar,
            text="Privacy-Friendly Expense Manager",
            font=("Segoe UI", 10),
            text_color=("#64748B", "#64748B")
        )
        self.tagline_label.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        # Nav Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("transactions", "📑 Transactions"),
            ("budgets", "🎯 Budget Profiles"),
            ("reports", "📄 Reports & Export"),
        ]

        for idx, (key, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=("Segoe UI", 13, "bold"),
                anchor="w",
                fg_color="transparent",
                text_color=("#334155", "#94A3B8"),
                hover_color=("#E2E8F0", "#1E293B"),
                height=40,
                corner_radius=8,
                command=lambda k=key: self.navigate_to(k)
            )
            btn.grid(row=idx, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        # Spacer row 6 expands automatically

        # Active Budget Box
        self.budget_box = ctk.CTkFrame(
            self.sidebar,
            fg_color=("white", "#1E293B"),
            corner_radius=10,
            border_width=1,
            border_color=("#CBD5E1", "#334155")
        )
        self.budget_box.grid(row=7, column=0, padx=14, pady=10, sticky="ew")

        self.budget_box_lbl = ctk.CTkLabel(
            self.budget_box,
            text="Active Budget:",
            font=("Segoe UI", 10, "bold"),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        self.budget_box_lbl.pack(fill="x", padx=10, pady=(8, 2))

        self.active_budget_val = ctk.CTkLabel(
            self.budget_box,
            text="Default Budget",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        self.active_budget_val.pack(fill="x", padx=10, pady=(0, 8))

        # Appearance Theme Toggle
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Dark Mode 🌙",
            font=("Segoe UI", 11),
            command=self._toggle_theme
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=8, column=0, padx=20, pady=(10, 20), sticky="w")

        # ---------------- 2. Main View Container ----------------
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Initialize Views
        self.views = {
            "dashboard": DashboardView(self.content_container, db=self.db, on_navigate=self._on_dashboard_navigate),
            "transactions": TransactionsView(self.content_container, db=self.db),
            "budgets": BudgetsView(self.content_container, db=self.db, on_budget_changed=self._on_budget_changed),
            "reports": ReportsView(self.content_container, db=self.db),
        }

        self.current_view_key = "dashboard"
        self.navigate_to("dashboard")
        self._update_active_budget_label()

    def navigate_to(self, view_key: str):
        self.current_view_key = view_key

        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(
                    fg_color="#3B82F6",
                    text_color="white",
                    hover_color="#2563EB"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("#334155", "#94A3B8"),
                    hover_color=("#E2E8F0", "#1E293B")
                )

        for view in self.views.values():
            view.grid_forget()

        target_view = self.views[view_key]
        target_view.grid(row=0, column=0, sticky="nsew")
        if hasattr(target_view, "refresh"):
            target_view.refresh()

    def _on_dashboard_navigate(self, view_key: str, action: str = ""):
        self.navigate_to(view_key)
        if view_key == "transactions" and action == "add":
            self.views["transactions"].open_add_dialog()

    def _on_budget_changed(self):
        self._update_active_budget_label()
        for view in self.views.values():
            if hasattr(view, "refresh"):
                view.refresh()

    def _update_active_budget_label(self):
        active = self.db.get_active_budget()
        if active:
            self.active_budget_val.configure(text=f"{active.title} ({active.currency_symbol})")

    def _toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
            self.current_theme = "Dark"
            is_dark = True
        else:
            ctk.set_appearance_mode("Light")
            self.current_theme = "Light"
            is_dark = False

        for view in self.views.values():
            if hasattr(view, "set_theme"):
                view.set_theme(is_dark)
            elif hasattr(view, "refresh"):
                view.refresh()
