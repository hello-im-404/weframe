#!/usr/bin/env python3

import os
import sys
from typing import List, Optional

class PasswordPolicy:
    
    def __init__(self):
        self._length: Optional[int] = None
        self._require_upper: bool = False
        self._require_special: bool = False
        self._require_nums: bool = False
        self._special_chars: List[str] = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "{", "}", "'", "№", "?"]
    
    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _get_boolean_input(self, prompt: str) -> bool:
        while True:
            response = input(prompt).lower()
            if response in ('y', 'yes', ''):
                return True
            elif response in ('n', 'no'):
                return False
            print("Please enter Y or N")
    
    def _get_positive_int_input(self, prompt: str) -> int:
        while True:
            try:
                value = int(input(prompt))
                if value > 0:
                    return value
                print("Length must be a positive number")
            except ValueError:
                print("Please enter an integer")
    
    def configure_policy(self) -> None:
        print("=== Password Policy Configuration ===")
        
        self._length = self._get_positive_int_input("Enter minimum password length\n> ")
        self._require_upper = self._get_boolean_input("Require uppercase letters? [Y/n]\n> ")
        self._require_special = self._get_boolean_input("Require special characters? [Y/n]\n> ")
        self._require_nums = self._get_boolean_input("Require numbers? [Y/n]\n> ")
    
    def analyze_password(self, password: str) -> bool:
        issues = []
        
        if len(password) < self._length:
            issues.append(f"Password length ({len(password)}) is less than required ({self._length})")
        
        if self._require_upper and not any(c.isupper() for c in password):
            issues.append("Missing uppercase letters")
        
        if self._require_special and not any(c in self._special_chars for c in password):
            issues.append("Missing special characters")
        
        if self._require_nums and not any(c.isdigit() for c in password):
            issues.append("Missing numbers")
        
        if issues:
            print(f"Password '{password}' does not meet policy requirements:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"Password '{password}' meets policy requirements")
            return True
    
    def analyze_single_password(self) -> None:
        password = input("Enter password for analysis\n> ")
        self.analyze_password(password)
    
    def analyze_wordlist(self) -> None:
        list_path = input("Enter path to wordlist\n> ")
        
        if not os.path.isfile(list_path):
            print("[!] File not found")
            return
        
        valid_passwords = 0
        total_passwords = 0
        
        try:
            with open(list_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    password = line.strip()
                    if password:
                        total_passwords += 1
                        if self.analyze_password(password):
                            valid_passwords += 1
                        
                        if total_passwords % 100 == 0:
                            print(f"Processed {total_passwords} passwords...")
            
            print(f"\n=== Analysis Results ===")
            print(f"Total passwords: {total_passwords}")
            print(f"Valid passwords: {valid_passwords}")
            print(f"Invalid passwords: {total_passwords - valid_passwords}")
            
        except Exception as e:
            print(f"[!] Error reading file: {e}")
    
    def run_analysis(self) -> None:
        while True:
            print("\n=== Select Analysis Type ===")
            print("1 - Analyze wordlist")
            print("2 - Analyze single password")
            print("3 - Exit")
            
            choice = input("> ").strip()
            
            if choice == '1':
                self.analyze_wordlist()
            elif choice == '2':
                self.analyze_single_password()
            elif choice == '3':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter 1, 2 or 3")

def main():
    policy = PasswordPolicy()
    policy.clear_screen()
    
    try:
        policy.configure_policy()
        
        policy.run_analysis()
        
    except KeyboardInterrupt:
        print("\n\nExecution stopped by user")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")

if __name__ == '__main__':
    main()
