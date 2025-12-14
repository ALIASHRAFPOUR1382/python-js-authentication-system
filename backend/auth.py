#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication and session management
"""

import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path


class AuthManager:
    """Authentication management class"""
    
    def __init__(self, database):
        self.db = database
        self.session_duration_days = 2
    
    def create_session(self, user_id):
        """Create new session"""
        session_token = secrets.token_urlsafe(32)
        
        data = self.db._read_data()
        if 'sessions' not in data:
            data['sessions'] = {}
        
        expires_at = datetime.now() + timedelta(days=self.session_duration_days)
        
        data['sessions'][session_token] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat()
        }
        
        self.db._write_data(data)
        
        return session_token
    
    def validate_session(self, session_token):
        """Validate session"""
        data = self.db._read_data()
        
        if 'sessions' not in data:
            return False
        
        session = data['sessions'].get(session_token)
        if not session:
            return False
        
        # Check expiration
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            # Delete expired session
            del data['sessions'][session_token]
            self.db._write_data(data)
            return False
        
        return True
    
    def get_user_by_session(self, session_token):
        """Get user by session"""
        if not self.validate_session(session_token):
            return None
        
        data = self.db._read_data()
        session = data['sessions'].get(session_token)
        if not session:
            return None
        
        user_id = session['user_id']
        return self.db.get_user_by_id(user_id)
    
    def delete_session(self, session_token):
        """Delete session"""
        data = self.db._read_data()
        
        if 'sessions' in data and session_token in data['sessions']:
            del data['sessions'][session_token]
            self.db._write_data(data)
    
    def cleanup_expired_sessions(self):
        """Cleanup expired sessions"""
        data = self.db._read_data()
        
        if 'sessions' not in data:
            return
        
        now = datetime.now()
        expired_tokens = []
        
        for token, session in data['sessions'].items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if now > expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del data['sessions'][token]
        
        if expired_tokens:
            self.db._write_data(data)
