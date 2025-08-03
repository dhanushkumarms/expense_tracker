from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns

app = Flask(__name__)

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Ensure the static directory exists
if not os.path.exists('static'):
    os.makedirs('static')

# Path to the expenses CSV file
EXPENSES_FILE = 'data/expenses.csv'

def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        return pd.read_csv(EXPENSES_FILE)
    return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

def save_expenses(df):
    df.to_csv(EXPENSES_FILE, index=False)

def generate_monthly_chart(monthly_data):
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid')  # Using a cleaner style
    
    # Create the line plot with enhanced styling
    plt.plot(monthly_data.index, monthly_data['Amount'], 
             marker='o', 
             linewidth=2.5, 
             color='#6c5ce7',
             markersize=8,
             markerfacecolor='white',
             markeredgewidth=2)
    
    # Fill the area under the line with a gradient
    plt.fill_between(monthly_data.index, monthly_data['Amount'], 
                     alpha=0.2, 
                     color='#6c5ce7',
                     hatch='///')
    
    # Customize the chart with enhanced styling
    plt.title('Monthly Expenses Trend', 
              fontsize=16, 
              fontweight='bold', 
              pad=20,
              color='#2d3436')
    
    plt.xlabel('Month', 
               fontsize=12, 
               labelpad=10,
               color='#2d3436')
    
    plt.ylabel('Amount (₹)', 
               fontsize=12, 
               labelpad=10,
               color='#2d3436')
    
    # Enhanced grid styling
    plt.grid(True, 
             linestyle='--', 
             alpha=0.7,
             color='#b2bec3')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Format y-axis to show currency with enhanced styling
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # Remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save the chart to a bytes buffer with higher DPI
    img = io.BytesIO()
    plt.savefig(img, 
                format='png', 
                dpi=150,  # Increased DPI for better quality
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')

def generate_category_chart(category_data):
    plt.figure(figsize=(12, 8))  # Increased figure size for better spacing
    plt.style.use('seaborn-v0_8-whitegrid')  # Using a cleaner style
    
    # Define a more sophisticated color palette
    colors = ['#6c5ce7', '#a363d9', '#74b9ff', '#00cec9', 
              '#55efc4', '#81ecec', '#74b9ff', '#a29bfe', 
              '#ffeaa7', '#fab1a0']
    
    # Create the pie chart with enhanced styling
    wedges, texts, autotexts = plt.pie(category_data['Amount'], 
                                      labels=None,  # Remove labels from pie chart
                                      autopct='%1.1f%%', 
                                      startangle=90, 
                                      colors=colors,
                                      wedgeprops={'edgecolor': 'white', 
                                                'linewidth': 1.5,
                                                'width': 0.7},  # Make it a donut chart
                                      textprops={'fontsize': 10,
                                                'color': '#2d3436'})
    
    # Enhance percentage labels
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Add a title with enhanced styling
    plt.title('Expense Distribution by Category', 
              fontsize=16, 
              fontweight='bold', 
              pad=20,
              color='#2d3436')
    
    # Add a legend with enhanced styling
    legend = plt.legend(wedges, 
              category_data.index, 
              title='Categories', 
              loc='center left', 
              bbox_to_anchor=(1.1, 0.5),  # Moved legend further to the right
              frameon=True,
              edgecolor='#dfe6e9',
              title_fontsize=12,
              fontsize=10)
    
    # Add percentage values to the legend
    total_amount = category_data['Amount'].sum()
    for i, (wedge, label) in enumerate(zip(wedges, category_data.index)):
        # Use iloc to access by position instead of using integer indexing
        percentage = category_data['Amount'].iloc[i] / total_amount * 100
        legend.get_texts()[i].set_text(f"{label}: {percentage:.1f}%")
    
    # Make the pie chart circular
    plt.axis('equal')
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save the chart to a bytes buffer with higher DPI
    img = io.BytesIO()
    plt.savefig(img, 
                format='png', 
                dpi=150,  # Increased DPI for better quality
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')

def generate_daily_chart(daily_data):
    plt.figure(figsize=(12, 6))
    plt.style.use('seaborn-v0_8-whitegrid')  # Using a cleaner style
    
    # Format the date index to show only day and month
    daily_data.index = daily_data.index.strftime('%d-%b')
    
    # Create the bar chart with enhanced styling
    bars = plt.bar(daily_data.index, 
                   daily_data['Amount'], 
                   color='#6c5ce7', 
                   alpha=0.8,
                   width=0.8,
                   edgecolor='white',
                   linewidth=1)
    
    # Add value labels on top of each bar with enhanced styling
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., 
                height + 0.1,
                f'₹{height:,.0f}', 
                ha='center', 
                va='bottom', 
                fontsize=9,
                fontweight='bold',
                color='#2d3436')
    
    # Customize the chart with enhanced styling
    plt.title('Daily Expenses (Last 30 Days)', 
              fontsize=16, 
              fontweight='bold', 
              pad=20,
              color='#2d3436')
    
    plt.xlabel('Date', 
               fontsize=12, 
               labelpad=10,
               color='#2d3436')
    
    plt.ylabel('Amount (₹)', 
               fontsize=12, 
               labelpad=10,
               color='#2d3436')
    
    # Enhanced grid styling
    plt.grid(True, 
             linestyle='--', 
             alpha=0.7,
             color='#b2bec3',
             axis='y')
    
    # Rotate x-axis labels for better readability and adjust alignment
    plt.xticks(rotation=45, ha='right')
    
    # Format y-axis to show currency with enhanced styling
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # Remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save the chart to a bytes buffer with higher DPI
    img = io.BytesIO()
    plt.savefig(img, 
                format='png', 
                dpi=150,  # Increased DPI for better quality
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')

def get_analytics_data(df):
    if df.empty:
        return {
            'monthly_totals': [],
            'category_totals': [],
            'daily_expenses': [],
            'top_expenses': [],
            'spending_trends': [],
            'monthly_breakdown': [],
            'monthly_chart': '',
            'category_chart': '',
            'daily_chart': ''
        }
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Monthly totals
    monthly_data = df.groupby(df['Date'].dt.strftime('%Y-%m'))[['Amount']].sum()
    monthly_totals = {
        'labels': monthly_data.index.tolist(),
        'data': monthly_data['Amount'].tolist()
    }
    
    # Generate monthly chart
    monthly_chart = generate_monthly_chart(monthly_data)
    
    # Category totals
    category_data = df.groupby('Category')[['Amount']].sum().sort_values('Amount', ascending=False)
    category_totals = {
        'labels': category_data.index.tolist(),
        'data': category_data['Amount'].tolist()
    }
    
    # Generate category chart
    category_chart = generate_category_chart(category_data)
    
    # Daily expenses for the last 30 days
    last_30_days = df[df['Date'] >= (df['Date'].max() - pd.Timedelta(days=30))]
    daily_data = last_30_days.groupby('Date')[['Amount']].sum()
    daily_expenses = {
        'labels': daily_data.index.strftime('%Y-%m-%d').tolist(),
        'data': daily_data['Amount'].tolist()
    }
    
    # Generate daily chart
    daily_chart = generate_daily_chart(daily_data)
    
    # Top 5 highest expenses
    top_expenses = df.nlargest(5, 'Amount')[['Date', 'Category', 'Amount', 'Description']]
    top_expenses['Date'] = top_expenses['Date'].dt.strftime('%Y-%m-%d')
    top_expenses = top_expenses.to_dict('records')
    
    # Monthly spending trends by category
    spending_trends = df.pivot_table(
        index=df['Date'].dt.strftime('%Y-%m'),
        columns='Category',
        values='Amount',
        aggfunc='sum'
    ).fillna(0).to_dict('index')
    
    # Monthly breakdown with category details
    monthly_breakdown = []
    for month in df['Date'].dt.strftime('%Y-%m').unique():
        month_data = df[df['Date'].dt.strftime('%Y-%m') == month]
        month_total = month_data['Amount'].sum()
        category_details = month_data.groupby('Category')['Amount'].sum().to_dict()
        monthly_breakdown.append({
            'month': month,
            'total': month_total,
            'categories': category_details
        })
    
    return {
        'monthly_totals': monthly_totals,
        'category_totals': category_totals,
        'daily_expenses': daily_expenses,
        'top_expenses': top_expenses,
        'spending_trends': spending_trends,
        'monthly_breakdown': monthly_breakdown,
        'monthly_chart': monthly_chart,
        'category_chart': category_chart,
        'daily_chart': daily_chart
    }

@app.route('/')
def index():
    df = load_expenses()
    total_expenses = df['Amount'].sum()
    category_totals = df.groupby('Category')['Amount'].sum().to_dict()
    analytics_data = get_analytics_data(df)
    
    return render_template('index.html', 
                         expenses=df.to_dict('records'),
                         total_expenses=total_expenses,
                         category_totals=category_totals,
                         analytics=analytics_data)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    df = load_expenses()
    new_expense = {
        'Date': request.form['date'],
        'Category': request.form['category'],
        'Amount': float(request.form['amount']),
        'Description': request.form.get('description', '')  # Make description optional
    }
    df = pd.concat([df, pd.DataFrame([new_expense])], ignore_index=True)
    save_expenses(df)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 