import sqlite3
import datetime
import sys
from typing import List, Optional, Dict, Tuple
from db import get_connection, create_schema, insert_default_data, load_transactions_from_db, add_transaction_to_db, update_transaction_in_db, delete_transaction_from_db
import state  # holds shared runtime state (state.transactions)


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
    if not state.transactions:
        print("\nNo transactions available!")
        return None
        
    while True:
        try:
            transaction_id = int(input(prompt))
            
            selected = None
            for transaction in state.transactions:
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
            state.transactions.remove(selected)
            print("\n✓ Transaction deleted successfully from database!")
        else:
            print("\n✗ Failed to delete transaction from database!")


def display_transactions():
    """Display all transactions in a nice format"""
    if not state.transactions:
        print("\nNo transactions found!")
        return
    
    print(f"\n{'='*90}")
    print(f"{'ID':<6} {'Amount':<12} {'Category':<15} {'Account':<15} {'Date':<12} Description")
    print(f"{'='*90}")
    
    total_amount = 0
    for transaction in state.transactions:
        amount = float(transaction['Amount'])
        total_amount += amount
        
        print(f"{transaction['ID']:<6} ${amount:<11.2f} "
                f"{transaction['Category']:<15} {transaction['Account']:<15} "
                f"{transaction['Date']:<12} {transaction['Description']}")
    
    print(f"{'='*90}")
    print(f"Total transactions: {len(state.transactions)}")
    print(f"Net amount: ${total_amount:.2f}")
    print(f"{'='*90}")