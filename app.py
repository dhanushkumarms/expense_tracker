import matplotlib
matplotlib.use('Agg')  # ✅ Fixes GUI/threading issues

import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import io
import base64


app = Flask(__name__)

DATA_DIR = 'data'
INCOME_CSV = os.path.join(DATA_DIR, 'incomes.csv')
EXPENSE_CSV = os.path.join(DATA_DIR, 'expenses.csv')

os.makedirs(DATA_DIR, exist_ok=True)

def load_data(file):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
    return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

def save_data(df, file):
    df.to_csv(file, index=False)

def generate_pie_chart(data):
    if data.empty:
        return ""
    plt.figure(figsize=(6, 6))
    plt.pie(data['Amount'], labels=data['Category'], autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return encoded

def generate_monthly_chart(df):
    if df.empty:
        return ""
    df['Date'] = pd.to_datetime(df['Date'])
    monthly = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().reset_index()
    monthly['Date'] = monthly['Date'].astype(str)
    plt.figure(figsize=(10, 4))
    plt.plot(monthly['Date'], monthly['Amount'], marker='o')
    plt.xticks(rotation=45)
    plt.grid(True)
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return encoded

@app.route('/')
def dashboard():
    income_df = load_data(INCOME_CSV)
    expense_df = load_data(EXPENSE_CSV)
    total_income = income_df['Amount'].sum()
    total_expense = expense_df['Amount'].sum()
    total_balance = total_income - total_expense
    return render_template('index.html', total_income=total_income, total_expense=total_expense, total_balance=total_balance)

@app.route('/income', methods=['GET'])
def income():
    df = load_data(INCOME_CSV)
    total_income = df['Amount'].sum()
    category_totals = df.groupby('Category')['Amount'].sum().to_dict() if not df.empty else {}
    chart = generate_monthly_chart(df)
    pie = generate_pie_chart(df.groupby('Category')['Amount'].sum().reset_index())
    top_items = df.nlargest(5, 'Amount') if not df.empty else pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
    return render_template('income.html', items=df.to_dict('records'), total_income=total_income, category_totals=category_totals, analytics={
        'monthly_chart': chart,
        'category_chart': pie,
        'top_items': top_items.to_dict('records'),
        'category_totals': {'labels': list(category_totals.keys())},
        'daily_expenses': {'data': df.groupby('Date')['Amount'].sum().tolist() if not df.empty else []}
    })

@app.route('/expense', methods=['GET'])
def expense():
    df = load_data(EXPENSE_CSV)
    total_expense = df['Amount'].sum()
    category_totals = df.groupby('Category')['Amount'].sum().to_dict() if not df.empty else {}
    chart = generate_monthly_chart(df)
    pie = generate_pie_chart(df.groupby('Category')['Amount'].sum().reset_index())
    top_items = df.nlargest(5, 'Amount') if not df.empty else pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
    return render_template('expense.html', items=df.to_dict('records'), total_expense=total_expense, category_totals=category_totals, analytics={
        'monthly_chart': chart,
        'category_chart': pie,
        'top_items': top_items.to_dict('records'),
        'category_totals': {'labels': list(category_totals.keys())},
        'daily_expenses': {'data': df.groupby('Date')['Amount'].sum().tolist() if not df.empty else []}
    })

@app.route('/balance')
def balance():
    income_df = load_data(INCOME_CSV)
    expense_df = load_data(EXPENSE_CSV)
    total_income = income_df['Amount'].sum()
    total_expense = expense_df['Amount'].sum()
    total_balance = total_income - total_expense
    income_chart = generate_pie_chart(income_df.groupby('Category')['Amount'].sum().reset_index())
    expense_chart = generate_pie_chart(expense_df.groupby('Category')['Amount'].sum().reset_index())
    return render_template('balance.html', total_income=total_income, total_expense=total_expense, total_balance=total_balance, income_chart=income_chart, expense_chart=expense_chart)

@app.route('/add_income', methods=['POST'])
def add_income():
    df = load_data(INCOME_CSV)
    new_entry = {
        'Date': request.form['date'],
        'Category': request.form['category'],
        'Amount': float(request.form['amount']),
        'Description': request.form.get('description', '')
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(df, INCOME_CSV)
    return redirect(url_for('income'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    df = load_data(EXPENSE_CSV)
    new_entry = {
        'Date': request.form['date'],
        'Category': request.form['category'],
        'Amount': float(request.form['amount']),
        'Description': request.form.get('description', '')
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(df, EXPENSE_CSV)
    return redirect(url_for('expense'))

if __name__ == '__main__':
    app.run(debug=True)
