#!/usr/bin/env python3
"""
Personal Finance Tracker - Fixed Version
"""

import csv
import datetime
import os
import sys
from typing import List, Optional, Dict

class PersonalFinance:
    """Helper class for getting validated user input"""
    transactions = []  # List to store transactions in memory
    
    CATEGORIES = [
        "Checking", 
        "Savings", 
        "Credit Card", 
        "Investment",
        "Other"
    ]
    
    @staticmethod
    def load_transactions_from_csv():
        """Load existing transactions from CSV file"""
        PersonalFinance.transactions = []  # Clear existing transactions
        
        if not os.path.exists("transactions.csv"):
            print("No existing transactions.csv file found. Starting fresh!")
            return
        
        try:
            with open("transactions.csv", mode="r") as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Convert data types properly
                    transaction = {
                        "ID": int(row["ID"]),
                        "Amount": float(row["Amount"]),
                        "Description": row["Description"],
                        "Category": row["Category"],
                        "Date": row["Date"]
                    }
                    PersonalFinance.transactions.append(transaction)
                    
            print(f"Loaded {len(PersonalFinance.transactions)} existing transactions from CSV")
            
        except FileNotFoundError:
            print("transactions.csv file not found! Starting fresh.")
        except Exception as e:
            print(f"Error loading transactions: {e}")
            print("Starting fresh...")
    
    @staticmethod
    def save_transactions_to_csv():
        """Save all transactions to CSV file"""
        try:
            with open("transactions.csv", mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["ID", "Amount", "Description", "Category", "Date"])
                writer.writeheader()
                writer.writerows(PersonalFinance.transactions)
            
            print(f"\n{len(PersonalFinance.transactions)} transactions saved to transactions.csv")
            return True
        except Exception as e:
            print(f"Error saving transactions: {e}")
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
                    return choice - 1
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
    def get_transaction_id(prompt="Enter transaction ID: ") -> int:
        """Get transaction ID with validation"""
        while True:
            try:
                transaction_id = int(input(prompt))
                if transaction_id > 0:
                    return transaction_id
                else:
                    print("Transaction ID must be greater than 0")
            except ValueError:
                print("Please enter a valid transaction ID number")
    
    @staticmethod
    def display_transactions():
        """Display all transactions in a nice format"""
        if not PersonalFinance.transactions:
            print("\nNo transactions found!")
            return
        
        print(f"\n{'='*80}")
        print(f"{"ID":<10}{'Amount':<10} {'Category':<15} {'Date':<12} Description")
        print(f"{'='*80}")
        
        total_amount = 0
        for transaction in PersonalFinance.transactions:
            amount = float(transaction['Amount'])
            total_amount += amount
            
            print(f"{transaction['ID']: <10} ${amount:<9.2f} "
                  f"{transaction['Category']:<15} {transaction['Date']:<12} "
                  f"{transaction['Description']}")
        
        print(f"{'='*80}")
        print(f"Total transactions: {len(PersonalFinance.transactions)}")
        print(f"Total amount: ${total_amount:.2f}")
        print(f"{'='*80}")

def main():
    """Main program function"""
    print("=== Personal Finance Tracker ===")
    print("Loading existing transactions...")
    
    # Load existing transactions at startup
    PersonalFinance.load_transactions_from_csv()
    
    main_menu_options = [
        "Add Transaction",
        "View Transactions", 
        "Search Transactions",
        "Exit"
    ]
    
    while True:
        choice = PersonalFinance.get_menu_choice("Main Menu", main_menu_options)
        
        if choice == 0:  # Add Transaction
            print("\n--- Add New Transaction ---")
            '''
            # Get next available ID
            if PersonalFinance.transactions:
                next_id = max(int(t['ID']) for t in PersonalFinance.transactions) + 1
                print(f"Next transaction ID will be: {next_id}")
                use_auto_id = PersonalFinance.get_yes_no("Use automatic ID?")
                if use_auto_id:
                    transaction_id = next_id
                else:
                    transaction_id = PersonalFinance.get_transaction_id("Enter transaction ID: ")
            else:
                transaction_id = PersonalFinance.get_transaction_id("Enter transaction ID: ")
            '''
            # Create new transaction
            new_transaction = {
                "ID": len(PersonalFinance.transactions) + 1,  # Auto-increment ID
                "Amount": PersonalFinance.get_amount("Enter transaction amount: $"),
                "Description": PersonalFinance.get_description("Enter description: "),
                "Category": PersonalFinance.get_category(),
                "Date": PersonalFinance.get_date().strftime('%Y-%m-%d')
            }
            
            # Add to transactions list
            PersonalFinance.transactions.append(new_transaction)
            print(f"\n✓ Transaction added successfully!")
            print(f"Amount: ${new_transaction['Amount']:.2f}")
            
        elif choice == 1:  # View Transactions
            PersonalFinance.display_transactions()
            
        elif choice == 2:  # Search Transactions (placeholder)
            print("\nSearch functionality coming soon!")
            
        elif choice == 3:  # Exit
            print("\nSaving transactions before exit...")
            if PersonalFinance.save_transactions_to_csv():
                print("✓ All transactions saved successfully!")
            else:
                print("✗ Error saving transactions!")
                if not PersonalFinance.get_yes_no("Exit anyway?"):
                    continue
            
            print("Thank you for using Personal Finance Tracker!")
            sys.exit(0)

if __name__ == "__main__":
    main()