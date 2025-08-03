# Expense Tracker Web Application

A simple web application to track your daily expenses built with Flask.

## Features

- Add new expenses with date, category, amount, and description
- View all expenses in a table format
- See total expenses and category-wise breakdown
- Modern and responsive UI using Bootstrap

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to:
```
http://localhost:5000
```

## Data Storage

The application stores expenses in a CSV file located in the `data` directory. The file is automatically created when you add your first expense.

## Categories

The application supports the following expense categories:
- Groceries
- Transport
- Entertainment
- Vegetables
- Fruits
- Shopping
- Utilities
- Health & Fitness
- Stationary 