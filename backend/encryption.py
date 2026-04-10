"""Encryption utilities for sensitive document fields"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os
from config import settings


class DocumentEncryption:
    def __init__(self):
        # Use a master key from environment or settings
        self.master_key = settings.ENCRYPTION_KEY or self._generate_key()
        self.cipher_suite = Fernet(self.master_key)
    
    def _generate_key(self):
        """Generate a new encryption key (for dev only)"""
        return Fernet.generate_key()
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a sensitive field"""
        if not plaintext:
            return None
        try:
            encrypted = self.cipher_suite.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt a sensitive field"""
        if not ciphertext:
            return None
        try:
            decrypted = self.cipher_suite.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# Sensitive fields to encrypt
SENSITIVE_FIELDS = {
    "id_number",  # Aadhaar
    "phone",
    "address"
}


def should_encrypt(field_name: str) -> bool:
    """Check if a field should be encrypted"""
    return field_name in SENSITIVE_FIELDS
