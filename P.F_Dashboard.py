#!/usr/bin/env python3
"""
Personal Finance Tracker with SQLite Database
"""

import sqlite3
import datetime
import sys
from typing import List, Optional, Dict

class PersonalFinance:
    """Helper class for managing personal finance transactions"""
    transactions = []  # List to store transactions in memory
    DB_NAME = "finance_tracker.db"
    
    CATEGORIES = [
        "Checking", 
        "Savings", 
        "Credit Card", 
        "Investment",
        "Other"
    ]
    
    @staticmethod
    def init_database():
        """Initialize the SQLite database and create tables if they don't exist"""
        conn = sqlite3.connect(PersonalFinance.DB_NAME)
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {PersonalFinance.DB_NAME}")
    
    @staticmethod
    def load_transactions_from_db():
        """Load all transactions from SQLite database into memory"""
        PersonalFinance.transactions = []
        
        try:
            conn = sqlite3.connect(PersonalFinance.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, amount, description, category, date 
                FROM transactions 
                ORDER BY id
            ''')
            
            rows = cursor.fetchall()
            
            for row in rows:
                transaction = {
                    "ID": row[0],
                    "Amount": row[1],
                    "Description": row[2],
                    "Category": row[3],
                    "Date": row[4]
                }
                PersonalFinance.transactions.append(transaction)
            
            conn.close()
            print(f"Loaded {len(PersonalFinance.transactions)} transactions from database")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            print("Starting with empty transaction list...")
    
    @staticmethod
    def add_transaction_to_db(amount: float, description: str, category: str, date: str) -> int:
        """Add a new transaction to the database and return its ID"""
        try:
            conn = sqlite3.connect(PersonalFinance.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (amount, description, category, date)
                VALUES (?, ?, ?, ?)
            ''', (amount, description, category, date))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return transaction_id
            
        except sqlite3.Error as e:
            print(f"Error adding transaction: {e}")
            return None
    
    @staticmethod
    def update_transaction_in_db(transaction_id: int, amount: float, description: str, 
                                 category: str, date: str) -> bool:
        """Update an existing transaction in the database"""
        try:
            conn = sqlite3.connect(PersonalFinance.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE transactions 
                SET amount = ?, description = ?, category = ?, date = ?
                WHERE id = ?
            ''', (amount, description, category, date, transaction_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating transaction: {e}")
            return False
    
    @staticmethod
    def delete_transaction_from_db(transaction_id: int) -> bool:
        """Delete a transaction from the database"""
        try:
            conn = sqlite3.connect(PersonalFinance.DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    @staticmethod
    def get_amount(prompt="Enter amount: $") -> float:
        """Get a valid monetary amount from user"""
        while True:
            try:
                amount_str = input(prompt).replace('$', '').replace(',', '')
                amount = float(amount_str)
                if amount >= 100000000 or amount <= -100000000:
                    print("Amount must be + or - of 100 million")
                    continue
                return round(amount, 2)
            except ValueError:
                print("Please enter a valid number (e.g., 25.50)")
    
    @staticmethod
    def get_description(prompt="Enter description: ") -> str:
        """Get transaction description"""
        while True:
            description = input(prompt).strip()
            if description:
                return description
            print("Description cannot be empty")
    
    @staticmethod
    def get_category() -> str:
        """Get expense category from predefined list"""
        print("\nSelect a category:")
        for i, category in enumerate(PersonalFinance.CATEGORIES, 1):
            print(f"{i:2d}. {category}")
        
        while True:
            try:
                choice = int(input("Enter category number: "))
                if 1 <= choice <= len(PersonalFinance.CATEGORIES):
                    return PersonalFinance.CATEGORIES[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(PersonalFinance.CATEGORIES)}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
    def get_date(prompt="Enter date (YYYY-MM-DD) or press Enter for today: ") -> datetime.datetime:
        """Get date input with validation"""
        while True:
            date_input = input(prompt).strip()
            
            if not date_input:  # Empty = today
                return datetime.datetime.now()
            
            # Try different date formats
            date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]
            
            for fmt in date_formats:
                try:
                    return datetime.datetime.strptime(date_input, fmt)
                except ValueError:
                    continue
            
            print("Invalid date format. Try: YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY")
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
    def get_transaction_id(prompt="Enter transaction ID: "):
        """Get transaction ID with validation and display it"""
        if not PersonalFinance.transactions:
            print("\nNo transactions available!")
            return None
            
        while True:
            try:
                transaction_id = int(input(prompt))
                
                # Find transaction with matching ID
                selected = None
                for transaction in PersonalFinance.transactions:
                    if transaction['ID'] == transaction_id:
                        selected = transaction
                        break
                
                if selected:
                    # Display nicely
                    print(f"\n{'='*80}")
                    print(f"{'ID':<10}{'Amount':<10} {'Category':<15} {'Date':<12} Description")
                    print(f"{'='*80}")
                    print(f"{selected['ID']:<10} ${selected['Amount']:<9.2f} "
                        f"{selected['Category']:<15} {selected['Date']:<12} "
                        f"{selected['Description']}")
                    print(f"{'='*80}")
                    return selected
                else:
                    print(f"Transaction ID {transaction_id} not found. Please try again.")
            except ValueError:
                print("Please enter a valid transaction ID number")
                
    @staticmethod
    def edit_transaction():
        """Edit an existing Transaction"""
        print("\n=== Edit Transaction ===")
        
        selected = PersonalFinance.get_transaction_id()
        if not selected:
            return
        
        # Edit Amount
        if PersonalFinance.get_yes_no("Edit amount?"):
            selected["Amount"] = PersonalFinance.get_amount("Enter new amount: $")
        
        # Edit Description
        if PersonalFinance.get_yes_no("Edit description?"):
            selected["Description"] = PersonalFinance.get_description("Enter new description: ")
        
        # Edit Category
        if PersonalFinance.get_yes_no("Edit category?"):
            selected["Category"] = PersonalFinance.get_category()
        
        # Edit Date
        if PersonalFinance.get_yes_no("Edit date?"):
            selected["Date"] = PersonalFinance.get_date().strftime('%Y-%m-%d')
        
        # Update in database
        if PersonalFinance.update_transaction_in_db(
            selected["ID"], 
            selected["Amount"], 
            selected["Description"],
            selected["Category"], 
            selected["Date"]
        ):
            print("\n✓ Transaction updated successfully in database!")
        else:
            print("\n✗ Failed to update transaction in database!")
    
    @staticmethod
    def delete_transaction():
        """Delete an existing transaction"""
        print("\n=== Delete Transaction ===")
        
        selected = PersonalFinance.get_transaction_id()
        if not selected:
            return
        
        if PersonalFinance.get_yes_no("Are you sure you want to delete this transaction?"):
            if PersonalFinance.delete_transaction_from_db(selected["ID"]):
                PersonalFinance.transactions.remove(selected)
                print("\n✓ Transaction deleted successfully from database!")
            else:
                print("\n✗ Failed to delete transaction from database!")
    
    @staticmethod
    def display_transactions():
        """Display all transactions in a nice format"""
        if not PersonalFinance.transactions:
            print("\nNo transactions found!")
            return
        
        print(f"\n{'='*80}")
        print(f"{'ID':<10}{'Amount':<10} {'Category':<15} {'Date':<12} Description")
        print(f"{'='*80}")
        
        total_amount = 0
        for transaction in PersonalFinance.transactions:
            amount = float(transaction['Amount'])
            total_amount += amount
            
            print(f"{transaction['ID']:<10} ${amount:<9.2f} "
                  f"{transaction['Category']:<15} {transaction['Date']:<12} "
                  f"{transaction['Description']}")
        
        print(f"{'='*80}")
        print(f"Total transactions: {len(PersonalFinance.transactions)}")
        print(f"Total amount: ${total_amount:.2f}")
        print(f"{'='*80}")


def main():
    """Main program function"""
    print("=== Personal Finance Tracker (SQLite Edition) ===")
    
    # Initialize database
    PersonalFinance.init_database()
    
    # Load existing transactions
    print("Loading existing transactions...")
    PersonalFinance.load_transactions_from_db()
    
    main_menu_options = [
        "Add Transaction",
        "View Transactions", 
        "Edit Transaction",
        "Delete Transaction",
        "Search Transaction",
        "Exit"
    ]
    
    while True:
        choice = PersonalFinance.get_menu_choice("Main Menu", main_menu_options)
        
        if choice == 1:  # Add Transaction
            print("\n--- Add New Transaction ---")

            amount = PersonalFinance.get_amount("Enter transaction amount: $")
            description = PersonalFinance.get_description("Enter description: ")
            category = PersonalFinance.get_category()
            date = PersonalFinance.get_date().strftime('%Y-%m-%d')
            
            # Add to database
            transaction_id = PersonalFinance.add_transaction_to_db(amount, description, category, date)
            
            if transaction_id:
                # Add to in-memory list
                new_transaction = {
                    "ID": transaction_id,
                    "Amount": amount,
                    "Description": description,
                    "Category": category,
                    "Date": date
                }
                PersonalFinance.transactions.append(new_transaction)
                
                print(f"\n✓ Transaction added successfully!")
                print(f"Transaction ID: {transaction_id}")
                print(f"Amount: ${amount:.2f}")
            else:
                print("\n✗ Failed to add transaction to database!")
            
        elif choice == 2:  # View Transactions
            PersonalFinance.display_transactions()
            
        elif choice == 3:  # Edit Transaction
            PersonalFinance.edit_transaction()
            
        elif choice == 4:  # Delete Transaction
            PersonalFinance.delete_transaction()
            
        elif choice == 5:  # Search Transaction
            PersonalFinance.get_transaction_id()
            
        elif choice == 6:  # Exit
            print("\nThank you for using Personal Finance Tracker!")
            print("All changes have been saved to the database automatically.")
            sys.exit(0)


if __name__ == "__main__":
    main()