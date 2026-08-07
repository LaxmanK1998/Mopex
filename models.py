"""
Data models for Mopex Expense Manager.
"""
import datetime
from dataclasses import dataclass, field
from typing import Optional


DEFAULT_CURRENCIES = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "A$",
    "CHF": "CHF",
    "CNY": "¥",
    "BRL": "R$",
}

DEFAULT_CATEGORIES = {
    "expense": [
        "Food & Dining",
        "Housing & Rent",
        "Utilities & Bills",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Healthcare",
        "Education",
        "Travel",
        "Misc Expense",
    ],
    "income": [
        "Salary & Wages",
        "Freelance / Business",
        "Investments",
        "Gifts & Grants",
        "Refunds",
        "Misc Income",
    ]
}

GOAL_ICONS = ["🎯", "🏠", "✈️", "🚗", "📱", "💻", "💍", "🎓", "🏋️", "💰", "🎁", "🌱"]

MOOD_OPTIONS = {
    "great": "😄 Great",
    "good": "🙂 Good",
    "neutral": "😐 Neutral",
    "stressed": "😰 Stressed",
    "bad": "😞 Bad",
}

RECUR_INTERVALS = ["daily", "weekly", "monthly"]


@dataclass
class Budget:
    id: Optional[int] = None
    title: str = "Monthly Expenses"
    total_budget: float = 0.0
    currency: str = "INR"
    currency_symbol: str = "₹"
    user_name: str = "User"
    created_at: str = field(default_factory=lambda: datetime.date.today().isoformat())
    is_active: bool = True
    alert_yellow_pct: float = 75.0
    alert_red_pct: float = 100.0

    def formatted_budget(self) -> str:
        return f"{self.currency_symbol}{self.total_budget:,.2f}"


@dataclass
class Transaction:
    id: Optional[int] = None
    budget_id: int = 1
    title: str = ""
    amount: float = 0.0
    type: str = "expense"  # 'income' or 'expense'
    category: str = "Misc Expense"
    date: str = field(default_factory=lambda: datetime.date.today().isoformat())
    notes: str = ""
    is_recurring: bool = False
    recur_interval: str = ""  # 'daily', 'weekly', 'monthly'

    def formatted_amount(self, symbol: str = "₹") -> str:
        prefix = "+" if self.type == "income" else "-"
        return f"{prefix}{symbol}{abs(self.amount):,.2f}"


@dataclass
class Goal:
    id: Optional[int] = None
    budget_id: int = 1
    title: str = ""
    target_amount: float = 0.0
    saved_amount: float = 0.0
    deadline: str = ""
    description: str = ""
    icon: str = "🎯"
    created_at: str = field(default_factory=lambda: datetime.date.today().isoformat())

    @property
    def progress_pct(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        return min(self.saved_amount / self.target_amount * 100, 100.0)

    @property
    def remaining(self) -> float:
        return max(self.target_amount - self.saved_amount, 0.0)

    @property
    def is_achieved(self) -> bool:
        return self.saved_amount >= self.target_amount


@dataclass
class JournalNote:
    id: Optional[int] = None
    budget_id: int = 1
    date: str = field(default_factory=lambda: datetime.date.today().isoformat())
    title: str = ""
    content: str = ""
    mood: str = "neutral"
    created_at: str = field(default_factory=lambda: datetime.date.today().isoformat())
