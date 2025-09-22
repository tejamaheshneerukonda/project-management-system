from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from core.models import (
    Company, Employee, Project, Task, Notification, Announcement,
    PerformanceMetric, CompanyMetric, CompanySetting, UserPreference,
    WorkflowTemplate, WorkflowInstance, ActivityLog
)

class Command(BaseCommand):
    help = 'Populate database with sample data for enhanced features'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Get or create a company - use existing 'teja' company if available
        try:
            company = Company.objects.get(name='teja')
            self.stdout.write(f'Using existing company: {company.name}')
        except Company.DoesNotExist:
            company, created = Company.objects.get_or_create(
                name='TechCorp Solutions',
                defaults={
                    'domain': 'techcorp.com',
                    'max_users': 100,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created company: {company.name}')
        
        # Create company settings
        settings, created = CompanySetting.objects.get_or_create(
            company=company,
            defaults={
                'timezone': 'America/New_York',
                'date_format': 'MM/DD/YYYY',
                'currency': 'USD',
                'working_hours_start': '09:00',
                'working_hours_end': '17:00',
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'allow_employee_registration': True,
                'require_email_verification': True,
                'max_file_upload_size': 10
            }
        )
        
        # Create sample employees
        departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']
        positions = ['Manager', 'Developer', 'Analyst', 'Coordinator', 'Specialist']
        
        employees = []
        for i in range(20):
            employee, created = Employee.objects.get_or_create(
                company=company,
                employee_id=f'EMP{i+1:03d}',
                defaults={
                    'first_name': f'Employee{i+1}',
                    'last_name': f'LastName{i+1}',
                    'email': f'employee{i+1}@techcorp.com',
                    'department': random.choice(departments),
                    'position': random.choice(positions),
                    'is_verified': random.choice([True, True, True, False])  # 75% verified
                }
            )
            employees.append(employee)
        
        self.stdout.write(f'Created {len(employees)} employees')
        
        # Create sample projects
        project_names = [
            'Website Redesign',
            'Mobile App Development',
            'Database Migration',
            'Customer Portal',
            'Analytics Dashboard',
            'API Integration',
            'Security Audit',
            'Performance Optimization'
        ]
        
        projects = []
        for i, name in enumerate(project_names):
            project, created = Project.objects.get_or_create(
                company=company,
                name=name,
                defaults={
                    'description': f'Description for {name} project',
                    'status': random.choice(['PLANNING', 'ACTIVE', 'ACTIVE', 'COMPLETED']),
                    'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                    'start_date': timezone.now().date() - timedelta(days=random.randint(1, 30)),
                    'end_date': timezone.now().date() + timedelta(days=random.randint(30, 90)),
                    'budget': Decimal(random.randint(10000, 100000)),
                    'project_manager': random.choice(employees) if employees else None
                }
            )
            projects.append(project)
        
        self.stdout.write(f'Created {len(projects)} projects')
        
        # Create sample tasks
        task_titles = [
            'Design mockups',
            'Write documentation',
            'Code review',
            'Testing',
            'Deployment',
            'User training',
            'Bug fixes',
            'Performance testing',
            'Security testing',
            'Integration testing'
        ]
        
        tasks = []
        for project in projects:
            for i in range(random.randint(3, 8)):
                task, created = Task.objects.get_or_create(
                    project=project,
                    title=f"{random.choice(task_titles)} - {project.name}",
                    defaults={
                        'description': f'Task description for {project.name}',
                        'status': random.choice(['TODO', 'IN_PROGRESS', 'REVIEW', 'DONE']),
                        'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                        'due_date': timezone.now() + timedelta(days=random.randint(1, 30)),
                        'estimated_hours': Decimal(random.randint(1, 40)),
                        'actual_hours': Decimal(random.randint(1, 40)) if random.choice([True, False]) else None,
                        'assigned_to': random.choice(employees) if employees else None
                    }
                )
                tasks.append(task)
        
        self.stdout.write(f'Created {len(tasks)} tasks')
        
        # Create sample performance metrics
        metric_types = ['PRODUCTIVITY', 'ATTENDANCE', 'TASK_COMPLETION', 'CUSTOMER_SATISFACTION']
        
        for employee in employees[:10]:  # Only for first 10 employees
            for metric_type in metric_types:
                PerformanceMetric.objects.get_or_create(
                    employee=employee,
                    metric_type=metric_type,
                    period_start=timezone.now().date() - timedelta(days=30),
                    period_end=timezone.now().date(),
                    defaults={
                        'value': Decimal(random.randint(70, 100)),
                        'target_value': Decimal(random.randint(80, 95)),
                        'notes': f'Performance notes for {employee.first_name}'
                    }
                )
        
        self.stdout.write('Created performance metrics')
        
        # Create sample notifications
        notification_titles = [
            'New project assigned',
            'Task deadline approaching',
            'System maintenance scheduled',
            'New employee joined',
            'Project completed',
            'Performance review due',
            'Training session scheduled',
            'Security update required'
        ]
        
        for i in range(15):
            Notification.objects.get_or_create(
                company=company,
                title=random.choice(notification_titles),
                defaults={
                    'message': f'This is a sample notification message {i+1}',
                    'notification_type': random.choice(['INFO', 'WARNING', 'SUCCESS']),
                    'is_read': random.choice([True, False]),
                    'is_global': random.choice([True, False])
                }
            )
        
        self.stdout.write('Created notifications')
        
        # Create sample announcements
        announcement_titles = [
            'Company Meeting Next Week',
            'New Policy Update',
            'Holiday Schedule',
            'Office Renovation',
            'Team Building Event',
            'System Upgrade Notice'
        ]
        
        # Create a superuser for announcements
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@techcorp.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True
            }
        )
        
        for i, title in enumerate(announcement_titles):
            Announcement.objects.get_or_create(
                company=company,
                title=title,
                defaults={
                    'content': f'This is the content for announcement: {title}. Please read carefully.',
                    'priority': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                    'is_active': True,
                    'created_by': admin_user,
                    'expires_at': timezone.now() + timedelta(days=30)
                }
            )
        
        self.stdout.write('Created announcements')
        
        # Create sample company metrics
        metric_names = [
            'Monthly Revenue',
            'Customer Satisfaction',
            'Employee Productivity',
            'Project Completion Rate',
            'System Uptime',
            'Customer Acquisition Cost',
            'Employee Retention Rate',
            'Average Project Duration'
        ]
        
        for i, metric_name in enumerate(metric_names):
            CompanyMetric.objects.get_or_create(
                company=company,
                metric_name=metric_name,
                period_start=timezone.now().date() - timedelta(days=30),
                period_end=timezone.now().date(),
                defaults={
                    'metric_value': Decimal(random.randint(1000, 100000)),
                    'metric_unit': random.choice(['USD', '%', 'hours', 'days', 'count']),
                    'category': random.choice(['REVENUE', 'PRODUCTIVITY', 'CUSTOMER', 'OPERATIONAL'])
                }
            )
        
        self.stdout.write('Created company metrics')
        
        # Create sample workflow templates
        workflow_templates = [
            {
                'name': 'Employee Onboarding',
                'description': 'Standard process for onboarding new employees',
                'steps': [
                    {'name': 'Send welcome email', 'assigned_to': 'HR'},
                    {'name': 'Schedule orientation', 'assigned_to': 'HR'},
                    {'name': 'Setup workstation', 'assigned_to': 'IT'},
                    {'name': 'Complete paperwork', 'assigned_to': 'Employee'},
                    {'name': 'First day meeting', 'assigned_to': 'Manager'}
                ]
            },
            {
                'name': 'Project Approval',
                'description': 'Process for approving new projects',
                'steps': [
                    {'name': 'Submit project proposal', 'assigned_to': 'Project Manager'},
                    {'name': 'Review budget', 'assigned_to': 'Finance'},
                    {'name': 'Technical review', 'assigned_to': 'Engineering'},
                    {'name': 'Final approval', 'assigned_to': 'CEO'}
                ]
            }
        ]
        
        for template_data in workflow_templates:
            WorkflowTemplate.objects.get_or_create(
                company=company,
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'steps': template_data['steps'],
                    'is_active': True,
                    'created_by': admin_user
                }
            )
        
        self.stdout.write('Created workflow templates')
        
        # Create sample activity logs
        actions = [
            'LOGIN',
            'LOGOUT',
            'PROJECT_CREATED',
            'TASK_UPDATED',
            'EMPLOYEE_ADDED',
            'SETTINGS_UPDATED',
            'REPORT_GENERATED',
            'FILE_UPLOADED'
        ]
        
        for i in range(50):
            ActivityLog.objects.create(
                user=admin_user,
                company=company,
                action=random.choice(actions),
                description=f'Sample activity log entry {i+1}',
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Sample Browser)',
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30))
            )
        
        self.stdout.write('Created activity logs')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
