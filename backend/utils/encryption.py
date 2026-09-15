"""
Encryption utilities for sensitive data
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class EncryptionManager:
    """Manage encryption and decryption of sensitive data"""
    
    def __init__(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise RuntimeError('ENCRYPTION_KEY must be configured')
        # Ensure key is 32 bytes for Fernet
        if len(key) < 32:
            key = key.ljust(32, 'x')
        elif len(key) > 32:
            key = key[:32]
        
        # Convert to base64 format for Fernet
        import base64
        key_bytes = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'x'))
        self.cipher = Fernet(key_bytes)
    
    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher.encrypt(data).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
        return self.cipher.decrypt(encrypted_data).decode('utf-8')

# Global encryption manager instance
encryption_manager = EncryptionManager()

def encrypt_sensitive_data(data):
    """Encrypt sensitive data"""
    return encryption_manager.encrypt(data)

def decrypt_sensitive_data(encrypted_data):
    """Decrypt sensitive data"""
    return encryption_manager.decrypt(encrypted_data)
