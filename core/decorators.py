"""
Decorators for audit logging and automatic action tracking
"""
import json
from functools import wraps
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from .models import AuditLog


def audit_log(action_type, resource_type, description=None, severity='MEDIUM', capture_changes=True):
    """
    Decorator for automatic audit logging of view functions
    
    Args:
        action_type: Type of action being performed (from AuditLog.ACTION_TYPES)
        resource_type: Type of resource being affected (from AuditLog.RESOURCE_TYPES)
        description: Optional description (will use function name if not provided)
        severity: Severity level (default: MEDIUM)
        capture_changes: Whether to capture request data changes
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get user information
            user = request.user if request.user.is_authenticated else None
            
            # Get request context
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            request_path = request.path
            request_method = request.method
            session_key = request.session.session_key
            
            # Prepare audit log data
            audit_data = {
                'user': user,
                'action_type': action_type,
                'resource_type': resource_type,
                'action_description': description or f"{view_func.__name__} executed",
                'severity': severity,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'request_path': request_path,
                'request_method': request_method,
                'session_key': session_key,
            }
            
            # Capture request data if needed
            if capture_changes and request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    if hasattr(request, 'POST') and request.POST:
                        audit_data['new_values'] = dict(request.POST)
                    elif hasattr(request, 'body') and request.body:
                        try:
                            audit_data['new_values'] = json.loads(request.body.decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
                except Exception:
                    pass
            
            # Extract resource information from URL parameters
            if 'pk' in kwargs:
                audit_data['resource_id'] = str(kwargs['pk'])
            elif 'id' in kwargs:
                audit_data['resource_id'] = str(kwargs['id'])
            
            # Get company context if available
            company = None
            if hasattr(request.user, 'company_admin_profile'):
                company = request.user.company_admin_profile.company
            elif hasattr(request.user, 'system_owner_profile'):
                # For system owners, try to get company from request or context
                company_id = request.GET.get('company_id') or request.POST.get('company_id')
                if company_id:
                    try:
                        from .models import Company
                        company = Company.objects.get(id=company_id)
                    except Company.DoesNotExist:
                        pass
            
            if company:
                audit_data['company'] = company
            
            # Execute the view function
            success = True
            error_message = ""
            response = None
            
            try:
                response = view_func(request, *args, **kwargs)
                
                # Check if response indicates an error
                if hasattr(response, 'status_code') and response.status_code >= 400:
                    success = False
                    if isinstance(response, JsonResponse):
                        try:
                            response_data = json.loads(response.content.decode('utf-8'))
                            error_message = response_data.get('error', f"HTTP {response.status_code}")
                        except:
                            error_message = f"HTTP {response.status_code}"
                    else:
                        error_message = f"HTTP {response.status_code}"
                
            except Exception as e:
                success = False
                error_message = str(e)
                raise  # Re-raise the exception
            
            finally:
                # Log the action
                audit_data.update({
                    'success': success,
                    'error_message': error_message,
                })
                
                try:
                    AuditLog.objects.create(**audit_data)
                except Exception as e:
                    # Don't let audit logging break the main functionality
                    print(f"Audit logging failed: {e}")
            
            return response
        
        return wrapper
    return decorator


def audit_model_changes(action_type, resource_type=None, severity='MEDIUM'):
    """
    Decorator for tracking model changes in view functions
    
    This decorator captures before/after states of model instances
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Store original model states if we can identify the model
            original_state = None
            model_instance = None
            
            # Try to get the model instance from kwargs
            if 'pk' in kwargs:
                try:
                    # This is a simplified approach - in practice, you'd need to
                    # determine the model class from the view or URL pattern
                    pass
                except:
                    pass
            
            # Execute the view
            response = view_func(request, *args, **kwargs)
            
            # Log the change with before/after states
            user = request.user if request.user.is_authenticated else None
            
            audit_data = {
                'user': user,
                'action_type': action_type,
                'resource_type': resource_type or 'OTHER',
                'action_description': f"{view_func.__name__} - Model change tracked",
                'severity': severity,
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'request_path': request.path,
                'request_method': request.method,
                'success': True,
            }
            
            if 'pk' in kwargs:
                audit_data['resource_id'] = str(kwargs['pk'])
            
            try:
                AuditLog.objects.create(**audit_data)
            except Exception as e:
                print(f"Audit logging failed: {e}")
            
            return response
        
        return wrapper
    return decorator


def get_client_ip(request):
    """Get the client IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_action(user, action_type, resource_type, description, **kwargs):
    """
    Utility function to manually log user actions
    
    Args:
        user: User instance
        action_type: Action type from AuditLog.ACTION_TYPES
        resource_type: Resource type from AuditLog.RESOURCE_TYPES
        description: Description of the action
        **kwargs: Additional audit log fields
    """
    try:
        AuditLog.log_action(
            user=user,
            action_type=action_type,
            resource_type=resource_type,
            description=description,
            **kwargs
        )
    except Exception as e:
        print(f"Manual audit logging failed: {e}")


def log_security_event(user, description, severity='HIGH', **kwargs):
    """
    Utility function to log security-related events
    
    Args:
        user: User instance (can be None for system events)
        description: Description of the security event
        severity: Severity level (default: HIGH)
        **kwargs: Additional audit log fields
    """
    try:
        AuditLog.log_action(
            user=user,
            action_type='SECURITY_EVENT',
            resource_type='SYSTEM',
            description=description,
            severity=severity,
            **kwargs
        )
    except Exception as e:
        print(f"Security event logging failed: {e}")


def log_system_event(description, severity='MEDIUM', **kwargs):
    """
    Utility function to log system events
    
    Args:
        description: Description of the system event
        severity: Severity level (default: MEDIUM)
        **kwargs: Additional audit log fields
    """
    try:
        AuditLog.log_action(
            user=None,  # System events don't have a user
            action_type='CRITICAL',
            resource_type='SYSTEM',
            description=description,
            severity=severity,
            **kwargs
        )
    except Exception as e:
        print(f"System event logging failed: {e}")