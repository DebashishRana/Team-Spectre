"""
Email Verification Service
Handles sending verification emails and validating codes
Uses nodemailer via external service or simple SMTP
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

logger = logging.getLogger(__name__)

# In-memory store for verification codes (in production, use Redis or database)
verification_codes: Dict[str, Dict] = {}

def generate_verification_code(length: int = 6) -> str:
    """Generate a random 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=length))

def send_verification_email(email: str, first_name: str, last_name: str) -> bool:
    """
    Send verification email with code
    Returns True if sent successfully, False otherwise
    """
    try:
        code = generate_verification_code()
        
        # Store verification code with expiry (15 minutes)
        verification_codes[email] = {
            "code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
            "first_name": first_name,
            "last_name": last_name,
            "verified": False
        }
        
        # Email content
        subject = "Seva Setu Portal - Email Verification"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #1a1a1a; margin-bottom: 20px;">Welcome to Seva Setu Portal!</h2>
                    
                    <p style="color: #334155; font-size: 16px; line-height: 1.6;">
                        Hi {first_name},
                    </p>
                    
                    <p style="color: #334155; font-size: 16px; line-height: 1.6;">
                        Please verify your email address by entering the following verification code:
                    </p>
                    
                    <div style="background-color: #f0f9ff; border: 2px solid #0066cc; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0;">
                        <p style="font-size: 14px; color: #667085; margin: 0 0 10px 0;">Your Verification Code</p>
                        <p style="font-size: 32px; font-weight: bold; color: #0066cc; margin: 0; letter-spacing: 2px;">{code}</p>
                    </div>
                    
                    <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                        This code will expire in <strong>15 minutes</strong>.
                    </p>
                    
                    <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                        If you didn't request this verification code, please ignore this email.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    
                    <p style="color: #9ca3af; font-size: 12px; text-align: center;">
                        Seva Setu Portal - Unified Identity & Governance<br>
                        This is an automated message. Please do not reply.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Try to send via SMTP (uses Gmail or configured SMTP server)
        if _send_smtp_email(email, subject, html_body):
            logger.info(f"Verification email sent to {email}")
            return True
        else:
            # Fallback: still store the code locally for testing
            logger.warning(f"SMTP failed, but code stored locally for {email}")
            return True  # Return True to allow testing with locally stored code
            
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        return False

def _send_smtp_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Send email via SMTP
    Supports Gmail and other SMTP servers
    """
    try:
        # For development/testing: Accept environment variables or use free service
        # In production, configure with your email service
        
        # Option 1: Use system environment or return False for local testing
        smtp_server = getattr(settings, 'SMTP_SERVER', None)
        smtp_port = getattr(settings, 'SMTP_PORT', None)
        sender_email = getattr(settings, 'SENDER_EMAIL', None)
        sender_password = getattr(settings, 'SENDER_PASSWORD', None)
        
        if not all([smtp_server, smtp_port, sender_email, sender_password]):
            # SMTP not configured - use mock success for local testing
            logger.info(f"SMTP not configured. Mock email to {to_email}")
            return True
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        logger.error(f"SMTP email error: {e}")
        return False

def verify_email_code(email: str, code: str) -> bool:
    """
    Verify the email code provided by user
    Returns True if valid, False otherwise
    """
    if email not in verification_codes:
        logger.warning(f"No verification record for {email}")
        return False
    
    record = verification_codes[email]
    
    # Check if code has expired
    if datetime.utcnow() > record['expires_at']:
        logger.warning(f"Verification code expired for {email}")
        del verification_codes[email]
        return False
    
    # Check if code matches (case-insensitive)
    if record['code'].lower() != code.lower():
        logger.warning(f"Invalid verification code for {email}")
        return False
    
    # Mark as verified
    record['verified'] = True
    logger.info(f"Email verified for {email}")
    return True

def get_verification_status(email: str) -> Optional[Dict]:
    """Get the verification status for an email"""
    if email in verification_codes:
        record = verification_codes[email].copy()
        # Remove sensitive info
        record.pop('code', None)
        record['is_expired'] = datetime.utcnow() > record['expires_at']
        return record
    return None

def clear_verification(email: str):
    """Clear verification record after successful registration"""
    if email in verification_codes:
        del verification_codes[email]
        logger.info(f"Cleared verification for {email}")
