#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Server for Authentication System
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from auth import AuthManager
from otp_manager import OTPManager
from email_sender import EmailSender

PORT = 8000
BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Class instances
db = Database(DATA_DIR / "users.json")
auth_manager = AuthManager(db)
otp_manager = OTPManager(DATA_DIR)
email_sender = EmailSender()


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def log_message(self, format, *args):
        """Log messages"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def _set_cors_headers(self):
        """Set CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
    
    def _send_json_response(self, data, status_code=200, cookies=None):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._set_cors_headers()
        
        # Set cookies before end_headers
        if cookies:
            for cookie in cookies:
                self.send_header('Set-Cookie', cookie)
        
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error_response(self, message, status_code=400):
        """Send error response"""
        self._send_json_response({'success': False, 'message': message}, status_code)
    
    def _send_success_response(self, data=None, message=None, cookies=None):
        """Send success response"""
        response = {'success': True}
        if data:
            response.update(data)
        if message:
            response['message'] = message
        self._send_json_response(response, cookies=cookies)
    
    def _get_post_data(self):
        """Read POST data"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {}
            post_data = self.rfile.read(content_length)
            if not post_data:
                return {}
            try:
                decoded_data = post_data.decode('utf-8')
                return json.loads(decoded_data)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Received data: {post_data[:200]}")
                return {}
            except UnicodeDecodeError as e:
                print(f"Unicode decode error: {e}")
                return {}
        except Exception as e:
            print(f"Error reading POST data: {e}")
            return {}
    
    def _set_cookie(self, name, value, max_age_days=2):
        """Set cookie - returns cookie string to be added before end_headers"""
        expires = datetime.now(timezone.utc) + timedelta(days=max_age_days)
        expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        cookie = f"{name}={value}; Path=/; Max-Age={max_age_days * 24 * 60 * 60}; Expires={expires_str}; HttpOnly; SameSite=Lax"
        return cookie
    
    def _get_cookies(self):
        """Read cookies"""
        cookies = {}
        cookie_header = self.headers.get('Cookie', '')
        if cookie_header:
            for cookie in cookie_header.split(';'):
                if '=' in cookie:
                    key, value = cookie.strip().split('=', 1)
                    cookies[key] = value
        return cookies
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path.startswith('/api/'):
            try:
                self._handle_api_get()
            except Exception as e:
                print(f"Error handling GET request: {e}")
                import traceback
                traceback.print_exc()
                self._send_error_response(f'Server error: {str(e)}', 500)
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/'):
            try:
                self._handle_api_post()
            except Exception as e:
                print(f"Error handling POST request: {e}")
                import traceback
                traceback.print_exc()
                self._send_error_response(f'Server error: {str(e)}', 500)
        else:
            self._send_error_response('Not found', 404)
    
    def _handle_api_get(self):
        """Handle API GET requests"""
        if self.path == '/api/check-auth':
            cookies = self._get_cookies()
            session_token = cookies.get('session_token')
            
            if session_token and auth_manager.validate_session(session_token):
                user = auth_manager.get_user_by_session(session_token)
                self._send_success_response({
                    'authenticated': True,
                    'user': {
                        'first_name': user.get('first_name'),
                        'last_name': user.get('last_name'),
                        'email': user.get('email'),
                        'phone': user.get('phone')
                    }
                })
            else:
                self._send_success_response({'authenticated': False})
        else:
            self._send_error_response('Endpoint not found', 404)
    
    def _handle_api_post(self):
        """Handle API POST requests"""
        if self.path == '/api/register':
            self._handle_register()
        elif self.path == '/api/verify-otp':
            self._handle_verify_otp()
        elif self.path == '/api/verify-login-otp':
            self._handle_verify_login_otp()
        elif self.path == '/api/login':
            self._handle_login()
        elif self.path == '/api/logout':
            self._handle_logout()
        else:
            self._send_error_response('Endpoint not found', 404)
    
    def _handle_register(self):
        """Handle registration"""
        try:
            data = self._get_post_data()
            
            if not data:
                self._send_error_response('Invalid request data')
                return
            
            first_name = data.get('first_name', '').strip() if data.get('first_name') else ''
            last_name = data.get('last_name', '').strip() if data.get('last_name') else ''
            email = data.get('email', '').strip() if data.get('email') else ''
            phone = data.get('phone', '').strip() if data.get('phone') else ''
            
            # Validation
            if not first_name or not last_name:
                self._send_error_response('First name and last name are required')
                return
            
            if not email and not phone:
                self._send_error_response('Email or phone number is required')
                return
            
            # Check if user exists (only check actual registered users in database)
            if email and db.user_exists(email=email):
                self._send_error_response('This email is already registered. Please login instead.')
                return
            
            if phone and db.user_exists(phone=phone):
                self._send_error_response('This phone number is already registered. Please login instead.')
                return
            
            # Generate OTP
            identifier = email if email else phone
            
            # Clean up any old temporary registration data for this identifier
            # This allows users to retry registration if they entered wrong OTP
            otp_manager.delete_temp_registration(identifier)
            
            # Generate new OTP
            otp_code = otp_manager.generate_otp(identifier)
            
            # Save temporary data (user is NOT created yet - only after OTP verification)
            temp_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email if email else None,
                'phone': phone if phone else None,
                'otp': otp_code,
                'created_at': datetime.now().isoformat()
            }
            otp_manager.save_temp_registration(identifier, temp_data)
            
            # Send OTP to email
            if email:
                # Send OTP to the email address entered by the user
                email_sent = email_sender.send_otp_email(
                    to_email=email,
                    otp_code=otp_code,
                    name=f"{first_name} {last_name}"
                )
                if email_sent:
                    print(f"✅ OTP email sent successfully to {email}")
                else:
                    print(f"⚠️  Failed to send email to {email}, OTP displayed in console")
            else:
                # If no email, just print to console
                print(f"[OTP for {identifier}]: {otp_code}")
            
            self._send_success_response(
                {'identifier': identifier},
                'Verification code sent'
            )
        except Exception as e:
            print(f"Error in register process: {e}")
            import traceback
            traceback.print_exc()
            self._send_error_response(f'Registration error: {str(e)}')
    
    def _handle_verify_otp(self):
        """Handle OTP verification"""
        try:
            data = self._get_post_data()
            
            if not data:
                self._send_error_response('Invalid request data')
                return
            
            identifier = data.get('identifier', '').strip() if data.get('identifier') else ''
            otp = data.get('otp', '').strip() if data.get('otp') else ''
            
            if not identifier or not otp:
                self._send_error_response('Identifier and OTP code are required')
                return
            
            # Verify OTP first
            if not otp_manager.verify_otp(identifier, otp):
                self._send_error_response('Invalid verification code. Please check and try again.')
                return
            
            # Get temporary data
            temp_data = otp_manager.get_temp_registration(identifier)
            if not temp_data:
                self._send_error_response('Registration data not found. Please register again.')
                return
            
            # Check if user already exists (double-check before creating)
            email = temp_data.get('email')
            phone = temp_data.get('phone')
            
            if email and db.user_exists(email=email):
                # User already registered, delete temp data and OTP
                otp_manager.delete_temp_registration(identifier)
                otp_manager.delete_otp(identifier)
                self._send_error_response('This email is already registered. Please login instead.')
                return
            
            if phone and db.user_exists(phone=phone):
                # User already registered, delete temp data and OTP
                otp_manager.delete_temp_registration(identifier)
                otp_manager.delete_otp(identifier)
                self._send_error_response('This phone number is already registered. Please login instead.')
                return
            
            # Create user only after successful OTP verification
            user = db.create_user(
                first_name=temp_data['first_name'],
                last_name=temp_data['last_name'],
                email=temp_data['email'],
                phone=temp_data['phone']
            )
            
            # Create session
            session_token = auth_manager.create_session(user['id'])
            
            # Delete temporary data (OTP already deleted in verify_otp)
            otp_manager.delete_temp_registration(identifier)
            
            # Set cookie (before sending response)
            cookie = self._set_cookie('session_token', session_token, max_age_days=2)
            
            self._send_success_response({
                'user': {
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user.get('email'),
                    'phone': user.get('phone')
                }
            }, 'Registration successful', cookies=[cookie])
        except Exception as e:
            print(f"Error in verify OTP process: {e}")
            import traceback
            traceback.print_exc()
            self._send_error_response(f'Verification error: {str(e)}')
    
    def _handle_login(self):
        """Handle login"""
        try:
            data = self._get_post_data()
            
            if not data:
                self._send_error_response('Invalid request data')
                return
            
            email = data.get('email', '').strip() if data.get('email') else ''
            phone = data.get('phone', '').strip() if data.get('phone') else ''
            
            if not email and not phone:
                self._send_error_response('Email or phone number is required')
                return
        
            identifier = email if email else phone
            
            # Check if user exists
            user = db.get_user(email=email) if email else db.get_user(phone=phone)
            if not user:
                error_msg = f'User not found. Please register first with this {"email" if email else "phone number"}.'
                self._send_error_response(error_msg)
                return
            
            # Check existing cookie - if valid and belongs to this user, allow direct login
            cookies = self._get_cookies()
            session_token = cookies.get('session_token')
            
            if session_token and auth_manager.validate_session(session_token):
                # Get user from session
                session_user = auth_manager.get_user_by_session(session_token)
                
                # Check if session belongs to the same user trying to login
                if session_user and session_user['id'] == user['id']:
                    # Cookie is valid and belongs to this user - refresh it and allow direct login
                    cookie = self._set_cookie('session_token', session_token, max_age_days=2)
                    self._send_success_response({
                        'user': {
                            'first_name': user['first_name'],
                            'last_name': user['last_name'],
                            'email': user.get('email'),
                            'phone': user.get('phone')
                        },
                        'direct_login': True
                    }, cookies=[cookie])
                    return
                # If cookie belongs to different user, continue to OTP verification
            
            # Requires re-verification
            otp_code = otp_manager.generate_otp(identifier)
            otp_manager.save_temp_login(identifier, user['id'])
            
            # Send OTP to email
            if email:
                # Send OTP to the email address entered by the user
                email_sent = email_sender.send_otp_email(
                    to_email=email,
                    otp_code=otp_code,
                    name=f"{user['first_name']} {user['last_name']}"
                )
                if email_sent:
                    print(f"✅ OTP email sent successfully to {email}")
                else:
                    print(f"⚠️  Failed to send email to {email}, OTP displayed in console")
            else:
                # If no email, just print to console
                print(f"[OTP for {identifier}]: {otp_code}")
            
            self._send_success_response(
                {'identifier': identifier, 'requires_verification': True},
                'Verification code sent'
            )
        except Exception as e:
            print(f"Error in login process: {e}")
            import traceback
            traceback.print_exc()
            self._send_error_response(f'Login error: {str(e)}')
    
    def _handle_verify_login_otp(self):
        """Handle OTP verification for login"""
        try:
            data = self._get_post_data()
            
            if not data:
                self._send_error_response('Invalid request data')
                return
            
            identifier = data.get('identifier', '').strip() if data.get('identifier') else ''
            otp = data.get('otp', '').strip() if data.get('otp') else ''
            
            if not identifier or not otp:
                self._send_error_response('Identifier and OTP code are required')
                return
            
            # Verify OTP first
            if not otp_manager.verify_otp(identifier, otp):
                self._send_error_response('Invalid verification code. Please check and try again.')
                return
            
            # Get temporary login data
            user_id = otp_manager.get_temp_login(identifier)
            if not user_id:
                self._send_error_response('Login data not found. Please try logging in again.')
                return
            
            user = db.get_user_by_id(user_id)
            if not user:
                self._send_error_response('User not found')
                return
            
            # Create session
            session_token = auth_manager.create_session(user['id'])
            
            # Delete temporary data (OTP already deleted in verify_otp)
            otp_manager.delete_temp_login(identifier)
            
            # Set cookie (before sending response)
            cookie = self._set_cookie('session_token', session_token, max_age_days=2)
            
            self._send_success_response({
                'user': {
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user.get('email'),
                    'phone': user.get('phone')
                }
            }, 'Login successful', cookies=[cookie])
        except Exception as e:
            print(f"Error in verify login OTP process: {e}")
            import traceback
            traceback.print_exc()
            self._send_error_response(f'Verification error: {str(e)}')
    
    def _handle_logout(self):
        """Handle logout"""
        cookies = self._get_cookies()
        session_token = cookies.get('session_token')
        
        if session_token:
            auth_manager.delete_session(session_token)
        
        # Delete cookie
        clear_cookie = 'session_token=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
        self._send_success_response(message='Logout successful', cookies=[clear_cookie])


def main():
    """Main function"""
    with socketserver.TCPServer(("", PORT), AuthHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            httpd.shutdown()


if __name__ == "__main__":
    main()

