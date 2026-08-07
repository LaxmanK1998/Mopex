"""
Reports & Analytical Summary View for Mopex.
"""
import os
import json
import csv
import tempfile
import webbrowser
from tkinter import filedialog, messagebox
import customtkinter as ctk
from database import DatabaseManager


class ReportsView(ctk.CTkScrollableFrame):
    """
    Reports View featuring financial summary cards, breakdown statement, CSV/JSON export tools, and Print functionality.
    """
    def __init__(self, master, db: DatabaseManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db

        self.grid_columnconfigure(0, weight=1)

        # Header Title
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(12, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Financial Reports & Export 📄",
            font=("Segoe UI", 22, "bold"),
            anchor="w"
        )
        self.title_label.pack(side="left")

        # Action / Export Buttons
        self.export_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.export_frame.pack(side="right")

        self.print_btn = ctk.CTkButton(
            self.export_frame,
            text="🖨️ Print Report",
            font=("Segoe UI", 12, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=36,
            command=self.print_report
        )
        self.print_btn.pack(side="left", padx=4)

        self.export_csv_btn = ctk.CTkButton(
            self.export_frame,
            text="📥 Export CSV",
            font=("Segoe UI", 12, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            command=self.export_csv
        )
        self.export_csv_btn.pack(side="left", padx=4)

        self.export_json_btn = ctk.CTkButton(
            self.export_frame,
            text="📥 Export JSON",
            font=("Segoe UI", 12, "bold"),
            fg_color="#6366F1",
            hover_color="#4F46E5",
            height=36,
            command=self.export_json
        )
        self.export_json_btn.pack(side="left", padx=4)

        # Content Summary Container
        self.summary_box = ctk.CTkTextbox(
            self,
            font=("Consolas", 12),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            wrap="none",
            height=450
        )
        self.summary_box.pack(fill="both", expand=True, padx=16, pady=10)

        self.refresh()

    def refresh(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        summary = self.db.get_budget_summary(active_budget.id)
        txs = self.db.get_transactions(active_budget.id)
        symbol = active_budget.currency_symbol

        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append(f"  MOPEX FINANCIAL STATEMENT & BUDGET REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"Budget Title   : {active_budget.title}")
        report_lines.append(f"User / Profile : {active_budget.user_name}")
        report_lines.append(f"Currency       : {active_budget.currency} ({symbol})")
        report_lines.append(f"Target Budget  : {symbol}{active_budget.total_budget:,.2f}")
        report_lines.append("-" * 70)

        tot_inc = summary.get("total_income", 0.0)
        tot_exp = summary.get("total_expense", 0.0)
        net_res = summary.get("net_result", 0.0)

        report_lines.append(f"Total Income   : {symbol}{tot_inc:,.2f}")
        report_lines.append(f"Total Expense  : {symbol}{tot_exp:,.2f}")
        report_lines.append(f"Net Result     : {symbol}{net_res:,.2f}  ({'PROFIT / NET SAVINGS' if net_res >= 0 else 'DEFICIT / LOSS'})")
        report_lines.append("-" * 70)

        diff = active_budget.total_budget - tot_exp
        if diff > 0:
            report_lines.append(f"Budget Diff    : Saved {symbol}{diff:,.2f} less than target limit.")
        elif diff == 0:
            report_lines.append(f"Budget Diff    : Spent exact target budget limit.")
        else:
            report_lines.append(f"Budget Diff    : Exceeded budget by {symbol}{abs(diff):,.2f}.")

        report_lines.append("\n" + "-" * 70)
        report_lines.append(f"EXPENSE BREAKDOWN BY CATEGORY")
        report_lines.append("-" * 70)
        exp_by_cat = summary.get("expense_by_category", {})
        if exp_by_cat:
            for cat, amt in sorted(exp_by_cat.items(), key=lambda x: x[1], reverse=True):
                pct = (amt / tot_exp * 100) if tot_exp > 0 else 0
                report_lines.append(f"  - {cat:<24} : {symbol}{amt:>10,.2f} ({pct:>5.1f}%)")
        else:
            report_lines.append("  (No expense transactions found)")

        report_lines.append("\n" + "-" * 70)
        report_lines.append(f"TRANSACTION LEDGER ({len(txs)} entries)")
        report_lines.append("-" * 70)
        report_lines.append(f"{'Date':<12} {'Type':<10} {'Category':<20} {'Narration':<20} {'Amount':>12}")
        report_lines.append("-" * 70)

        for t in txs:
            amt_str = f"{'+' if t.type == 'income' else '-'}{symbol}{t.amount:,.2f}"
            report_lines.append(f"{t.date:<12} {t.type.upper():<10} {t.category:<20} {t.title[:18]:<20} {amt_str:>12}")

        report_lines.append("=" * 70)

        self.summary_box.configure(state="normal")
        self.summary_box.delete("1.0", "end")
        self.summary_box.insert("1.0", "\n".join(report_lines))
        self.summary_box.configure(state="disabled")

    def print_report(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        summary = self.db.get_budget_summary(active_budget.id)
        txs = self.db.get_transactions(active_budget.id)
        symbol = active_budget.currency_symbol

        tot_inc = summary.get("total_income", 0.0)
        tot_exp = summary.get("total_expense", 0.0)
        net_res = summary.get("net_result", 0.0)
        exp_by_cat = summary.get("expense_by_category", {})

        # Generate Printable HTML Document
        rows_html = ""
        for t in txs:
            badge_cls = "income-badge" if t.type == "income" else "expense-badge"
            sign = "+" if t.type == "income" else "-"
            rows_html += f"""
            <tr>
                <td>{t.date}</td>
                <td><span class="{badge_cls}">{t.type.upper()}</span></td>
                <td>{t.category}</td>
                <td><strong>{t.title}</strong></td>
                <td style="text-align: right;">{sign}{symbol}{t.amount:,.2f}</td>
            </tr>
            """

        cat_html = ""
        for cat, amt in sorted(exp_by_cat.items(), key=lambda x: x[1], reverse=True):
            pct = (amt / tot_exp * 100) if tot_exp > 0 else 0
            cat_html += f"""
            <tr>
                <td>{cat}</td>
                <td style="text-align: right;">{symbol}{amt:,.2f}</td>
                <td style="text-align: right;">{pct:.1f}%</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mopex Financial Statement - {active_budget.title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; color: #1e293b; line-height: 1.5; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #3b82f6; padding-bottom: 15px; margin-bottom: 25px; }}
        .brand {{ font-size: 26px; font-weight: bold; color: #3b82f6; }}
        .subtitle {{ font-size: 13px; color: #64748b; }}
        .meta-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 25px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .meta-item label {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; display: block; }}
        .meta-item span {{ font-size: 16px; font-weight: bold; color: #0f172a; }}
        h2 {{ font-size: 16px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 8px 12px; text-align: left; }}
        th {{ background: #f1f5f9; color: #334155; font-weight: bold; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        .income-badge {{ background: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .expense-badge {{ background: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <span>🖨️ <strong>Print Preview Ready:</strong> Click Print to select your printer or save as PDF.</span>
        <button onclick="window.print()" style="background: #3b82f6; color: white; border: none; padding: 8px 18px; border-radius: 6px; font-weight: bold; cursor: pointer;">Print Document Now</button>
    </div>

    <div class="header">
        <div>
            <div class="brand">💎 MOPEX FINANCIAL REPORT</div>
            <div class="subtitle">Personal Desktop Expense & Budget Manager</div>
        </div>
        <div style="text-align: right; font-size: 12px; color: #64748b;">
            Date Generated: {active_budget.created_at}<br>
            Budget ID: #{active_budget.id}
        </div>
    </div>

    <div class="meta-card">
        <div class="meta-item">
            <label>Budget Title</label>
            <span>{active_budget.title}</span>
        </div>
        <div class="meta-item">
            <label>User Profile</label>
            <span>{active_budget.user_name}</span>
        </div>
        <div class="meta-item">
            <label>Currency</label>
            <span>{active_budget.currency} ({symbol})</span>
        </div>
        <div class="meta-item">
            <label>Target Budget Limit</label>
            <span>{symbol}{active_budget.total_budget:,.2f}</span>
        </div>
    </div>

    <h2>Financial Overview Summary</h2>
    <table>
        <tr>
            <th>Total Income</th>
            <th>Total Expense</th>
            <th>Net Profit / Loss</th>
            <th>Budget Remaining</th>
        </tr>
        <tr>
            <td style="color: #15803d; font-weight: bold;">{symbol}{tot_inc:,.2f}</td>
            <td style="color: #b91c1c; font-weight: bold;">{symbol}{tot_exp:,.2f}</td>
            <td style="font-weight: bold;">{symbol}{net_res:,.2f}</td>
            <td style="font-weight: bold;">{symbol}{(active_budget.total_budget - tot_exp):,.2f}</td>
        </tr>
    </table>

    <h2>Expense Category Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Category</th>
                <th style="text-align: right;">Total Amount</th>
                <th style="text-align: right;">Share (%)</th>
            </tr>
        </thead>
        <tbody>
            {cat_html or "<tr><td colspan='3'>No expense categories found</td></tr>"}
        </tbody>
    </table>

    <h2>Transaction Ledger ({len(txs)} Entries)</h2>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Category</th>
                <th>Narration</th>
                <th style="text-align: right;">Amount</th>
            </tr>
        </thead>
        <tbody>
            {rows_html or "<tr><td colspan='5'>No transactions found</td></tr>"}
        </tbody>
    </table>

    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 500);
        }};
    </script>
</body>
</html>"""

        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"Mopex_Report_{active_budget.id}.html")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file://{file_path}")

    def export_csv(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"Mopex_{active_budget.title.replace(' ', '_')}_Report.csv"
        )
        if not file_path:
            return

        txs = self.db.get_transactions(active_budget.id)
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Title / Narration", "Type", "Category", f"Amount ({active_budget.currency})"])
            for t in txs:
                writer.writerow([t.id, t.date, t.title, t.type, t.category, t.amount])

        messagebox.showinfo("Export Successful", f"Report successfully exported to:\n{file_path}")

    def export_json(self):
        active_budget = self.db.get_active_budget()
        if not active_budget:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialfile=f"Mopex_{active_budget.title.replace(' ', '_')}_Report.json"
        )
        if not file_path:
            return

        summary = self.db.get_budget_summary(active_budget.id)
        txs = self.db.get_transactions(active_budget.id)

        data = {
            "budget": {
                "title": active_budget.title,
                "user_name": active_budget.user_name,
                "currency": active_budget.currency,
                "currency_symbol": active_budget.currency_symbol,
                "total_budget": active_budget.total_budget,
                "created_at": active_budget.created_at
            },
            "summary": {
                "total_income": summary.get("total_income", 0.0),
                "total_expense": summary.get("total_expense", 0.0),
                "net_result": summary.get("net_result", 0.0),
                "expense_by_category": summary.get("expense_by_category", {})
            },
            "transactions": [
                {
                    "id": t.id,
                    "date": t.date,
                    "title": t.title,
                    "type": t.type,
                    "category": t.category,
                    "amount": t.amount
                }
                for t in txs
            ]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Export Successful", f"JSON report successfully exported to:\n{file_path}")
