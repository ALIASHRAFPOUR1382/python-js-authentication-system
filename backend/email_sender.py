#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email sending module
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import json
from pathlib import Path


class EmailSender:
    """Email sending class"""
    
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = Path(__file__).parent.parent / "email_config.json"
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self):
        """Load email configuration"""
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "use_tls": True,
            "email": "",
            "password": "",
            "from_name": "Authentication System"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                print(f"✅ Email configuration loaded from {self.config_file}")
            except Exception as e:
                print(f"❌ Error reading email configuration: {e}")
                print("Using default configuration")
        else:
            print(f"⚠️  Email configuration file not found: {self.config_file}")
            print("   Email sending will be disabled. OTP will be displayed in console only.")
            print("   To enable email sending, create email_config.json file.")
        
        return default_config
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def send_otp_email(self, to_email, otp_code, name=None):
        """Send OTP code to email"""
        # Always print OTP to console for debugging
        print(f"\n{'='*60}")
        print(f"[OTP CODE for {to_email}]")
        print(f"Code: {otp_code}")
        print(f"{'='*60}\n")
        
        if not self.config.get("email") or not self.config.get("password"):
            print("⚠️  Email configuration is incomplete!")
            print("⚠️  Please configure email_config.json file with your email settings.")
            print("⚠️  OTP is displayed in console only. Email not sent.")
            print(f"⚠️  To receive OTP via email, configure: {self.config_file}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{Header(self.config['from_name'], 'utf-8')} <{self.config['email']}>"
            msg['To'] = to_email
            msg['Subject'] = Header('Login Verification Code', 'utf-8')
            
            # Email content
            greeting = f"Hello {name}," if name else "Hello,"
            
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="fa">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        direction: rtl;
                        background-color: #f5f5f5;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px 10px 0 0;
                        text-align: center;
                        margin: -30px -30px 30px -30px;
                    }}
                    .otp-code {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        font-size: 32px;
                        font-weight: bold;
                        text-align: center;
                        padding: 20px;
                        border-radius: 10px;
                        letter-spacing: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        text-align: center;
                        color: #666;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Login Verification Code</h1>
                    </div>
                    <p>{greeting}</p>
                    <p>Your verification code for login:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p>This code is valid for 5 minutes.</p>
                    <p>If you did not make this request, please ignore this email.</p>
                    <div class="footer">
                        <p>This is an automated email. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Hello {name if name else 'User'},

Your verification code for login:

{otp_code}

This code is valid for 5 minutes.

If you did not make this request, please ignore this email.

---
This is an automated email. Please do not reply to this email.
            """
            
            # Add content
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Connect to SMTP server and send
            print(f"Connecting to SMTP server: {self.config['smtp_server']}:{self.config['smtp_port']}")
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.set_debuglevel(1)  # Enable debug output
            
            if self.config.get('use_tls'):
                print("Starting TLS...")
                server.starttls()
            
            print(f"Logging in as: {self.config['email']}")
            server.login(self.config['email'], self.config['password'])
            print("Login successful")
            
            print(f"Sending email to: {to_email}")
            server.send_message(msg)
            server.quit()
            print("Email sent successfully")
            
            print(f"✅ OTP email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print("❌ SMTP Authentication Error!")
            print("   Error: Username and Password not accepted")
            print("   This usually means:")
            print("   1. You're using your regular Gmail password (WRONG!)")
            print("   2. You need to use App Password instead")
            print("   3. Make sure 2-Step Verification is enabled in your Google account")
            print("   4. Generate App Password from: https://myaccount.google.com/apppasswords")
            print(f"   Full error: {e}")
            print(f"\n[OTP for {to_email}]: {otp_code}")
            print("   OTP is displayed in console. Email not sent.")
            return False
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            print(f"[OTP for {to_email}]: {otp_code}")
            return False
    
    def test_connection(self):
        """Test SMTP server connection"""
        if not self.config.get("email") or not self.config.get("password"):
            return False, "Email configuration is incomplete"
        
        try:
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            if self.config.get('use_tls'):
                server.starttls()
            server.login(self.config['email'], self.config['password'])
            server.quit()
            return True, "Connection successful"
        except Exception as e:
            return False, f"Error: {str(e)}"


def create_email_config_template():
    """Create configuration template file"""
    template = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "use_tls": True,
        "email": "your-email@gmail.com",
        "password": "your-app-password",
        "from_name": "Authentication System"
    }
    
    config_file = Path(__file__).parent.parent / "email_config.json"
    
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"✅ Configuration template file created at {config_file}")
        print("Please enter your email information in this file.")
    else:
        print("Configuration file already exists.")

