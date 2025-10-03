import sqlite3
from typing import List, Dict, Optional

DB_NAME = "finance_tracker.db"

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

def load_transactions_from_db() -> List[Dict]:
    """Load all transactions from SQLite database and return as a list of dicts"""
    transactions_local: List[Dict] = []

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
            transactions_local.append(transaction)

        conn.close()
        print(f"Loaded {len(transactions_local)} transactions from database")
        return transactions_local

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        print("Starting with empty transaction list...")
        return transactions_local


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