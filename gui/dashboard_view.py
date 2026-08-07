"""
Dashboard View for Mopex Desktop Application.
"""
import customtkinter as ctk
from typing import Callable, Optional
from database import DatabaseManager
from gui.widgets import StatCard, BudgetProgressBarCard, ChartWidget, TransactionTable


class SpendingInsightsCard(ctk.CTkFrame):
    """Card showing daily / weekly / monthly average spend & transaction count."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )

        title_lbl = ctk.CTkLabel(
            self, text="📈 Spending Insights", font=("Segoe UI", 14, "bold"),
            text_color=("#0F172A", "#F8FAFC"), anchor="w"
        )
        title_lbl.pack(fill="x", padx=16, pady=(12, 6))

        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="x", padx=12, pady=(0, 12))
        self.grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="insights")

        self._cells = {}
        for col, (label, key) in enumerate([
            ("Daily Avg", "daily"),
            ("Weekly Avg", "weekly"),
            ("Monthly Avg", "monthly"),
            ("Transactions", "count"),
        ]):
            cell = ctk.CTkFrame(
                self.grid_frame,
                fg_color=("white", "#0F172A"),
                corner_radius=8,
                border_width=1,
                border_color=("#E2E8F0", "#1E293B")
            )
            cell.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(cell, text=label, font=("Segoe UI", 10, "bold"),
                         text_color=("#64748B", "#94A3B8")).pack(pady=(8, 2))
            val_lbl = ctk.CTkLabel(cell, text="—", font=("Segoe UI", 15, "bold"),
                                   text_color=("#0F172A", "#F8FAFC"))
            val_lbl.pack(pady=(0, 8))
            self._cells[key] = val_lbl

    def update_insights(self, daily: float, weekly: float, monthly: float, count: int, symbol: str = "₹"):
        self._cells["daily"].configure(text=f"{symbol}{daily:,.0f}")
        self._cells["weekly"].configure(text=f"{symbol}{weekly:,.0f}")
        self._cells["monthly"].configure(text=f"{symbol}{monthly:,.0f}")
        self._cells["count"].configure(text=str(count))


class DashboardView(ctk.CTkScrollableFrame):
    """
    Overview Dashboard displaying summary stat cards, spending insights,
    budget gauge, charts, and recent transactions.
    """
    def __init__(self, master, db: DatabaseManager, on_navigate: Optional[Callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db
        self.on_navigate = on_navigate
        self.is_dark = True

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            header_frame, text="Dashboard Overview 📊",
            font=("Segoe UI", 22, "bold"), anchor="w"
        ).pack(side="left")

        self.add_tx_btn = ctk.CTkButton(
            header_frame, text="+ Add Transaction", font=("Segoe UI", 12, "bold"),
            fg_color="#3B82F6", hover_color="#2563EB", height=36, corner_radius=8,
            command=self._on_add_transaction_clicked
        )
        self.add_tx_btn.pack(side="right")

        # 1. Metric Stat Cards Row (4 cards)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=16, pady=8)
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_cards")

        self.card_budget = StatCard(self.cards_frame, title="Budget Limit", value="₹0",
                                    subtitle="Target Budget", accent_color="#6366F1", icon_text="🎯")
        self.card_budget.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        self.card_income = StatCard(self.cards_frame, title="Total Income", value="₹0",
                                    subtitle="Total Inflows", accent_color="#10B981", icon_text="💵")
        self.card_income.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        self.card_expense = StatCard(self.cards_frame, title="Total Expense", value="₹0",
                                     subtitle="Total Outflows", accent_color="#EF4444", icon_text="💸")
        self.card_expense.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")

        self.card_net = StatCard(self.cards_frame, title="Net Balance", value="₹0",
                                 subtitle="Profit / Savings", accent_color="#F59E0B", icon_text="⚖️")
        self.card_net.grid(row=0, column=3, padx=6, pady=6, sticky="nsew")

        # 2. Budget Progress Gauge
        self.budget_progress_card = BudgetProgressBarCard(self)
        self.budget_progress_card.pack(fill="x", padx=22, pady=10)

        # 3. Spending Insights Card
        self.insights_card = SpendingInsightsCard(self)
        self.insights_card.pack(fill="x", padx=22, pady=(0, 10))

        # 4. Charts (Pie + Bar side by side)
        self.charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_frame.pack(fill="x", padx=16, pady=10)
        self.charts_frame.grid_columnconfigure((0, 1), weight=1, uniform="charts")

        self.pie_chart_widget = ChartWidget(self.charts_frame, title="Expense Distribution by Category")
        self.pie_chart_widget.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        self.bar_chart_widget = ChartWidget(self.charts_frame, title="Monthly Income vs Expense Trends")
        self.bar_chart_widget.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        # 5. Recent Transactions
        recent_frame = ctk.CTkFrame(self, fg_color="transparent")
        recent_frame.pack(fill="x", padx=22, pady=(12, 20))

        recent_header = ctk.CTkFrame(recent_frame, fg_color="transparent")
        recent_header.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(recent_header, text="Recent Transactions 🕒",
                     font=("Segoe UI", 14, "bold"), anchor="w").pack(side="left")

        ctk.CTkButton(
            recent_header, text="View Ledger →", font=("Segoe UI", 11),
            fg_color="transparent", text_color="#3B82F6",
            hover_color=("#E2E8F0", "#334155"), width=90,
            command=self._on_view_all_clicked
        ).pack(side="right")

        self.recent_table = TransactionTable(recent_frame)
        self.recent_table.pack(fill="x", expand=True)

        self.refresh()

    def set_theme(self, is_dark: bool):
        self.is_dark = is_dark
        self.recent_table.set_theme_colors(is_dark)
        self.refresh()

    def refresh(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        summary = self.db.get_budget_summary(active_budget.id)
        symbol = active_budget.currency_symbol

        self.card_budget.update_value(
            f"{symbol}{active_budget.total_budget:,.2f}", f"{active_budget.currency} Target"
        )
        self.card_income.update_value(
            f"{symbol}{summary.get('total_income', 0):,.2f}", "Inflows"
        )
        self.card_expense.update_value(
            f"{symbol}{summary.get('total_expense', 0):,.2f}", "Outflows"
        )
        net_res = summary.get('net_result', 0)
        self.card_net.update_value(
            f"{symbol}{net_res:,.2f}",
            "Profit / Savings" if net_res >= 0 else "Net Deficit"
        )

        # Budget gauge — use custom thresholds from budget profile
        self.budget_progress_card.update_budget_progress(
            total_budget=active_budget.total_budget,
            total_expense=summary.get('total_expense', 0),
            net_result=net_res,
            symbol=symbol,
            yellow_pct=active_budget.alert_yellow_pct,
            red_pct=active_budget.alert_red_pct,
        )

        # Spending Insights
        self.insights_card.update_insights(
            daily=summary.get("daily_avg_expense", 0),
            weekly=summary.get("weekly_avg_expense", 0),
            monthly=summary.get("monthly_avg_expense", 0),
            count=summary.get("transaction_count", 0),
            symbol=symbol,
        )

        # Charts
        self.pie_chart_widget.render_pie_chart(summary.get("expense_by_category", {}), is_dark=self.is_dark)
        self.bar_chart_widget.render_bar_chart(summary.get("monthly_data", {}), is_dark=self.is_dark)

        # Recent 5 transactions
        txs = self.db.get_transactions(active_budget.id)
        self.recent_table.update_transactions(txs[:5], symbol=symbol)

    def _on_add_transaction_clicked(self):
        if self.on_navigate:
            self.on_navigate("transactions", action="add")

    def _on_view_all_clicked(self):
        if self.on_navigate:
            self.on_navigate("transactions")
