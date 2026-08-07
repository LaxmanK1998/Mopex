"""
Budgets & Projects Management View for Mopex.
"""
import customtkinter as ctk
from typing import Callable, Optional
from database import DatabaseManager
from models import Budget, DEFAULT_CURRENCIES


class BudgetDialog(ctk.CTkToplevel):
    """
    Modal dialog to create or edit a budget project profile.
    """
    def __init__(self, master, db: DatabaseManager, budget: Optional[Budget] = None, on_save: Optional[Callable] = None):
        super().__init__(master)
        self.db = db
        self.budget = budget
        self.on_save = on_save

        self.title("Edit Budget Profile" if budget else "Create New Budget Profile")
        self.geometry("450x480")
        self.resizable(False, False)
        self.grab_set()
        self.after(10, self._center_window)

        self.header_label = ctk.CTkLabel(
            self,
            text="✏️ Edit Budget Project" if budget else "🎯 Create New Budget Project",
            font=("Segoe UI", 18, "bold")
        )
        self.header_label.pack(pady=(20, 16))

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=24, pady=0)

        # 1. Budget Title
        self.title_label = ctk.CTkLabel(self.form_frame, text="Budget Title:", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 4))

        self.title_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="E.g. Kitchen Repairs, Summer Trip, Monthly Living",
            height=36
        )
        if budget:
            self.title_entry.insert(0, budget.title)
        self.title_entry.pack(fill="x", pady=(0, 12))

        # 2. User Name
        self.user_label = ctk.CTkLabel(self.form_frame, text="User Name / Profile:", font=("Segoe UI", 12, "bold"))
        self.user_label.pack(anchor="w", pady=(0, 4))

        self.user_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="E.g. Alex, Family",
            height=36
        )
        default_user = budget.user_name if budget else "User"
        self.user_entry.insert(0, default_user)
        self.user_entry.pack(fill="x", pady=(0, 12))

        # 3. Currency Choice
        self.curr_label = ctk.CTkLabel(self.form_frame, text="Currency Code:", font=("Segoe UI", 12, "bold"))
        self.curr_label.pack(anchor="w", pady=(0, 4))

        curr_options = [f"{code} ({symbol})" for code, symbol in DEFAULT_CURRENCIES.items()]
        self.curr_dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            values=curr_options,
            height=36
        )
        if budget:
            self.curr_dropdown.set(f"{budget.currency} ({budget.currency_symbol})")
        else:
            self.curr_dropdown.set("INR (₹)")
        self.curr_dropdown.pack(fill="x", pady=(0, 12))

        # 4. Total Target Budget Limit Amount
        ctk.CTkLabel(self.form_frame, text="Target Budget Limit Amount:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.amount_entry = ctk.CTkEntry(self.form_frame, placeholder_text="0.00", height=36)
        if budget:
            self.amount_entry.insert(0, str(budget.total_budget))
        self.amount_entry.pack(fill="x", pady=(0, 12))

        # 5. Alert Thresholds Row
        alert_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        alert_frame.pack(fill="x", pady=(0, 12))
        alert_frame.grid_columnconfigure((0, 1), weight=1)

        yellow_cell = ctk.CTkFrame(alert_frame, fg_color="transparent")
        yellow_cell.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(yellow_cell, text="⚠️ Yellow Alert (%)", font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w", pady=(0, 3))
        self.yellow_entry = ctk.CTkEntry(yellow_cell, placeholder_text="75", height=34)
        self.yellow_entry.insert(0, str(int(budget.alert_yellow_pct)) if budget else "75")
        self.yellow_entry.pack(fill="x")

        red_cell = ctk.CTkFrame(alert_frame, fg_color="transparent")
        red_cell.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(red_cell, text="🔴 Red Alert (%)", font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w", pady=(0, 3))
        self.red_entry = ctk.CTkEntry(red_cell, placeholder_text="100", height=34)
        self.red_entry.insert(0, str(int(budget.alert_red_pct)) if budget else "100")
        self.red_entry.pack(fill="x")

        # Error label
        self.error_label = ctk.CTkLabel(self.form_frame, text="", text_color="#EF4444", font=("Segoe UI", 11))
        self.error_label.pack(fill="x", pady=(0, 8))

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=24, pady=(0, 20))

        self.cancel_btn = ctk.CTkButton(
            self.btn_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            text_color=("#475569", "#CBD5E1"),
            command=self.destroy,
            height=38,
            width=100
        )
        self.cancel_btn.pack(side="left")

        self.save_btn = ctk.CTkButton(
            self.btn_frame,
            text="Save Profile",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._save_budget,
            height=38,
            width=140
        )
        self.save_btn.pack(side="right")

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _save_budget(self):
        title = self.title_entry.get().strip()
        user_name = self.user_entry.get().strip() or "User"
        curr_str = self.curr_dropdown.get()
        amount_str = self.amount_entry.get().strip()
        yellow_str = self.yellow_entry.get().strip() or "75"
        red_str = self.red_entry.get().strip() or "100"

        if not title:
            self.error_label.configure(text="Please enter a budget title.")
            return

        try:
            amount = float(amount_str)
            if amount < 0:
                self.error_label.configure(text="Budget limit cannot be negative.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid amount. Enter a numeric value.")
            return

        try:
            yellow_pct = float(yellow_str)
            red_pct = float(red_str)
            if not (0 < yellow_pct < red_pct):
                self.error_label.configure(text="Yellow % must be less than Red % and both must be > 0.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid alert percentage. Use numeric values (e.g. 75, 100).")
            return

        code = curr_str.split()[0]
        symbol = DEFAULT_CURRENCIES.get(code, "₹")

        if self.budget:
            self.budget.title = title
            self.budget.user_name = user_name
            self.budget.currency = code
            self.budget.currency_symbol = symbol
            self.budget.total_budget = amount
            self.budget.alert_yellow_pct = yellow_pct
            self.budget.alert_red_pct = red_pct
            self.db.update_budget(self.budget)
        else:
            new_budget = Budget(
                title=title,
                user_name=user_name,
                currency=code,
                currency_symbol=symbol,
                total_budget=amount,
                alert_yellow_pct=yellow_pct,
                alert_red_pct=red_pct,
                is_active=True
            )
            self.db.create_budget(new_budget)

        if self.on_save:
            self.on_save()
        self.destroy()


class BudgetsView(ctk.CTkScrollableFrame):
    """
    Budgets View displaying all budget projects with quick switch, edit, and deletion capabilities.
    """
    def __init__(self, master, db: DatabaseManager, on_budget_changed: Optional[Callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.on_budget_changed = on_budget_changed

        self.grid_columnconfigure(0, weight=1)

        # Header Title
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(12, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Budget Projects & Profiles 🎯",
            font=("Segoe UI", 22, "bold"),
            anchor="w"
        )
        self.title_label.pack(side="left")

        self.create_btn = ctk.CTkButton(
            self.header_frame,
            text="+ Create New Budget",
            font=("Segoe UI", 12, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=36,
            command=self.open_create_dialog
        )
        self.create_btn.pack(side="right")

        # Container for Budget Cards
        self.cards_container = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_container.pack(fill="x", padx=16, pady=8)

        self.refresh()

    def refresh(self):
        for child in self.cards_container.winfo_children():
            child.destroy()

        budgets = self.db.get_all_budgets()
        for budget in budgets:
            self._render_budget_card(budget)

    def _render_budget_card(self, budget: Budget):
        card = ctk.CTkFrame(
            self.cards_container,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=2 if budget.is_active else 1,
            border_color="#3B82F6" if budget.is_active else ("#E2E8F0", "#334155")
        )
        card.pack(fill="x", pady=8, padx=4)

        summary = self.db.get_budget_summary(budget.id)
        total_exp = summary.get("total_expense", 0.0)
        total_inc = summary.get("total_income", 0.0)
        symbol = budget.currency_symbol

        # Left Info section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=16, pady=14)

        title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_frame.pack(fill="x", anchor="w")

        title_lbl = ctk.CTkLabel(
            title_frame,
            text=f"{budget.title}",
            font=("Segoe UI", 16, "bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        title_lbl.pack(side="left")

        if budget.is_active:
            active_badge = ctk.CTkLabel(
                title_frame,
                text="ACTIVE",
                font=("Segoe UI", 10, "bold"),
                text_color="white",
                fg_color="#3B82F6",
                corner_radius=6,
                padx=8,
                pady=1
            )
            active_badge.pack(side="left", padx=10)

        subtitle_lbl = ctk.CTkLabel(
            info_frame,
            text=f"Owner: {budget.user_name}  |  Created: {budget.created_at}  |  Currency: {budget.currency} ({symbol})",
            font=("Segoe UI", 11),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        subtitle_lbl.pack(fill="x", pady=(4, 6))

        stats_lbl = ctk.CTkLabel(
            info_frame,
            text=f"Target Limit: {symbol}{budget.total_budget:,.2f}   •   Income: {symbol}{total_inc:,.2f}   •   Spent: {symbol}{total_exp:,.2f}",
            font=("Segoe UI", 12, "bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        stats_lbl.pack(fill="x")

        # Right Action Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=16, pady=14)

        if not budget.is_active:
            switch_btn = ctk.CTkButton(
                btn_frame,
                text="Set Active",
                font=("Segoe UI", 11, "bold"),
                fg_color="#10B981",
                hover_color="#059669",
                width=90,
                height=32,
                command=lambda b_id=budget.id: self._set_active(b_id)
            )
            switch_btn.pack(side="left", padx=4)

        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Edit",
            font=("Segoe UI", 11),
            fg_color="transparent",
            border_width=1,
            text_color=("#334155", "#CBD5E1"),
            width=70,
            height=32,
            command=lambda b=budget: self.open_edit_dialog(b)
        )
        edit_btn.pack(side="left", padx=4)

        del_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            font=("Segoe UI", 12),
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=40,
            height=32,
            command=lambda b_id=budget.id: self._delete_budget(b_id)
        )
        del_btn.pack(side="left", padx=4)

    def _set_active(self, budget_id: int):
        self.db.set_active_budget(budget_id)
        self.refresh()
        if self.on_budget_changed:
            self.on_budget_changed()

    def open_create_dialog(self):
        BudgetDialog(self, self.db, on_save=self._on_saved)

    def open_edit_dialog(self, budget: Budget):
        BudgetDialog(self, self.db, budget=budget, on_save=self._on_saved)

    def _on_saved(self):
        self.refresh()
        if self.on_budget_changed:
            self.on_budget_changed()

    def _delete_budget(self, budget_id: int):
        all_b = self.db.get_all_budgets()
        if len(all_b) <= 1:
            return  # Prevent deleting the last budget profile
        self.db.delete_budget(budget_id)
        self.refresh()
        if self.on_budget_changed:
            self.on_budget_changed()
