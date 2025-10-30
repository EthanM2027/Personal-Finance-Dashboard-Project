#Run this in terminal to run code:  python app.py in browser http://127.0.0.1:5000
#If I run python PF_Main.py it will run the CLI version of the Personal Finance app
#Flask incorporates the same logic but provides a web interface instead of CLI

from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
from db import (get_connection, create_schema, insert_default_data, 
                load_transactions_from_db, add_transaction_to_db, 
                update_transaction_in_db, delete_transaction_from_db)
import state
    
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database and load transactions at startup
create_schema()
state.transactions = load_transactions_from_db()


@app.route('/')
def index():
    """Home page - displays all transactions (replaces display_transactions)"""
    # Reload transactions from database to get latest data
    state.transactions = load_transactions_from_db()
    
    if not state.transactions:
        total_amount = 0
    else:
        total_amount = sum(float(t['Amount']) for t in state.transactions)
    
    return render_template('index.html', 
                         transactions=state.transactions, 
                         total=total_amount)


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    """Add new transaction (replaces your CLI add_transaction)"""
    
    if request.method == 'POST':
        # Get form data (replaces your input() calls)
        try:
            amount = float(request.form['amount'])
            description = request.form['description'].strip()
            category_id = int(request.form['category_id'])
            account_id = int(request.form['account_id'])
            date_str = request.form['date']
            
            # Validate (same as your get_amount and get_description functions)
            if not description:
                flash('Description cannot be empty', 'error')
                return redirect(url_for('add_transaction'))
            
            if amount == 0:
                flash('Amount cannot be zero', 'error')
                return redirect(url_for('add_transaction'))
            
            if abs(amount) >= 100000000:
                flash('Amount must be less than 100 million', 'error')
                return redirect(url_for('add_transaction'))
            
            # Add to database using your existing function from db.py
            transaction_id = add_transaction_to_db(account_id, category_id, amount, description, date_str)
            
            if transaction_id:
                flash('Transaction added successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Failed to add transaction to database', 'error')
                
        except (ValueError, KeyError) as e:
            flash(f'Invalid input: {str(e)}', 'error')
    
    # GET request - show form with categories and accounts
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get categories (replaces your get_category function)
    cursor.execute('SELECT id, name, type FROM categories WHERE is_active = 1 ORDER BY name')
    categories = cursor.fetchall()
    
    # Get accounts (replaces your get_account function)
    cursor.execute('SELECT id, name, type, balance FROM accounts WHERE is_active = 1 ORDER BY name')
    accounts = cursor.fetchall()
    
    conn.close()
    
    # Default date to today (replaces your get_date function)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    return render_template('add_transaction.html', 
                         categories=categories, 
                         accounts=accounts,
                         today=today)


@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    """Edit existing transaction (replaces your edit_transaction function)"""
    
    # Find the transaction
    state.transactions = load_transactions_from_db()
    selected = None
    for t in state.transactions:
        if t['ID'] == transaction_id:
            selected = t
            break
    
    if not selected:
        flash('Transaction not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get updated values from form
            amount = float(request.form['amount'])
            description = request.form['description'].strip()
            category_id = int(request.form['category_id'])
            date_str = request.form['date']
            
            # Validate
            if not description:
                flash('Description cannot be empty', 'error')
                return redirect(url_for('edit_transaction', transaction_id=transaction_id))
            
            if amount == 0:
                flash('Amount cannot be zero', 'error')
                return redirect(url_for('edit_transaction', transaction_id=transaction_id))
            
            if abs(amount) >= 100000000:
                flash('Amount must be less than 100 million', 'error')
                return redirect(url_for('edit_transaction', transaction_id=transaction_id))
            
            # Update in database using your existing function from db.py
            if update_transaction_in_db(transaction_id, category_id, amount, description, date_str):
                flash('Transaction updated successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Failed to update transaction', 'error')
                
        except (ValueError, KeyError) as e:
            flash(f'Invalid input: {str(e)}', 'error')
    
    # GET request - show form pre-filled with current values
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, type FROM categories WHERE is_active = 1 ORDER BY name')
    categories = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_transaction.html', 
                         transaction=selected, 
                         categories=categories)


@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    """Delete transaction (replaces your delete_transaction function)"""
    
    # Delete from database using your existing function from db.py
    if delete_transaction_from_db(transaction_id):
        flash('Transaction deleted successfully!', 'success')
    else:
        flash('Failed to delete transaction', 'error')
    
    return redirect(url_for('index'))


@app.route('/report')
def report():
    """Generate filtered report (replaces your display_report function)"""
    
    # Reload transactions
    state.transactions = load_transactions_from_db()
    
    # Get filter parameters from URL query string
    range_type = request.args.get('range', 'all')
    year = request.args.get('year', '')
    month = request.args.get('month', '')
    
    filtered = state.transactions
    
    # Apply filters (same logic as your CLI version)
    if range_type == 'year' and year:
        filtered = [t for t in state.transactions if t['Date'].startswith(year)]
    elif range_type == 'month' and year and month:
        month_padded = month.zfill(2)  # '1' -> '01'
        filtered = [t for t in state.transactions if t['Date'].startswith(f"{year}-{month_padded}")]
    
    # Calculate total
    if filtered:
        total = sum(float(t['Amount']) for t in filtered)
    else:
        total = 0
    
    return render_template('report.html', 
                         transactions=filtered, 
                         total=total,
                         range_type=range_type, 
                         year=year, 
                         month=month)
    


if __name__ == '__main__':
    
    app.run(debug=True, port=5000)