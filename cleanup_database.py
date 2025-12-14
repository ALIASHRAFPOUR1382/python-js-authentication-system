#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Cleanup Script
This script helps clean up the database for testing purposes.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"
TEMP_DATA_FILE = DATA_DIR / "temp_data.json"
OTP_STORAGE_FILE = DATA_DIR / "otp_storage.json"

def show_database():
    """Show current database contents"""
    print("\n" + "="*60)
    print("CURRENT DATABASE CONTENTS")
    print("="*60)
    
    # Show users
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = data.get('users', [])
            print(f"\n📊 Registered Users: {len(users)}")
            for user in users:
                print(f"  - ID: {user['id']}")
                print(f"    Name: {user['first_name']} {user['last_name']}")
                print(f"    Email: {user.get('email', 'N/A')}")
                print(f"    Phone: {user.get('phone', 'N/A')}")
                print(f"    Created: {user.get('created_at', 'N/A')}")
                print()
    else:
        print("\n📊 No users database found")
    
    # Show temp registrations
    if TEMP_DATA_FILE.exists():
        with open(TEMP_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            registrations = data.get('registrations', {})
            print(f"📝 Temporary Registrations: {len(registrations)}")
            for identifier, reg_data in registrations.items():
                print(f"  - {identifier}: {reg_data.get('first_name')} {reg_data.get('last_name')}")
    else:
        print("📝 No temporary data found")
    
    # Show OTPs
    if OTP_STORAGE_FILE.exists():
        with open(OTP_STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"🔐 Active OTPs: {len(data)}")
            for identifier in data.keys():
                print(f"  - {identifier}")
    else:
        print("🔐 No OTP storage found")
    
    print("="*60 + "\n")

def clear_all_users():
    """Clear all registered users"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        user_count = len(data.get('users', []))
        data['users'] = []
        data['sessions'] = {}
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleared {user_count} users from database")
    else:
        print("⚠️  No users database found")

def clear_temp_data():
    """Clear all temporary registration data"""
    if TEMP_DATA_FILE.exists():
        with open(TEMP_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        reg_count = len(data.get('registrations', {}))
        data['registrations'] = {}
        data['logins'] = {}
        
        with open(TEMP_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleared {reg_count} temporary registrations")
    else:
        print("⚠️  No temporary data file found")

def clear_otps():
    """Clear all OTPs"""
    if OTP_STORAGE_FILE.exists():
        with open(OTP_STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        otp_count = len(data)
        data = {}
        
        with open(OTP_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cleared {otp_count} OTPs")
    else:
        print("⚠️  No OTP storage file found")

def clear_all():
    """Clear everything"""
    clear_all_users()
    clear_temp_data()
    clear_otps()
    print("\n✅ All data cleared!")

def delete_user_by_email(email):
    """Delete a specific user by email"""
    if not USERS_FILE.exists():
        print("⚠️  No users database found")
        return False
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data.get('users', [])
    original_count = len(users)
    
    # Remove user
    data['users'] = [u for u in users if u.get('email') != email]
    
    # Remove sessions for deleted user
    deleted_user_ids = [u['id'] for u in users if u.get('email') == email]
    sessions = data.get('sessions', {})
    data['sessions'] = {k: v for k, v in sessions.items() if v.get('user_id') not in deleted_user_ids}
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    deleted_count = original_count - len(data['users'])
    if deleted_count > 0:
        print(f"✅ Deleted {deleted_count} user(s) with email: {email}")
        return True
    else:
        print(f"⚠️  No user found with email: {email}")
        return False

def main():
    """Main function"""
    print("\n" + "="*60)
    print("DATABASE CLEANUP TOOL")
    print("="*60)
    
    show_database()
    
    print("Options:")
    print("1. Show database contents")
    print("2. Clear all registered users")
    print("3. Clear temporary registration data")
    print("4. Clear all OTPs")
    print("5. Clear everything")
    print("6. Delete user by email")
    print("0. Exit")
    
    choice = input("\nEnter your choice: ").strip()
    
    if choice == "1":
        show_database()
    elif choice == "2":
        confirm = input("Are you sure you want to clear all users? (yes/no): ").strip().lower()
        if confirm == "yes":
            clear_all_users()
        else:
            print("Cancelled")
    elif choice == "3":
        confirm = input("Are you sure you want to clear temporary data? (yes/no): ").strip().lower()
        if confirm == "yes":
            clear_temp_data()
        else:
            print("Cancelled")
    elif choice == "4":
        confirm = input("Are you sure you want to clear all OTPs? (yes/no): ").strip().lower()
        if confirm == "yes":
            clear_otps()
        else:
            print("Cancelled")
    elif choice == "5":
        confirm = input("Are you sure you want to clear EVERYTHING? (yes/no): ").strip().lower()
        if confirm == "yes":
            clear_all()
        else:
            print("Cancelled")
    elif choice == "6":
        email = input("Enter email to delete: ").strip()
        if email:
            delete_user_by_email(email)
        else:
            print("⚠️  Email is required")
    elif choice == "0":
        print("Exiting...")
    else:
        print("⚠️  Invalid choice")
    
    print()

if __name__ == "__main__":
    main()

