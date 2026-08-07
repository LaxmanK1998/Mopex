"""
Mopex - Desktop Expense Manager Application.
Entry point script.
"""
import sys
import datetime
from database import DatabaseManager
from models import Transaction, Budget, Goal, JournalNote
from gui.app import MopexApp


def seed_sample_data_if_empty(db: DatabaseManager):
    """
    Seed realistic initial financial entries if database has no transactions yet.
    """
    active_budget = db.get_active_budget()
    if not active_budget:
        return

    existing_txs = db.get_transactions(active_budget.id)
    if existing_txs:
        return  # Data already exists

    today = datetime.date.today()
    curr_month = today.strftime("%Y-%m")

    sample_transactions = [
        Transaction(
            budget_id=active_budget.id,
            title="Monthly Software Developer Salary",
            amount=75000.00,
            type="income",
            category="Salary & Wages",
            date=f"{curr_month}-01",
            notes="Direct deposit pay",
            is_recurring=True,
            recur_interval="monthly",
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Freelance UI/UX Design Project",
            amount=18500.00,
            type="income",
            category="Freelance / Business",
            date=f"{curr_month}-03",
            notes="Client payment",
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Apartment Rent Payment",
            amount=15000.00,
            type="expense",
            category="Housing & Rent",
            date=f"{curr_month}-02",
            notes="Monthly rent",
            is_recurring=True,
            recur_interval="monthly",
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Supermarket Grocery Shopping",
            amount=3200.00,
            type="expense",
            category="Food & Dining",
            date=f"{curr_month}-05",
            notes="Weekly groceries",
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Electricity & Internet Bill",
            amount=2100.00,
            type="expense",
            category="Utilities & Bills",
            date=f"{curr_month}-06",
            notes="Utility bills",
            is_recurring=True,
            recur_interval="monthly",
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Weekend Dinner & Movie",
            amount=1450.00,
            type="expense",
            category="Entertainment",
            date=f"{curr_month}-07",
            notes="Dining out",
        ),
    ]
    for tx in sample_transactions:
        db.add_transaction(tx)

    # Seed sample goals if none exist
    existing_goals = db.get_goals(active_budget.id)
    if not existing_goals:
        sample_goals = [
            Goal(
                budget_id=active_budget.id,
                title="Emergency Fund",
                target_amount=100000.0,
                saved_amount=35000.0,
                deadline="2026-12-31",
                description="6-month emergency fund",
                icon="💰",
            ),
            Goal(
                budget_id=active_budget.id,
                title="New Laptop",
                target_amount=80000.0,
                saved_amount=25000.0,
                deadline="2026-10-15",
                description="MacBook Pro or equivalent",
                icon="💻",
            ),
        ]
        for g in sample_goals:
            db.add_goal(g)

    # Seed sample journal note if none exist
    existing_notes = db.get_journal_notes(active_budget.id)
    if not existing_notes:
        db.add_journal_note(JournalNote(
            budget_id=active_budget.id,
            date=today.isoformat(),
            title="First Month Financial Review",
            content="Started tracking expenses today with Mopex. Income looks healthy this month. "
                    "Need to cut back on dining out and entertainment spending.",
            mood="good",
        ))


def main():
    print("Starting Mopex Desktop Application...")
    db = DatabaseManager()
    seed_sample_data_if_empty(db)

    app = MopexApp(db)
    app.mainloop()


if __name__ == "__main__":
    main()