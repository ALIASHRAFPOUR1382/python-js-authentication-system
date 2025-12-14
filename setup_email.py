#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت راه‌اندازی تنظیمات ایمیل
"""

from backend.email_sender import create_email_config_template, EmailSender
import json
from pathlib import Path

def setup_email():
    """راه‌اندازی تنظیمات ایمیل"""
    print("=" * 50)
    print("راه‌اندازی سیستم ارسال ایمیل")
    print("=" * 50)
    print()
    
    # ایجاد فایل نمونه
    create_email_config_template()
    
    config_file = Path("email_config.json")
    
    if config_file.exists():
        print("\nلطفاً اطلاعات زیر را وارد کنید:\n")
        
        email = input("آدرس ایمیل شما (مثلاً: your-email@gmail.com): ").strip()
        password = input("رمز عبور یا App Password: ").strip()
        smtp_server = input("آدرس سرور SMTP (پیش‌فرض: smtp.gmail.com): ").strip() or "smtp.gmail.com"
        smtp_port = input("پورت SMTP (پیش‌فرض: 587): ").strip() or "587"
        from_name = input("نام فرستنده (پیش‌فرض: سیستم احراز هویت): ").strip() or "سیستم احراز هویت"
        
        config = {
            "smtp_server": smtp_server,
            "smtp_port": int(smtp_port),
            "use_tls": True,
            "email": email,
            "password": password,
            "from_name": from_name
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ تنظیمات ذخیره شد")
        print("\nدر حال تست اتصال...")
        
        email_sender = EmailSender()
        success, message = email_sender.test_connection()
        
        if success:
            print(f"✅ {message}")
            print("\nسیستم آماده ارسال ایمیل است!")
        else:
            print(f"❌ {message}")
            print("\nلطفاً تنظیمات را بررسی کنید.")
            print("\nبرای Gmail:")
            print("1. به حساب Google خود بروید")
            print("2. Security > 2-Step Verification را فعال کنید")
            print("3. App Passwords را ایجاد کنید")
            print("4. رمز عبور ایجاد شده را در تنظیمات وارد کنید")
    else:
        print("❌ خطا در ایجاد فایل تنظیمات")

if __name__ == "__main__":
    setup_email()

