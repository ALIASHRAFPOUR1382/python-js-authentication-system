#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test email configuration and sending
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from email_sender import EmailSender

def test_email():
    """Test email configuration and sending"""
    print("=" * 60)
    print("Email Configuration Test")
    print("=" * 60)
    print()
    
    email_sender = EmailSender()
    
    # Check configuration
    print("1. Checking email configuration...")
    config = email_sender.config
    
    if not config.get("email"):
        print("❌ Email address is not configured")
        print("   Please set 'email' in email_config.json")
        return False
    
    if not config.get("password"):
        print("❌ Email password is not configured")
        print("   Please set 'password' in email_config.json")
        return False
    
    print(f"✅ Email: {config.get('email')}")
    print(f"✅ SMTP Server: {config.get('smtp_server')}")
    print(f"✅ SMTP Port: {config.get('smtp_port')}")
    print()
    
    # Test connection
    print("2. Testing SMTP connection...")
    success, message = email_sender.test_connection()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        print()
        print("Common issues:")
        print("- For Gmail: Make sure 2-Step Verification is enabled")
        print("- For Gmail: Use App Password, not your regular password")
        print("- Check your email and password in email_config.json")
        print("- Check your internet connection")
        return False
    
    print()
    
    # Test sending email
    print("3. Testing email sending...")
    test_email = input("Enter your email address to receive test OTP: ").strip()
    
    if not test_email:
        print("❌ No email address provided")
        return False
    
    test_otp = "123456"
    print(f"Sending test OTP ({test_otp}) to {test_email}...")
    
    email_sent = email_sender.send_otp_email(
        to_email=test_email,
        otp_code=test_otp,
        name="Test User"
    )
    
    if email_sent:
        print(f"✅ Test email sent successfully to {test_email}")
        print("   Please check your inbox (and spam folder)")
        return True
    else:
        print(f"❌ Failed to send test email")
        print("   Check the error messages above")
        return False

if __name__ == "__main__":
    try:
        test_email()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

