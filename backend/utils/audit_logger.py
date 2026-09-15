"""
Audit Logging Utility Module
Tracks user actions for compliance and security
"""

from datetime import datetime
from flask import request
from enhanced_models import AuditLog
from functools import wraps
import json


class AuditLogger:
    """Handles audit logging of user actions"""
    
    @staticmethod
    def log_action(user_id, action, action_type="CREATE", 
                   table_name=None, record_id=None, 
                   old_values=None, new_values=None):
        """
        Log a user action
        
        Args:
            user_id: User performing the action
            action: Action name (e.g., 'login', 'add_transaction')
            action_type: Type of action (CREATE, READ, UPDATE, DELETE)
            table_name: Database table affected
            record_id: ID of affected record
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
        """
        try:
            from enhanced_app import db
            
            log = AuditLog(
                user_id=user_id,
                action=action,
                action_type=action_type,
                table_name=table_name,
                record_id=record_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            db.session.add(log)
            db.session.commit()
            
            print(f"✅ Audit logged: {action} by user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log audit: {e}")
            return False
    
    @staticmethod
    def log_login(user_id, success=True):
        """Log user login"""
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        AuditLogger.log_action(
            user_id=user_id,
            action=action,
            action_type="READ",
            table_name="users"
        )
    
    @staticmethod
    def log_logout(user_id):
        """Log user logout"""
        AuditLogger.log_action(
            user_id=user_id,
            action="LOGOUT",
            action_type="UPDATE",
            table_name="sessions"
        )
    
    @staticmethod
    def log_transaction(user_id, transaction_id, transaction_data):
        """Log transaction creation"""
        AuditLogger.log_action(
            user_id=user_id,
            action="ADD_TRANSACTION",
            action_type="CREATE",
            table_name="transactions",
            record_id=transaction_id,
            new_values=transaction_data
        )
    
    @staticmethod
    def log_account(user_id, account_id, account_data):
        """Log account creation"""
        AuditLogger.log_action(
            user_id=user_id,
            action="ADD_ACCOUNT",
            action_type="CREATE",
            table_name="bank_accounts",
            record_id=account_id,
            new_values=account_data
        )
    
    @staticmethod
    def log_budget(user_id, budget_id, budget_data):
        """Log budget creation"""
        AuditLogger.log_action(
            user_id=user_id,
            action="SET_BUDGET",
            action_type="CREATE",
            table_name="budgets",
            record_id=budget_id,
            new_values=budget_data
        )
    
    @staticmethod
    def log_profile_update(user_id, old_data, new_data):
        """Log profile updates"""
        AuditLogger.log_action(
            user_id=user_id,
            action="UPDATE_PROFILE",
            action_type="UPDATE",
            table_name="users",
            record_id=user_id,
            old_values=old_data,
            new_values=new_data
        )
    
    @staticmethod
    def get_user_activity(user_id, limit=50):
        """Get user's recent activity"""
        try:
            from enhanced_app import db
            
            logs = AuditLog.query.filter_by(user_id=user_id)\
                .order_by(AuditLog.created_at.desc())\
                .limit(limit)\
                .all()
            
            return logs
            
        except Exception as e:
            print(f"❌ Failed to retrieve activity: {e}")
            return []


def audit_log_action(action, action_type="CREATE", table_name=None):
    """Decorator to automatically log actions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            
            result = f(*args, **kwargs)
            
            if current_user.is_authenticated:
                AuditLogger.log_action(
                    user_id=current_user.id,
                    action=action,
                    action_type=action_type,
                    table_name=table_name
                )
            
            return result
        
        return decorated_function
    return decorator


def get_audit_report(user_id, days=30):
    """Generate audit report for user"""
    from enhanced_app import db
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = AuditLog.query.filter(
        AuditLog.user_id == user_id,
        AuditLog.created_at >= start_date
    ).order_by(AuditLog.created_at.desc()).all()
    
    # Summarize by action
    summary = {}
    for log in logs:
        action = log.action
        summary[action] = summary.get(action, 0) + 1
    
    return {
        'user_id': user_id,
        'period_days': days,
        'total_actions': len(logs),
        'summary': summary,
        'logs': logs
    }
