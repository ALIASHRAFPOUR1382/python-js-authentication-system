#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Database Management
"""

import json
import os
from datetime import datetime
from pathlib import Path


class Database:
    """Database management class"""
    
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists"""
        if not self.db_path.exists():
            self._write_data({'users': [], 'sessions': {}})
    
    def _read_data(self):
        """Read data from file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'users': [], 'sessions': {}}
    
    def _write_data(self, data):
        """Write data to file"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_user(self, first_name, last_name, email=None, phone=None):
        """Create new user"""
        data = self._read_data()
        
        # Generate unique ID
        user_id = str(len(data['users']) + 1)
        
        user = {
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['users'].append(user)
        self._write_data(data)
        
        return user
    
    def get_user(self, email=None, phone=None, user_id=None):
        """Get user"""
        data = self._read_data()
        
        for user in data['users']:
            if user_id and user['id'] == user_id:
                return user
            if email and user.get('email') == email:
                return user
            if phone and user.get('phone') == phone:
                return user
        
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.get_user(user_id=user_id)
    
    def user_exists(self, email=None, phone=None):
        """Check if user exists"""
        return self.get_user(email=email, phone=phone) is not None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        data = self._read_data()
        
        for user in data['users']:
            if user['id'] == user_id:
                for key, value in kwargs.items():
                    if value is not None:
                        user[key] = value
                user['updated_at'] = datetime.now().isoformat()
                self._write_data(data)
                return user
        
        return None
