#!/usr/bin/env python3
"""
Password Security Analyzer & Manager - Basic Version
Uses only Python built-in libraries - no external dependencies!

This version focuses on:
1. Password strength analysis
2. Basic secure storage (simple encryption)
3. Foundation for adding external libraries later
"""

import re
import json
import os
import getpass
import hashlib
import base64
import secrets
import string
from datetime import datetime

class PasswordAnalyzer:
    """Analyzes password strength using built-in Python only."""
    
    def __init__(self):
        # Common passwords list (you can expand this)
        self.common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', '1234567890',
            'monkey', 'dragon', 'pass', 'mustang', 'master'
        }
    
    def analyze_strength(self, password):
        """Analyze password strength and return detailed results."""
        score = 0
        feedback = []
        
        # Length scoring
        length = len(password)
        if length >= 16:
            score += 30
        elif length >= 12:
            score += 25
        elif length >= 8:
            score += 15
            feedback.append("Consider using a longer password (12+ characters)")
        else:
            feedback.append("Password is too short (minimum 8 characters)")
        
        # Character variety checks
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        if has_lower:
            score += 10
        else:
            feedback.append("Add lowercase letters")
            
        if has_upper:
            score += 10
        else:
            feedback.append("Add uppercase letters")
            
        if has_digit:
            score += 10
        else:
            feedback.append("Add numbers")
            
        if has_special:
            score += 15
        else:
            feedback.append("Add special characters (!@#$%^&*)")
        
        # Character variety bonus
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        if char_types >= 3:
            score += 10
        
        # Pattern checks
        if not re.search(r'(.)\1{2,}', password):  # No 3+ repeated chars
            score += 5
        else:
            feedback.append("Avoid repeating characters (aaa, 111)")
            
        if not re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            score += 5
        else:
            feedback.append("Avoid sequential numbers")
            
        if not re.search(r'(abc|bcd|cde|def|efg|fgh)', password.lower()):
            score += 5
        else:
            feedback.append("Avoid sequential letters")
        
        # Dictionary word check (simple)
        if password.lower() not in self.common_passwords:
            score += 10
        else:
            feedback.append("This is a commonly used password - avoid it!")
            score = min(score, 25)  # Cap score for common passwords
        
        # Determine strength level
        if score >= 85:
            strength = "Excellent"
        elif score >= 70:
            strength = "Very Strong"
        elif score >= 55:
            strength = "Strong"
        elif score >= 40:
            strength = "Moderate"
        elif score >= 25:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback,
            'length': length,
            'char_types': char_types
        }

class PasswordGenerator:
    """Generate strong passwords using built-in secrets module."""
    
    def generate_password(self, length=16, use_symbols=True):
        """Generate a cryptographically strong random password."""
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*(),.?\":{}|<>" if use_symbols else ""
        
        # Ensure at least one character from each type
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits)
        ]
        
        if use_symbols:
            password.append(secrets.choice(symbols))
        
        # Fill remaining length with random choices from all characters
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def generate_passphrase(self, num_words=4):
        """Generate a memorable passphrase."""
        # Simple word list (you could expand this)
        words = [
            'apple', 'banana', 'orange', 'grape', 'cherry', 'melon', 'peach',
            'ocean', 'mountain', 'forest', 'river', 'desert', 'valley', 'beach',
            'castle', 'bridge', 'tower', 'garden', 'window', 'candle', 'mirror',
            'silver', 'golden', 'purple', 'crimson', 'azure', 'emerald', 'amber'
        ]
        
        chosen_words = [secrets.choice(words) for _ in range(num_words)]
        # Capitalize random words and add numbers/symbols
        passphrase = []
        for word in chosen_words:
            if secrets.randbelow(2):  # 50% chance to capitalize
                word = word.capitalize()
            passphrase.append(word)
        
        # Add a random number
        passphrase.append(str(secrets.randbelow(100)))
        
        return '-'.join(passphrase)

