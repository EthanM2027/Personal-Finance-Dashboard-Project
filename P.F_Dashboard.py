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


class UserInputHelper:
    """Helper class for getting validated user input"""
    
    CATEGORIES = [
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
    def get_amount(prompt="Enter amount: $") -> float:
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
        for i, category in enumerate(UserInputHelper.CATEGORIES, 1):
            print(f"{i:2d}. {category}")
        
        while True:
            try:
                choice = int(input("Enter category number: "))
                if 1 <= choice <= len(UserInputHelper.CATEGORIES):
                    return UserInputHelper.CATEGORIES[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(UserInputHelper.CATEGORIES)}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
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
                    return choice - 1  # Return 0-based index
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
    def get_search_term(prompt="Enter search term: ") -> str:
        """Get search term (can be empty)"""
        return input(prompt).strip()
    
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
    def pause_for_user():
        """Pause and wait for user to press Enter"""
        input("\nPress Enter to continue...")
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

# Example usage and testing
def demo_input_functions():
    """Demonstrate all input functions"""
    helper = UserInputHelper()
    
    print("=== Finance Tracker Input Demo ===\n")
    
    # Get transaction details
    amount = helper.get_amount("Enter transaction amount: $")
    print(f"Amount: ${amount:.2f}")
    
    description = helper.get_description("Enter description: ")
    print(f"Description: {description}")
    
    category = helper.get_category()
    print(f"Category: {category}")
    
    date = helper.get_date()
    print(f"Date: {date.strftime('%Y-%m-%d')}")
    
    # Confirmation
    if helper.get_yes_no("Save this transaction?"):
        print("Transaction would be saved!")
        
    else:
        print("Transaction cancelled")
    
    helper.pause_for_user()

if __name__ == "__main__":
    demo_input_functions()