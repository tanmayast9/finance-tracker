"""
OTP & Verification Utility Module
Handles OTP generation, sending, and verification
"""

import random
import string
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class OTPManager:
    """Manages OTP generation and verification"""
    
    @staticmethod
    def generate_otp(length=6):
        """Generate random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_email_otp(email, otp_code):
        """Send OTP via email"""
        try:
            sender_email = current_app.config.get('EMAIL_USER')
            sender_password = current_app.config.get('EMAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                print("❌ Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "🔐 Your OTP Code - Finance Tracker"
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Email Verification</h2>
                    <p>Your One-Time Password (OTP) is:</p>
                    <h1 style="color: #3498db; letter-spacing: 5px;">{otp_code}</h1>
                    <p>This OTP expires in 5 minutes.</p>
                    <p style="color: #7f8c8d; font-size: 12px;">
                        If you didn't request this, please ignore this email.
                    </p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ OTP sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email OTP: {e}")
            return False
    
    @staticmethod
    def send_sms_otp(phone_number, otp_code):
        """Send OTP via SMS using Twilio"""
        if not TWILIO_AVAILABLE:
            print("❌ Twilio not installed. Install with: pip install twilio")
            return False
        
        try:
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                print("❌ Twilio credentials not configured")
                return False
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=f"🔐 Your Finance Tracker OTP is: {otp_code}. Valid for 5 minutes.",
                from_=from_number,
                to=phone_number
            )
            
            print(f"✅ OTP sent to {phone_number}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send SMS OTP: {e}")
            return False
    
    @staticmethod
    def verify_otp(stored_otp, provided_otp, max_age_minutes=5):
        """
        Verify OTP code
        
        Args:
            stored_otp: OTP code stored in database
            provided_otp: OTP code entered by user
            max_age_minutes: Maximum age of OTP in minutes
        
        Returns:
            bool: True if OTP is valid
        """
        if stored_otp == provided_otp:
            return True
        return False


def require_otp_verified(f):
    """Decorator to require OTP verification for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            return {'error': 'User not authenticated'}, 401
        
        if not current_user.email_verified and not current_user.phone_verified:
            return {'error': 'User must verify email or phone'}, 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def log_otp_event(user_id, contact_value, verification_type, success):
    """Log OTP events for security audit"""
    from enhanced_models import AuditLog
    from enhanced_app import db
    
    action = "OTP_SENT_SUCCESS" if success else "OTP_SENT_FAILED"
    
    log = AuditLog(
        user_id=user_id,
        action=action,
        action_type="CREATE",
        table_name="verifications",
        new_values={
            'verification_type': verification_type,
            'contact_value': contact_value
        }
    )
    
    db.session.add(log)
    db.session.commit()
