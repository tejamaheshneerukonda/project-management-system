#!/usr/bin/env python
"""
Script to create sample audit log data for testing the audit trail functionality.
Run this script from the Django project root directory.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import AuditLog, Company

def create_sample_audit_logs():
    """Create sample audit log entries for testing."""
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Get or create a test company
    company, created = Company.objects.get_or_create(
        name='Test Company',
        defaults={
            'domain': 'testcompany.com',
            'admin_user': user,
            'max_users': 50
        }
    )
    
    # Sample audit log data
    sample_logs = [
        {
            'user': user,
            'company': company,
            'action_type': 'LOGIN',
            'resource_type': 'USER',
            'resource_id': str(user.id),
            'resource_name': f'{user.first_name} {user.last_name}',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'success': True,
            'severity': 'LOW',
            'action_description': 'User successfully logged in',
            'request_path': '/login/',
            'request_method': 'POST'
        },
        {
            'user': user,
            'company': company,
            'action_type': 'CREATE',
            'resource_type': 'PROJECT',
            'resource_id': '1',
            'resource_name': 'Sample Project',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'success': True,
            'severity': 'MEDIUM',
            'action_description': 'Created new project: Sample Project',
            'new_values': '{"name": "Sample Project", "status": "active"}',
            'request_path': '/projects/create/',
            'request_method': 'POST'
        },
        {
            'user': user,
            'company': company,
            'action_type': 'UPDATE',
            'resource_type': 'USER',
            'resource_id': str(user.id),
            'resource_name': f'{user.first_name} {user.last_name}',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'success': True,
            'severity': 'MEDIUM',
            'action_description': 'Updated user profile information',
            'old_values': '{"email": "test@example.com"}',
            'new_values': '{"email": "newemail@example.com"}',
            'changed_fields': '["email"]',
            'request_path': '/profile/update/',
            'request_method': 'POST'
        },
        {
            'user': user,
            'company': company,
            'action_type': 'DELETE',
            'resource_type': 'FILE',
            'resource_id': '5',
            'resource_name': 'document.pdf',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'success': False,
            'severity': 'HIGH',
            'action_description': 'Failed to delete file: Permission denied',
            'error_message': 'Insufficient permissions to delete file',
            'request_path': '/files/delete/5/',
            'request_method': 'DELETE'
        },
        {
            'user': user,
            'company': company,
            'action_type': 'LOGIN',
            'resource_type': 'USER',
            'resource_id': str(user.id),
            'resource_name': f'{user.first_name} {user.last_name}',
            'ip_address': '10.0.0.50',
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'success': False,
            'severity': 'HIGH',
            'action_description': 'Failed login attempt: Invalid credentials',
            'error_message': 'Invalid username or password',
            'request_path': '/login/',
            'request_method': 'POST'
        },
        {
            'user': user,
            'company': company,
            'action_type': 'EXPORT',
            'resource_type': 'DATA',
            'resource_id': 'audit_logs',
            'resource_name': 'Audit Logs Export',
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'success': True,
            'severity': 'MEDIUM',
            'action_description': 'Exported audit logs to CSV',
            'additional_data': '{"export_format": "csv", "record_count": 25}',
            'request_path': '/audit-logs/export/',
            'request_method': 'GET'
        }
    ]
    
    # Create the audit log entries
    created_count = 0
    for i, log_data in enumerate(sample_logs):
        # Create unique audit logs by adding a timestamp offset
        timestamp_offset = timezone.now() - timedelta(hours=1) + timedelta(minutes=i*10)
        log_data['timestamp'] = timestamp_offset
        
        audit_log = AuditLog.objects.create(**log_data)
        created_count += 1
    
    print(f"Successfully created {created_count} sample audit log entries.")
    print(f"Total audit logs in database: {AuditLog.objects.count()}")

if __name__ == '__main__':
    create_sample_audit_logs()