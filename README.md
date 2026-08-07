# 💎 Mopex - Privacy-Friendly Desktop Expense Manager

**Mopex** is an open-source, privacy-focused Desktop GUI Expense Manager application for Windows PC. Designed to keep all your financial data 100% offline, local, and secure.

---

## ✨ Features

- 📊 **Modern Dashboard**: High-resolution desktop GUI with Dark/Light themes, KPI summary stat cards, and real-time net profit/loss metrics.
- 🎯 **Budget Limit Progress Gauge**: Visual progress bar indicating spent vs target budget limit, with color-coded safety warnings (Within Budget, Approaching Limit, Over Budget).
- 📈 **Interactive Charts**: Category breakdown pie charts and monthly income vs expense trend bar charts.
- 📑 **Transaction Ledger**: Search, filter, add, edit, and delete transactions with custom categories and auto-calculated totals.
- 💼 **Multi-Budget & Currency Manager**: Create and switch between multiple budget profiles (e.g. Monthly Home, Kitchen Repair, Vacation) with multi-currency support (USD $, EUR €, GBP £, INR ₹, JPY ¥, CAD $, AUD $, etc.).
- 📄 **Financial Reports & Exporting**: Generate formatted profit/loss financial statements and export reports to **CSV** and **JSON** formats.
- 🔒 **100% Offline & Private**: Powered by a local SQLite database (`mopex.db`). No cloud accounts or external servers required.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** installed on Windows.

### Dependencies
Install the required packages using pip:
```bash
pip install customtkinter matplotlib pillow
```

### Launch Application
Run `main.py` from your terminal or double-click to launch:
```bash
python main.py
```

---

## 🛠️ Architecture & Tech Stack

- **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern Tkinter extensions)
- **Database**: SQLite 3 (`sqlite3`)
- **Data Visualization**: Matplotlib (`matplotlib.backends.backend_tkagg`)
- **Language**: Python 3
