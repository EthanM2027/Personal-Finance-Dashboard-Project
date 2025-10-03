#!/usr/bin/env python3
"""
Personal Finance Tracker with SQLite Database - Fixed Schema Implementation
"""

import sqlite3
import datetime
import sys
from typing import List, Optional, Dict, Tuple
from db import get_connection, create_schema, insert_default_data, load_transactions_from_db, add_transaction_to_db, update_transaction_in_db, delete_transaction_from_db
from utils import get_menu_choice, get_account, get_amount, get_description, get_category, get_date, display_transactions, edit_transaction, delete_transaction, get_transaction_id
import state

DB_NAME = "finance_tracker.db"




def main():
    """Main program function"""
    print("=== Personal Finance Tracker (Fixed Schema Edition) ===")
    
    # Initialize database
    create_schema()
    
    # Load existing transactions into memory (store into shared state)
    print("Loading existing transactions...")
    state.transactions = load_transactions_from_db()
    
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
                state.transactions.insert(0, new_transaction)
                
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