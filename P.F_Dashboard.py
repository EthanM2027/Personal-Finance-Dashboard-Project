#!/usr/bin/env python3
"""
User Input Helper Functions for Personal Finance Tracker
These functions handle user input with validation and error handling.
"""

import csv          # For reading/writing CSV files
import datetime     # For handling dates and times
import os           # For file system operations
import sys          # For system operations and exit codes
from typing import List, Optional, Dict  # For type hints (Python 3.5+)


class PersonalFinance:
    """Helper class for getting validated user input"""
    transactions = []  # List to store transactions in memory
    
    CATEGORIES = [      # Predefined expense categories
        "Food & Dining",
        "Transportation", 
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Travel",
        "Education",
        "Other"
    ]
    
    @staticmethod
    def get_amount(prompt="Enter amount: $") -> float:  #This gets the value ammount in 1.00 format or 1,000.00 format
        """Get a valid monetary amount from user"""
        while True:
            try:
                amount_str = input(prompt).replace('$', '').replace(',', '')
                amount = float(amount_str)
                if amount <= 0:
                    print("Amount must be greater than 0")
                    continue
                return round(amount, 2)  # Round to 2 decimal places
            except ValueError:
                print("Please enter a valid number (e.g., 25.50)")
    
    @staticmethod
    def get_description(prompt="Enter description: ") -> str:   #This gets the description of the transaction while ensuring it is not empty
        """Get transaction description"""
        while True:
            description = input(prompt).strip()
            if description:
                return description
            print("Description cannot be empty")
    
    @staticmethod
    def get_category() -> str:  #This gets the category from a predefined list
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
    
    @staticmethod   #This gets the date of the transaction and allows for multiple formats
    def get_date(prompt="Enter date (YYYY-MM-DD) or press Enter for today: ") -> datetime:
        """Get date input with validation"""
        while True:
            date_input = input(prompt).strip()
            
            if not date_input:  # Empty = today
                return datetime.datetime.now()      #have to go into datetime then datetime again to get now()
            
            # Try different date formats
            date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_input, fmt)
                except ValueError:
                    continue
            
            print("Invalid date format. Try: YYYY-MM-DD, MM/DD/YYYY, or MM-DD-YYYY")
    
    @staticmethod
    def get_yes_no(prompt) -> bool: #This gets a yes or no answer from the user
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
    def get_menu_choice(title: str, options: List[str]) -> int: #This displays a menu and gets the user's choice
        """Display menu and get user choice"""
        print(f"\n{title}")
        print("=" * len(title))
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(input("\nEnter your choice: "))
                if 1 <= choice <= len(options):
                    return choice - 1  # Return 0-based index
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
    def get_search_term(prompt="Enter search term: ") -> str:   #Gets a search term from the user
        """Get search term (can be empty)"""
        return input(prompt).strip()
    
    @staticmethod
    def get_transaction_id(prompt="Enter transaction ID: ") -> int: #This gets a transaction ID and ensures it is a positive integer
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
    def clear_screen(): #This clears the terminal screen
        """Clear the terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

# Example usage and testing
def main():
    """Demonstrate all input functions"""
    pFinance = PersonalFinance()
    print("=== Finance Tracker Input Demo ===\n")
    
    while True:
        transactions = {
            "ID": PersonalFinance.get_transaction_id("Enter transaction ID: "),
            "Amount": PersonalFinance.get_amount("Enter transaction amount: $"),
            "Description": PersonalFinance.get_description("Enter description: "),
            "Category": PersonalFinance.get_category(),
            "Date": PersonalFinance.get_date().strftime('%Y-%m-%d')
        }
        PersonalFinance.transactions.append(transactions)
        print(f"\nTransaction added: {transactions}\n")
        if not pFinance.get_yes_no("Add another transaction?"):
            break
    print("\nAll Transactions:")
    for t in PersonalFinance.transactions:
        print(t)    

    with open("transactions.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID","Amount", "Description", "Category", "Date"])
        writer.writeheader()  # writes the header row
        writer.writerows(PersonalFinance.transactions)  # writes all transactions
        
    print("\nTransactions saved to transactions.csv")
    
    # Confirmation
    if pFinance.get_yes_no("Save this transaction?"):
        print("Transaction would be saved!")
    else:
        print("Transaction cancelled")
    
    print("\nGoodbye")
if __name__ == "__main__":
    main()