"""
Mopex - Desktop Expense Manager Application.
Entry point script.
"""
import sys
import datetime
from database import DatabaseManager
from models import Transaction, Budget
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
            amount=4200.00,
            type="income",
            category="Salary & Wages",
            date=f"{curr_month}-01",
            notes="Direct deposit pay"
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Freelance UI/UX Design Project",
            amount=850.00,
            type="income",
            category="Freelance / Business",
            date=f"{curr_month}-03",
            notes="Client payment"
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Apartment Rent Payment",
            amount=1200.00,
            type="expense",
            category="Housing & Rent",
            date=f"{curr_month}-02",
            notes="Monthly rent"
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Supermarket Grocery Shopping",
            amount=245.50,
            type="expense",
            category="Food & Dining",
            date=f"{curr_month}-05",
            notes="Weekly groceries"
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Electricity & High-Speed Internet Bill",
            amount=115.80,
            type="expense",
            category="Utilities & Bills",
            date=f"{curr_month}-06",
            notes="Utility bills"
        ),
        Transaction(
            budget_id=active_budget.id,
            title="Weekend Dinner & Movie with Friends",
            amount=78.20,
            type="expense",
            category="Entertainment",
            date=f"{curr_month}-07",
            notes="Dining out"
        ),
    ]

    for tx in sample_transactions:
        db.add_transaction(tx)


def main():
    print("Starting Mopex Desktop Application...")
    db = DatabaseManager()
    seed_sample_data_if_empty(db)

    app = MopexApp(db)
    app.mainloop()


if __name__ == "__main__":
    main()