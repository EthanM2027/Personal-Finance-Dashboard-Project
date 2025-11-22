import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional

# Adjust these to match your PostgreSQL setup
DB_CONFIG = {
    "dbname": "finance",
    "user": "ethan",
    "password": "strongpassword",
    "host": "postgres",
    "port": 5432
}


def get_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**DB_CONFIG)


def create_schema():
    """Create all PostgreSQL tables, indexes, and triggers"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('Income', 'Expense', 'Transfer')),
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE
            );
        """)

        # 2. Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN (
                    'Checking', 'Savings', 'Credit Card', 'Investment', 'Cash', 'Other'
                )),
                balance NUMERIC(12,2) DEFAULT 0.00,
                currency TEXT DEFAULT 'USD',
                created_at TIMESTAMP DEFAULT NOW(),
                is_active BOOLEAN DEFAULT TRUE,
                notes TEXT
            );
        """)

        # 3. Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
                category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
                amount NUMERIC(12,2) NOT NULL CHECK(amount != 0),
                description TEXT NOT NULL,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                notes TEXT,
                reference_number TEXT,
                is_reconciled BOOLEAN DEFAULT FALSE
            );
        """)

        # Indexes for speed
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);")

        # Trigger: update updated_at timestamp
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_transaction_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_timestamp ON transactions;
            CREATE TRIGGER trigger_update_timestamp
            BEFORE UPDATE ON transactions
            FOR EACH ROW
            EXECUTE FUNCTION update_transaction_timestamp();
        """)

        conn.commit()
        insert_default_data(conn)
        conn.close()

    except Exception as e:
        print("❌ Database schema error:", e)


def insert_default_data(conn):
    """Insert default categories and one default account"""
    cursor = conn.cursor()

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

    cursor.executemany("""
        INSERT INTO categories (name, type, description)
        VALUES (%s, %s, %s)
        ON CONFLICT (name) DO NOTHING;
    """, default_categories)

    cursor.execute("""
        INSERT INTO accounts (name, type, currency, notes)
        VALUES ('Main Checking', 'Checking', 'USD', 'Primary checking account')
        ON CONFLICT (name) DO NOTHING;
    """)

    conn.commit()
    print("✓ Default categories & accounts loaded.")


def load_transactions_from_db() -> List[Dict]:
    """Load all transactions as list of dicts"""
    transactions_local = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                t.id,
                t.amount,
                t.description,
                c.name AS category_name,
                t.transaction_date,
                a.name AS account_name,
                t.account_id,
                t.category_id
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            JOIN accounts a ON t.account_id = a.id
            ORDER BY t.transaction_date DESC, t.id DESC;
        """)

        rows = cursor.fetchall()

        for r in rows:
            transactions_local.append({
                "ID": r[0],
                "Amount": float(r[1]),
                "Description": r[2],
                "Category": r[3],
                "Date": str(r[4]),
                "Account": r[5],
                "AccountID": r[6],
                "CategoryID": r[7]
            })

        conn.close()
        return transactions_local

    except Exception as e:
        print("❌ Load error:", e)
        return []


def add_transaction_to_db(account_id: int, category_id: int, amount: float,
                          description: str, transaction_date: str) -> Optional[int]:
    """Add transaction to PostgreSQL"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Validate account
        cursor.execute("SELECT id FROM accounts WHERE id = %s AND is_active = TRUE;", (account_id,))
        if not cursor.fetchone():
            conn.close()
            return None

        # Validate category
        cursor.execute("SELECT id FROM categories WHERE id = %s AND is_active = TRUE;", (category_id,))
        if not cursor.fetchone():
            conn.close()
            return None

        cursor.execute("""
            INSERT INTO transactions (account_id, category_id, amount, description, transaction_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (account_id, category_id, amount, description, transaction_date))

        transaction_id = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        return transaction_id

    except Exception as e:
        print("❌ Insert error:", e)
        return None


def update_transaction_in_db(transaction_id: int, category_id: int,
                             amount: float, description: str, transaction_date: str) -> bool:
    """Update transaction"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM categories WHERE id = %s AND is_active = TRUE;", (category_id,))
        if not cursor.fetchone():
            conn.close()
            return False

        cursor.execute("""
            UPDATE transactions
            SET category_id = %s, amount = %s, description = %s, transaction_date = %s
            WHERE id = %s;
        """, (category_id, amount, description, transaction_date, transaction_id))

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    except Exception as e:
        print("❌ Update error:", e)
        return False


def delete_transaction_from_db(transaction_id: int) -> bool:
    """Delete transaction"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM transactions WHERE id = %s;", (transaction_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    except Exception as e:
        print("❌ Delete error:", e)
        return False
