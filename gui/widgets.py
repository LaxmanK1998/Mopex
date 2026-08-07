"""
Custom UI widgets for Mopex Desktop Application.
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class StatCard(ctk.CTkFrame):
    """
    A modern metric summary card with title, large formatted value, badge, and color accent.
    """
    def __init__(
        self,
        master,
        title: str,
        value: str = "$0.00",
        subtitle: str = "",
        accent_color: str = "#3B82F6",
        icon_text: str = "📊",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.accent_color = accent_color

        # Left color bar
        self.accent_bar = ctk.CTkFrame(
            self,
            width=5,
            fg_color=accent_color,
            corner_radius=2
        )
        self.accent_bar.pack(side="left", fill="y", padx=(6, 12), pady=12)

        # Content container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=10)

        # Header layout (Icon + Title)
        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", anchor="w")

        self.icon_label = ctk.CTkLabel(
            self.header_frame,
            text=icon_text,
            font=("Segoe UI Emoji", 14),
            width=20
        )
        self.icon_label.pack(side="left", padx=(0, 6))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title.upper(),
            font=("Segoe UI", 11, "bold"),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        self.title_label.pack(side="left")

        # Value label
        self.value_label = ctk.CTkLabel(
            self.content_frame,
            text=value,
            font=("Segoe UI", 20, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        self.value_label.pack(fill="x", pady=(4, 2))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text=subtitle,
            font=("Segoe UI", 11),
            text_color=("#475569", "#CBD5E1"),
            anchor="w"
        )
        self.subtitle_label.pack(fill="x")

    def update_value(self, value: str, subtitle: str = ""):
        self.value_label.configure(text=value)
        if subtitle:
            self.subtitle_label.configure(text=subtitle)


class BudgetProgressBarCard(ctk.CTkFrame):
    """
    Budget Gauge & Limit tracker card.
    """
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(14, 6))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🎯 Budget Estimate & Limit Progress",
            font=("Segoe UI", 14, "bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.title_label.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            self.header_frame,
            text="On Track",
            font=("Segoe UI", 11, "bold"),
            text_color="white",
            fg_color="#10B981",
            corner_radius=8,
            padx=10,
            pady=2
        )
        self.status_badge.pack(side="right")

        # Details summary
        self.details_label = ctk.CTkLabel(
            self,
            text="Budget: $0.00 | Total Spent: $0.00 (0%)",
            font=("Segoe UI", 12),
            text_color=("#475569", "#94A3B8"),
            anchor="w"
        )
        self.details_label.pack(fill="x", padx=16, pady=(0, 8))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=14,
            corner_radius=7,
            progress_color="#10B981"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 10))

        # Helper text
        self.helper_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 11, "italic"),
            text_color=("#64748B", "#CBD5E1"),
            anchor="w"
        )
        self.helper_label.pack(fill="x", padx=16, pady=(0, 12))

    def update_budget_progress(self, total_budget: float, total_expense: float, net_result: float,
                               symbol: str = "₹", yellow_pct: float = 75.0, red_pct: float = 100.0):
        if total_budget <= 0:
            usage_pct = 0.0
        else:
            usage_pct = (total_expense / total_budget)

        yellow_threshold = yellow_pct / 100.0
        red_threshold = red_pct / 100.0

        pct_display = min(usage_pct * 100, 999.0)
        self.details_label.configure(
            text=f"Target Budget: {symbol}{total_budget:,.2f}  |  Total Expense: {symbol}{total_expense:,.2f} ({pct_display:.1f}%)"
        )
        self.progress_bar.set(min(max(usage_pct, 0.0), 1.0))

        if usage_pct < yellow_threshold:
            self.progress_bar.configure(progress_color="#10B981")
            self.status_badge.configure(text="Within Budget", fg_color="#10B981")
            saved = total_budget - total_expense
            self.helper_label.configure(
                text=f"Good news! You have spent {symbol}{saved:,.2f} less than your estimated budget."
            )
        elif usage_pct < red_threshold:
            self.progress_bar.configure(progress_color="#F59E0B")
            self.status_badge.configure(text="Near Limit", fg_color="#F59E0B")
            remaining = total_budget - total_expense
            self.helper_label.configure(
                text=f"Caution: Approaching your budget limit. Remaining: {symbol}{remaining:,.2f}"
            )
        else:
            self.progress_bar.configure(progress_color="#EF4444")
            self.status_badge.configure(text="Over Budget", fg_color="#EF4444")
            exceeded = total_expense - total_budget
            self.helper_label.configure(
                text=f"Warning! You have exceeded your budget by {symbol}{exceeded:,.2f}."
            )


class ChartWidget(ctk.CTkFrame):
    """
    Embedded matplotlib chart widget (Pie Chart or Bar Chart) for visual breakdown.
    """
    def __init__(self, master, title: str = "Expense Breakdown", **kwargs):
        super().__init__(
            master,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 13, "bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        self.title_label.pack(fill="x", padx=16, pady=(12, 6))

        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.canvas_widget = None

    def render_pie_chart(self, category_data: Dict[str, float], is_dark: bool = True):
        self._clear_chart()

        if not MATPLOTLIB_AVAILABLE or not category_data:
            self._render_empty_placeholder("No expense categories to display")
            return

        bg_color = "#1E293B" if is_dark else "#FFFFFF"
        text_color = "#F8FAFC" if is_dark else "#0F172A"

        colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6", "#6366F1", "#F97316"]

        fig = Figure(figsize=(4, 3.2), dpi=100, facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)

        labels = list(category_data.keys())
        sizes = list(category_data.values())

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors[:len(labels)],
            textprops={"color": text_color, "fontsize": 9},
            wedgeprops={"edgecolor": bg_color, "linewidth": 1.5}
        )

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(8)
            autotext.set_weight("bold")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def render_bar_chart(self, monthly_data: Dict[str, Dict[str, float]], is_dark: bool = True):
        self._clear_chart()

        if not MATPLOTLIB_AVAILABLE or not monthly_data:
            self._render_empty_placeholder("No monthly trend data available")
            return

        bg_color = "#1E293B" if is_dark else "#FFFFFF"
        text_color = "#F8FAFC" if is_dark else "#0F172A"

        fig = Figure(figsize=(4.5, 3.2), dpi=100, facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)

        months = list(sorted(monthly_data.keys()))
        incomes = [monthly_data[m]["income"] for m in months]
        expenses = [monthly_data[m]["expense"] for m in months]

        import numpy as np
        x = np.arange(len(months))
        width = 0.35

        rects1 = ax.bar(x - width/2, incomes, width, label="Income", color="#10B981")
        rects2 = ax.bar(x + width/2, expenses, width, label="Expense", color="#EF4444")

        ax.set_xticks(x)
        ax.set_xticklabels(months, color=text_color, fontsize=8)
        ax.tick_params(colors=text_color, labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(text_color)
        ax.spines['bottom'].set_color(text_color)

        ax.legend(facecolor=bg_color, edgecolor="none", labelcolor=text_color, fontsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def _clear_chart(self):
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None
        for child in self.chart_container.winfo_children():
            child.destroy()

    def _render_empty_placeholder(self, text: str):
        lbl = ctk.CTkLabel(
            self.chart_container,
            text=f"📉 {text}",
            font=("Segoe UI", 12),
            text_color=("#94A3B8", "#64748B")
        )
        lbl.pack(expand=True, pady=40)


class TransactionTable(ctk.CTkFrame):
    """
    Styled Transaction Ledger Table with custom columns and scrollbars.
    """
    def __init__(self, master, on_select_callback: Optional[Callable] = None, **kwargs):
        super().__init__(
            master,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.on_select_callback = on_select_callback

        # Container setup
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Style configuration for ttk.Treeview
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Treeview Widget
        columns = ("id", "date", "title", "category", "type", "amount")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10
        )

        self._configure_styles()

        # Headings setup
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date 📅")
        self.tree.heading("title", text="Narration / Title 📝")
        self.tree.heading("category", text="Category 🏷️")
        self.tree.heading("type", text="Type 🔀")
        self.tree.heading("amount", text="Amount 💰")

        # Columns setup
        self.tree.column("id", width=40, anchor="center", stretch=False)
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("title", width=220, anchor="w")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("amount", width=110, anchor="e")

        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(2, 10), pady=10)

        # Tags for alternate coloring
        self.tree.tag_configure("evenrow", background="#1E293B", foreground="#F8FAFC")
        self.tree.tag_configure("oddrow", background="#0F172A", foreground="#F8FAFC")
        self.tree.tag_configure("income_txt", foreground="#10B981")
        self.tree.tag_configure("expense_txt", foreground="#F87171")

        if self.on_select_callback:
            self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def set_theme_colors(self, is_dark: bool = True):
        bg = "#1E293B" if is_dark else "#FFFFFF"
        fg = "#F8FAFC" if is_dark else "#0F172A"
        header_bg = "#0F172A" if is_dark else "#F1F5F9"
        header_fg = "#94A3B8" if is_dark else "#475569"
        odd_bg = "#0F172A" if is_dark else "#F8FAFC"
        select_bg = "#3B82F6"

        self.style.configure(
            "Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=bg,
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading",
            background=header_bg,
            foreground=header_fg,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", select_bg)], foreground=[("selected", "white")])

        self.tree.tag_configure("evenrow", background=bg, foreground=fg)
        self.tree.tag_configure("oddrow", background=odd_bg, foreground=fg)

    def _configure_styles(self):
        self.set_theme_colors(is_dark=True)

    def update_transactions(self, transactions, currency_symbol: str = "$", symbol: Optional[str] = None):
        if symbol is not None:
            currency_symbol = symbol
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, tx in enumerate(transactions):
            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            type_str = "Income 🟢" if tx.type == "income" else "Expense 🔴"
            amt_str = f"{'+' if tx.type == 'income' else '-'}{currency_symbol}{tx.amount:,.2f}"

            self.tree.insert(
                "",
                "end",
                iid=str(tx.id),
                values=(
                    tx.id,
                    tx.date,
                    tx.title,
                    tx.category,
                    type_str,
                    amt_str
                ),
                tags=(row_tag,)
            )

    def get_selected_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if selected:
            try:
                return int(selected[0])
            except ValueError:
                return None
        return None

    def _on_select(self, event):
        if self.on_select_callback:
            selected_id = self.get_selected_id()
            if selected_id:
                self.on_select_callback(selected_id)
