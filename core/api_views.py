from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
import json

from .models import (
    Company, Employee, Project, Task, Notification, Announcement,
    PerformanceMetric, CompanyMetric, CompanySetting, UserPreference,
    WorkflowTemplate, WorkflowInstance, ActivityLog, PaymentMethod,
    LeaveRequest, Timesheet
)
from .decorators import audit_log

@csrf_exempt
@login_required
@require_http_methods(["POST"])
@audit_log('CREATE', 'PROJECT', 'Project creation via API', 'MEDIUM')
def create_project(request):
    """Create a new project"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        data = json.loads(request.body)
        
        project = Project.objects.create(
            company=company,
            name=data.get('name'),
            description=data.get('description', ''),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            priority=data.get('priority', 'MEDIUM'),
            status='PLANNING'
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PROJECT_CREATED',
            description=f'Created project: {project.name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'project_id': project.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
@audit_log('CREATE', 'TASK', 'Task creation via API', 'MEDIUM')
def create_task(request):
    """Create a new task"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        data = json.loads(request.body)
        
        project = get_object_or_404(Project, id=data.get('project_id'), company=company)
        
        task = Task.objects.create(
            project=project,
            title=data.get('title'),
            description=data.get('description', ''),
            priority=data.get('priority', 'MEDIUM'),
            due_date=data.get('due_date'),
            estimated_hours=data.get('estimated_hours')
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='TASK_CREATED',
            description=f'Created task: {task.title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'task_id': task.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
@audit_log('UPDATE', 'TASK', 'Task update via API', 'MEDIUM')
def update_task(request, task_id):
    """Update an existing task"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        task = get_object_or_404(Task, id=task_id, project__company=company)
        data = json.loads(request.body)
        
        # Update task fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = data['due_date'] if data['due_date'] else None
        if 'estimated_hours' in data:
            task.estimated_hours = data['estimated_hours']
        if 'actual_hours' in data:
            task.actual_hours = data['actual_hours']
        if 'assigned_to' in data:
            if data['assigned_to']:
                task.assigned_to = get_object_or_404(Employee, id=data['assigned_to'], company=company)
            else:
                task.assigned_to = None
        
        task.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='TASK_UPDATED',
            description=f'Updated task: {task.title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'task_id': task.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_task(request, task_id):
    """Get task details"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        task = get_object_or_404(Task, id=task_id, project__company=company)
        
        # Prepare task data with detailed information
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'estimated_hours': float(task.estimated_hours) if task.estimated_hours else None,
            'actual_hours': float(task.actual_hours) if task.actual_hours else None,
            'assigned_to': {
                'id': task.assigned_to.id if task.assigned_to else None,
                'first_name': task.assigned_to.first_name if task.assigned_to else None,
                'last_name': task.assigned_to.last_name if task.assigned_to else None
            } if task.assigned_to else None,
            'project': {
                'id': task.project.id,
                'name': task.project.name,
                'status': task.project.status,
                'project_manager': {
                    'id': task.project.project_manager.id if task.project.project_manager else None,
                    'first_name': task.project.project_manager.first_name if task.project.project_manager else None,
                    'last_name': task.project.project_manager.last_name if task.project.project_manager else None
                } if task.project.project_manager else None
            },
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }
        
        return JsonResponse({'success': True, 'task': task_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
@audit_log('DELETE', 'TASK', 'Task deletion via API', 'MEDIUM')
def delete_task(request, task_id):
    """Delete an existing task"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        task = get_object_or_404(Task, id=task_id, project__company=company)
        task_title = task.title
        
        task.delete()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='TASK_DELETED',
            description=f'Deleted task: {task_title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_announcement(request):
    """Create a new announcement"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        data = json.loads(request.body)
        
        announcement = Announcement.objects.create(
            company=company,
            title=data.get('title'),
            content=data.get('content'),
            priority=data.get('priority', 'MEDIUM'),
            created_by=request.user
        )
        
        # Create notifications for all company employees
        employees = Employee.objects.filter(company=company, user_account__isnull=False)
        for employee in employees:
            Notification.objects.create(
                user=employee.user_account,
                company=company,
                title=f"New Announcement: {announcement.title}",
                message=announcement.content,
                notification_type='INFO',
                is_global=True
            )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='ANNOUNCEMENT_CREATED',
            description=f'Created announcement: {announcement.title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'announcement_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def unread_notifications(request):
    """Get unread notifications count"""
    try:
        if hasattr(request.user, 'company_admin_profile'):
            company = request.user.company_admin_profile.company
            count = Notification.objects.filter(
                company=company,
                is_read=False
            ).count()
        else:
            count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        
        return JsonResponse({'count': count})
        
    except Exception as e:
        return JsonResponse({'count': 0, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def dashboard_analytics(request):
    """Get dashboard analytics data"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get analytics data
        analytics = {
            'total_employees': Employee.objects.filter(company=company).count(),
            'active_projects': Project.objects.filter(company=company, status='ACTIVE').count(),
            'completed_tasks': Task.objects.filter(project__company=company, status='DONE').count(),
            'total_tasks': Task.objects.filter(project__company=company).count(),
            'recent_activities': ActivityLog.objects.filter(
                company=company,
                timestamp__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        
        return JsonResponse({'success': True, 'analytics': analytics})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def search_employees(request):
    """Search employees"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        query = request.GET.get('q', '')
        
        employees = Employee.objects.filter(
            company=company,
            first_name__icontains=query
        ) | Employee.objects.filter(
            company=company,
            last_name__icontains=query
        ) | Employee.objects.filter(
            company=company,
            email__icontains=query
        )
        
        results = []
        for employee in employees[:10]:  # Limit to 10 results
            results.append({
                'id': employee.id,
                'name': f"{employee.first_name} {employee.last_name}",
                'email': employee.email,
                'department': employee.department,
                'is_verified': employee.is_verified
            })
        
        return JsonResponse({'success': True, 'results': results})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_company_settings(request):
    """Update company settings"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        data = json.loads(request.body)
        
        settings, created = CompanySetting.objects.get_or_create(company=company)
        
        # Update settings
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='SETTINGS_UPDATED',
            description='Updated company settings',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_user_preferences(request):
    """Update user preferences"""
    try:
        data = json.loads(request.body)
        
        preferences, created = UserPreference.objects.get_or_create(user=request.user)
        
        # Update preferences
        for key, value in data.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        
        preferences.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_workflow(request):
    """Create a new workflow template"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        data = json.loads(request.body)
        
        workflow = WorkflowTemplate.objects.create(
            company=company,
            name=data.get('name'),
            description=data.get('description', ''),
            steps=data.get('steps', []),
            created_by=request.user
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='WORKFLOW_CREATED',
            description=f'Created workflow: {workflow.name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'workflow_id': workflow.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def project_detail(request, project_id):
    """Get project details"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        project = get_object_or_404(Project, id=project_id, company=company)
        
        project_data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'status': project.status,
            'priority': project.priority,
            'start_date': project.start_date.isoformat(),
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'budget': float(project.budget) if project.budget else None,
            'created_at': project.created_at.isoformat(),
        }
        
        return JsonResponse({'success': True, 'project': project_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def project_tasks(request, project_id):
    """Get project tasks"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        project = get_object_or_404(Project, id=project_id, company=company)
        
        tasks = Task.objects.filter(project=project)
        tasks_data = []
        
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'estimated_hours': float(task.estimated_hours) if task.estimated_hours else None,
                'actual_hours': float(task.actual_hours) if task.actual_hours else None,
                'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else None,
            })
        
        return JsonResponse({'success': True, 'tasks': tasks_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
@audit_log('UPDATE', 'TASK', 'Task update via API', 'MEDIUM')
def update_task(request, task_id):
    """Update task status"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        task = get_object_or_404(Task, id=task_id, project__company=company)
        data = json.loads(request.body)
        
        # Update task
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='TASK_UPDATED',
            description=f'Updated task: {task.title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def list_announcements(request):
    """List company announcements"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        announcements = Announcement.objects.filter(
            company=company,
            is_active=True
        ).order_by('-created_at')
        
        announcements_data = []
        for announcement in announcements:
            announcements_data.append({
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'priority': announcement.priority,
                'created_at': announcement.created_at.isoformat(),
                'created_by': announcement.created_by.get_full_name(),
            })
        
        return JsonResponse({'success': True, 'announcements': announcements_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def performance_analytics(request):
    """Get performance analytics"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get performance metrics
        metrics = PerformanceMetric.objects.filter(
            employee__company=company
        ).order_by('-created_at')[:20]
        
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'id': metric.id,
                'employee_name': f"{metric.employee.first_name} {metric.employee.last_name}",
                'metric_type': metric.metric_type,
                'value': float(metric.value),
                'target_value': float(metric.target_value) if metric.target_value else None,
                'period_start': metric.period_start.isoformat(),
                'period_end': metric.period_end.isoformat(),
                'notes': metric.notes,
            })
        
        return JsonResponse({'success': True, 'metrics': metrics_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
@audit_log('CREATE', 'EMPLOYEE', 'Employee creation via API', 'MEDIUM')
def create_employee(request):
    """Create a new employee"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get form data
        employee_id = request.POST.get('employee_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        department = request.POST.get('department', '')
        position = request.POST.get('position', '')
        hire_date = request.POST.get('hire_date')
        
        # Validate required fields
        if not all([employee_id, first_name, last_name, email]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        # Check if employee ID already exists
        if Employee.objects.filter(company=company, employee_id=employee_id).exists():
            return JsonResponse({'success': False, 'error': 'Employee ID already exists'})
        
        # Check if email already exists
        if Employee.objects.filter(company=company, email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'})
        
        # Create employee
        employee = Employee.objects.create(
            company=company,
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            position=position,
            hire_date=hire_date if hire_date else None,
            is_verified=False
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='EMPLOYEE_CREATED',
            description=f'Created employee: {employee.first_name} {employee.last_name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'employee_id': employee.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_employee(request, employee_id):
    """Get employee details"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        employee_data = {
            'id': employee.id,
            'employee_id': employee.employee_id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'phone': getattr(employee, 'phone', ''),
            'department': employee.department,
            'position': employee.position,
            'is_verified': employee.is_verified,
            'hire_date': employee.hire_date.isoformat() if getattr(employee, 'hire_date', None) else None,
            'created_at': employee.created_at.isoformat(),
            'updated_at': employee.updated_at.isoformat(),
            'photo_url': employee.get_photo_url(),
            'thumbnail_url': employee.get_thumbnail_url(),
            'initials': employee.get_initials(),
        }
        
        return JsonResponse({'success': True, 'employee': employee_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
@audit_log('UPDATE', 'EMPLOYEE', 'Employee update via API', 'MEDIUM')
def update_employee(request, employee_id):
    """Update employee information"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        department = request.POST.get('department', '')
        position = request.POST.get('position', '')
        hire_date = request.POST.get('hire_date')
        is_verified = request.POST.get('is_verified') == 'true'
        
        # Validate required fields
        if not all([first_name, last_name, email]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        # Check if email already exists for another employee
        if Employee.objects.filter(company=company, email=email).exclude(id=employee_id).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'})
        
        # Update employee
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        if hasattr(employee, 'phone'):
            employee.phone = phone
        employee.department = department
        employee.position = position
        employee.is_verified = is_verified
        if hire_date and hasattr(employee, 'hire_date'):
            employee.hire_date = hire_date
        employee.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='EMPLOYEE_UPDATED',
            description=f'Updated employee: {employee.first_name} {employee.last_name}',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return JsonResponse({'success': True, 'message': f'Employee {employee.first_name} {employee.last_name} updated successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
@audit_log('DELETE', 'EMPLOYEE', 'Employee deletion via API', 'HIGH')
def delete_employee(request, employee_id):
    """Delete an employee"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            messages.error(request, 'Access denied')
            return redirect('core:employee_directory')
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        # Store employee info for logging
        employee_name = f"{employee.first_name} {employee.last_name}"
        employee_email = employee.email
        
        # Delete the employee (this will cascade delete the user account if it exists)
        employee.delete()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='EMPLOYEE_DELETED',
            description=f'Deleted employee: {employee_name} ({employee_email})',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        messages.success(request, f'Employee {employee_name} deleted successfully')
        return redirect('core:employee_directory')
        
    except Exception as e:
        messages.error(request, f'Error deleting employee: {str(e)}')
        return redirect('core:employee_directory')

@login_required
@require_http_methods(["POST"])
@audit_log('BULK_ACTION', 'EMPLOYEE', 'Bulk employee operations via API', 'HIGH')
def bulk_employee_operations(request):
    """Handle bulk operations on employees"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        operation = request.POST.get('operation')
        employee_ids_json = request.POST.get('employee_ids')
        
        if not operation or not employee_ids_json:
            return JsonResponse({'success': False, 'error': 'Missing operation or employee IDs'})
        
        try:
            employee_ids = json.loads(employee_ids_json)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid employee IDs format'})
        
        # Get employees belonging to the company
        employees = Employee.objects.filter(id__in=employee_ids, company=company)
        
        if not employees.exists():
            return JsonResponse({'success': False, 'error': 'No valid employees found'})
        
        success_count = 0
        errors = []
        
        if operation == 'verify':
            # Bulk verify employees
            for employee in employees:
                try:
                    employee.is_verified = True
                    employee.save()
                    success_count += 1
                    
                    # Log activity
                    ActivityLog.objects.create(
                        user=request.user,
                        company=company,
                        action='EMPLOYEE_VERIFIED',
                        description=f'Verified employee: {employee.first_name} {employee.last_name}',
                        ip_address=request.META.get('REMOTE_ADDR'),
                    )
                except Exception as e:
                    errors.append(f"Error verifying {employee.first_name} {employee.last_name}: {str(e)}")
            
            message = f'Successfully verified {success_count} employee(s)'
            
        elif operation == 'delete':
            # Bulk delete employees
            employee_names = []
            for employee in employees:
                try:
                    employee_name = f"{employee.first_name} {employee.last_name}"
                    employee_names.append(employee_name)
                    employee.delete()
                    success_count += 1
                    
                    # Log activity
                    ActivityLog.objects.create(
                        user=request.user,
                        company=company,
                        action='EMPLOYEE_DELETED',
                        description=f'Deleted employee: {employee_name}',
                        ip_address=request.META.get('REMOTE_ADDR'),
                    )
                except Exception as e:
                    errors.append(f"Error deleting {employee.first_name} {employee.last_name}: {str(e)}")
            
            message = f'Successfully deleted {success_count} employee(s)'
            
        elif operation == 'export':
            # Bulk export employees
            import csv
            import io
            from django.http import HttpResponse
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Employee ID', 'First Name', 'Last Name', 'Email', 'Department', 'Position', 'Status', 'Created Date'])
            
            # Write employee data
            for employee in employees:
                writer.writerow([
                    employee.employee_id,
                    employee.first_name,
                    employee.last_name,
                    employee.email,
                    employee.department or '',
                    employee.position or '',
                    'Verified' if employee.is_verified else 'Pending',
                    employee.created_at.strftime('%Y-%m-%d')
                ])
                success_count += 1
            
            # Create response
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            filename = f'employees_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            message = f'Successfully exported {success_count} employee(s)'
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                company=company,
                action='EMPLOYEES_EXPORTED',
                description=f'Exported {success_count} employees to CSV',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            return response
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid operation'})
        
        # Prepare response
        response_data = {
            'success': True,
            'message': message,
            'success_count': success_count,
            'total_count': len(employee_ids)
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['error_count'] = len(errors)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def upload_employee_photo(request, employee_id):
    """Upload employee photo"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        # Check if photo was uploaded
        if 'photo' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No photo uploaded'})
        
        photo = request.FILES['photo']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if photo.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'Invalid file type. Only JPEG, PNG, and GIF files are allowed.'})
        
        # Validate file size (5MB max)
        if photo.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File too large. Maximum size is 5MB.'})
        
        # Delete old photo if exists
        if employee.photo:
            try:
                employee.photo.delete(save=False)
                if employee.photo_thumbnail:
                    employee.photo_thumbnail.delete(save=False)
            except:
                pass
        
        # Save new photo
        employee.photo = photo
        employee.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='EMPLOYEE_PHOTO_UPLOADED',
            description=f'Uploaded photo for employee: {employee.first_name} {employee.last_name}',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Photo uploaded successfully',
            'photo_url': employee.get_photo_url(),
            'thumbnail_url': employee.get_thumbnail_url()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def delete_employee_photo(request, employee_id):
    """Delete employee photo"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        if not employee.photo:
            return JsonResponse({'success': False, 'error': 'No photo to delete'})
        
        # Delete photos
        try:
            employee.photo.delete(save=False)
            if employee.photo_thumbnail:
                employee.photo_thumbnail.delete(save=False)
        except:
            pass
        
        # Clear photo fields
        employee.photo = None
        employee.photo_thumbnail = None
        employee.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='EMPLOYEE_PHOTO_DELETED',
            description=f'Deleted photo for employee: {employee.first_name} {employee.last_name}',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Photo deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def employee_performance(request, employee_id):
    """Get employee performance data"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        # Get performance metrics for this employee
        metrics = PerformanceMetric.objects.filter(
            employee=employee
        ).order_by('-created_at')
        
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'id': metric.id,
                'metric_type': metric.metric_type,
                'value': float(metric.value),
                'target_value': float(metric.target_value) if metric.target_value else None,
                'period_start': metric.period_start.isoformat(),
                'period_end': metric.period_end.isoformat(),
                'notes': metric.notes,
            })
        
        employee_data = {
            'id': employee.id,
            'name': f"{employee.first_name} {employee.last_name}",
            'email': employee.email,
            'department': employee.department,
            'position': employee.position,
            'is_verified': employee.is_verified,
            'metrics': metrics_data
        }
        
        return JsonResponse({'success': True, 'employee': employee_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def execute_workflow(request, workflow_id):
    """Execute a workflow instance"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        workflow_template = get_object_or_404(WorkflowTemplate, id=workflow_id, company=company)
        data = json.loads(request.body)
        
        # Create workflow instance
        workflow_instance = WorkflowInstance.objects.create(
            template=workflow_template,
            title=data.get('title'),
            assigned_to=request.user,
            data=data.get('data', {})
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='WORKFLOW_EXECUTED',
            description=f'Executed workflow: {workflow_instance.title}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({'success': True, 'workflow_instance_id': workflow_instance.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Additional API endpoints for templates
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def verify_employee(request):
    """Verify an employee"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            employee_id = data.get('employee_id')
        else:
            employee_id = request.POST.get('employee_id')
        
        if not employee_id:
            return JsonResponse({'success': False, 'error': 'Employee ID is required'})
        
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        employee.is_verified = True
        employee.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_department(request):
    """Create a new department"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Create department using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Department: {name}",
            content=description,
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'department_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_department(request, department_id):
    """Get department details"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get department from Announcement model
        announcement = Announcement.objects.get(
            id=department_id,
            company=company,
            title__startswith='Department: '
        )
        
        return JsonResponse({
            'success': True,
            'department': {
                'id': announcement.id,
                'name': announcement.title.replace('Department: ', ''),
                'description': announcement.content,
                'created_at': announcement.created_at.isoformat()
            }
        })
        
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Department not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def update_department(request, department_id):
    """Update department details"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get department from Announcement model
        announcement = Announcement.objects.get(
            id=department_id,
            company=company,
            title__startswith='Department: '
        )
        
        # Update fields
        if 'name' in request.POST:
            announcement.title = f"Department: {request.POST.get('name')}"
        if 'description' in request.POST:
            announcement.content = request.POST.get('description', '')
        
        announcement.save()
        
        return JsonResponse({'success': True})
        
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Department not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_department(request, department_id):
    """Delete department"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get department from Announcement model
        announcement = Announcement.objects.get(
            id=department_id,
            company=company,
            title__startswith='Department: '
        )
        
        announcement.delete()
        
        return JsonResponse({'success': True})
        
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Department not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_performance(request):
    """Create a performance record"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee_id = request.POST.get('employee_id')
        metric_type = request.POST.get('metric_type')
        value = request.POST.get('value')
        
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        performance = PerformanceMetric.objects.create(
            employee=employee,
            metric_type=metric_type,
            value=value,
            period_start=timezone.now().date(),
            period_end=timezone.now().date()
        )
        
        return JsonResponse({'success': True, 'performance_id': performance.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_performance(request, performance_id):
    """Get performance record details"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get performance record
        performance = PerformanceMetric.objects.get(
            id=performance_id,
            employee__company=company
        )
        
        return JsonResponse({
            'success': True,
            'performance': {
                'id': performance.id,
                'employee_id': performance.employee.id,
                'employee_name': f"{performance.employee.first_name} {performance.employee.last_name}",
                'metric_type': performance.metric_type,
                'value': float(performance.value),
                'target_value': float(performance.target_value) if performance.target_value else None,
                'period_start': performance.period_start.isoformat(),
                'period_end': performance.period_end.isoformat(),
                'notes': performance.notes,
                'created_at': performance.created_at.isoformat()
            }
        })
        
    except PerformanceMetric.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Performance record not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def update_performance(request, performance_id):
    """Update performance record"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get performance record
        performance = PerformanceMetric.objects.get(
            id=performance_id,
            employee__company=company
        )
        
        # Update fields
        if 'metric_type' in request.POST:
            performance.metric_type = request.POST.get('metric_type')
        if 'value' in request.POST:
            performance.value = request.POST.get('value')
        if 'target_value' in request.POST:
            performance.target_value = request.POST.get('target_value')
        if 'notes' in request.POST:
            performance.notes = request.POST.get('notes')
        
        performance.save()
        
        return JsonResponse({'success': True})
        
    except PerformanceMetric.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Performance record not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_performance(request, performance_id):
    """Delete performance record"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get performance record
        performance = PerformanceMetric.objects.get(
            id=performance_id,
            employee__company=company
        )
        
        performance.delete()
        
        return JsonResponse({'success': True})
        
    except PerformanceMetric.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Performance record not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Send an internal message"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Create message using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Message: {subject}",
            content=message,
            announcement_type='MESSAGE',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'message_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def send_chat_message(request):
    """Send a chat message"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        message = request.POST.get('message')
        
        # Create chat message using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title="Chat Message",
            content=message,
            announcement_type='CHAT',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'message_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def clear_chat(request):
    """Clear chat history"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Clear chat messages (using Announcement model as placeholder)
        Announcement.objects.filter(
            company=company,
            announcement_type='CHAT'
        ).delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def upload_file(request):
    """Upload a file"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        file = request.FILES.get('file')
        description = request.POST.get('description', '')
        
        if not file:
            return JsonResponse({'success': False, 'error': 'No file provided'})
        
        # Create file record using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"File: {file.name}",
            content=description,
            announcement_type='FILE',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'file_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_ticket(request):
    """Create a support ticket"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'MEDIUM')
        
        # Create ticket using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Ticket: {title}",
            content=description,
            priority=priority,
            announcement_type='TICKET',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'ticket_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_customer(request):
    """Create a customer record"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        
        # Create customer using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Customer: {name}",
            content=f"Email: {email}, Phone: {phone}",
            announcement_type='CUSTOMER',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'customer_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_attendance(request):
    """Create an attendance record"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        employee_id = request.POST.get('employee_id')
        date = request.POST.get('date')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        
        # Create attendance using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Attendance: {date}",
            content=f"Check In: {check_in}, Check Out: {check_out}",
            announcement_type='ATTENDANCE',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'attendance_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_benefit(request):
    """Create an employee benefit"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('name')
        description = request.POST.get('description')
        benefit_type = request.POST.get('benefit_type')
        
        # Create benefit using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Benefit: {name}",
            content=f"Type: {benefit_type}, Description: {description}",
            announcement_type='BENEFIT',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'benefit_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_leave(request):
    """Create a leave request"""
    try:
        # Parse JSON data from request body
        import json
        data = json.loads(request.body)
        
        # Allow both employees and company admins to create leave requests
        if hasattr(request.user, 'employee_profile'):
            # Regular employee submitting own leave request
            employee = request.user.employee_profile
            company = employee.company
            leave_type = data.get('leave_type')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            reason = data.get('reason')
            
            # Create actual LeaveRequest object
            from datetime import datetime
            
            # Parse dates and calculate total days
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            total_days = (end_date_obj - start_date_obj).days + 1  # +1 to include both start and end dates
            
            leave_request = LeaveRequest.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date_obj,
                end_date=end_date_obj,
                total_days=total_days,
                reason=reason,
                status='PENDING'
            )
            
            # Send WebSocket notification to company admins
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'leave_requests_company_{company.id}',
                    {
                        'type': 'leave_request_update',
                        'action': 'new_request',
                        'data': {
                            'id': leave_request.id,
                            'employee_name': f"{employee.first_name} {employee.last_name}",
                            'leave_type': leave_request.get_leave_type_display(),
                            'start_date': leave_request.start_date.strftime('%Y-%m-%d'),
                            'end_date': leave_request.end_date.strftime('%Y-%m-%d'),
                            'total_days': str(leave_request.total_days),
                            'reason': leave_request.reason,
                            'status': leave_request.status,
                            'created_at': leave_request.created_at.strftime('%Y-%m-%d %H:%M'),
                        }
                    }
                )
            
            return JsonResponse({'success': True, 'leave_id': leave_request.id})
        elif hasattr(request.user, 'company_admin_profile'):
            # Company admin creating leave request (possibly for someone else)
            company = request.user.company_admin_profile.company
            employee_id = data.get('employee_id')
            leave_type = data.get('leave_type')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            reason = data.get('reason')
            
            # Find the employee
            if employee_id:
                try:
                    employee = Employee.objects.get(id=employee_id, company=company)
                    # Create actual LeaveRequest object
                    # Parse dates and calculate total days
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    total_days = (end_date_obj - start_date_obj).days + 1  # +1 to include both start and end dates
                    
                    leave_request = LeaveRequest.objects.create(
                        employee=employee,
                        leave_type=leave_type,
                        start_date=start_date_obj,
                        end_date=end_date_obj,
                        total_days=total_days,
                        reason=reason,
                        status='PENDING'
                    )
                    return JsonResponse({'success': True, 'leave_id': leave_request.id})
                except Employee.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Employee not found'})
            else:
                return JsonResponse({'success': False, 'error': 'Employee ID is required'})
        else:
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def approve_leave(request, request_id):
    """Approve a leave request"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        try:
            leave_request = LeaveRequest.objects.get(
                id=request_id,
                employee__company=company
            )
        except LeaveRequest.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Leave request not found'})
        
        if leave_request.status != 'PENDING':
            return JsonResponse({'success': False, 'error': 'Only pending requests can be approved'})
        
        # Update leave request
        leave_request.status = 'APPROVED'
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()
        leave_request.save()
        
        # Send WebSocket notification
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Calculate updated leave balance for the employee
            def calculate_employee_leave_balance(emp):
                annual_allocation = 20
                sick_allocation = 10
                personal_allocation = 5
                
                approved_annual = LeaveRequest.objects.filter(
                    employee=emp,
                    leave_type='VACATION',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                approved_sick = LeaveRequest.objects.filter(
                    employee=emp,
                    leave_type='SICK_LEAVE',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                approved_personal = LeaveRequest.objects.filter(
                    employee=emp,
                    leave_type='PERSONAL',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                return {
                    'annual': float(annual_allocation - approved_annual),
                    'sick': float(sick_allocation - approved_sick),
                    'personal': float(personal_allocation - approved_personal),
                }
            
            updated_balance = calculate_employee_leave_balance(leave_request.employee)
            
            async_to_sync(channel_layer.group_send)(
                f'leave_requests_company_{company.id}',
                {
                    'type': 'leave_request_update',
                    'action': 'status_update',
                    'data': {
                        'id': leave_request.id,
                        'status': 'APPROVED',
                        'reviewed_by': request.user.username,
                        'reviewed_at': leave_request.reviewed_at.strftime('%Y-%m-%d %H:%M'),
                    }
                }
            )
            
            # Send balance update to employee-specific room
            async_to_sync(channel_layer.group_send)(
                f'employee_balance_{leave_request.employee.id}',
                {
                    'type': 'leave_balance_update',
                    'action': 'balance_changed',
                    'data': {
                        'employee_id': leave_request.employee.id,
                        'leave_balance': updated_balance,
                        'leave_type': leave_request.get_leave_type_display(),
                        'days_used': str(leave_request.total_days),
                        'status': 'APPROVED',
                    }
                }
            )
        
        return JsonResponse({'success': True, 'message': 'Leave request approved successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def reject_leave(request, request_id):
    """Reject a leave request"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        try:
            leave_request = LeaveRequest.objects.get(
                id=request_id,
                employee__company=company
            )
        except LeaveRequest.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Leave request not found'})
        
        if leave_request.status != 'PENDING':
            return JsonResponse({'success': False, 'error': 'Only pending requests can be rejected'})
        
        # Update leave request
        leave_request.status = 'REJECTED'
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()
        leave_request.save()
        
        # Send WebSocket notification
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Calculate updated leave balance for the employee (rejection doesn't change balance)
            def calculate_employee_leave_balance(emp):
                annual_allocation = 20
                sick_allocation = 10
                personal_allocation = 5
                
                approved_annual = LeaveRequest.objects.filter(
                    employee=emp,
                    leave_type='VACATION',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                approved_sick = LeaveRequest.objects.filter(
                    employee=emp,
                    leave_type='SICK_LEAVE',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                approved_personal = LeaveRequest.objects.filter(
                    employee=emp,
                    leave_type='PERSONAL',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                return {
                    'annual': float(annual_allocation - approved_annual),
                    'sick': float(sick_allocation - approved_sick),
                    'personal': float(personal_allocation - approved_personal),
                }
            
            updated_balance = calculate_employee_leave_balance(leave_request.employee)
            
            async_to_sync(channel_layer.group_send)(
                f'leave_requests_company_{company.id}',
                {
                    'type': 'leave_request_update',
                    'action': 'status_update',
                    'data': {
                        'id': leave_request.id,
                        'status': 'REJECTED',
                        'reviewed_by': request.user.username,
                        'reviewed_at': leave_request.reviewed_at.strftime('%Y-%m-%d %H:%M'),
                    }
                }
            )
            
            # Send balance update to employee-specific room (balance unchanged for rejection)
            async_to_sync(channel_layer.group_send)(
                f'employee_balance_{leave_request.employee.id}',
                {
                    'type': 'leave_balance_update',
                    'action': 'status_changed',
                    'data': {
                        'employee_id': leave_request.employee.id,
                        'leave_balance': updated_balance,
                        'leave_type': leave_request.get_leave_type_display(),
                        'days_requested': str(leave_request.total_days),
                        'status': 'REJECTED',
                        'message': 'Leave request rejected - balance unchanged'
                    }
                }
            )
        
        return JsonResponse({'success': True, 'message': 'Leave request rejected successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_asset(request):
    """Create an asset record"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('name')
        asset_type = request.POST.get('asset_type')
        description = request.POST.get('description')
        
        # Create asset using Project model as placeholder
        project = Project.objects.create(
            company=company,
            name=f"Asset: {name}",
            description=f"Type: {asset_type}, Description: {description}",
            status='ACTIVE'
        )
        
        return JsonResponse({'success': True, 'asset_id': project.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_security_setting(request):
    """Create a security setting"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('setting_name')
        setting_type = request.POST.get('setting_type')
        value = request.POST.get('setting_value')
        description = request.POST.get('description')
        
        # Create security setting using Announcement model as placeholder
        announcement = Announcement.objects.create(
            company=company,
            title=f"Security Setting: {name}",
            content=f"Type: {setting_type}, Value: {value}, Description: {description}",
            announcement_type='SECURITY',
            created_by=request.user
        )
        
        return JsonResponse({'success': True, 'setting_id': announcement.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_integration(request):
    """Create an integration"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('integration_name')
        integration_type = request.POST.get('integration_type')
        api_key = request.POST.get('api_key')
        description = request.POST.get('description')
        
        # Create integration using Project model as placeholder
        project = Project.objects.create(
            company=company,
            name=f"Integration: {name}",
            description=f"Type: {integration_type}, Description: {description}",
            status='ACTIVE'
        )
        
        return JsonResponse({'success': True, 'integration_id': project.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_endpoint(request):
    """Create an API endpoint"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        name = request.POST.get('endpoint_name')
        http_method = request.POST.get('http_method')
        url = request.POST.get('endpoint_url')
        description = request.POST.get('description')
        
        # Create endpoint using WorkflowInstance model as placeholder
        workflow_instance = WorkflowInstance.objects.create(
            template=WorkflowTemplate.objects.filter(company=company).first(),
            title=f"API Endpoint: {name}",
            assigned_to=request.user,
            status=http_method
        )
        
        return JsonResponse({'success': True, 'endpoint_id': workflow_instance.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_company_profile(request):
    """Update company profile"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Update company fields
        company.name = request.POST.get('company_name', company.name)
        company.email = request.POST.get('company_email', company.email)
        company.phone = request.POST.get('company_phone', company.phone)
        company.website = request.POST.get('company_website', company.website)
        company.industry = request.POST.get('company_industry', company.industry)
        company.size = request.POST.get('company_size', company.size)
        company.address = request.POST.get('company_address', company.address)
        company.description = request.POST.get('company_description', company.description)
        
        company.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def upload_logo(request):
    """Upload company logo"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        logo_file = request.FILES.get('logo_file')
        
        if not logo_file:
            return JsonResponse({'success': False, 'error': 'No logo file provided'})
        
        # Handle logo upload (simplified - in real implementation, you'd save the file)
        company.logo = logo_file
        company.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def generate_performance_report(request):
    """Generate performance report"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get report parameters from request
        report_type = request.POST.get('report_type', 'summary')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        department = request.POST.get('department', '')
        
        # Generate report data (simplified implementation)
        report_data = {
            'company_name': company.name,
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
            'department': department,
            'generated_at': timezone.now().isoformat(),
            'total_employees': Employee.objects.filter(company=company).count(),
            'performance_metrics': list(PerformanceMetric.objects.filter(
                employee__company=company
            ).values('employee__first_name', 'employee__last_name', 'metric_name', 'value', 'date_recorded'))
        }
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PERFORMANCE_REPORT_GENERATED',
            description=f'Generated {report_type} performance report',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Generate downloadable report URL
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"performance_report_{company.name}_{timestamp}.json"
        
        return JsonResponse({
            'success': True, 
            'data': report_data,
            'report_url': f'/api/performance/download-report/?filename={report_filename}&data={report_type}',
            'message': 'Report generated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def download_performance_report(request):
    """Download performance report as JSON file"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get parameters
        filename = request.GET.get('filename', f'performance_report_{company.name}.json')
        report_type = request.GET.get('data', 'summary')
        
        # Generate the same report data as in generate_performance_report
        report_data = {
            'company_name': company.name,
            'report_type': report_type,
            'generated_at': timezone.now().isoformat(),
            'total_employees': Employee.objects.filter(company=company).count(),
            'performance_metrics': list(PerformanceMetric.objects.filter(
                employee__company=company
            ).values('employee__first_name', 'employee__last_name', 'metric_name', 'value', 'date_recorded'))
        }
        
        # Return JSON file
        from django.http import HttpResponse
        import json
        
        response = HttpResponse(
            json.dumps(report_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_performance_reviews(request):
    """Export performance reviews to CSV"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        review_type_filter = request.GET.get('review_type', '')
        employee_filter = request.GET.get('employee', '')
        
        # Base queryset
        reviews = PerformanceReview.objects.filter(employee__company=company)
        
        # Apply filters
        if status_filter:
            reviews = reviews.filter(status=status_filter)
        if review_type_filter:
            reviews = reviews.filter(review_type=review_type_filter)
        if employee_filter:
            reviews = reviews.filter(employee__id=employee_filter)
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Employee Name', 'Department', 'Review Type', 'Status', 
            'Start Date', 'End Date', 'Overall Rating', 'Created At'
        ])
        
        # Write data
        for review in reviews:
            writer.writerow([
                f"{review.employee.first_name} {review.employee.last_name}",
                review.employee.department or 'N/A',
                review.get_review_type_display(),
                review.get_status_display(),
                review.start_date.strftime('%Y-%m-%d'),
                review.end_date.strftime('%Y-%m-%d'),
                review.overall_rating or 'N/A',
                review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PERFORMANCE_REVIEWS_EXPORTED',
            description='Exported performance reviews to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="performance_reviews_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_performance_goals(request):
    """Export performance goals to CSV"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        employee_filter = request.GET.get('employee', '')
        overdue_filter = request.GET.get('overdue', '')
        
        # Base queryset
        goals = PerformanceGoal.objects.filter(employee__company=company)
        
        # Apply filters
        if status_filter:
            goals = goals.filter(status=status_filter)
        if priority_filter:
            goals = goals.filter(priority=priority_filter)
        if employee_filter:
            goals = goals.filter(employee__id=employee_filter)
        if overdue_filter == 'true':
            goals = goals.filter(
                status__in=['NOT_STARTED', 'IN_PROGRESS'],
                target_date__lt=timezone.now().date()
            )
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Employee Name', 'Department', 'Goal Title', 'Goal Type', 'Priority', 'Status',
            'Start Date', 'Target Date', 'Current Value', 'Target Value', 'Unit', 'Progress %', 'Created At'
        ])
        
        # Write data
        for goal in goals:
            progress_percent = 0
            if goal.target_value and goal.target_value > 0:
                progress_percent = round((goal.current_value / goal.target_value) * 100, 2)
            
            writer.writerow([
                f"{goal.employee.first_name} {goal.employee.last_name}",
                goal.employee.department or 'N/A',
                goal.title,
                goal.get_goal_type_display(),
                goal.get_priority_display(),
                goal.get_status_display(),
                goal.start_date.strftime('%Y-%m-%d'),
                goal.target_date.strftime('%Y-%m-%d'),
                goal.current_value,
                goal.target_value or 'N/A',
                goal.unit or 'N/A',
                f"{progress_percent}%",
                goal.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PERFORMANCE_GOALS_EXPORTED',
            description='Exported performance goals to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="performance_goals_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_performance_feedback(request):
    """Export performance feedback to CSV"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get filter parameters
        feedback_type_filter = request.GET.get('feedback_type', '')
        status_filter = request.GET.get('status', '')
        employee_filter = request.GET.get('employee', '')
        
        # Base queryset
        feedback = Feedback.objects.filter(employee__company=company)
        
        # Apply filters
        if feedback_type_filter:
            feedback = feedback.filter(feedback_type=feedback_type_filter)
        if status_filter:
            feedback = feedback.filter(status=status_filter)
        if employee_filter:
            feedback = feedback.filter(employee__id=employee_filter)
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Employee Name', 'Department', 'Reviewer', 'Feedback Type', 'Status', 'Rating',
            'Strengths', 'Areas for Improvement', 'Suggestions', 'Overall Comments', 'Created At', 'Submitted At'
        ])
        
        # Write data
        for item in feedback:
            writer.writerow([
                f"{item.employee.first_name} {item.employee.last_name}",
                item.employee.department or 'N/A',
                item.reviewer.get_full_name() or item.reviewer.username,
                item.get_feedback_type_display(),
                item.get_status_display(),
                item.rating or 'N/A',
                item.strengths or 'N/A',
                item.areas_for_improvement or 'N/A',
                item.suggestions or 'N/A',
                item.overall_comments or 'N/A',
                item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                item.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if item.submitted_at else 'N/A'
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PERFORMANCE_FEEDBACK_EXPORTED',
            description='Exported performance feedback to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="performance_feedback_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_performance_reports(request):
    """Export performance reports to CSV"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get filter parameters
        report_type_filter = request.GET.get('report_type', '')
        period_filter = request.GET.get('period', '')
        
        # Base queryset
        reports = PerformanceReport.objects.filter(company=company)
        
        # Apply filters
        if report_type_filter:
            reports = reports.filter(report_type=report_type_filter)
        if period_filter:
            reports = reports.filter(period=period_filter)
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Report Type', 'Period', 'Period Start', 'Period End', 'Generated By', 'Generated At',
            'Include Goals', 'Include Reviews', 'Include Feedback', 'Include Metrics', 'Data Points'
        ])
        
        # Write data
        for report in reports:
            data_points = len(report.report_data) if report.report_data else 0
            writer.writerow([
                report.get_report_type_display(),
                report.get_period_display(),
                report.period_start.strftime('%Y-%m-%d'),
                report.period_end.strftime('%Y-%m-%d'),
                report.generated_by.get_full_name() or report.generated_by.username,
                report.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if report.include_goals else 'No',
                'Yes' if report.include_reviews else 'No',
                'Yes' if report.include_feedback else 'No',
                'Yes' if report.include_metrics else 'No',
                data_points
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PERFORMANCE_REPORTS_EXPORTED',
            description='Exported performance reports to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="performance_reports_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def generate_attendance_report(request):
    """Generate attendance report"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get report parameters from request
        report_type = request.POST.get('report_type', 'summary')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        department = request.POST.get('department', '')
        
        # Base queryset
        attendance = Attendance.objects.filter(employee__company=company)
        
        # Apply filters
        if date_from:
            attendance = attendance.filter(date__gte=date_from)
        if date_to:
            attendance = attendance.filter(date__lte=date_to)
        if department:
            attendance = attendance.filter(employee__department=department)
        
        # Generate report data
        report_data = {
            'company_name': company.name,
            'report_type': report_type,
            'date_from': date_from,
            'date_to': date_to,
            'department': department,
            'generated_at': timezone.now().isoformat(),
            'total_employees': Employee.objects.filter(company=company).count(),
            'total_records': attendance.count(),
            'attendance_records': []
        }
        
        # Add attendance records to report
        for record in attendance:
            hours_worked = 'N/A'
            if record.check_in_time and record.check_out_time:
                delta = record.check_out_time - record.check_in_time
                hours_worked = f"{delta.total_seconds() / 3600:.2f}"
            
            report_data['attendance_records'].append({
                'employee_name': f"{record.employee.first_name} {record.employee.last_name}",
                'department': record.employee.department or 'N/A',
                'date': record.date.strftime('%Y-%m-%d'),
                'status': record.get_status_display(),
                'check_in': record.check_in_time.strftime('%H:%M:%S') if record.check_in_time else 'N/A',
                'check_out': record.check_out_time.strftime('%H:%M:%S') if record.check_out_time else 'N/A',
                'hours_worked': hours_worked,
                'notes': record.notes or 'N/A'
            })
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='ATTENDANCE_REPORT_GENERATED',
            description=f'Generated {report_type} attendance report',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Generate downloadable report URL
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"attendance_report_{company.name}_{timestamp}.json"
        
        # For now, return the data with a download URL
        # In a real implementation, you might save this to a file and return the URL
        return JsonResponse({
            'success': True, 
            'data': report_data,
            'report_url': f'/api/attendance/download-report/?filename={report_filename}&data={report_type}',
            'message': 'Report generated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def download_attendance_report(request):
    """Download attendance report as JSON file"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get parameters
        filename = request.GET.get('filename', f'attendance_report_{company.name}.json')
        report_type = request.GET.get('data', 'summary')
        
        # Generate the same report data as in generate_attendance_report
        attendance = Attendance.objects.filter(employee__company=company)
        
        report_data = {
            'company_name': company.name,
            'report_type': report_type,
            'generated_at': timezone.now().isoformat(),
            'total_employees': Employee.objects.filter(company=company).count(),
            'total_records': attendance.count(),
            'attendance_records': []
        }
        
        # Add attendance records
        for record in attendance:
            hours_worked = 'N/A'
            if record.check_in_time and record.check_out_time:
                delta = record.check_out_time - record.check_in_time
                hours_worked = f"{delta.total_seconds() / 3600:.2f}"
            
            report_data['attendance_records'].append({
                'employee_name': f"{record.employee.first_name} {record.employee.last_name}",
                'department': record.employee.department or 'N/A',
                'date': record.date.strftime('%Y-%m-%d'),
                'status': record.get_status_display(),
                'check_in': record.check_in_time.strftime('%H:%M:%S') if record.check_in_time else 'N/A',
                'check_out': record.check_out_time.strftime('%H:%M:%S') if record.check_out_time else 'N/A',
                'hours_worked': hours_worked,
                'notes': record.notes or 'N/A'
            })
        
        # Return JSON file
        from django.http import HttpResponse
        import json
        
        response = HttpResponse(
            json.dumps(report_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_attendance_data(request):
    """Export attendance data to CSV"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        company = request.user.company_admin_profile.company
        
        # Get filter parameters
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        department = request.GET.get('department', '')
        
        # Base queryset
        attendance = Attendance.objects.filter(employee__company=company)
        
        # Apply filters
        if date_from:
            attendance = attendance.filter(date__gte=date_from)
        if date_to:
            attendance = attendance.filter(date__lte=date_to)
        if department:
            attendance = attendance.filter(employee__department=department)
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Employee Name', 'Department', 'Date', 'Status', 'Check In', 'Check Out', 'Hours Worked', 'Notes'
        ])
        
        # Write data
        for record in attendance:
            hours_worked = 'N/A'
            if record.check_in_time and record.check_out_time:
                delta = record.check_out_time - record.check_in_time
                hours_worked = f"{delta.total_seconds() / 3600:.2f}"
            
            writer.writerow([
                f"{record.employee.first_name} {record.employee.last_name}",
                record.employee.department or 'N/A',
                record.date.strftime('%Y-%m-%d'),
                record.get_status_display(),
                record.check_in_time.strftime('%H:%M:%S') if record.check_in_time else 'N/A',
                record.check_out_time.strftime('%H:%M:%S') if record.check_out_time else 'N/A',
                hours_worked,
                record.notes or 'N/A'
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='ATTENDANCE_DATA_EXPORTED',
            description='Exported attendance data to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_data_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_timesheet_data(request):
    """Export timesheet data to CSV"""
    try:
        # Check if user has company admin profile
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied. Company admin access required.'})
        
        company = request.user.company_admin_profile.company
        
        # Get filter parameters
        employee_filter = request.GET.get('employee', '')
        project_filter = request.GET.get('project', '')
        status_filter = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Base queryset
        timesheets = Timesheet.objects.filter(employee__company=company)
        
        # Apply filters
        if employee_filter:
            timesheets = timesheets.filter(employee__id=employee_filter)
        if project_filter:
            timesheets = timesheets.filter(project__id=project_filter)
        if status_filter:
            timesheets = timesheets.filter(status=status_filter)
        if date_from:
            timesheets = timesheets.filter(date__gte=date_from)
        if date_to:
            timesheets = timesheets.filter(date__lte=date_to)
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Employee Name', 'Employee Email', 'Department', 'Project', 'Date', 
            'Start Time', 'End Time', 'Break Duration', 'Total Hours', 
            'Task Description', 'Work Performed', 'Status', 'Billable', 
            'Hourly Rate', 'Submitted At', 'Approved By', 'Approved At'
        ])
        
        # Write data rows
        for timesheet in timesheets:
            writer.writerow([
                f"{timesheet.employee.first_name} {timesheet.employee.last_name}",
                timesheet.employee.email,
                timesheet.employee.department.name if timesheet.employee.department else 'No Department',
                timesheet.project.name if timesheet.project else 'No Project',
                timesheet.date.strftime('%Y-%m-%d'),
                timesheet.start_time.strftime('%H:%M'),
                timesheet.end_time.strftime('%H:%M'),
                str(timesheet.break_duration),
                str(timesheet.total_hours),
                timesheet.task_description,
                timesheet.work_performed,
                timesheet.get_status_display(),
                'Yes' if timesheet.billable else 'No',
                str(timesheet.hourly_rate) if timesheet.hourly_rate else '',
                timesheet.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if timesheet.submitted_at else '',
                f"{timesheet.approved_by.first_name} {timesheet.approved_by.last_name}" if timesheet.approved_by else '',
                timesheet.approved_at.strftime('%Y-%m-%d %H:%M:%S') if timesheet.approved_at else ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='TIMESHEET_DATA_EXPORTED',
            description='Exported timesheet data to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="timesheet_data_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def export_shift_data(request):
    """Export shift data to CSV"""
    try:
        # Check if user has company admin profile
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied. Company admin access required.'})
        
        company = request.user.company_admin_profile.company
        
        # Get shifts and employee assignments
        shifts = Shift.objects.filter(company=company)
        employee_shifts = EmployeeShift.objects.filter(shift__company=company)
        
        # Create CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header for shifts
        writer.writerow([
            'Shift Name', 'Shift Type', 'Start Time', 'End Time', 'Break Duration', 
            'Max Employees', 'Hourly Rate Multiplier', 'Overtime Rate Multiplier', 
            'Description', 'Is Active', 'Created At'
        ])
        
        # Write shift data
        for shift in shifts:
            writer.writerow([
                shift.name,
                shift.get_shift_type_display(),
                shift.start_time.strftime('%H:%M'),
                shift.end_time.strftime('%H:%M'),
                str(shift.break_duration),
                str(shift.max_employees) if shift.max_employees else 'Unlimited',
                str(shift.hourly_rate_multiplier),
                str(shift.overtime_rate_multiplier),
                shift.description,
                'Yes' if shift.is_active else 'No',
                shift.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Add separator row
        writer.writerow([])
        writer.writerow(['EMPLOYEE ASSIGNMENTS'])
        writer.writerow([])
        
        # Write header for employee assignments
        writer.writerow([
            'Employee Name', 'Employee Email', 'Department', 'Shift Name', 'Shift Type',
            'Start Date', 'End Date', 'Is Active', 'Assignment Created At'
        ])
        
        # Write employee assignment data
        for assignment in employee_shifts:
            writer.writerow([
                f"{assignment.employee.first_name} {assignment.employee.last_name}",
                assignment.employee.email,
                assignment.employee.department.name if assignment.employee.department else 'No Department',
                assignment.shift.name,
                assignment.shift.get_shift_type_display(),
                assignment.start_date.strftime('%Y-%m-%d'),
                assignment.end_date.strftime('%Y-%m-%d') if assignment.end_date else 'Ongoing',
                'Yes' if assignment.is_active else 'No',
                assignment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='SHIFT_DATA_EXPORTED',
            description='Exported shift data to CSV',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return CSV file
        from django.http import HttpResponse
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="shift_data_{company.name}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Payment Method API Views
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def add_payment_method(request):
    """Add a new payment method"""
    try:
        print(f"Add payment method request from user: {request.user}")
        print(f"User has company_admin_profile: {hasattr(request.user, 'company_admin_profile')}")
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")
        print(f"Request body (raw): {request.body}")
        print(f"Request body (decoded): {request.body.decode('utf-8') if request.body else 'Empty'}")
        
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'success': False, 'error': f'Invalid JSON data: {str(e)}'}, status=400)
        
        if not hasattr(request.user, 'company_admin_profile'):
            print("Access denied - no company_admin_profile")
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        company = request.user.company_admin_profile.company
        
        # Extract payment method data
        payment_type = data.get('payment_type', 'CREDIT_CARD')
        card_type = data.get('card_type')
        last_four_digits = data.get('last_four_digits')
        expiry_month = data.get('expiry_month')
        expiry_year = data.get('expiry_year')
        cardholder_name = data.get('cardholder_name')
        is_default = data.get('is_default', False)
        
        # Validate required fields
        if not last_four_digits:
            print("Validation failed - no last four digits")
            return JsonResponse({'success': False, 'error': 'Last four digits are required'}, status=400)
        
        print(f"Creating payment method for company: {company}")
        print(f"Payment method data: {payment_type}, {card_type}, {last_four_digits}, {expiry_month}, {expiry_year}, {cardholder_name}")
        
        # Create payment method
        payment_method = PaymentMethod.objects.create(
            company=company,
            payment_type=payment_type,
            card_type=card_type,
            last_four_digits=last_four_digits,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            cardholder_name=cardholder_name,
            is_default=is_default,
            created_by=request.user
        )
        
        print(f"Payment method created successfully: {payment_method}")
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method added successfully',
            'payment_method': {
                'id': payment_method.id,
                'display_name': payment_method.get_display_name(),
                'expiry_display': payment_method.get_expiry_display(),
                'is_default': payment_method.is_default
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_payment_method(request):
    """Update an existing payment method"""
    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        company = request.user.company_admin_profile.company
        
        try:
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id,
                company=company
            )
        except PaymentMethod.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment method not found'}, status=404)
        
        # Update fields
        if 'cardholder_name' in data:
            payment_method.cardholder_name = data['cardholder_name']
        if 'is_default' in data:
            payment_method.is_default = data['is_default']
        if 'is_active' in data:
            payment_method.is_active = data['is_active']
        
        payment_method.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method updated successfully',
            'payment_method': {
                'id': payment_method.id,
                'display_name': payment_method.get_display_name(),
                'expiry_display': payment_method.get_expiry_display(),
                'is_default': payment_method.is_default,
                'is_active': payment_method.is_active
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def remove_payment_method(request):
    """Remove a payment method"""
    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        company = request.user.company_admin_profile.company
        
        try:
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id,
                company=company
            )
        except PaymentMethod.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment method not found'}, status=404)
        
        payment_method.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method removed successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_payment_methods(request):
    """Get all payment methods for a company"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        company = request.user.company_admin_profile.company
        payment_methods = PaymentMethod.objects.filter(company=company, is_active=True)
        
        methods_data = []
        for method in payment_methods:
            methods_data.append({
                'id': method.id,
                'payment_type': method.payment_type,
                'card_type': method.card_type,
                'display_name': method.get_display_name(),
                'expiry_display': method.get_expiry_display(),
                'cardholder_name': method.cardholder_name,
                'is_default': method.is_default,
                'created_at': method.created_at.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'success': True,
            'payment_methods': methods_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_timesheet(request):
    """Create a timesheet entry"""
    try:
        # Parse JSON data from request body
        import json
        data = json.loads(request.body)
        
        # Get employee profile
        if not hasattr(request.user, 'employee_profile'):
            return JsonResponse({'success': False, 'message': 'Employee profile not found'}, status=400)
        
        employee = request.user.employee_profile
        
        # Extract form data
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        task_description = data.get('task_description', '')
        work_performed = data.get('work_performed', '')
        
        # Validate required fields
        if not all([date_str, start_time_str, end_time_str]):
            return JsonResponse({'success': False, 'message': 'Date, start time, and end time are required'}, status=400)
        
        # Parse date and times
        from datetime import datetime, date, time
        
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError as e:
            return JsonResponse({'success': False, 'message': f'Invalid date/time format: {str(e)}'}, status=400)
        
        # Validate times
        start_datetime = datetime.combine(entry_date, start_time)
        end_datetime = datetime.combine(entry_date, end_time)
        
        if end_datetime <= start_datetime:
            return JsonResponse({'success': False, 'message': 'End time must be after start time'}, status=400)
        
        # Create timesheet entry - let the model's save method calculate total_hours
        timesheet = Timesheet.objects.create(
            employee=employee,
            date=entry_date,
            start_time=start_time,
            end_time=end_time,
            task_description=task_description,
            work_performed=work_performed,
            status='DRAFT'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Timesheet entry created successfully',
            'timesheet_id': timesheet.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating timesheet: {str(e)}'}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_timesheet(request, timesheet_id):
    """Update a timesheet entry"""
    try:
        # Parse JSON data from request body
        import json
        data = json.loads(request.body)
        
        # Get employee profile
        if not hasattr(request.user, 'employee_profile'):
            return JsonResponse({'success': False, 'message': 'Employee profile not found'}, status=400)
        
        employee = request.user.employee_profile
        
        # Get the timesheet
        try:
            timesheet = Timesheet.objects.get(
                id=timesheet_id,
                employee=employee
            )
        except Timesheet.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Timesheet not found'}, status=404)
        
        # Only allow editing of draft timesheets
        if timesheet.status != 'DRAFT':
            return JsonResponse({'success': False, 'message': 'Only draft timesheets can be edited'}, status=400)
        
        # Extract form data
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        task_description = data.get('task_description', '')
        work_performed = data.get('work_performed', '')
        
        # Validate required fields
        if not all([date_str, start_time_str, end_time_str]):
            return JsonResponse({'success': False, 'message': 'Date, start time, and end time are required'}, status=400)
        
        # Parse date and times
        from datetime import datetime
        
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError as e:
            return JsonResponse({'success': False, 'message': f'Invalid date/time format: {str(e)}'}, status=400)
        
        # Validate times
        start_datetime = datetime.combine(entry_date, start_time)
        end_datetime = datetime.combine(entry_date, end_time)
        
        if end_datetime <= start_datetime:
            return JsonResponse({'success': False, 'message': 'End time must be after start time'}, status=400)
        
        # Update timesheet entry - let the model's save method calculate total_hours
        timesheet.date = entry_date
        timesheet.start_time = start_time
        timesheet.end_time = end_time
        timesheet.task_description = task_description
        timesheet.work_performed = work_performed
        timesheet.save()  # This will trigger the model's save method to calculate total_hours
        
        return JsonResponse({
            'success': True,
            'message': 'Timesheet entry updated successfully',
            'timesheet_id': timesheet.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating timesheet: {str(e)}'}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def submit_timesheet(request, timesheet_id):
    """Submit a timesheet for approval"""
    try:
        # Get employee profile
        if not hasattr(request.user, 'employee_profile'):
            return JsonResponse({'success': False, 'message': 'Employee profile not found'}, status=400)
        
        employee = request.user.employee_profile
        
        # Get the timesheet
        try:
            timesheet = Timesheet.objects.get(
                id=timesheet_id,
                employee=employee
            )
        except Timesheet.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Timesheet not found'}, status=404)
        
        # Only allow submitting draft timesheets
        if timesheet.status != 'DRAFT':
            return JsonResponse({'success': False, 'message': 'Only draft timesheets can be submitted'}, status=400)
        
        # Validate times
        from datetime import datetime
        start_datetime = datetime.combine(timesheet.date, timesheet.start_time)
        end_datetime = datetime.combine(timesheet.date, timesheet.end_time)
        
        if end_datetime <= start_datetime:
            return JsonResponse({'success': False, 'message': 'End time must be after start time'}, status=400)
        
        # Submit the timesheet
        timesheet.status = 'SUBMITTED'
        timesheet.submitted_at = datetime.now()
        timesheet.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=employee.company,
            action='TIMESHEET_SUBMITTED',
            description=f'Submitted timesheet entry {timesheet.id}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Timesheet submitted successfully',
            'timesheet_id': timesheet.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error submitting timesheet: {str(e)}'}, status=500)
