#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTP (One-Time Password) Management
"""

import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path


class OTPManager:
    """OTP management class"""
    
    def __init__(self, otp_dir=None):
        if otp_dir is None:
            otp_dir = Path(__file__).parent.parent / "data"
        self.otp_dir = Path(otp_dir)
        self.otp_dir.mkdir(exist_ok=True)
        self.otp_file = self.otp_dir / "otp_storage.json"
        self.temp_file = self.otp_dir / "temp_data.json"
        self.otp_expiry_minutes = 5
    
    def _read_otp_data(self):
        """Read OTP data"""
        if not self.otp_file.exists():
            return {}
        try:
            with open(self.otp_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _write_otp_data(self, data):
        """Write OTP data"""
        with open(self.otp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _read_temp_data(self):
        """Read temporary data"""
        if not self.temp_file.exists():
            return {}
        try:
            with open(self.temp_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _write_temp_data(self, data):
        """Write temporary data"""
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_otp(self, identifier):
        """Generate OTP code"""
        # Generate 6-digit code
        otp_code = str(secrets.randbelow(900000) + 100000)
        
        data = self._read_otp_data()
        
        expires_at = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        
        data[identifier] = {
            'code': otp_code,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat()
        }
        
        self._write_otp_data(data)
        
        return otp_code
    
    def verify_otp(self, identifier, otp_code):
        """Verify OTP code"""
        data = self._read_otp_data()
        
        if identifier not in data:
            return False
        
        otp_data = data[identifier]
        
        # Check expiration
        expires_at = datetime.fromisoformat(otp_data['expires_at'])
        if datetime.now() > expires_at:
            del data[identifier]
            self._write_otp_data(data)
            return False
        
        # Check code
        if otp_data['code'] != otp_code:
            # Wrong code - don't delete OTP yet, user might want to try again
            return False
        
        # Code is correct - delete OTP immediately to prevent reuse
        del data[identifier]
        self._write_otp_data(data)
        return True
    
    def delete_otp(self, identifier):
        """Delete OTP"""
        data = self._read_otp_data()
        if identifier in data:
            del data[identifier]
            self._write_otp_data(data)
    
    def save_temp_registration(self, identifier, temp_data):
        """Save temporary registration data"""
        data = self._read_temp_data()
        if 'registrations' not in data:
            data['registrations'] = {}
        data['registrations'][identifier] = temp_data
        self._write_temp_data(data)
    
    def get_temp_registration(self, identifier):
        """Get temporary registration data"""
        data = self._read_temp_data()
        return data.get('registrations', {}).get(identifier)
    
    def delete_temp_registration(self, identifier):
        """Delete temporary registration data"""
        data = self._read_temp_data()
        if 'registrations' in data and identifier in data['registrations']:
            del data['registrations'][identifier]
            self._write_temp_data(data)
    
    def save_temp_login(self, identifier, user_id):
        """Save temporary login data"""
        data = self._read_temp_data()
        if 'logins' not in data:
            data['logins'] = {}
        data['logins'][identifier] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat()
        }
        self._write_temp_data(data)
    
    def get_temp_login(self, identifier):
        """Get temporary login data"""
        data = self._read_temp_data()
        login_data = data.get('logins', {}).get(identifier)
        return login_data.get('user_id') if login_data else None
    
    def delete_temp_login(self, identifier):
        """Delete temporary login data"""
        data = self._read_temp_data()
        if 'logins' in data and identifier in data['logins']:
            del data['logins'][identifier]
            self._write_temp_data(data)
    
    def cleanup_expired_otps(self):
        """Cleanup expired OTPs"""
        data = self._read_otp_data()
        now = datetime.now()
        expired_identifiers = []
        
        for identifier, otp_data in data.items():
            expires_at = datetime.fromisoformat(otp_data['expires_at'])
            if now > expires_at:
                expired_identifiers.append(identifier)
        
        for identifier in expired_identifiers:
            del data[identifier]
        
        if expired_identifiers:
            self._write_otp_data(data)
