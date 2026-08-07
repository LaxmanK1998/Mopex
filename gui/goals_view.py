"""
Financial Goals / Savings Targets View for Mopex.
"""
import datetime
import customtkinter as ctk
from typing import Optional, Callable
from database import DatabaseManager
from models import Goal, GOAL_ICONS


class GoalDialog(ctk.CTkToplevel):
    """Modal dialog to create or edit a financial savings goal."""

    def __init__(self, master, db: DatabaseManager, budget_id: int,
                 goal: Optional[Goal] = None, on_save: Optional[Callable] = None):
        super().__init__(master)
        self.db = db
        self.budget_id = budget_id
        self.goal = goal
        self.on_save = on_save

        self.title("Edit Goal" if goal else "New Savings Goal")
        self.geometry("440x540")
        self.resizable(False, False)
        self.grab_set()
        self.after(10, self._center_window)

        ctk.CTkLabel(self, text="✏️ Edit Goal" if goal else "🌟 New Savings Goal",
                     font=("Segoe UI", 18, "bold")).pack(pady=(18, 12))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24)

        # Icon picker
        ctk.CTkLabel(form, text="Icon:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.icon_var = ctk.StringVar(value=goal.icon if goal else "🎯")
        icon_frame = ctk.CTkFrame(form, fg_color="transparent")
        icon_frame.pack(fill="x", pady=(0, 10))
        for ico in GOAL_ICONS:
            btn = ctk.CTkButton(
                icon_frame, text=ico, width=38, height=34, font=("Segoe UI Emoji", 14),
                fg_color="transparent", border_width=1, hover_color=("#E2E8F0", "#334155"),
                command=lambda i=ico: self._select_icon(i)
            )
            btn.pack(side="left", padx=2)

        # Title
        ctk.CTkLabel(form, text="Goal Title:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.title_entry = ctk.CTkEntry(form, placeholder_text="E.g. New Laptop, Emergency Fund, Vacation", height=36)
        if goal:
            self.title_entry.insert(0, goal.title)
        self.title_entry.pack(fill="x", pady=(0, 10))

        # Target amount
        ctk.CTkLabel(form, text="Target Amount:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.target_entry = ctk.CTkEntry(form, placeholder_text="0.00", height=36)
        if goal:
            self.target_entry.insert(0, str(goal.target_amount))
        self.target_entry.pack(fill="x", pady=(0, 10))

        # Saved so far
        ctk.CTkLabel(form, text="Already Saved:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.saved_entry = ctk.CTkEntry(form, placeholder_text="0.00", height=36)
        if goal:
            self.saved_entry.insert(0, str(goal.saved_amount))
        self.saved_entry.pack(fill="x", pady=(0, 10))

        # Deadline
        ctk.CTkLabel(form, text="Target Deadline (YYYY-MM-DD, optional):", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
        self.deadline_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD", height=36)
        if goal and goal.deadline:
            self.deadline_entry.insert(0, goal.deadline)
        self.deadline_entry.pack(fill="x", pady=(0, 10))

        self.error_label = ctk.CTkLabel(form, text="", text_color="#EF4444", font=("Segoe UI", 11))
        self.error_label.pack(fill="x", pady=(0, 4))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 18))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=1,
                      text_color=("#475569", "#CBD5E1"), command=self.destroy, height=38, width=100).pack(side="left")
        ctk.CTkButton(btn_frame, text="💾 Save Goal", fg_color="#3B82F6", hover_color="#2563EB",
                      command=self._save, height=38, width=140, font=("Segoe UI", 12, "bold")).pack(side="right")

    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()//2)-(w//2)}+{(self.winfo_screenheight()//2)-(h//2)}")

    def _select_icon(self, icon: str):
        self.icon_var.set(icon)

    def _save(self):
        title = self.title_entry.get().strip()
        target_str = self.target_entry.get().strip()
        saved_str = self.saved_entry.get().strip() or "0"
        deadline = self.deadline_entry.get().strip()
        icon = self.icon_var.get() or "🎯"

        if not title:
            self.error_label.configure(text="Please enter a goal title.")
            return
        try:
            target = float(target_str)
            saved = float(saved_str)
            if target <= 0:
                self.error_label.configure(text="Target amount must be greater than zero.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid amount. Enter numeric values.")
            return

        if self.goal:
            self.goal.title = title
            self.goal.target_amount = target
            self.goal.saved_amount = saved
            self.goal.deadline = deadline
            self.goal.icon = icon
            self.db.update_goal(self.goal)
        else:
            new_goal = Goal(
                budget_id=self.budget_id,
                title=title,
                target_amount=target,
                saved_amount=saved,
                deadline=deadline,
                icon=icon,
            )
            self.db.add_goal(new_goal)

        if self.on_save:
            self.on_save()
        self.destroy()


class GoalsView(ctk.CTkScrollableFrame):
    """Financial Goals view with progress tracking cards."""

    def __init__(self, master, db: DatabaseManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db = db

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 10))

        ctk.CTkLabel(header, text="Savings Goals 🌟", font=("Segoe UI", 22, "bold"), anchor="w").pack(side="left")

        ctk.CTkButton(
            header, text="+ Add Goal", font=("Segoe UI", 12, "bold"),
            fg_color="#3B82F6", hover_color="#2563EB", height=36,
            command=self._open_add_dialog
        ).pack(side="right")

        self.cards_container = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True, padx=16, pady=8)

        self.refresh()

    def refresh(self):
        for w in self.cards_container.winfo_children():
            w.destroy()

        budget = self.db.get_active_budget()
        if not budget:
            return

        goals = self.db.get_goals(budget.id)
        symbol = budget.currency_symbol

        if not goals:
            ctk.CTkLabel(
                self.cards_container,
                text="No savings goals yet.\nClick '+ Add Goal' to create your first savings target!",
                font=("Segoe UI", 14),
                text_color=("#64748B", "#94A3B8"),
            ).pack(pady=60)
            return

        # Summary strip
        total_target = sum(g.target_amount for g in goals)
        total_saved = sum(g.saved_amount for g in goals)
        achieved = sum(1 for g in goals if g.is_achieved)
        strip = ctk.CTkFrame(self.cards_container, fg_color=("white", "#1E293B"),
                             corner_radius=10, border_width=1, border_color=("#E2E8F0", "#334155"))
        strip.pack(fill="x", pady=(0, 12))
        for col, (lbl, val) in enumerate([
            ("Total Goals", str(len(goals))),
            ("Total Target", f"{symbol}{total_target:,.0f}"),
            ("Total Saved", f"{symbol}{total_saved:,.0f}"),
            ("Achieved 🏆", str(achieved)),
        ]):
            cell = ctk.CTkFrame(strip, fg_color="transparent")
            cell.grid(row=0, column=col, padx=18, pady=12, sticky="ew")
            strip.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(cell, text=lbl, font=("Segoe UI", 10, "bold"),
                         text_color=("#64748B", "#94A3B8")).pack()
            ctk.CTkLabel(cell, text=val, font=("Segoe UI", 16, "bold")).pack()

        for goal in goals:
            self._render_goal_card(goal, symbol)

    def _render_goal_card(self, goal: Goal, symbol: str):
        pct = goal.progress_pct
        is_done = goal.is_achieved

        card = ctk.CTkFrame(
            self.cards_container,
            fg_color=("white", "#1E293B"),
            corner_radius=12,
            border_width=2 if is_done else 1,
            border_color="#10B981" if is_done else ("#E2E8F0", "#334155"),
        )
        card.pack(fill="x", pady=6)

        # Top row
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(top, text=f"{goal.icon} {goal.title}", font=("Segoe UI", 15, "bold")).pack(side="left")

        if is_done:
            ctk.CTkLabel(top, text="✅ Achieved!", font=("Segoe UI", 11, "bold"),
                         text_color="white", fg_color="#10B981", corner_radius=6, padx=8, pady=2).pack(side="right")
        else:
            remaining = f"{symbol}{goal.remaining:,.0f} to go"
            ctk.CTkLabel(top, text=remaining, font=("Segoe UI", 11),
                         text_color=("#64748B", "#94A3B8")).pack(side="right")

        # Progress bar
        bar = ctk.CTkProgressBar(card, height=12, corner_radius=6,
                                  progress_color="#10B981" if is_done else "#3B82F6")
        bar.set(pct / 100)
        bar.pack(fill="x", padx=16, pady=(4, 4))

        # Detail row
        detail = ctk.CTkFrame(card, fg_color="transparent")
        detail.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(detail, text=f"Saved: {symbol}{goal.saved_amount:,.0f}", font=("Segoe UI", 11)).pack(side="left")
        ctk.CTkLabel(detail, text=f"Target: {symbol}{goal.target_amount:,.0f}", font=("Segoe UI", 11)).pack(side="left", padx=16)
        ctk.CTkLabel(detail, text=f"{pct:.1f}%", font=("Segoe UI", 11, "bold"),
                     text_color="#3B82F6").pack(side="left")
        if goal.deadline:
            ctk.CTkLabel(detail, text=f"Deadline: {goal.deadline}", font=("Segoe UI", 11),
                         text_color=("#64748B", "#94A3B8")).pack(side="left", padx=16)

        # Action buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(btn_row, text="✏️ Edit", width=70, height=28, font=("Segoe UI", 11),
                      fg_color="transparent", border_width=1,
                      command=lambda g=goal: self._open_edit_dialog(g)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btn_row, text="🗑️", width=38, height=28, font=("Segoe UI", 12),
                      fg_color="#EF4444", hover_color="#DC2626",
                      command=lambda g=goal: self._delete_goal(g.id)).pack(side="left")

    def _open_add_dialog(self):
        budget = self.db.get_active_budget()
        if budget:
            GoalDialog(self, self.db, budget.id, on_save=self.refresh)

    def _open_edit_dialog(self, goal: Goal):
        budget = self.db.get_active_budget()
        if budget:
            GoalDialog(self, self.db, budget.id, goal=goal, on_save=self.refresh)

    def _delete_goal(self, goal_id: int):
        self.db.delete_goal(goal_id)
        self.refresh()
