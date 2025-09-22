import logging
from django.utils import timezone
from django.contrib.auth.models import User
from .models import SystemLog

class SystemLogger:
    """Utility class for creating system logs"""
    
    @staticmethod
    def log(level, category, message, user=None, request=None, additional_data=None):
        """Create a system log entry"""
        try:
            log_entry = SystemLog.objects.create(
                level=level,
                category=category,
                message=message,
                user=user,
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
                request_path=request.path if request else '',
                request_method=request.method if request else '',
                additional_data=additional_data
            )
            return log_entry
        except Exception as e:
            # Fallback to Django's logging if database logging fails
            logger = logging.getLogger('system')
            logger.error(f"Failed to create system log: {e}")
            return None
    
    @staticmethod
    def debug(category, message, user=None, request=None, additional_data=None):
        return SystemLogger.log('DEBUG', category, message, user, request, additional_data)
    
    @staticmethod
    def info(category, message, user=None, request=None, additional_data=None):
        return SystemLogger.log('INFO', category, message, user, request, additional_data)
    
    @staticmethod
    def warning(category, message, user=None, request=None, additional_data=None):
        return SystemLogger.log('WARNING', category, message, user, request, additional_data)
    
    @staticmethod
    def error(category, message, user=None, request=None, additional_data=None):
        return SystemLogger.log('ERROR', category, message, user, request, additional_data)
    
    @staticmethod
    def critical(category, message, user=None, request=None, additional_data=None):
        return SystemLogger.log('CRITICAL', category, message, user, request, additional_data)

# Convenience functions
def log_auth(message, user=None, request=None, additional_data=None):
    """Log authentication events"""
    return SystemLogger.info('AUTH', message, user, request, additional_data)

def log_user_action(message, user=None, request=None, additional_data=None):
    """Log user management events"""
    return SystemLogger.info('USER', message, user, request, additional_data)

def log_company_action(message, user=None, request=None, additional_data=None):
    """Log company management events"""
    return SystemLogger.info('COMPANY', message, user, request, additional_data)

def log_backup_action(message, user=None, request=None, additional_data=None):
    """Log backup/restore events"""
    return SystemLogger.info('BACKUP', message, user, request, additional_data)

def log_security_event(message, user=None, request=None, additional_data=None):
    """Log security events"""
    return SystemLogger.warning('SECURITY', message, user, request, additional_data)

def log_system_event(message, user=None, request=None, additional_data=None):
    """Log system events"""
    return SystemLogger.info('SYSTEM', message, user, request, additional_data)

def log_error(message, user=None, request=None, additional_data=None):
    """Log errors"""
    return SystemLogger.error('SYSTEM', message, user, request, additional_data)
