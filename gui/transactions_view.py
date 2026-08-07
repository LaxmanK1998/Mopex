"""
Transactions View for Mopex Desktop Application.
"""
import datetime
from tkinter import filedialog, messagebox
from typing import Optional, Callable
import customtkinter as ctk
from database import DatabaseManager
from models import Transaction, DEFAULT_CATEGORIES, RECUR_INTERVALS
from gui.widgets import TransactionTable


class TransactionDialog(ctk.CTkToplevel):
    """
    Modal Dialog to Add or Edit a Transaction (with recurring support).
    """
    def __init__(self, master, db: DatabaseManager, budget_id: int,
                 tx: Optional[Transaction] = None, on_save: Optional[Callable] = None):
        super().__init__(master)
        self.db = db
        self.budget_id = budget_id
        self.tx = tx
        self.on_save = on_save

        self.title("Edit Transaction" if tx else "Add New Transaction")
        self.geometry("460x620")
        self.resizable(False, False)
        self.grab_set()
        self.after(10, self._center_window)

        self.header_label = ctk.CTkLabel(
            self,
            text="✏️ Edit Transaction" if tx else "➕ Add New Transaction",
            font=("Segoe UI", 18, "bold")
        )
        self.header_label.pack(pady=(18, 12))

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=24, pady=0)

        # 1. Type
        ctk.CTkLabel(self.form_frame, text="Transaction Type:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.type_segmented = ctk.CTkSegmentedButton(
            self.form_frame, values=["Expense", "Income"], command=self._on_type_changed
        )
        self.type_segmented.set("Income" if (tx and tx.type == "income") else "Expense")
        self.type_segmented.pack(fill="x", pady=(0, 10))

        # 2. Title
        ctk.CTkLabel(self.form_frame, text="Narration / Description:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.title_entry = ctk.CTkEntry(self.form_frame, placeholder_text="E.g. Grocery, Salary, Rent", height=36)
        if tx:
            self.title_entry.insert(0, tx.title)
        self.title_entry.pack(fill="x", pady=(0, 10))

        # 3. Amount
        ctk.CTkLabel(self.form_frame, text="Amount:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.amount_entry = ctk.CTkEntry(self.form_frame, placeholder_text="0.00", height=36)
        if tx:
            self.amount_entry.insert(0, str(tx.amount))
        self.amount_entry.pack(fill="x", pady=(0, 10))

        # 4. Category
        ctk.CTkLabel(self.form_frame, text="Category:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.category_dropdown = ctk.CTkOptionMenu(self.form_frame, values=[], height=36)
        self.category_dropdown.pack(fill="x", pady=(0, 10))
        self._update_categories()
        if tx and tx.category:
            self.category_dropdown.set(tx.category)

        # 5. Date
        ctk.CTkLabel(self.form_frame, text="Date (YYYY-MM-DD):", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.date_entry = ctk.CTkEntry(self.form_frame, placeholder_text="YYYY-MM-DD", height=36)
        self.date_entry.insert(0, tx.date if tx else datetime.date.today().isoformat())
        self.date_entry.pack(fill="x", pady=(0, 10))

        # 6. Recurring Transaction
        recur_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        recur_frame.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(recur_frame, text="Recurring:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 12))
        self.recur_switch = ctk.CTkSwitch(recur_frame, text="", width=50, command=self._toggle_recur)
        if tx and tx.is_recurring:
            self.recur_switch.select()
        self.recur_switch.pack(side="left")

        self.recur_interval_dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            values=["daily", "weekly", "monthly"],
            height=32,
            width=120
        )
        if tx and tx.recur_interval:
            self.recur_interval_dropdown.set(tx.recur_interval)
        else:
            self.recur_interval_dropdown.set("monthly")
        self.recur_interval_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.recur_interval_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.recur_interval_frame, text="Repeat every:", font=("Segoe UI", 11)).pack(side="left", padx=(0, 8))
        self.recur_interval_dropdown = ctk.CTkOptionMenu(self.recur_interval_frame, values=["daily", "weekly", "monthly"], height=32)
        if tx and tx.recur_interval:
            self.recur_interval_dropdown.set(tx.recur_interval)
        else:
            self.recur_interval_dropdown.set("monthly")
        self.recur_interval_dropdown.pack(side="left")

        self._toggle_recur()

        # Error label
        self.error_label = ctk.CTkLabel(self.form_frame, text="", text_color="#EF4444", font=("Segoe UI", 11))
        self.error_label.pack(fill="x", pady=(0, 6))

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=24, pady=(0, 18))

        ctk.CTkButton(
            self.btn_frame, text="Cancel", fg_color="transparent", border_width=1,
            text_color=("#475569", "#CBD5E1"), command=self.destroy, height=38, width=100
        ).pack(side="left")

        ctk.CTkButton(
            self.btn_frame, text="💾 Save Entry", fg_color="#3B82F6", hover_color="#2563EB",
            command=self._save_transaction, height=38, width=140, font=("Segoe UI", 12, "bold")
        ).pack(side="right")

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_type_changed(self, value: str):
        self._update_categories()

    def _update_categories(self):
        selected_type = self.type_segmented.get().lower()
        cats = DEFAULT_CATEGORIES.get(selected_type, [])
        self.category_dropdown.configure(values=cats)
        if cats:
            self.category_dropdown.set(cats[0])

    def _toggle_recur(self):
        enabled = self.recur_switch.get()
        state = "normal" if enabled else "disabled"
        self.recur_interval_dropdown.configure(state=state)

    def _save_transaction(self):
        title = self.title_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        tx_type = self.type_segmented.get().lower()
        category = self.category_dropdown.get()
        date_str = self.date_entry.get().strip()
        is_recurring = bool(self.recur_switch.get())
        recur_interval = self.recur_interval_dropdown.get() if is_recurring else ""

        if not title:
            self.error_label.configure(text="Please enter a narration/title.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                self.error_label.configure(text="Amount must be greater than zero.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid amount. Enter a numeric value.")
            return

        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            self.error_label.configure(text="Date must be in YYYY-MM-DD format.")
            return

        if self.tx:
            self.tx.title = title
            self.tx.amount = amount
            self.tx.type = tx_type
            self.tx.category = category
            self.tx.date = date_str
            self.tx.is_recurring = is_recurring
            self.tx.recur_interval = recur_interval
            self.db.update_transaction(self.tx)
        else:
            new_tx = Transaction(
                budget_id=self.budget_id,
                title=title, amount=amount, type=tx_type,
                category=category, date=date_str,
                is_recurring=is_recurring, recur_interval=recur_interval
            )
            self.db.add_transaction(new_tx)

        if self.on_save:
            self.on_save()
        self.destroy()


class TransactionsView(ctk.CTkFrame):
    """
    Transactions View with search, date-range filter, category filter, type filter,
    ledger table, CRUD actions, and CSV import.
    """
    def __init__(self, master, db: DatabaseManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.is_dark = True

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ---- Header ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))

        ctk.CTkLabel(header, text="Transaction Ledger 📑", font=("Segoe UI", 22, "bold"), anchor="w").pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        ctk.CTkButton(actions, text="+ New Entry", font=("Segoe UI", 12, "bold"),
                      fg_color="#10B981", hover_color="#059669", height=36,
                      command=self.open_add_dialog).pack(side="left", padx=3)

        ctk.CTkButton(actions, text="✏️ Edit", font=("Segoe UI", 12),
                      fg_color="#3B82F6", hover_color="#2563EB", height=36, width=80,
                      command=self.open_edit_dialog).pack(side="left", padx=3)

        ctk.CTkButton(actions, text="🗑️ Delete", font=("Segoe UI", 12),
                      fg_color="#EF4444", hover_color="#DC2626", height=36, width=85,
                      command=self.delete_selected).pack(side="left", padx=3)

        ctk.CTkButton(actions, text="📥 Import CSV", font=("Segoe UI", 12),
                      fg_color="#6366F1", hover_color="#4F46E5", height=36,
                      command=self.import_csv).pack(side="left", padx=3)

        # ---- Filter Row 1: Search + Type + Category ----
        filter1 = ctk.CTkFrame(self, fg_color="transparent")
        filter1.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 2))

        self.search_entry = ctk.CTkEntry(filter1, placeholder_text="🔍 Search narration / keyword...", height=34)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self.type_filter = ctk.CTkOptionMenu(filter1, values=["All Types", "Income", "Expense"],
                                              command=lambda v: self.refresh(), width=120, height=34)
        self.type_filter.set("All Types")
        self.type_filter.pack(side="left", padx=3)

        self.category_filter = ctk.CTkOptionMenu(filter1, values=["All Categories"],
                                                   command=lambda v: self.refresh(), width=160, height=34)
        self.category_filter.set("All Categories")
        self.category_filter.pack(side="left", padx=3)

        # ---- Filter Row 2: Date Range ----
        filter2 = ctk.CTkFrame(self, fg_color="transparent")
        filter2.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 4))

        ctk.CTkLabel(filter2, text="From:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 4))
        self.date_from = ctk.CTkEntry(filter2, placeholder_text="YYYY-MM-DD", width=120, height=32)
        self.date_from.pack(side="left", padx=(0, 10))
        self.date_from.bind("<KeyRelease>", lambda e: self.refresh())

        ctk.CTkLabel(filter2, text="To:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 4))
        self.date_to = ctk.CTkEntry(filter2, placeholder_text="YYYY-MM-DD", width=120, height=32)
        self.date_to.pack(side="left", padx=(0, 10))
        self.date_to.bind("<KeyRelease>", lambda e: self.refresh())

        ctk.CTkButton(filter2, text="Clear Filters", fg_color="transparent", border_width=1,
                      text_color=("#475569", "#94A3B8"), height=30, width=100,
                      command=self._clear_filters).pack(side="left", padx=6)

        # ---- Table ----
        self.grid_rowconfigure(3, weight=1)
        self.table = TransactionTable(self)
        self.table.grid(row=3, column=0, sticky="nsew", padx=16, pady=(4, 14))

        self._populate_category_filter()
        self.refresh()

    def set_theme(self, is_dark: bool):
        self.is_dark = is_dark
        self.table.set_theme_colors(is_dark)
        self.refresh()

    def _populate_category_filter(self):
        all_cats = ["All Categories"] + DEFAULT_CATEGORIES["expense"] + DEFAULT_CATEGORIES["income"]
        self.category_filter.configure(values=all_cats)

    def _clear_filters(self):
        self.search_entry.delete(0, "end")
        self.type_filter.set("All Types")
        self.category_filter.set("All Categories")
        self.date_from.delete(0, "end")
        self.date_to.delete(0, "end")
        self.refresh()

    def refresh(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        search = self.search_entry.get().strip()
        tx_type = self.type_filter.get()
        if tx_type == "All Types":
            tx_type = "All"
        cat = self.category_filter.get()
        if cat == "All Categories":
            cat = "All"
        date_from = self.date_from.get().strip()
        date_to = self.date_to.get().strip()

        txs = self.db.get_transactions(
            budget_id=active_budget.id,
            search=search,
            category=cat,
            tx_type=tx_type,
            date_from=date_from,
            date_to=date_to,
        )
        self.table.update_transactions(txs, symbol=active_budget.currency_symbol)

    def open_add_dialog(self):
        active_budget = self.db.get_active_budget()
        if active_budget:
            TransactionDialog(self, self.db, active_budget.id, on_save=self.refresh)

    def open_edit_dialog(self):
        tx_id = self.table.get_selected_id()
        if not tx_id:
            return
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return
        txs = self.db.get_transactions(active_budget.id)
        target_tx = next((t for t in txs if t.id == tx_id), None)
        if target_tx:
            TransactionDialog(self, self.db, active_budget.id, tx=target_tx, on_save=self.refresh)

    def delete_selected(self):
        tx_id = self.table.get_selected_id()
        if not tx_id:
            return
        self.db.delete_transaction(tx_id)
        self.refresh()

    def import_csv(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        file_path = filedialog.askopenfilename(
            title="Import Transactions from CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        count, errors = self.db.import_csv(file_path, active_budget.id)
        self.refresh()

        msg = f"Successfully imported {count} transaction(s)."
        if errors:
            msg += f"\n\nWarnings ({len(errors)}):\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n...and {len(errors) - 10} more."
        messagebox.showinfo("CSV Import Complete", msg)