class SimpleStorage:
    """Basic password storage using built-in libraries."""
    
    def __init__(self, master_password):
        self.storage_file = "passwords.json"
        self.master_key = self._create_key(master_password)
    
    def _create_key(self, password):
        """Create a simple key from master password (basic demo only)."""
        # This is a simplified approach - in production use proper key derivation
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _simple_encrypt(self, text, key):
        """Simple XOR encryption (for demo - not production ready)."""
        key_bytes = key.encode()
        text_bytes = text.encode()
        encrypted = []
        
        for i, char in enumerate(text_bytes):
            key_char = key_bytes[i % len(key_bytes)]
            encrypted.append(char ^ key_char)
        
        return base64.b64encode(bytes(encrypted)).decode()
    
    def _simple_decrypt(self, encrypted_text, key):
        """Simple XOR decryption."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode())
            key_bytes = key.encode()
            decrypted = []
            
            for i, char in enumerate(encrypted_bytes):
                key_char = key_bytes[i % len(key_bytes)]
                decrypted.append(char ^ key_char)
            
            return bytes(decrypted).decode()
        except:
            return None
    
    def save_password(self, service, username, password, notes=""):
        """Save a password entry."""
        try:
            # Load existing data
            data = self.load_all_passwords()
            
            # Create new entry
            entry = {
                'username': username,
                'password': self._simple_encrypt(password, self.master_key),
                'notes': notes,
                'created': datetime.now().isoformat(),
                'modified': datetime.now().isoformat()
            }
            
            data[service] = entry
            
            # Save to file
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving password: {e}")
            return False
    
    def load_all_passwords(self):
        """Load all stored passwords."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def get_password(self, service):
        """Retrieve password for a service."""
        data = self.load_all_passwords()
        entry = data.get(service)
        
        if entry:
            # Decrypt password
            decrypted_password = self._simple_decrypt(entry['password'], self.master_key)
            if decrypted_password:
                entry_copy = entry.copy()
                entry_copy['password'] = decrypted_password
                return entry_copy
        
        return None
    
    def list_services(self):
        """List all stored services."""
        data = self.load_all_passwords()
        return list(data.keys())
    
    def delete_password(self, service):
        """Delete a password entry."""
        try:
            data = self.load_all_passwords()
            if service in data:
                del data[service]
                with open(self.storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
                return True
            return False
        except:
            return False

def main():
    """Main application interface."""
    print("🔐 Password Security Analyzer & Manager (Basic Version)")
    print("=" * 60)
    print("📌 Uses only built-in Python libraries - no external dependencies!")
    print()
    
    analyzer = PasswordAnalyzer()
    generator = PasswordGenerator()
    
    while True:
        print("\n📋 Main Menu:")
        print("1. Analyze password strength")
        print("2. Generate strong password")
        print("3. Generate passphrase")
        print("4. Store password securely")
        print("5. Retrieve stored password")
        print("6. List stored services")
        print("7. Delete stored password")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            password = getpass.getpass("Enter password to analyze: ")
            if not password:
                print("❌ No password entered")
                continue
                
            result = analyzer.analyze_strength(password)
            
            print(f"\n📊 Password Analysis Results:")
            print(f"Strength: {result['strength']} (Score: {result['score']}/100)")
            print(f"Length: {result['length']} characters")
            print(f"Character types used: {result['char_types']}/4")
            
            if result['feedback']:
                print("\n💡 Suggestions for improvement:")
                for suggestion in result['feedback']:
                    print(f"  • {suggestion}")
        
        elif choice == '2':
            try:
                length = int(input("Password length (default 16): ") or "16")
                use_symbols = input("Include symbols? (y/n, default y): ").lower() != 'n'
                
                password = generator.generate_password(length, use_symbols)
                print(f"\n🔑 Generated Password: {password}")
                
                # Auto-analyze the generated password
                result = analyzer.analyze_strength(password)
                print(f"Strength: {result['strength']} (Score: {result['score']}/100)")
                
            except ValueError:
                print("❌ Invalid length entered")
        
        elif choice == '3':
            try:
                num_words = int(input("Number of words (default 4): ") or "4")
                passphrase = generator.generate_passphrase(num_words)
                print(f"\n🔑 Generated Passphrase: {passphrase}")
                
                # Auto-analyze the passphrase
                result = analyzer.analyze_strength(passphrase)
                print(f"Strength: {result['strength']} (Score: {result['score']}/100)")
                
            except ValueError:
                print("❌ Invalid number entered")
        
        elif choice == '4':
            master_password = getpass.getpass("Enter master password for storage: ")
            if not master_password:
                print("❌ Master password required")
                continue
                
            storage = SimpleStorage(master_password)
            
            service = input("Service/Website name: ").strip()
            username = input("Username/Email: ").strip()
            password = getpass.getpass("Password to store: ")
            notes = input("Notes (optional): ").strip()
            
            if service and username and password:
                if storage.save_password(service, username, password, notes):
                    print("✅ Password saved successfully!")
                else:
                    print("❌ Failed to save password")
            else:
                print("❌ Service, username, and password are required")
        
        elif choice == '5':
            master_password = getpass.getpass("Enter master password: ")
            if not master_password:
                continue
                
            storage = SimpleStorage(master_password)
            
            services = storage.list_services()
            if not services:
                print("❌ No passwords stored yet")
                continue
            
            print("\nStored services:")
            for i, service in enumerate(services, 1):
                print(f"{i}. {service}")
            
            try:
                choice_idx = int(input("\nSelect service number: ")) - 1
                if 0 <= choice_idx < len(services):
                    service = services[choice_idx]
                    entry = storage.get_password(service)
                    
                    if entry:
                        print(f"\n📋 Password for {service}:")
                        print(f"Username: {entry['username']}")
                        print(f"Password: {entry['password']}")
                        if entry.get('notes'):
                            print(f"Notes: {entry['notes']}")
                        print(f"Created: {entry['created']}")
                    else:
                        print("❌ Could not decrypt password (wrong master password?)")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid number entered")
        
        elif choice == '6':
            master_password = getpass.getpass("Enter master password: ")
            if not master_password:
                continue
                
            storage = SimpleStorage(master_password)
            services = storage.list_services()
            
            if services:
                print(f"\n📋 Stored services ({len(services)}):")
                for i, service in enumerate(services, 1):
                    print(f"{i}. {service}")
            else:
                print("❌ No passwords stored yet")
        
        elif choice == '7':
            master_password = getpass.getpass("Enter master password: ")
            if not master_password:
                continue
                
            storage = SimpleStorage(master_password)
            services = storage.list_services()
            
            if not services:
                print("❌ No passwords stored")
                continue
            
            print("\nStored services:")
            for i, service in enumerate(services, 1):
                print(f"{i}. {service}")
            
            try:
                choice_idx = int(input("\nSelect service to delete: ")) - 1
                if 0 <= choice_idx < len(services):
                    service = services[choice_idx]
                    confirm = input(f"Delete password for '{service}'? (y/N): ")
                    if confirm.lower() == 'y':
                        if storage.delete_password(service):
                            print("✅ Password deleted successfully!")
                        else:
                            print("❌ Failed to delete password")
                    else:
                        print("Deletion cancelled")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid number entered")
        
        elif choice == '8':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()