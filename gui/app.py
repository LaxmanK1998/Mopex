"""
Main GUI Window Application for Mopex.
"""
import customtkinter as ctk
from database import DatabaseManager
from gui.dashboard_view import DashboardView
from gui.transactions_view import TransactionsView
from gui.budgets_view import BudgetsView
from gui.reports_view import ReportsView
from gui.goals_view import GoalsView
from gui.journal_view import JournalView


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
        self.geometry("1150x760")
        self.minsize(980, 620)

        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ───────────────── Sidebar ─────────────────
        self.sidebar = ctk.CTkFrame(
            self, width=230, corner_radius=0,
            fg_color=("#F1F5F9", "#0F172A")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)  # spacer row

        # Brand header
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")
        ctk.CTkLabel(logo_frame, text="💎 MOPEX", font=("Segoe UI", 22, "bold"),
                     text_color="#3B82F6").pack(side="left")

        ctk.CTkLabel(self.sidebar, text="Privacy-Friendly Expense Manager",
                     font=("Segoe UI", 10), text_color=("#64748B", "#64748B")
                     ).grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        # Navigation items: (key, label)
        nav_items = [
            ("dashboard",    "📊  Dashboard"),
            ("transactions", "📑  Transactions"),
            ("budgets",      "🎯  Budget Profiles"),
            ("goals",        "🌟  Savings Goals"),
            ("journal",      "📔  Journal"),
            ("reports",      "📄  Reports & Export"),
        ]

        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        for idx, (key, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar, text=label, font=("Segoe UI", 13, "bold"),
                anchor="w", fg_color="transparent",
                text_color=("#334155", "#94A3B8"),
                hover_color=("#E2E8F0", "#1E293B"),
                height=42, corner_radius=8,
                command=lambda k=key: self.navigate_to(k)
            )
            btn.grid(row=idx, column=0, padx=12, pady=3, sticky="ew")
            self.nav_buttons[key] = btn

        # Active Budget Box (row 9 after spacer 8)
        self.budget_box = ctk.CTkFrame(
            self.sidebar, fg_color=("white", "#1E293B"),
            corner_radius=10, border_width=1,
            border_color=("#CBD5E1", "#334155")
        )
        self.budget_box.grid(row=9, column=0, padx=14, pady=6, sticky="ew")

        ctk.CTkLabel(self.budget_box, text="Active Budget:", font=("Segoe UI", 10, "bold"),
                     text_color=("#64748B", "#94A3B8"), anchor="w"
                     ).pack(fill="x", padx=10, pady=(8, 2))

        self.active_budget_val = ctk.CTkLabel(
            self.budget_box, text="—", font=("Segoe UI", 12, "bold"), anchor="w"
        )
        self.active_budget_val.pack(fill="x", padx=10, pady=(0, 8))

        # Theme toggle
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar, text="Dark Mode 🌙", font=("Segoe UI", 11),
            command=self._toggle_theme
        )
        self.theme_switch.select()
        self.theme_switch.grid(row=10, column=0, padx=20, pady=(8, 22), sticky="w")

        # ───────────────── Content Container ─────────────────
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Instantiate all views
        self.views: dict[str, ctk.CTkBaseClass] = {
            "dashboard":    DashboardView(self.content_container, db=self.db, on_navigate=self._on_dashboard_navigate),
            "transactions": TransactionsView(self.content_container, db=self.db),
            "budgets":      BudgetsView(self.content_container, db=self.db, on_budget_changed=self._on_budget_changed),
            "goals":        GoalsView(self.content_container, db=self.db),
            "journal":      JournalView(self.content_container, db=self.db),
            "reports":      ReportsView(self.content_container, db=self.db),
        }

        self.navigate_to("dashboard")
        self._update_active_budget_label()

        # Auto-generate any due recurring transactions on launch
        try:
            active = self.db.get_active_budget()
            if active:
                generated = self.db.generate_recurring_due(active.id)
                if generated:
                    print(f"[Mopex] Auto-generated {generated} recurring transaction(s).")
        except Exception as e:
            print(f"[Mopex] Recurring generation error: {e}")

    def navigate_to(self, view_key: str):
        self.current_view_key = view_key

        # Update nav button styles
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(fg_color="#3B82F6", text_color="white", hover_color="#2563EB")
            else:
                btn.configure(fg_color="transparent", text_color=("#334155", "#94A3B8"),
                              hover_color=("#E2E8F0", "#1E293B"))

        # Swap visible view
        for view in self.views.values():
            view.grid_forget()

        target = self.views[view_key]
        target.grid(row=0, column=0, sticky="nsew")
        if hasattr(target, "refresh"):
            target.refresh()

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
            self.active_budget_val.configure(
                text=f"{active.title[:22]}\n{active.currency_symbol} {active.currency}"
            )

    def _toggle_theme(self):
        is_dark = self.theme_switch.get() == 1
        ctk.set_appearance_mode("Dark" if is_dark else "Light")
        self.current_theme = "Dark" if is_dark else "Light"
        for view in self.views.values():
            if hasattr(view, "set_theme"):
                view.set_theme(is_dark)
            elif hasattr(view, "refresh"):
                view.refresh()
