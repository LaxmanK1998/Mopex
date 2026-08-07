"""
Database manager for Mopex Expense Manager using SQLite.
"""
import os
import sqlite3
import datetime
import csv
from typing import List, Dict, Any, Optional
from models import Budget, Transaction, Goal, JournalNote, DEFAULT_CURRENCIES


DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mopex.db")


class DatabaseManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create Budgets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    total_budget REAL DEFAULT 0.0,
                    currency TEXT DEFAULT 'INR',
                    currency_symbol TEXT DEFAULT '₹',
                    user_name TEXT DEFAULT 'User',
                    created_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    alert_yellow_pct REAL DEFAULT 75.0,
                    alert_red_pct REAL DEFAULT 100.0
                )
            """)

            # Add alert threshold columns if upgrading from old schema
            for col, default in [("alert_yellow_pct", "75.0"), ("alert_red_pct", "100.0")]:
                try:
                    cursor.execute(f"ALTER TABLE budgets ADD COLUMN {col} REAL DEFAULT {default}")
                except Exception:
                    pass  # Column already exists

            # Create Transactions Table with recurring support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    budget_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    is_recurring INTEGER DEFAULT 0,
                    recur_interval TEXT DEFAULT '',
                    FOREIGN KEY (budget_id) REFERENCES budgets (id) ON DELETE CASCADE
                )
            """)

            # Add recurring columns if upgrading from old schema
            for col, default in [("is_recurring", "0"), ("recur_interval", "''")]:
                try:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col} TEXT DEFAULT {default}")
                except Exception:
                    pass

            # Create Goals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    budget_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    saved_amount REAL DEFAULT 0.0,
                    deadline TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    icon TEXT DEFAULT '🎯',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (budget_id) REFERENCES budgets (id) ON DELETE CASCADE
                )
            """)

            # Create Journal Notes Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS journal_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    budget_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT DEFAULT '',
                    mood TEXT DEFAULT 'neutral',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (budget_id) REFERENCES budgets (id) ON DELETE CASCADE
                )
            """)

            conn.commit()

        # Create a default budget if none exists
        budgets = self.get_all_budgets()
        if not budgets:
            default_budget = Budget(
                title="Default Monthly Budget",
                total_budget=50000.0,
                currency="INR",
                currency_symbol="₹",
                user_name="User",
                is_active=True
            )
            self.create_budget(default_budget)

    # ---------------- Budget Operations ----------------

    def create_budget(self, budget: Budget) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if budget.is_active:
                cursor.execute("UPDATE budgets SET is_active = 0")
            cursor.execute("""
                INSERT INTO budgets (title, total_budget, currency, currency_symbol, user_name, created_at, is_active, alert_yellow_pct, alert_red_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                budget.title,
                budget.total_budget,
                budget.currency,
                budget.currency_symbol,
                budget.user_name,
                budget.created_at,
                1 if budget.is_active else 0,
                budget.alert_yellow_pct,
                budget.alert_red_pct,
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_budgets(self) -> List[Budget]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM budgets ORDER BY id DESC")
            rows = cursor.fetchall()
            return [self._row_to_budget(row) for row in rows]

    def _row_to_budget(self, row) -> Budget:
        keys = row.keys()
        return Budget(
            id=row['id'],
            title=row['title'],
            total_budget=row['total_budget'],
            currency=row['currency'],
            currency_symbol=row['currency_symbol'],
            user_name=row['user_name'],
            created_at=row['created_at'],
            is_active=bool(row['is_active']),
            alert_yellow_pct=row['alert_yellow_pct'] if 'alert_yellow_pct' in keys else 75.0,
            alert_red_pct=row['alert_red_pct'] if 'alert_red_pct' in keys else 100.0,
        )

    def get_active_budget(self) -> Optional[Budget]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM budgets WHERE is_active = 1 LIMIT 1")
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT * FROM budgets ORDER BY id ASC LIMIT 1")
                row = cursor.fetchone()
            return self._row_to_budget(row) if row else None

    def set_active_budget(self, budget_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE budgets SET is_active = 0")
            cursor.execute("UPDATE budgets SET is_active = 1 WHERE id = ?", (budget_id,))
            conn.commit()

    def update_budget(self, budget: Budget):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE budgets
                SET title = ?, total_budget = ?, currency = ?, currency_symbol = ?, user_name = ?,
                    alert_yellow_pct = ?, alert_red_pct = ?
                WHERE id = ?
            """, (
                budget.title,
                budget.total_budget,
                budget.currency,
                budget.currency_symbol,
                budget.user_name,
                budget.alert_yellow_pct,
                budget.alert_red_pct,
                budget.id
            ))
            conn.commit()

    def delete_budget(self, budget_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE budget_id = ?", (budget_id,))
            cursor.execute("DELETE FROM goals WHERE budget_id = ?", (budget_id,))
            cursor.execute("DELETE FROM journal_notes WHERE budget_id = ?", (budget_id,))
            cursor.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
            conn.commit()

        active = self.get_active_budget()
        if active and not active.is_active:
            self.set_active_budget(active.id)

    # ---------------- Transaction Operations ----------------

    def add_transaction(self, tx: Transaction) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (budget_id, title, amount, type, category, date, notes, is_recurring, recur_interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tx.budget_id,
                tx.title,
                tx.amount,
                tx.type,
                tx.category,
                tx.date,
                tx.notes,
                1 if tx.is_recurring else 0,
                tx.recur_interval,
            ))
            conn.commit()
            return cursor.lastrowid

    def update_transaction(self, tx: Transaction):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions
                SET title = ?, amount = ?, type = ?, category = ?, date = ?, notes = ?,
                    is_recurring = ?, recur_interval = ?
                WHERE id = ?
            """, (
                tx.title,
                tx.amount,
                tx.type,
                tx.category,
                tx.date,
                tx.notes,
                1 if tx.is_recurring else 0,
                tx.recur_interval,
                tx.id
            ))
            conn.commit()

    def delete_transaction(self, tx_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
            conn.commit()

    def get_transactions(
        self,
        budget_id: int,
        search: str = "",
        category: str = "All",
        tx_type: str = "All",
        date_from: str = "",
        date_to: str = "",
    ) -> List[Transaction]:
        query = "SELECT * FROM transactions WHERE budget_id = ?"
        params: List[Any] = [budget_id]

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if tx_type and tx_type != "All":
            query += " AND type = ?"
            params.append(tx_type.lower())

        if search:
            query += " AND (title LIKE ? OR notes LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if date_from:
            query += " AND date >= ?"
            params.append(date_from)

        if date_to:
            query += " AND date <= ?"
            params.append(date_to)

        query += " ORDER BY date DESC, id DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_transaction(row) for row in rows]

    def _row_to_transaction(self, row) -> Transaction:
        keys = row.keys()
        return Transaction(
            id=row['id'],
            budget_id=row['budget_id'],
            title=row['title'],
            amount=row['amount'],
            type=row['type'],
            category=row['category'],
            date=row['date'],
            notes=row['notes'],
            is_recurring=bool(row['is_recurring']) if 'is_recurring' in keys else False,
            recur_interval=row['recur_interval'] if 'recur_interval' in keys else "",
        )

    def get_recurring_transactions(self, budget_id: int) -> List[Transaction]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM transactions WHERE budget_id = ? AND is_recurring = 1 ORDER BY date DESC",
                (budget_id,)
            )
            return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def generate_recurring_due(self, budget_id: int):
        """Generate copies of recurring transactions that are due today or overdue."""
        recurring = self.get_recurring_transactions(budget_id)
        today = datetime.date.today()
        generated = 0

        for tx in recurring:
            try:
                tx_date = datetime.date.fromisoformat(tx.date)
            except Exception:
                continue

            interval = tx.recur_interval
            if interval == "daily":
                delta = datetime.timedelta(days=1)
            elif interval == "weekly":
                delta = datetime.timedelta(weeks=1)
            elif interval == "monthly":
                # approximate one month
                delta = datetime.timedelta(days=30)
            else:
                continue

            next_date = tx_date + delta
            while next_date <= today:
                # Only create if no duplicate on that date
                existing = self.get_transactions(budget_id, search=tx.title, date_from=str(next_date), date_to=str(next_date))
                matching = [t for t in existing if t.title == tx.title and t.amount == tx.amount]
                if not matching:
                    new_tx = Transaction(
                        budget_id=budget_id,
                        title=tx.title,
                        amount=tx.amount,
                        type=tx.type,
                        category=tx.category,
                        date=str(next_date),
                        notes=f"[Auto-generated] {tx.notes}",
                        is_recurring=False,  # generated copies are not templates
                        recur_interval="",
                    )
                    self.add_transaction(new_tx)
                    generated += 1
                next_date += delta

        return generated

    def import_csv(self, file_path: str, budget_id: int) -> tuple[int, list]:
        """Import transactions from a CSV file. Returns (count_imported, errors)."""
        imported = 0
        errors = []

        with open(file_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                try:
                    title = row.get("title") or row.get("Title") or row.get("narration") or row.get("Narration") or ""
                    amount_raw = row.get("amount") or row.get("Amount") or "0"
                    tx_type = (row.get("type") or row.get("Type") or "expense").strip().lower()
                    category = row.get("category") or row.get("Category") or "Misc Expense"
                    date = row.get("date") or row.get("Date") or datetime.date.today().isoformat()
                    notes = row.get("notes") or row.get("Notes") or ""

                    if not title:
                        errors.append(f"Row {i}: Missing title/narration — skipped.")
                        continue

                    amount = abs(float(str(amount_raw).replace(",", "").strip()))
                    if amount <= 0:
                        errors.append(f"Row {i}: Invalid amount '{amount_raw}' — skipped.")
                        continue

                    if tx_type not in ("income", "expense"):
                        tx_type = "expense"

                    tx = Transaction(
                        budget_id=budget_id,
                        title=title.strip(),
                        amount=amount,
                        type=tx_type,
                        category=category.strip(),
                        date=date.strip(),
                        notes=notes.strip(),
                    )
                    self.add_transaction(tx)
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {i}: {str(e)}")

        return imported, errors

    # ---------------- Goals Operations ----------------

    def add_goal(self, goal: "Goal") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO goals (budget_id, title, target_amount, saved_amount, deadline, description, icon, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.budget_id,
                goal.title,
                goal.target_amount,
                goal.saved_amount,
                goal.deadline,
                goal.description,
                goal.icon,
                goal.created_at,
            ))
            conn.commit()
            return cursor.lastrowid

    def update_goal(self, goal: "Goal"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE goals
                SET title = ?, target_amount = ?, saved_amount = ?, deadline = ?, description = ?, icon = ?
                WHERE id = ?
            """, (goal.title, goal.target_amount, goal.saved_amount, goal.deadline, goal.description, goal.icon, goal.id))
            conn.commit()

    def delete_goal(self, goal_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
            conn.commit()

    def get_goals(self, budget_id: int) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM goals WHERE budget_id = ? ORDER BY created_at DESC", (budget_id,))
            return [self._row_to_goal(row) for row in cursor.fetchall()]

    def _row_to_goal(self, row) -> "Goal":
        from models import Goal
        return Goal(
            id=row['id'],
            budget_id=row['budget_id'],
            title=row['title'],
            target_amount=row['target_amount'],
            saved_amount=row['saved_amount'],
            deadline=row['deadline'],
            description=row['description'],
            icon=row['icon'],
            created_at=row['created_at'],
        )

    # ---------------- Journal Notes Operations ----------------

    def add_journal_note(self, note: "JournalNote") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO journal_notes (budget_id, date, title, content, mood, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (note.budget_id, note.date, note.title, note.content, note.mood, note.created_at))
            conn.commit()
            return cursor.lastrowid

    def update_journal_note(self, note: "JournalNote"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE journal_notes SET title = ?, content = ?, mood = ?  WHERE id = ?
            """, (note.title, note.content, note.mood, note.id))
            conn.commit()

    def delete_journal_note(self, note_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM journal_notes WHERE id = ?", (note_id,))
            conn.commit()

    def get_journal_notes(self, budget_id: int, search: str = "") -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if search:
                cursor.execute(
                    "SELECT * FROM journal_notes WHERE budget_id = ? AND (title LIKE ? OR content LIKE ?) ORDER BY date DESC",
                    (budget_id, f"%{search}%", f"%{search}%")
                )
            else:
                cursor.execute(
                    "SELECT * FROM journal_notes WHERE budget_id = ? ORDER BY date DESC",
                    (budget_id,)
                )
            return [self._row_to_note(row) for row in cursor.fetchall()]

    def _row_to_note(self, row) -> "JournalNote":
        from models import JournalNote
        return JournalNote(
            id=row['id'],
            budget_id=row['budget_id'],
            date=row['date'],
            title=row['title'],
            content=row['content'],
            mood=row['mood'],
            created_at=row['created_at'],
        )

    # ---------------- Analytics & Summary ----------------

    def get_budget_summary(self, budget_id: int) -> Dict[str, Any]:
        budget = self.get_active_budget()
        if not budget or budget.id != budget_id:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM budgets WHERE id = ?", (budget_id,))
                row = cursor.fetchone()
                budget = self._row_to_budget(row) if row else None

        if not budget:
            return {}

        txs = self.get_transactions(budget_id)
        total_income = sum(t.amount for t in txs if t.type == "income")
        total_expense = sum(t.amount for t in txs if t.type == "expense")
        net_result = total_income - total_expense

        # Category breakdowns
        expense_by_category: Dict[str, float] = {}
        income_by_category: Dict[str, float] = {}
        for t in txs:
            if t.type == "expense":
                expense_by_category[t.category] = expense_by_category.get(t.category, 0.0) + t.amount
            else:
                income_by_category[t.category] = income_by_category.get(t.category, 0.0) + t.amount

        # Monthly trends
        monthly_data: Dict[str, Dict[str, float]] = {}
        for t in txs:
            month_key = t.date[:7] if len(t.date) >= 7 else "Other"
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0.0, "expense": 0.0}
            if t.type == "income":
                monthly_data[month_key]["income"] += t.amount
            else:
                monthly_data[month_key]["expense"] += t.amount

        # Spending insights: averages
        import datetime as _dt
        dates_with_expense = sorted(set(t.date for t in txs if t.type == "expense"))
        if len(dates_with_expense) >= 2:
            first = _dt.date.fromisoformat(dates_with_expense[0])
            last = _dt.date.fromisoformat(dates_with_expense[-1])
            days_span = max((last - first).days, 1)
            daily_avg = total_expense / days_span
            weekly_avg = daily_avg * 7
            monthly_avg = daily_avg * 30
        else:
            daily_avg = weekly_avg = monthly_avg = total_expense

        remaining_budget = budget.total_budget - total_expense
        budget_usage_pct = (total_expense / budget.total_budget * 100) if budget.total_budget > 0 else 0.0

        return {
            "budget": budget,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_result": net_result,
            "remaining_budget": remaining_budget,
            "budget_usage_pct": budget_usage_pct,
            "transaction_count": len(txs),
            "expense_by_category": expense_by_category,
            "income_by_category": income_by_category,
            "monthly_data": monthly_data,
            "daily_avg_expense": daily_avg,
            "weekly_avg_expense": weekly_avg,
            "monthly_avg_expense": monthly_avg,
        }
