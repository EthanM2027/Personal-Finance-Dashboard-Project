#!/usr/bin/env python3
"""
Personal Finance Tracker with SQLite Database - Fixed Schema Implementation
"""

import sqlite3
import datetime
import sys
from typing import List, Optional, Dict, Tuple

  
DB_NAME = "finance_tracker.db"
transactions = []  # Store transactions in memory

def get_connection():
    """Get a database connection with foreign keys enabled"""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_schema():
    """Create a proper database schema with all tables and constraints"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('Income', 'Expense', 'Transfer')),
                description TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # 2. Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('Checking', 'Savings', 'Credit Card', 'Investment', 'Cash', 'Other')),
                balance REAL NOT NULL DEFAULT 0.00,
                currency TEXT NOT NULL DEFAULT 'USD',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER NOT NULL DEFAULT 1,
                notes TEXT
            )
        ''')
        
        # 3. Transactions table - account_id changes not allowed after creation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL CHECK(amount != 0),
                description TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                reference_number TEXT,
                is_reconciled INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_reconciled ON transactions(is_reconciled)')
        
        # Create trigger to update updated_at timestamp
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_transaction_timestamp 
            AFTER UPDATE ON transactions
            BEGIN
                UPDATE transactions SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END
        ''')
        
        # Fixed triggers that handle account changes properly
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_balance_on_insert
            AFTER INSERT ON transactions
            BEGIN
                UPDATE accounts 
                SET balance = balance + NEW.amount
                WHERE id = NEW.account_id;
            END
        ''')
        
        # Fixed update trigger - only updates amount, not account
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_balance_on_update
            AFTER UPDATE OF amount ON transactions
            WHEN OLD.account_id = NEW.account_id
            BEGIN
                UPDATE accounts 
                SET balance = balance - OLD.amount + NEW.amount
                WHERE id = NEW.account_id;
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_balance_on_delete
            AFTER DELETE ON transactions
            BEGIN
                UPDATE accounts 
                SET balance = balance - OLD.amount
                WHERE id = OLD.account_id;
            END
        ''')
        
        conn.commit()
        print("✓ Proper database schema created successfully!")
        
        # Now insert default data
        insert_default_data(conn)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()

def insert_default_data(conn):
    """Insert default categories and a sample account"""
    cursor = conn.cursor()
    
    # Default categories
    default_categories = [
        ('Groceries', 'Expense', 'Food and household items'),
        ('Salary', 'Income', 'Regular employment income'),
        ('Utilities', 'Expense', 'Electric, water, gas, internet'),
        ('Entertainment', 'Expense', 'Movies, games, hobbies'),
        ('Transportation', 'Expense', 'Gas, public transit, car maintenance'),
        ('Healthcare', 'Expense', 'Medical, dental, prescriptions'),
        ('Dining Out', 'Expense', 'Restaurants and takeout'),
        ('Rent/Mortgage', 'Expense', 'Housing payment'),
        ('Savings', 'Transfer', 'Transfer to savings'),
        ('Investment', 'Transfer', 'Investment contributions'),
        ('Freelance', 'Income', 'Side job income'),
        ('Gift', 'Income', 'Money received as gift'),
        ('Shopping', 'Expense', 'Clothing, electronics, etc'),
        ('Education', 'Expense', 'Books, courses, tuition'),
        ('Insurance', 'Expense', 'Health, car, life insurance'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO categories (name, type, description)
        VALUES (?, ?, ?)
    ''', default_categories)
    
    # Create a default checking account
    cursor.execute('''
        INSERT OR IGNORE INTO accounts (name, type, balance, currency, notes)
        VALUES ('Main Checking', 'Checking', 0.00, 'USD', 'Primary checking account')
    ''')
    
    conn.commit()
    print("✓ Default categories and accounts created!")

def load_transactions_from_db():
    """Load all transactions from SQLite database into memory with JOINs"""
    global transactions   # make sure we update the global list
    transactions = []     # clear it before loading fresh
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                t.id, 
                t.amount, 
                t.description, 
                c.name as category_name,
                t.transaction_date,
                a.name as account_name,
                t.account_id,
                t.category_id
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            JOIN accounts a ON t.account_id = a.id
            ORDER BY t.transaction_date DESC, t.id DESC
        ''')
        
        rows = cursor.fetchall()
        
        for row in rows:
            transaction = {
                "ID": row[0],
                "Amount": row[1],
                "Description": row[2],
                "Category": row[3],
                "Date": row[4],
                "Account": row[5],
                "AccountID": row[6],
                "CategoryID": row[7]
            }
            transactions.append(transaction)   # update the global list
        
        conn.close()
        print(f"Loaded {len(transactions)} transactions from database")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        print("Starting with empty transaction list...")


def add_transaction_to_db(account_id: int, category_id: int, amount: float, 
                            description: str, transaction_date: str) -> Optional[int]:
    """Add a new transaction to the database and return its ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate foreign keys exist
        cursor.execute('SELECT id FROM accounts WHERE id = ? AND is_active = 1', (account_id,))
        if not cursor.fetchone():
            print(f"Error: Account ID {account_id} not found or inactive")
            conn.close()
            return None
        
        cursor.execute('SELECT id FROM categories WHERE id = ? AND is_active = 1', (category_id,))
        if not cursor.fetchone():
            print(f"Error: Category ID {category_id} not found or inactive")
            conn.close()
            return None
        
        cursor.execute('''
            INSERT INTO transactions (account_id, category_id, amount, description, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (account_id, category_id, amount, description, transaction_date))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transaction_id
        
    except sqlite3.Error as e:
        print(f"Error adding transaction: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None

def update_transaction_in_db(transaction_id: int, category_id: int,
                            amount: float, description: str, transaction_date: str) -> bool:
    """Update an existing transaction (account cannot be changed)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validate category exists
        cursor.execute('SELECT id FROM categories WHERE id = ? AND is_active = 1', (category_id,))
        if not cursor.fetchone():
            print(f"Error: Category ID {category_id} not found or inactive")
            conn.close()
            return False
        
        # Update transaction (account_id is NOT included)
        cursor.execute('''
            UPDATE transactions 
            SET category_id = ?, amount = ?, description = ?, transaction_date = ?
            WHERE id = ?
        ''', (category_id, amount, description, transaction_date, transaction_id))
        
        if cursor.rowcount == 0:
            print(f"Error: Transaction ID {transaction_id} not found")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error updating transaction: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def delete_transaction_from_db(transaction_id: int) -> bool:
    """Delete a transaction from the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        
        if cursor.rowcount == 0:
            print(f"Error: Transaction ID {transaction_id} not found")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error deleting transaction: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    
def get_amount(prompt="Enter amount: $") -> float:
    """Get a valid monetary amount from user"""
    while True:
        try:
            amount_str = input(prompt).replace('$', '').replace(',', '')
            amount = float(amount_str)
            if amount == 0:
                print("Amount cannot be zero")
                continue
            if abs(amount) >= 100000000:
                print("Amount must be less than 100 million")
                continue
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid number (e.g., 25.50)")

def get_description(prompt="Enter description: ") -> str:
    """Get transaction description"""
    while True:
        description = input(prompt).strip()
        if description:
            return description
        print("Description cannot be empty")


def get_category() -> Tuple[Optional[int], Optional[str]]:
    """Get category from database and return (category_id, category_name)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, type FROM categories WHERE is_active = 1 ORDER BY name')
        categories = cursor.fetchall()
        conn.close()
        
        if not categories:
            print("No categories found! Please add categories first.")
            return None, None
        
        print("\nSelect a category:")
        for i, (cat_id, name, cat_type) in enumerate(categories, 1):
            print(f"{i:2d}. {name} ({cat_type})")
        
        while True:
            try:
                choice = int(input("Enter category number: "))
                if 1 <= choice <= len(categories):
                    selected = categories[choice - 1]
                    return selected[0], selected[1]
                else:
                    print(f"Please enter a number between 1 and {len(categories)}")
            except ValueError:
                print("Please enter a valid number")
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None, None


def get_account() -> Tuple[Optional[int], Optional[str]]:
    """Get account from database and return (account_id, account_name)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, type, balance FROM accounts WHERE is_active = 1 ORDER BY name')
        accounts = cursor.fetchall()
        conn.close()
        
        if not accounts:
            print("No accounts found! Please add accounts first.")
            return None, None
        
        print("\nSelect an account:")
        for i, (acc_id, name, acc_type, balance) in enumerate(accounts, 1):
            print(f"{i:2d}. {name} ({acc_type}) - Balance: ${balance:.2f}")
        
        while True:
            try:
                choice = int(input("Enter account number: "))
                if 1 <= choice <= len(accounts):
                    selected = accounts[choice - 1]
                    return selected[0], selected[1]
                else:
                    print(f"Please enter a number between 1 and {len(accounts)}")
            except ValueError:
                print("Please enter a valid number")
                
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None, None


def get_date(prompt="Enter date (YYYY-MM-DD) or press Enter for today: ") -> datetime.datetime:
    """Get date input with validation"""
    while True:
        date_input = input(prompt).strip()
        
        if not date_input:
            return datetime.datetime.now()
        
        date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]
        
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_input, fmt)
            except ValueError:
                continue
        
        print("Invalid date format. Try: YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY")


def get_yes_no(prompt) -> bool:
    """Get yes/no confirmation"""
    while True:
        answer = input(f"{prompt} (y/n): ").lower().strip()
        if answer in ['y', 'yes', '1']:
            return True
        elif answer in ['n', 'no', '0']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")


def get_menu_choice(title: str, options: List[str]) -> int:
    """Display menu and get user choice"""
    print(f"\n{title}")
    print("=" * len(title))
    
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= len(options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def get_transaction_id(prompt="Enter transaction ID: "):
    """Get transaction ID with validation and display it"""
    if not transactions:
        print("\nNo transactions available!")
        return None
        
    while True:
        try:
            transaction_id = int(input(prompt))
            
            selected = None
            for transaction in transactions:
                if transaction['ID'] == transaction_id:
                    selected = transaction
                    break
            
            if selected:
                print(f"\n{'='*90}")
                print(f"{'ID':<6} {'Amount':<12} {'Category':<15} {'Account':<15} {'Date':<12} Description")
                print(f"{'='*90}")
                print(f"{selected['ID']:<6} ${selected['Amount']:<11.2f} "
                    f"{selected['Category']:<15} {selected['Account']:<15} "
                    f"{selected['Date']:<12} {selected['Description']}")
                print(f"{'='*90}")
                return selected
            else:
                print(f"Transaction ID {transaction_id} not found. Please try again.")
        except ValueError:
            print("Please enter a valid transaction ID number")
            

def edit_transaction():
    """Edit an existing transaction (account cannot be changed)"""
    print("\n=== Edit Transaction ===")
    
    selected = get_transaction_id()
    if not selected:
        return
    
    # Store original values
    category_id = selected["CategoryID"]
    changes_made = False
    
    # Edit Amount
    if get_yes_no("Edit amount?"):
        selected["Amount"] = get_amount("Enter new amount: $")
        changes_made = True
    
    # Edit Description
    if get_yes_no("Edit description?"):
        selected["Description"] = get_description("Enter new description: ")
        changes_made = True
    
    # Note: Account cannot be changed to prevent balance issues
    print("\nNote: Account cannot be changed after creation (to maintain balance integrity)")
    
    # Edit Category
    if get_yes_no("Edit category?"):
        new_category_id, new_category_name = get_category()
        if new_category_id:
            category_id = new_category_id
            selected["Category"] = new_category_name
            selected["CategoryID"] = new_category_id
            changes_made = True
    
    # Edit Date
    if get_yes_no("Edit date?"):
        selected["Date"] = get_date().strftime('%Y-%m-%d')
        changes_made = True
    
    if not changes_made:
        print("\nNo changes made.")
        return
    
    # Update in database
    if update_transaction_in_db(
        selected["ID"], 
        category_id,
        selected["Amount"], 
        selected["Description"],
        selected["Date"]
    ):
        print("\n✓ Transaction updated successfully in database!")
    else:
        print("\n✗ Failed to update transaction in database!")


def delete_transaction():
    """Delete an existing transaction"""
    print("\n=== Delete Transaction ===")
    
    selected = get_transaction_id()
    if not selected:
        return
    
    if get_yes_no("Are you sure you want to delete this transaction?"):
        if delete_transaction_from_db(selected["ID"]):
            transactions.remove(selected)
            print("\n✓ Transaction deleted successfully from database!")
        else:
            print("\n✗ Failed to delete transaction from database!")


def display_transactions():
    """Display all transactions in a nice format"""
    if not transactions:
        print("\nNo transactions found!")
        return
    
    print(f"\n{'='*90}")
    print(f"{'ID':<6} {'Amount':<12} {'Category':<15} {'Account':<15} {'Date':<12} Description")
    print(f"{'='*90}")
    
    total_amount = 0
    for transaction in transactions:
        amount = float(transaction['Amount'])
        total_amount += amount
        
        print(f"{transaction['ID']:<6} ${amount:<11.2f} "
                f"{transaction['Category']:<15} {transaction['Account']:<15} "
                f"{transaction['Date']:<12} {transaction['Description']}")
    
    print(f"{'='*90}")
    print(f"Total transactions: {len(transactions)}")
    print(f"Net amount: ${total_amount:.2f}")
    print(f"{'='*90}")


def main():
    """Main program function"""
    print("=== Personal Finance Tracker (Fixed Schema Edition) ===")
    
    # Initialize database
    create_schema()
    
    # Load existing transactions
    print("Loading existing transactions...")
    load_transactions_from_db()
    
    main_menu_options = [
        "Add Transaction",
        "View Transactions", 
        "Edit Transaction",
        "Delete Transaction",
        "Search Transaction",
        "Exit"
    ]
    
    while True:
        choice = get_menu_choice("Main Menu", main_menu_options)
        
        if choice == 1:  # Add Transaction
            print("\n--- Add New Transaction ---")
            
            account_id, account_name = get_account()
            if not account_id:
                continue
            
            amount = get_amount("Enter transaction amount: $")
            description = get_description("Enter description: ")
            
            category_id, category_name = get_category()
            if not category_id:
                continue
            
            date = get_date().strftime('%Y-%m-%d')
            
            transaction_id = add_transaction_to_db(
                account_id, category_id, amount, description, date
            )
            
            if transaction_id:
                new_transaction = {
                    "ID": transaction_id,
                    "Amount": amount,
                    "Description": description,
                    "Category": category_name,
                    "Date": date,
                    "Account": account_name,
                    "AccountID": account_id,
                    "CategoryID": category_id
                }
                transactions.insert(0, new_transaction)
                
                print(f"\n✓ Transaction added successfully!")
                print(f"Transaction ID: {transaction_id}")
                print(f"Amount: ${amount:.2f}")
            else:
                print("\n✗ Failed to add transaction to database!")
            
        elif choice == 2:
            display_transactions()
            
        elif choice == 3:
            edit_transaction()
            
        elif choice == 4:
            delete_transaction()
            
        elif choice == 5:
            get_transaction_id()
            
        elif choice == 6:
            print("\nThank you for using Personal Finance Tracker!")
            print("All changes have been saved to the database automatically.")
            sys.exit(0)


if __name__ == "__main__":
    main()