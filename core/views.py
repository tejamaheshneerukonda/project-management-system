from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
import json
from .models import (
    Company, Employee, CompanyAdmin, SystemOwner, SubscriptionPlan, CompanySubscription, SubscriptionPayment,
    ActivityLog, PerformanceMetric, Project, Task, Notification, NotificationTemplate, 
    NotificationPreference, NotificationDigest, Announcement, CompanyMetric, 
    CompanySetting, UserPreference, WorkflowTemplate, WorkflowInstance, PerformanceReview, 
    PerformanceGoal, Feedback, PerformanceReport, Attendance, LeaveRequest, Timesheet,
    ChatRoom, ChatMessage, ChatParticipant, 
    Shift, EmployeeShift, OnboardingWorkflow, OnboardingTask, OnboardingAssignment,
    OnboardingTaskAssignment, OnboardingDocument, OnboardingDocumentSubmission,
    DocumentCategory, Document, DocumentVersion, DocumentShare, DocumentEmployeeShare,
    DocumentDepartmentShare, DocumentAccess, DocumentComment, DocumentTemplate,
    PaymentMethod, AuditLog, ChatRoom, ChatMessage, ChatParticipant, ChatNotification
)
from .forms import CompanyRegistrationForm, CompanyAdminRegistrationForm, EmployeeCSVImportForm, EmployeeVerificationForm, EmployeeRegistrationForm
from .logging_utils import SystemLogger, log_auth, log_user_action, log_company_action, log_backup_action, log_security_event, log_system_event, log_error
from .decorators import audit_log

def home(request):
    """Home page view"""
    context = {
        'title': 'Home',
        'user': request.user,
    }
    return render(request, 'core/home.html', context)

def pricing(request):
    """Pricing page view"""
    # Get subscription plans for display
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    # Get user's current plan information
    current_plan = None
    current_subscription_type = 'FREE'
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'company_admin_profile'):
            company = request.user.company_admin_profile.company
            current_subscription_type = company.subscription_type
            current_plan = company
        elif hasattr(request.user, 'system_owner_profile'):
            current_subscription_type = 'ENTERPRISE'  # System owners have enterprise access
    
    context = {
        'title': 'Pricing',
        'user': request.user,
        'plans': plans,
        'current_plan': current_plan,
        'current_subscription_type': current_subscription_type,
    }
    return render(request, 'core/pricing.html', context)

def terms_and_conditions(request):
    """Terms and Conditions page"""
    context = {
        'title': 'Terms and Conditions',
    }
    return render(request, 'core/terms_and_conditions.html', context)

def privacy_policy(request):
    """Privacy Policy page"""
    context = {
        'title': 'Privacy Policy',
    }
    return render(request, 'core/privacy_policy.html', context)

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Log successful login
            log_auth(f'User {user.username} logged in successfully', user, request)
            
            # Create ActivityLog entry for dashboard activity count
            if hasattr(user, 'company_admin_profile'):
                company = user.company_admin_profile.company
                ActivityLog.objects.create(
                    user=user,
                    company=company,
                    action='LOGIN',
                    description=f'Company admin {user.username} logged in',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            
            # Log failed login attempt
            log_security_event(f'Failed login attempt for username: {username}', request=request, additional_data={'username': username})
    
    return render(request, 'core/login.html')

def registration_selection(request):
    """Registration type selection page"""
    context = {
        'title': 'Choose Registration Type',
    }
    return render(request, 'core/registration_selection.html', context)

def register_view(request):
    """Registration view - redirects to registration selection"""
    return redirect('core:registration_selection')

def logout_view(request):
    """User logout view"""
    username = request.user.username if request.user.is_authenticated else 'Anonymous'
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    
    # Log logout
    log_auth(f'User {username} logged out', request=request)
    
    return redirect('core:home')

@login_required
def dashboard(request):
    """Generic dashboard view that redirects based on user type"""
    if hasattr(request.user, 'system_owner_profile'):
        return redirect('core:owner_dashboard')
    elif hasattr(request.user, 'company_admin_profile'):
        return redirect('core:company_dashboard')
    elif hasattr(request.user, 'employee_profile'):
        return redirect('core:employee_dashboard')
    else:
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')

@login_required
def owner_dashboard(request):
    """System owner dashboard"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.contrib.auth.models import User
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    import psutil
    import os
    
    # Basic company data
    companies = Company.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-created_at')
    total_companies = companies.count()
    active_companies = companies.filter(is_active=True).count()
    inactive_companies = total_companies - active_companies
    
    # User statistics
    total_users = User.objects.count()
    total_employees = Employee.objects.count()
    total_admins = CompanyAdmin.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_companies = companies.filter(created_at__gte=thirty_days_ago).count()
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Employee statistics
    verified_employees = Employee.objects.filter(is_verified=True).count()
    unverified_employees = total_employees - verified_employees
    registered_employees = Employee.objects.filter(user_account__isnull=False).count()
    unregistered_employees = total_employees - registered_employees
    
    # System health metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_health = {
            'cpu_usage': round(cpu_percent, 1),
            'memory_usage': round(memory.percent, 1),
            'disk_usage': round(disk.percent, 1),
            'memory_available': round(memory.available / (1024**3), 2),  # GB
            'disk_free': round(disk.free / (1024**3), 2),  # GB
        }
    except:
        system_health = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'memory_available': 0,
            'disk_free': 0,
        }
    
    # Recent activities for activity feed
    recent_activities = []
    
    # Recent company registrations
    for company in companies[:5]:
        recent_activities.append({
            'type': 'company_registered',
            'title': f'New company registered: {company.name}',
            'description': f'Company {company.name} was registered with domain {company.domain}',
            'timestamp': company.created_at,
            'icon': 'fas fa-building',
            'color': 'primary'
        })
    
    # Recent user registrations
    recent_users_list = User.objects.filter(date_joined__gte=thirty_days_ago).order_by('-date_joined')[:5]
    for user in recent_users_list:
        recent_activities.append({
            'type': 'user_registered',
            'title': f'New user registered: {user.username}',
            'description': f'User {user.username} joined the system',
            'timestamp': user.date_joined,
            'icon': 'fas fa-user-plus',
            'color': 'success'
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]  # Show only 10 most recent
    
    # Calculate growth percentages (more meaningful calculation)
    companies_growth = 0
    users_growth = 0
    
    # For growth, we need to compare with previous period
    # Since we don't have historical data, show recent activity as "new this month"
    if recent_companies > 0:
        companies_growth = recent_companies  # Show count of new companies
    if recent_users > 0:
        users_growth = recent_users  # Show count of new users
    
    # Revenue calculation (based on actual subscription data)
    try:
        # Calculate real revenue from active subscriptions
        active_subscriptions = CompanySubscription.objects.filter(status='ACTIVE')
        monthly_revenue = sum(subscription.plan.monthly_price for subscription in active_subscriptions)
        total_revenue = monthly_revenue * 12  # Annual projection
        
        # Subscription statistics
        total_subscriptions = CompanySubscription.objects.count()
        trial_subscriptions = CompanySubscription.objects.filter(status='TRIAL').count()
        expired_subscriptions = CompanySubscription.objects.filter(status='EXPIRED').count()
        
    except Exception as e:
        # Fallback to simulated revenue if no subscriptions exist
        base_monthly_fee = 99  # Base monthly fee per company
        monthly_revenue = total_companies * base_monthly_fee
        total_revenue = monthly_revenue * 12  # Annual projection
        total_subscriptions = 0
        trial_subscriptions = 0
        expired_subscriptions = 0
    
    # Get owner profile information
    owner_profile = request.user.system_owner_profile
    
    context = {
        'title': 'Owner Dashboard',
        'companies': companies,
        'owner_profile': owner_profile,
        
        # Company statistics
        'total_companies': total_companies,
        'active_companies': active_companies,
        'inactive_companies': inactive_companies,
        'recent_companies': recent_companies,
        'companies_growth': companies_growth,
        
        # User statistics
        'total_users': total_users,
        'active_users': active_users,
        'total_employees': total_employees,
        'total_admins': total_admins,
        'verified_employees': verified_employees,
        'unverified_employees': unverified_employees,
        'registered_employees': registered_employees,
        'unregistered_employees': unregistered_employees,
        'recent_users': recent_users,
        'users_growth': users_growth,
        
        # Revenue statistics
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        
        # Subscription statistics
        'total_subscriptions': total_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        
        # System health
        'system_health': system_health,
        
        # Activity feed
        'recent_activities': recent_activities,
        
        # Additional metrics
        'avg_employees_per_company': round(total_employees / total_companies, 1) if total_companies > 0 else 0,
        'verification_rate': round((verified_employees / total_employees) * 100, 1) if total_employees > 0 else 0,
    }
    return render(request, 'core/owner_dashboard.html', context)

@login_required
def owner_profile_settings(request):
    """Owner profile settings page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    owner_profile = request.user.system_owner_profile
    
    if request.method == 'POST':
        # Update owner profile
        owner_profile.phone = request.POST.get('phone', '')
        owner_profile.save()
        
        # Update user information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:owner_profile_settings')
    
    context = {
        'title': 'Owner Profile Settings',
        'owner_profile': owner_profile,
    }
    return render(request, 'core/owner_profile_settings.html', context)

@login_required
@audit_log('COMPANY_MANAGEMENT', 'COMPANY', 'Company registration', 'HIGH')
def register_company(request):
    """Register a new company (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create company (without admin user)
                    company = form.save(commit=False)
                    company.admin_user = None  # No admin user yet
                    company.save()
                    
                    messages.success(request, f'Company "{company.name}" registered successfully!')
                    messages.info(request, f'Company Key: {company.company_key}')
                    messages.warning(request, 'Give this key to the company admin to complete registration.')
                    return redirect('core:owner_dashboard')
                    
            except Exception as e:
                messages.error(request, f'Error creating company: {str(e)}')
    else:
        form = CompanyRegistrationForm()
    
    context = {
        'title': 'Register Company',
        'form': form,
    }
    return render(request, 'core/register_company.html', context)

@audit_log('USER_MANAGEMENT', 'USER', 'Company admin registration', 'HIGH')
def company_admin_registration(request):
    """Company admin registration - creates new company"""
    if request.method == 'POST':
        form = CompanyAdminRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create company admin user
                    admin_user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
                    
                    # Create new company
                    company = Company.objects.create(
                        name=form.cleaned_data['company_name'],
                        domain=form.cleaned_data['company_domain'],
                        admin_user=admin_user,
                        is_active=True
                    )
                    
                    # Create company admin profile
                    CompanyAdmin.objects.create(
                        user=admin_user,
                        company=company,
                        phone=form.cleaned_data.get('phone', '')
                    )
                    
                    messages.success(request, f'Registration successful! Welcome to {company.name}.')
                    messages.info(request, 'You are now using the free version. You can upgrade anytime for more features.')
                    messages.warning(request, 'You can now log in with your credentials.')
                    return redirect('core:login')
                    
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
    else:
        form = CompanyAdminRegistrationForm()
    
    context = {
        'title': 'Company Admin Registration',
        'form': form,
    }
    return render(request, 'core/company_admin_registration.html', context)

@login_required
def license_activation(request):
    """License activation page for company admins"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    if request.method == 'POST':
        license_key = request.POST.get('license_key', '').strip()
        
        if license_key:
            # Simple license validation (in real app, this would check against a database or API)
            if license_key.startswith('PM-PRO-') and len(license_key) == 20:
                # Activate premium features
                company.license_key = license_key
                company.is_premium = True
                company.subscription_type = 'PROFESSIONAL'
                company.license_expires_at = timezone.now() + timedelta(days=365)  # 1 year
                company.save()
                
                messages.success(request, 'License activated successfully! You now have access to premium features.')
                return redirect('core:company_dashboard')
            else:
                messages.error(request, 'Invalid license key. Please check your key and try again.')
        else:
            messages.error(request, 'Please enter a license key.')
    
    context = {
        'title': 'License Activation',
        'company': company,
    }
    return render(request, 'core/license_activation.html', context)

@login_required
def company_details(request, company_id):
    """View detailed information about a company (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    try:
        company = Company.objects.get(id=company_id)
        employees = Employee.objects.filter(company=company)
        
        context = {
            'title': f'{company.name} - Details',
            'company': company,
            'employees': employees,
            'total_employees': employees.count(),
            'verified_employees': employees.filter(is_verified=True).count(),
            'registered_users': employees.filter(user_account__isnull=False).count(),
        }
        return render(request, 'core/company_details.html', context)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
        return redirect('core:owner_dashboard')

@login_required
def edit_company(request, company_id):
    """Edit company information (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    try:
        company = Company.objects.get(id=company_id)
        
        if request.method == 'POST':
            form = CompanyRegistrationForm(request.POST, instance=company)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Update company
                        company = form.save()
                        
                        messages.success(request, f'Company "{company.name}" updated successfully!')
                        return redirect('core:company_details', company_id=company.id)
                        
                except Exception as e:
                    messages.error(request, f'Error updating company: {str(e)}')
        else:
            # Pre-populate form with existing data
            form_data = {
                'name': company.name,
                'domain': company.domain,
                'max_users': company.max_users,
            }
            form = CompanyRegistrationForm(initial=form_data)
        
        context = {
            'title': f'Edit {company.name}',
            'form': form,
            'company': company,
            'total_employees': company.employees.count(),
            'verified_employees': company.employees.filter(is_verified=True).count(),
            'registered_employees': company.employees.filter(user_account__isnull=False).count(),
        }
        return render(request, 'core/edit_company.html', context)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
        return redirect('core:owner_dashboard')

@login_required
@audit_log('COMPANY_MANAGEMENT', 'COMPANY', 'Company status toggle', 'HIGH')
def toggle_company_status(request, company_id):
    """Toggle company active/inactive status (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    try:
        company = Company.objects.get(id=company_id)
        company.is_active = not company.is_active
        company.save()
        
        status = "activated" if company.is_active else "deactivated"
        messages.success(request, f'Company "{company.name}" has been {status}.')
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
    
    return redirect('core:owner_dashboard')

@login_required
@audit_log('COMPANY_MANAGEMENT', 'COMPANY', 'Company deletion', 'CRITICAL')
def delete_company(request, company_id):
    """Delete a company and all associated data (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    try:
        company = Company.objects.get(id=company_id)
        company_name = company.name
        
        # Count all related data before deletion
        employee_count = company.employees.count()
        admin_count = company.admins.count()
        admin_user = company.admin_user
        
        # Log detailed deletion information
        from core.logging_utils import SystemLogger
        SystemLogger.log(
            'WARNING',
            'COMPANY',
            f'Company "{company_name}" deletion initiated - Employees: {employee_count}, Admins: {admin_count}, Admin User: {admin_user.username if admin_user else "None"}',
            user=request.user,
            request=request
        )
        
        # Delete company (this will cascade delete all related objects)
        # Django will automatically delete:
        # - All employees (Employee model)
        # - All employee user accounts (User model via employee.user_account)
        # - Company admin profile (CompanyAdmin model)
        # - Company admin user account (User model via company.admin_user)
        company.delete()
        
        # Log successful deletion
        SystemLogger.log(
            'WARNING',
            'COMPANY',
            f'Company "{company_name}" and all associated data successfully deleted',
            user=request.user,
            request=request
        )
        
        messages.success(request, f'Company "{company_name}" and all associated data have been permanently deleted.')
        
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
    except Exception as e:
        messages.error(request, f'Error deleting company: {str(e)}')
    
    return redirect('core:all_companies')

@login_required
def bulk_delete_companies(request):
    """Bulk delete companies (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    if request.method == 'POST':
        company_ids = request.POST.getlist('company_ids')
        
        if not company_ids:
            messages.error(request, 'No companies selected for deletion.')
            return redirect('core:all_companies')
        
        try:
            deleted_count = 0
            deleted_names = []
            
            # Log the bulk deletion
            from core.logging_utils import SystemLogger
            
            for company_id in company_ids:
                try:
                    company = Company.objects.get(id=company_id)
                    company_name = company.name
                    
                    # Count all related data before deletion
                    employee_count = company.employees.count()
                    admin_count = company.admins.count()
                    admin_user = company.admin_user
                    
                    # Log detailed deletion information
                    SystemLogger.log(
                        'WARNING',
                        'COMPANY',
                        f'Company "{company_name}" bulk deletion - Employees: {employee_count}, Admins: {admin_count}, Admin User: {admin_user.username if admin_user else "None"}',
                        user=request.user,
                        request=request
                    )
                    
                    # Delete company (cascade deletes all related data)
                    company.delete()
                    
                    # Log successful deletion
                    SystemLogger.log(
                        'WARNING',
                        'COMPANY',
                        f'Company "{company_name}" and all associated data successfully deleted (bulk operation)',
                        user=request.user,
                        request=request
                    )
                    
                    deleted_count += 1
                    deleted_names.append(company_name)
                    
                except Company.DoesNotExist:
                    continue
            
            if deleted_count > 0:
                messages.success(request, f'Successfully deleted {deleted_count} companies: {", ".join(deleted_names)}')
            else:
                messages.error(request, 'No companies were deleted.')
                
        except Exception as e:
            messages.error(request, f'Error during bulk deletion: {str(e)}')
    
    return redirect('core:all_companies')

@login_required
def export_companies(request):
    """Export companies data to CSV (owner only)"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="companies_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Company Name', 'Domain', 'Admin Username', 'Admin Email', 
        'Admin Name', 'Company Key', 'Status', 'Max Users', 'Created Date'
    ])
    
    companies = Company.objects.all().order_by('-created_at')
    for company in companies:
        # Handle cases where admin_user might be None
        admin_username = company.admin_user.username if company.admin_user else 'Not Registered'
        admin_email = company.admin_user.email if company.admin_user else 'N/A'
        admin_name = f"{company.admin_user.first_name} {company.admin_user.last_name}" if company.admin_user else 'N/A'
        
        writer.writerow([
            company.name,
            company.domain,
            admin_username,
            admin_email,
            admin_name,
            company.company_key,
            'Active' if company.is_active else 'Inactive',
            company.max_users,
            company.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
def company_dashboard(request):
    """Enhanced Company admin dashboard with analytics and features"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    employees = Employee.objects.filter(company=company)
    
    # Debug: Print company data
    print(f"DEBUG DASHBOARD: Company: {company.name}")
    print(f"DEBUG DASHBOARD: license_key: {company.license_key}")
    print(f"DEBUG DASHBOARD: is_premium: {company.is_premium}")
    print(f"DEBUG DASHBOARD: subscription_type: {company.subscription_type}")
    
    # Get subscription plan limits
    subscription_plan = None
    max_users = company.max_users  # Default fallback
    
    # Determine max users based on subscription type
    if company.subscription_type == 'FREE':
        max_users = 5  # Free plan limit
    elif company.subscription_type == 'STARTER':
        max_users = 25  # Starter plan limit
    elif company.subscription_type == 'PROFESSIONAL':
        max_users = 100  # Professional plan limit
    elif company.subscription_type == 'ENTERPRISE':
        max_users = 1000  # Enterprise plan limit (unlimited)
    
    # Check if company has premium features
    is_premium = company.is_premium and company.is_license_valid
    
    # Calculate warning threshold (80% of max users)
    warning_threshold = int(max_users * 0.8)
    
    # Note: Activity logging removed from dashboard view to prevent 
    # activity count from increasing on page refresh. Activity should 
    # only be logged on actual login/logout events, not page views.
    
    # Basic statistics
    total_employees = employees.count()
    verified_employees = employees.filter(is_verified=True).count()
    registered_users = employees.filter(user_account__isnull=False).count()
    
    # Enhanced analytics
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Q
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_activities = ActivityLog.objects.filter(
        company=company,
        timestamp__gte=week_ago
    ).count()
    
    # Project statistics
    projects = Project.objects.filter(company=company)
    active_projects = projects.filter(status='ACTIVE').count()
    completed_projects = projects.filter(status='COMPLETED').count()
    
    # Task statistics
    tasks = Task.objects.filter(project__company=company)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='DONE').count()
    overdue_tasks = tasks.filter(
        due_date__lt=datetime.now(),
        status__in=['TODO', 'IN_PROGRESS']
    ).count()
    
    # Performance metrics
    performance_metrics = PerformanceMetric.objects.filter(
        employee__company=company
    ).order_by('-created_at')[:5]
    
    # Recent notifications
    notifications = Notification.objects.filter(
        Q(company=company) | Q(user=request.user),
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Recent announcements
    announcements = Announcement.objects.filter(
        company=company,
        is_active=True
    ).order_by('-created_at')[:3]
    
    # Department statistics
    department_stats = employees.values('department').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Recent employees
    recent_employees = employees.order_by('-created_at')[:5]
    
    # Company metrics
    company_metrics = CompanyMetric.objects.filter(
        company=company
    ).order_by('-period_end')[:10]
    
    # Workflow instances
    workflow_instances = WorkflowInstance.objects.filter(
        template__company=company,
        status='ACTIVE'
    ).order_by('-created_at')[:5]
    
    # Leave statistics for company dashboard
    from django.db.models import Sum
    all_leave_requests = LeaveRequest.objects.filter(employee__company=company)
    
    # Leave request statistics
    total_leave_requests = all_leave_requests.count()
    pending_leave_requests = all_leave_requests.filter(status='PENDING').count()
    approved_leave_requests = all_leave_requests.filter(status='APPROVED').count()
    rejected_leave_requests = all_leave_requests.filter(status='REJECTED').count()
    
    # Calculate total leave days used by type
    total_annual_used = all_leave_requests.filter(
        leave_type='VACATION',
        status='APPROVED'
    ).aggregate(total=Sum('total_days'))['total'] or 0
    
    total_sick_used = all_leave_requests.filter(
        leave_type='SICK_LEAVE',
        status='APPROVED'
    ).aggregate(total=Sum('total_days'))['total'] or 0
    
    total_personal_used = all_leave_requests.filter(
        leave_type='PERSONAL',
        status='APPROVED'
    ).aggregate(total=Sum('total_days'))['total'] or 0
    
    # Calculate realistic leave metrics for company dashboard
    # Instead of showing total allocations, show usage patterns and trends
    
    # Calculate average leave usage per employee
    avg_annual_per_employee = total_annual_used / total_employees if total_employees > 0 else 0
    avg_sick_per_employee = total_sick_used / total_employees if total_employees > 0 else 0
    avg_personal_per_employee = total_personal_used / total_employees if total_employees > 0 else 0
    
    # Calculate leave utilization percentages (assuming standard allocations)
    annual_allocation_per_employee = 20
    sick_allocation_per_employee = 10
    personal_allocation_per_employee = 5
    
    annual_utilization = (avg_annual_per_employee / annual_allocation_per_employee) * 100 if annual_allocation_per_employee > 0 else 0
    sick_utilization = (avg_sick_per_employee / sick_allocation_per_employee) * 100 if sick_allocation_per_employee > 0 else 0
    personal_utilization = (avg_personal_per_employee / personal_allocation_per_employee) * 100 if personal_allocation_per_employee > 0 else 0
    
    # Calculate remaining balances per employee (for display purposes)
    annual_remaining_per_employee = annual_allocation_per_employee - avg_annual_per_employee
    sick_remaining_per_employee = sick_allocation_per_employee - avg_sick_per_employee
    personal_remaining_per_employee = personal_allocation_per_employee - avg_personal_per_employee
    
    # Recent leave requests (last 5)
    recent_leave_requests = all_leave_requests.order_by('-created_at')[:5]
    
    context = {
        'title': 'Company Dashboard',
        'company': company,
        'employees': employees,
        'total_employees': total_employees,
        'verified_employees': verified_employees,
        'registered_users': registered_users,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_activities': recent_activities,
        'performance_metrics': performance_metrics,
        'notifications': notifications,
        'announcements': announcements,
        'department_stats': department_stats,
        'recent_employees': recent_employees,
        'company_metrics': company_metrics,
        'workflow_instances': workflow_instances,
        'max_users': max_users,
        'is_premium': is_premium,
        'subscription_type': company.subscription_type,
        'warning_threshold': warning_threshold,
        # Leave statistics
        'total_leave_requests': total_leave_requests,
        'pending_leave_requests': pending_leave_requests,
        'approved_leave_requests': approved_leave_requests,
        'rejected_leave_requests': rejected_leave_requests,
        'total_annual_used': total_annual_used,
        'total_sick_used': total_sick_used,
        'total_personal_used': total_personal_used,
        # Realistic leave metrics
        'avg_annual_per_employee': round(avg_annual_per_employee, 1),
        'avg_sick_per_employee': round(avg_sick_per_employee, 1),
        'avg_personal_per_employee': round(avg_personal_per_employee, 1),
        'annual_utilization': round(annual_utilization, 1),
        'sick_utilization': round(sick_utilization, 1),
        'personal_utilization': round(personal_utilization, 1),
        'annual_remaining_per_employee': round(annual_remaining_per_employee, 1),
        'sick_remaining_per_employee': round(sick_remaining_per_employee, 1),
        'personal_remaining_per_employee': round(personal_remaining_per_employee, 1),
        'annual_allocation_per_employee': annual_allocation_per_employee,
        'sick_allocation_per_employee': sick_allocation_per_employee,
        'personal_allocation_per_employee': personal_allocation_per_employee,
        'recent_leave_requests': recent_leave_requests,
    }
    return render(request, 'core/company_dashboard.html', context)

@login_required
@audit_log('BULK_ACTION', 'EMPLOYEE', 'Employee CSV import', 'HIGH')
def import_employees(request):
    """Import employees from CSV (company admin only)"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    if request.method == 'POST':
        form = EmployeeCSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            try:
                # Read CSV file
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                imported_count = 0
                error_count = 0
                
                for row in reader:
                    try:
                        Employee.objects.create(
                            company=company,
                            employee_id=row['employee_id'],
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            email=row['email'],
                            department=row.get('department', ''),
                            position=row.get('position', ''),
                            is_verified=True
                        )
                        imported_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error importing row {row}: {e}")
                
                messages.success(request, f'Successfully imported {imported_count} employees.')
                if error_count > 0:
                    messages.warning(request, f'{error_count} rows had errors and were skipped.')
                    
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
            
            return redirect('core:company_dashboard')
    else:
        form = EmployeeCSVImportForm()
    
    # Get recent employees for display
    employees = Employee.objects.filter(company=company).order_by('-created_at')[:10]
    total_employees = Employee.objects.filter(company=company).count()
    
    context = {
        'title': 'Import Employees',
        'form': form,
        'company': company,
        'employees': employees,
        'total_employees': total_employees,
    }
    return render(request, 'core/import_employees.html', context)

# Team Management Views
@login_required
def employee_directory(request):
    """Employee directory page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    # Filter by department
    department_filter = request.GET.get('department', '')
    if department_filter:
        employees = employees.filter(department=department_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'verified':
        employees = employees.filter(is_verified=True)
    elif status_filter == 'pending':
        employees = employees.filter(is_verified=False)
    
    # Advanced search filters
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    email = request.GET.get('email', '')
    employee_id = request.GET.get('employee_id', '')
    position = request.GET.get('position', '')
    position_level = request.GET.get('position_level', '')
    hire_date_from = request.GET.get('hire_date_from', '')
    hire_date_to = request.GET.get('hire_date_to', '')
    created_from = request.GET.get('created_from', '')
    created_to = request.GET.get('created_to', '')
    experience_min = request.GET.get('experience_min', '')
    experience_max = request.GET.get('experience_max', '')
    location = request.GET.get('location', '')
    skills = request.GET.get('skills', '')
    new_employees = request.GET.get('new_employees', '')
    
    # Apply advanced filters
    if first_name:
        employees = employees.filter(first_name__icontains=first_name)
    if last_name:
        employees = employees.filter(last_name__icontains=last_name)
    if email:
        employees = employees.filter(email__icontains=email)
    if employee_id:
        employees = employees.filter(employee_id__icontains=employee_id)
    if position:
        employees = employees.filter(position__icontains=position)
    if position_level:
        # Map position levels to common position keywords
        level_mappings = {
            'entry': ['junior', 'entry', 'associate', 'trainee'],
            'mid': ['mid', 'intermediate', 'specialist'],
            'senior': ['senior', 'sr', 'lead'],
            'lead': ['lead', 'manager', 'supervisor', 'team lead'],
            'executive': ['director', 'vp', 'ceo', 'cto', 'executive']
        }
        if position_level in level_mappings:
            level_query = Q()
            for keyword in level_mappings[position_level]:
                level_query |= Q(position__icontains=keyword)
            employees = employees.filter(level_query)
    
    # Date filters
    if hire_date_from:
        try:
            from datetime import datetime
            hire_date_from_obj = datetime.strptime(hire_date_from, '%Y-%m-%d').date()
            employees = employees.filter(created_at__date__gte=hire_date_from_obj)
        except ValueError:
            pass
    if hire_date_to:
        try:
            from datetime import datetime
            hire_date_to_obj = datetime.strptime(hire_date_to, '%Y-%m-%d').date()
            employees = employees.filter(created_at__date__lte=hire_date_to_obj)
        except ValueError:
            pass
    if created_from:
        try:
            from datetime import datetime
            created_from_obj = datetime.strptime(created_from, '%Y-%m-%d').date()
            employees = employees.filter(created_at__date__gte=created_from_obj)
        except ValueError:
            pass
    if created_to:
        try:
            from datetime import datetime
            created_to_obj = datetime.strptime(created_to, '%Y-%m-%d').date()
            employees = employees.filter(created_at__date__lte=created_to_obj)
        except ValueError:
            pass
    
    # Experience filters (based on created_at date)
    if experience_min:
        try:
            from datetime import datetime, timedelta
            min_date = datetime.now().date() - timedelta(days=int(experience_min) * 365)
            employees = employees.filter(created_at__date__lte=min_date)
        except ValueError:
            pass
    if experience_max:
        try:
            from datetime import datetime, timedelta
            max_date = datetime.now().date() - timedelta(days=int(experience_max) * 365)
            employees = employees.filter(created_at__date__gte=max_date)
        except ValueError:
            pass
    
    # Location filter (if location field exists)
    if location and hasattr(Employee, 'location'):
        employees = employees.filter(location__icontains=location)
    
    # Skills filter (if skills field exists)
    if skills and hasattr(Employee, 'skills'):
        skill_list = [skill.strip() for skill in skills.split(',')]
        skills_query = Q()
        for skill in skill_list:
            skills_query |= Q(skills__icontains=skill)
        employees = employees.filter(skills_query)
    
    # New employees filter
    if new_employees:
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        employees = employees.filter(created_at__date__gte=thirty_days_ago)
    
    # Get unique departments for filter dropdown
    departments = Employee.objects.filter(company=company).values_list('department', flat=True).distinct().exclude(department='')
    
    # Pagination
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Employee Directory',
        'company': company,
        'employees': page_obj,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
    }
    return render(request, 'core/employee_directory.html', context)

@login_required
def employee_profile(request, employee_id):
    """Employee profile page with detailed information and activity history"""
    try:
        if not hasattr(request.user, 'company_admin_profile'):
            messages.error(request, 'Access denied')
            return redirect('core:company_dashboard')
        
        company = request.user.company_admin_profile.company
        employee = get_object_or_404(Employee, id=employee_id, company=company)
        
        # Get employee activity history
        activities = ActivityLog.objects.filter(
            Q(description__icontains=employee.first_name) |
            Q(description__icontains=employee.last_name) |
            Q(description__icontains=employee.email)
        ).order_by('-created_at')[:20]
        
        # Get performance metrics if available
        performance_metrics = []
        if hasattr(employee, 'performance_metrics'):
            performance_metrics = employee.performance_metrics.all().order_by('-period_start')[:10]
        
        # Get related employees (same department)
        related_employees = Employee.objects.filter(
            company=company,
            department=employee.department
        ).exclude(id=employee.id)[:5]
        
        # Calculate employee stats
        days_since_hire = (timezone.now().date() - employee.created_at.date()).days
        is_new_employee = days_since_hire <= 30
        
        # Get recent projects/tasks if available
        recent_activities = []
        if hasattr(employee, 'tasks'):
            recent_activities = employee.tasks.all().order_by('-created_at')[:5]
        
        context = {
            'employee': employee,
            'activities': activities,
            'performance_metrics': performance_metrics,
            'related_employees': related_employees,
            'days_since_hire': days_since_hire,
            'is_new_employee': is_new_employee,
            'recent_activities': recent_activities,
            'company': company,
        }
        
        return render(request, 'core/employee_profile.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading employee profile: {str(e)}')
        return redirect('core:employee_directory')

@login_required
def department_management(request):
    """Department management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get department statistics from Employee model
    employee_departments = Employee.objects.filter(company=company).values('department').annotate(
        employee_count=Count('id'),
        verified_count=Count('id', filter=Q(is_verified=True)),
        registered_count=Count('id', filter=Q(user_account__isnull=False))
    ).order_by('-employee_count')
    
    # Get department announcements (using title prefix to identify departments)
    department_announcements = Announcement.objects.filter(
        company=company,
        title__startswith='Department: '
    ).order_by('title')
    
    # Combine both data sources
    departments = []
    for dept in employee_departments:
        dept_name = dept['department'] or 'Unassigned'
        # Find corresponding announcement
        announcement = department_announcements.filter(
            title__icontains=dept_name
        ).first()
        
        # If no announcement exists, create one
        if not announcement and dept_name != 'Unassigned':
            announcement = Announcement.objects.create(
                company=company,
                title=f"Department: {dept_name}",
                content=f"Department: {dept_name}",
                created_by=request.user
            )
        
        departments.append({
            'department': dept_name,
            'employee_count': dept['employee_count'],
            'verified_count': dept['verified_count'],
            'registered_count': dept['registered_count'],
            'announcement_id': announcement.id if announcement else None,
            'description': announcement.content if announcement else ''
        })
    
    # Add departments that exist in announcements but have no employees
    for announcement in department_announcements:
        dept_name = announcement.title.replace('Department: ', '')
        if not any(d['department'] == dept_name for d in departments):
            departments.append({
                'department': dept_name,
                'employee_count': 0,
                'verified_count': 0,
                'registered_count': 0,
                'announcement_id': announcement.id,
                'description': announcement.content
            })
    
    context = {
        'title': 'Department Management',
        'company': company,
        'departments': departments,
    }
    return render(request, 'core/department_management.html', context)

@login_required
def team_performance(request):
    """Team performance analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Performance metrics by department
    department_performance = PerformanceMetric.objects.filter(
        employee__company=company
    ).values('employee__department').annotate(
        avg_value=Avg('value'),
        total_metrics=Count('id'),
        avg_productivity=Avg('value', filter=Q(metric_type='PRODUCTIVITY')),
        avg_quality=Avg('value', filter=Q(metric_type='TASK_COMPLETION')),
        avg_attendance=Avg('value', filter=Q(metric_type='ATTENDANCE'))
    ).order_by('-avg_value')
    
    # Recent performance reviews
    recent_reviews = PerformanceMetric.objects.filter(
        employee__company=company
    ).order_by('-created_at')[:10]
    
    context = {
        'title': 'Team Performance',
        'company': company,
        'department_performance': department_performance,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'core/team_performance.html', context)

@login_required
def company_employee_onboarding(request):
    """Employee onboarding management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Recent hires (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_hires = Employee.objects.filter(
        company=company,
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')
    
    # Pending verifications
    pending_verifications = Employee.objects.filter(
        company=company,
        is_verified=False
    ).order_by('-created_at')
    
    context = {
        'title': 'Employee Onboarding',
        'company': company,
        'recent_hires': recent_hires,
        'pending_verifications': pending_verifications,
    }
    return render(request, 'core/employee_onboarding.html', context)

# Project Management Views
@login_required
def project_list(request):
    """Project list page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    projects = Project.objects.filter(company=company).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Project statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='ACTIVE').count()
    completed_projects = projects.filter(status='COMPLETED').count()
    cancelled_projects = projects.filter(status='CANCELLED').count()
    
    context = {
        'title': 'Project List',
        'company': company,
        'projects': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'cancelled_projects': cancelled_projects,
    }
    return render(request, 'core/project_list.html', context)

@login_required
def task_management(request):
    """Task management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    tasks = Task.objects.filter(project__company=company).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(tasks, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Task statistics
    total_tasks = tasks.count()
    todo_tasks = tasks.filter(status='TODO').count()
    in_progress_tasks = tasks.filter(status='IN_PROGRESS').count()
    done_tasks = tasks.filter(status='DONE').count()
    overdue_tasks = tasks.filter(
        due_date__lt=datetime.now(),
        status__in=['TODO', 'IN_PROGRESS']
    ).count()
    
    context = {
        'title': 'Task Management',
        'company': company,
        'tasks': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'total_tasks': total_tasks,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'core/task_management.html', context)

@login_required
def project_analytics(request):
    """Project analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Project status distribution
    project_status = Project.objects.filter(company=company).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Project priority distribution
    project_priority = Project.objects.filter(company=company).values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Task completion by project
    task_completion = Task.objects.filter(project__company=company).values('project__name').annotate(
        total_tasks=Count('id'),
        completed_tasks=Count('id', filter=Q(status='DONE')),
        completion_rate=Count('id', filter=Q(status='DONE')) * 100.0 / Count('id')
    ).order_by('-completion_rate')
    
    # Recent project activity
    recent_projects = Project.objects.filter(company=company).order_by('-updated_at')[:10]
    
    # Project timeline (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    project_timeline = Project.objects.filter(
        company=company,
        created_at__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at) || '-01'"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'title': 'Project Analytics',
        'company': company,
        'project_status': project_status,
        'project_priority': project_priority,
        'task_completion': task_completion,
        'recent_projects': recent_projects,
        'project_timeline': project_timeline,
    }
    return render(request, 'core/project_analytics.html', context)

@login_required
def resource_planning(request):
    """Resource planning page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Employee workload analysis
    employee_workload = Task.objects.filter(
        project__company=company,
        assigned_to__isnull=False
    ).values('assigned_to__first_name', 'assigned_to__last_name', 'assigned_to__department').annotate(
        total_tasks=Count('id'),
        active_tasks=Count('id', filter=Q(status__in=['TODO', 'IN_PROGRESS'])),
        completed_tasks=Count('id', filter=Q(status='DONE')),
        overdue_tasks=Count('id', filter=Q(due_date__lt=datetime.now(), status__in=['TODO', 'IN_PROGRESS']))
    ).order_by('-total_tasks')
    
    # Department capacity
    department_capacity = Employee.objects.filter(company=company).values('department').annotate(
        total_employees=Count('id'),
        active_employees=Count('id', filter=Q(is_verified=True)),
        total_tasks=Count('task__id'),
        active_tasks=Count('task__id', filter=Q(task__status__in=['TODO', 'IN_PROGRESS']))
    ).order_by('-total_employees')
    
    # Project resource allocation
    project_resources = Project.objects.filter(company=company).annotate(
        total_tasks=Count('task'),
        assigned_tasks=Count('task', filter=Q(task__assigned_to__isnull=False)),
        unassigned_tasks=Count('task', filter=Q(task__assigned_to__isnull=True))
    ).order_by('-total_tasks')
    
    context = {
        'title': 'Resource Planning',
        'company': company,
        'employee_workload': employee_workload,
        'department_capacity': department_capacity,
        'project_resources': project_resources,
    }
    return render(request, 'core/resource_planning.html', context)

@login_required
def project_templates(request):
    """Project templates page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get workflow templates (using as project templates)
    templates = WorkflowTemplate.objects.filter(company=company).order_by('-created_at')
    
    # Template usage statistics
    template_usage = WorkflowInstance.objects.filter(
        template__company=company
    ).values('template__name').annotate(
        usage_count=Count('id'),
        active_instances=Count('id', filter=Q(status='ACTIVE')),
        completed_instances=Count('id', filter=Q(status='COMPLETED'))
    ).order_by('-usage_count')
    
    context = {
        'title': 'Project Templates',
        'company': company,
        'templates': templates,
        'template_usage': template_usage,
    }
    return render(request, 'core/project_templates.html', context)

# Communication & Collaboration Views
@login_required
def internal_messaging(request):
    """Internal messaging page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get recent messages (using notifications as messages)
    recent_messages = Notification.objects.filter(
        company=company,
        notification_type='MESSAGE'
    ).order_by('-created_at')[:20]
    
    # Message statistics
    total_messages = Notification.objects.filter(
        company=company,
        notification_type='MESSAGE'
    ).count()
    
    unread_messages = Notification.objects.filter(
        company=company,
        notification_type='MESSAGE',
        is_read=False
    ).count()
    
    # Employee list for messaging
    employees = Employee.objects.filter(company=company, is_verified=True).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Internal Messaging',
        'company': company,
        'recent_messages': recent_messages,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'employees': employees,
    }
    return render(request, 'core/internal_messaging.html', context)

@login_required
def team_chat(request):
    """Team chat page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get team chat messages (using announcements as chat messages)
    chat_messages = Announcement.objects.filter(
        company=company,
        announcement_type='CHAT'
    ).order_by('-created_at')[:50]
    
    # Active team members
    team_members = Employee.objects.filter(
        company=company,
        is_verified=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Team Chat',
        'company': company,
        'chat_messages': chat_messages,
        'team_members': team_members,
    }
    return render(request, 'core/team_chat.html', context)

@login_required
def meeting_scheduler(request):
    """Meeting scheduler page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get scheduled meetings (using workflow instances as meetings)
    scheduled_meetings = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='meeting'
    ).order_by('-created_at')[:20]
    
    # Available team members
    team_members = Employee.objects.filter(
        company=company,
        is_verified=True
    ).order_by('first_name', 'last_name')
    
    # Meeting statistics
    total_meetings = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='meeting'
    ).count()
    
    upcoming_meetings = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='meeting',
        status='ACTIVE'
    ).count()
    
    context = {
        'title': 'Meeting Scheduler',
        'company': company,
        'scheduled_meetings': scheduled_meetings,
        'team_members': team_members,
        'total_meetings': total_meetings,
        'upcoming_meetings': upcoming_meetings,
    }
    return render(request, 'core/meeting_scheduler.html', context)

@login_required
def announcements(request):
    """Announcements management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get all announcements
    announcements_list = Announcement.objects.filter(company=company).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        announcements_list = announcements_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        announcements_list = announcements_list.filter(announcement_type=type_filter)
    
    # Pagination
    paginator = Paginator(announcements_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Announcement statistics
    total_announcements = announcements_list.count()
    active_announcements = announcements_list.filter(is_active=True).count()
    recent_announcements = announcements_list.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    context = {
        'title': 'Announcements',
        'company': company,
        'announcements': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'total_announcements': total_announcements,
        'active_announcements': active_announcements,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'core/announcements.html', context)

@login_required
def video_meetings(request):
    """Video meetings page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get video meeting rooms (using projects as meeting rooms)
    meeting_rooms = Project.objects.filter(
        company=company,
        name__icontains='meeting'
    ).order_by('-created_at')
    
    # Meeting statistics
    total_rooms = meeting_rooms.count()
    active_rooms = meeting_rooms.filter(status='ACTIVE').count()
    
    # Recent meetings (using workflow instances)
    recent_meetings = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='video'
    ).order_by('-created_at')[:10]
    
    context = {
        'title': 'Video Meetings',
        'company': company,
        'meeting_rooms': meeting_rooms,
        'total_rooms': total_rooms,
        'active_rooms': active_rooms,
        'recent_meetings': recent_meetings,
    }
    return render(request, 'core/video_meetings.html', context)

# Document Management Views
@login_required
def file_sharing(request):
    """File sharing page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get shared files (using announcements as file records)
    shared_files = Announcement.objects.filter(
        company=company,
        announcement_type='FILE'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        shared_files = shared_files.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by file type
    file_type_filter = request.GET.get('file_type', '')
    if file_type_filter:
        shared_files = shared_files.filter(content__icontains=file_type_filter)
    
    # Pagination
    paginator = Paginator(shared_files, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # File statistics
    total_files = shared_files.count()
    recent_files = shared_files.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    context = {
        'title': 'File Sharing',
        'company': company,
        'files': page_obj,
        'search_query': search_query,
        'file_type_filter': file_type_filter,
        'total_files': total_files,
        'recent_files': recent_files,
    }
    return render(request, 'core/file_sharing.html', context)

@login_required
def version_control(request):
    """Version control page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get document versions (using workflow instances as version records)
    document_versions = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='document'
    ).order_by('-created_at')
    
    # Version statistics
    total_versions = document_versions.count()
    active_versions = document_versions.filter(status='ACTIVE').count()
    recent_versions = document_versions.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    context = {
        'title': 'Version Control',
        'company': company,
        'versions': document_versions[:20],
        'total_versions': total_versions,
        'active_versions': active_versions,
        'recent_versions': recent_versions,
    }
    return render(request, 'core/version_control.html', context)

@login_required
def document_templates(request):
    """Document templates page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get document templates (using workflow templates as document templates)
    templates = WorkflowTemplate.objects.filter(
        company=company,
        name__icontains='template'
    ).order_by('-created_at')
    
    # Template usage statistics
    template_usage = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='template'
    ).values('template__name').annotate(
        usage_count=Count('id'),
        active_instances=Count('id', filter=Q(status='ACTIVE')),
        completed_instances=Count('id', filter=Q(status='COMPLETED'))
    ).order_by('-usage_count')
    
    context = {
        'title': 'Document Templates',
        'company': company,
        'templates': templates,
        'template_usage': template_usage,
    }
    return render(request, 'core/document_templates.html', context)

@login_required
def document_analytics(request):
    """Document analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Document type distribution
    document_types = Announcement.objects.filter(
        company=company,
        announcement_type='FILE'
    ).values('content').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Document activity timeline
    thirty_days_ago = datetime.now() - timedelta(days=30)
    document_timeline = Announcement.objects.filter(
        company=company,
        announcement_type='FILE',
        created_at__gte=thirty_days_ago
    ).extra(
        select={'day': "strftime('%%Y-%%m-%%d', created_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Most active users
    active_users = Announcement.objects.filter(
        company=company,
        announcement_type='FILE'
    ).values('created_by__username').annotate(
        file_count=Count('id')
    ).order_by('-file_count')[:10]
    
    context = {
        'title': 'Document Analytics',
        'company': company,
        'document_types': document_types,
        'document_timeline': document_timeline,
        'active_users': active_users,
    }
    return render(request, 'core/document_analytics.html', context)

@login_required
def archive_management(request):
    """Archive management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get archived documents (using inactive announcements as archived files)
    archived_documents = Announcement.objects.filter(
        company=company,
        is_active=False
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        archived_documents = archived_documents.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(archived_documents, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Archive statistics
    total_archived = archived_documents.count()
    old_archives = archived_documents.filter(
        created_at__lt=datetime.now() - timedelta(days=365)
    ).count()
    
    context = {
        'title': 'Archive Management',
        'company': company,
        'archived_documents': page_obj,
        'search_query': search_query,
        'total_archived': total_archived,
        'old_archives': old_archives,
    }
    return render(request, 'core/archive_management.html', context)

# HR & Payroll Views
@login_required
def attendance_tracking(request):
    """Attendance tracking page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get attendance records (using workflow instances as attendance records)
    attendance_records = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='attendance'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        attendance_records = attendance_records.filter(
            Q(assigned_to__username__icontains=search_query) |
            Q(template__name__icontains=search_query)
        )
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        attendance_records = attendance_records.filter(created_at__date__gte=date_from)
    if date_to:
        attendance_records = attendance_records.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(attendance_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Attendance statistics
    total_records = attendance_records.count()
    present_today = attendance_records.filter(
        created_at__date=datetime.now().date(),
        status='COMPLETED'
    ).count()
    late_arrivals = attendance_records.filter(
        created_at__date=datetime.now().date(),
        status='ACTIVE'
    ).count()
    
    # Get employees for the company
    employees = Employee.objects.filter(company=company)
    
    context = {
        'title': 'Attendance Tracking',
        'company': company,
        'attendance_records': page_obj,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'total_records': total_records,
        'present_today': present_today,
        'late_arrivals': late_arrivals,
        'employees': employees,
    }
    return render(request, 'core/attendance_tracking.html', context)

# OLD leave_management function removed - using the correct one at line 7481

@login_required
def payroll_processing(request):
    """Payroll processing page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get payroll records (using projects as payroll periods)
    payroll_periods = Project.objects.filter(
        company=company,
        name__icontains='payroll'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        payroll_periods = payroll_periods.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        payroll_periods = payroll_periods.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(payroll_periods, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Payroll statistics
    total_periods = payroll_periods.count()
    completed_periods = payroll_periods.filter(status='COMPLETED').count()
    pending_periods = payroll_periods.filter(status='ACTIVE').count()
    
    context = {
        'title': 'Payroll Processing',
        'company': company,
        'payroll_periods': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_periods': total_periods,
        'completed_periods': completed_periods,
        'pending_periods': pending_periods,
    }
    return render(request, 'core/payroll_processing.html', context)

@login_required
def performance_reviews(request):
    """Performance reviews page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get performance reviews (using workflow instances as reviews)
    performance_reviews = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='review'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        performance_reviews = performance_reviews.filter(
            Q(assigned_to__username__icontains=search_query) |
            Q(template__name__icontains=search_query)
        )
    
    # Filter by rating
    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        performance_reviews = performance_reviews.filter(status=rating_filter)
    
    # Pagination
    paginator = Paginator(performance_reviews, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Performance statistics
    total_reviews = performance_reviews.count()
    completed_reviews = performance_reviews.filter(status='COMPLETED').count()
    pending_reviews = performance_reviews.filter(status='ACTIVE').count()
    
    context = {
        'title': 'Performance Reviews',
        'company': company,
        'performance_reviews': page_obj,
        'search_query': search_query,
        'rating_filter': rating_filter,
        'total_reviews': total_reviews,
        'completed_reviews': completed_reviews,
        'pending_reviews': pending_reviews,
    }
    return render(request, 'core/performance_reviews.html', context)

@login_required
def employee_benefits(request):
    """Employee benefits page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get benefits (using announcements as benefits)
    benefits = Announcement.objects.filter(
        company=company,
        announcement_type='BENEFIT'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        benefits = benefits.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by benefit type
    benefit_type_filter = request.GET.get('benefit_type', '')
    if benefit_type_filter:
        benefits = benefits.filter(content__icontains=benefit_type_filter)
    
    # Pagination
    paginator = Paginator(benefits, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Benefits statistics
    total_benefits = benefits.count()
    active_benefits = benefits.filter(is_active=True).count()
    
    context = {
        'title': 'Employee Benefits',
        'company': company,
        'benefits': page_obj,
        'search_query': search_query,
        'benefit_type_filter': benefit_type_filter,
        'total_benefits': total_benefits,
        'active_benefits': active_benefits,
    }
    return render(request, 'core/employee_benefits.html', context)

# Customer Management Views
@login_required
def crm_dashboard(request):
    """CRM dashboard page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get customer data (using announcements as customer records)
    customers = Announcement.objects.filter(
        company=company,
        announcement_type='CUSTOMER'
    ).order_by('-created_at')
    
    # Customer statistics
    total_customers = customers.count()
    active_customers = customers.filter(is_active=True).count()
    new_customers = customers.filter(
        created_at__gte=datetime.now() - timedelta(days=30)
    ).count()
    
    # Recent customer activities
    recent_activities = customers[:10]
    
    context = {
        'title': 'CRM Dashboard',
        'company': company,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'new_customers': new_customers,
        'recent_activities': recent_activities,
    }
    return render(request, 'core/crm_dashboard.html', context)

@login_required
def support_tickets(request):
    """Support tickets page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get support tickets (using workflow instances as tickets)
    support_tickets = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='support'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        support_tickets = support_tickets.filter(
            Q(template__name__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query)
        )
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        support_tickets = support_tickets.filter(status=priority_filter)
    
    # Pagination
    paginator = Paginator(support_tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Ticket statistics
    total_tickets = support_tickets.count()
    open_tickets = support_tickets.filter(status='ACTIVE').count()
    closed_tickets = support_tickets.filter(status='COMPLETED').count()
    
    context = {
        'title': 'Support Tickets',
        'company': company,
        'tickets': page_obj,
        'search_query': search_query,
        'priority_filter': priority_filter,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
    }
    return render(request, 'core/support_tickets.html', context)

@login_required
def client_portal(request):
    """Client portal page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get client projects (using projects as client work)
    client_projects = Project.objects.filter(
        company=company,
        name__icontains='client'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        client_projects = client_projects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        client_projects = client_projects.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(client_projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Client statistics
    total_clients = client_projects.count()
    active_projects = client_projects.filter(status='ACTIVE').count()
    completed_projects = client_projects.filter(status='COMPLETED').count()
    
    context = {
        'title': 'Client Portal',
        'company': company,
        'client_projects': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_clients': total_clients,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
    }
    return render(request, 'core/client_portal.html', context)

@login_required
def customer_analytics(request):
    """Customer analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Customer growth over time
    thirty_days_ago = datetime.now() - timedelta(days=30)
    customer_timeline = Announcement.objects.filter(
        company=company,
        announcement_type='CUSTOMER',
        created_at__gte=thirty_days_ago
    ).extra(
        select={'day': "strftime('%%Y-%%m-%%d', created_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Customer types distribution
    customer_types = Announcement.objects.filter(
        company=company,
        announcement_type='CUSTOMER'
    ).values('content').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Customer satisfaction (using workflow instances as satisfaction surveys)
    satisfaction_scores = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='satisfaction'
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'title': 'Customer Analytics',
        'company': company,
        'customer_timeline': customer_timeline,
        'customer_types': customer_types,
        'satisfaction_scores': satisfaction_scores,
    }
    return render(request, 'core/customer_analytics.html', context)

@login_required
def contact_management(request):
    """Contact management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get contacts (using announcements as contact records)
    contacts = Announcement.objects.filter(
        company=company,
        announcement_type='CONTACT'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(created_by__username__icontains=search_query)
        )
    
    # Filter by contact type
    contact_type_filter = request.GET.get('contact_type', '')
    if contact_type_filter:
        contacts = contacts.filter(content__icontains=contact_type_filter)
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contact statistics
    total_contacts = contacts.count()
    active_contacts = contacts.filter(is_active=True).count()
    recent_contacts = contacts.filter(
        created_at__gte=datetime.now() - timedelta(days=7)
    ).count()
    
    context = {
        'title': 'Contact Management',
        'company': company,
        'contacts': page_obj,
        'search_query': search_query,
        'contact_type_filter': contact_type_filter,
        'total_contacts': total_contacts,
        'active_contacts': active_contacts,
        'recent_contacts': recent_contacts,
    }
    return render(request, 'core/contact_management.html', context)

# Inventory & Assets Views
@login_required
def asset_tracking(request):
    """Asset tracking page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get assets (using projects as asset records)
    assets = Project.objects.filter(
        company=company,
        name__icontains='asset'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by asset type
    asset_type_filter = request.GET.get('asset_type', '')
    if asset_type_filter:
        assets = assets.filter(description__icontains=asset_type_filter)
    
    # Pagination
    paginator = Paginator(assets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Asset statistics
    total_assets = assets.count()
    active_assets = assets.filter(status='ACTIVE').count()
    maintenance_due = assets.filter(status='PENDING').count()
    
    # Get employees for the company
    employees = Employee.objects.filter(company=company)
    
    context = {
        'title': 'Asset Tracking',
        'company': company,
        'assets': page_obj,
        'search_query': search_query,
        'asset_type_filter': asset_type_filter,
        'total_assets': total_assets,
        'active_assets': active_assets,
        'maintenance_due': maintenance_due,
        'employees': employees,
    }
    return render(request, 'core/asset_tracking.html', context)

@login_required
def procurement_management(request):
    """Procurement management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get procurement orders (using workflow instances as orders)
    procurement_orders = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='procurement'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        procurement_orders = procurement_orders.filter(
            Q(template__name__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        procurement_orders = procurement_orders.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(procurement_orders, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Procurement statistics
    total_orders = procurement_orders.count()
    pending_orders = procurement_orders.filter(status='ACTIVE').count()
    completed_orders = procurement_orders.filter(status='COMPLETED').count()
    
    context = {
        'title': 'Procurement Management',
        'company': company,
        'orders': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
    }
    return render(request, 'core/procurement_management.html', context)

@login_required
def maintenance_scheduling(request):
    """Maintenance scheduling page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get maintenance schedules (using announcements as maintenance records)
    maintenance_schedules = Announcement.objects.filter(
        company=company,
        announcement_type='MAINTENANCE'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        maintenance_schedules = maintenance_schedules.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by maintenance type
    maintenance_type_filter = request.GET.get('maintenance_type', '')
    if maintenance_type_filter:
        maintenance_schedules = maintenance_schedules.filter(content__icontains=maintenance_type_filter)
    
    # Pagination
    paginator = Paginator(maintenance_schedules, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Maintenance statistics
    total_schedules = maintenance_schedules.count()
    upcoming_maintenance = maintenance_schedules.filter(is_active=True).count()
    completed_maintenance = maintenance_schedules.filter(is_active=False).count()
    
    context = {
        'title': 'Maintenance Scheduling',
        'company': company,
        'schedules': page_obj,
        'search_query': search_query,
        'maintenance_type_filter': maintenance_type_filter,
        'total_schedules': total_schedules,
        'upcoming_maintenance': upcoming_maintenance,
        'completed_maintenance': completed_maintenance,
    }
    return render(request, 'core/maintenance_scheduling.html', context)

@login_required
def inventory_reports(request):
    """Inventory reports page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get inventory data (using announcements as inventory records)
    inventory_items = Announcement.objects.filter(
        company=company,
        announcement_type='INVENTORY'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        inventory_items = inventory_items.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        inventory_items = inventory_items.filter(content__icontains=category_filter)
    
    # Pagination
    paginator = Paginator(inventory_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Inventory statistics
    total_items = inventory_items.count()
    low_stock_items = inventory_items.filter(is_active=True).count()
    out_of_stock_items = inventory_items.filter(is_active=False).count()
    
    context = {
        'title': 'Inventory Reports',
        'company': company,
        'inventory_items': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
    }
    return render(request, 'core/inventory_reports.html', context)

@login_required
def asset_analytics(request):
    """Asset analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Asset type distribution
    asset_types = Project.objects.filter(
        company=company,
        name__icontains='asset'
    ).values('description').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Asset status distribution
    asset_status = Project.objects.filter(
        company=company,
        name__icontains='asset'
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Maintenance frequency (using announcements as maintenance records)
    maintenance_frequency = Announcement.objects.filter(
        company=company,
        announcement_type='MAINTENANCE'
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at) || '-01'"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'title': 'Asset Analytics',
        'company': company,
        'asset_types': asset_types,
        'asset_status': asset_status,
        'maintenance_frequency': maintenance_frequency,
    }
    return render(request, 'core/asset_analytics.html', context)

# Security & Compliance Views
@login_required
def audit_logs(request):
    """Comprehensive audit logs page using the new AuditLog model"""
    # Allow both system owners and company admins to access audit logs
    is_owner = hasattr(request.user, 'owner_profile')
    is_company_admin = hasattr(request.user, 'company_admin_profile')
    
    if not (is_owner or is_company_admin):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    # Different query logic for owners vs company admins
    all_companies = None
    
    if is_owner:
        # Get all companies for owner filtering
        from .models import Company
        all_companies = Company.objects.all()
        
        # Owners see all audit logs, with optional company filtering
        audit_logs = AuditLog.objects.all().order_by('-timestamp')
        
        # Apply company filter if specified
        company_filter = request.GET.get('company_filter', '')
        if company_filter:
            try:
                company_id = int(company_filter)
                filtered_company = get_object_or_404(Company, id=company_id)
                # Filter logs by the selected company
                audit_logs = audit_logs.filter(
                    Q(company=filtered_company) | 
                    Q(company__isnull=True, user__company_admin__company=filtered_company)
                )
            except ValueError:
                pass
        
        company = None
    else:
        # Company admins see only their company's logs
        company = request.user.company_admin_profile.company
        audit_logs = AuditLog.objects.filter(
            Q(company=company) | Q(company__isnull=True, user__company_admin__company=company)
        ).order_by('-timestamp')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        audit_logs = audit_logs.filter(
            Q(action_description__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(resource_name__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    # Filter by action type
    action_filter = request.GET.get('action', '')
    if action_filter:
        audit_logs = audit_logs.filter(action_type=action_filter)
    
    # Filter by resource type
    resource_filter = request.GET.get('resource_type', '')
    if resource_filter:
        audit_logs = audit_logs.filter(resource_type=resource_filter)
    
    # Filter by severity
    severity_filter = request.GET.get('severity', '')
    if severity_filter:
        audit_logs = audit_logs.filter(severity=severity_filter)
    
    # Filter by success status
    success_filter = request.GET.get('success', '')
    if success_filter:
        audit_logs = audit_logs.filter(success=(success_filter == 'true'))
    
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            audit_logs = audit_logs.filter(timestamp__gte=from_date)
        except ValueError:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire end date
            to_date = to_date + timedelta(days=1)
            audit_logs = audit_logs.filter(timestamp__lt=to_date)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(audit_logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Audit statistics
    total_logs = audit_logs.count()
    recent_logs = audit_logs.filter(
        timestamp__gte=datetime.now() - timedelta(days=7)
    ).count()
    critical_events = audit_logs.filter(severity='CRITICAL').count()
    failed_actions = audit_logs.filter(success=False).count()
    
    # Get unique values for filter dropdowns
    action_types = AuditLog.ACTION_TYPES
    resource_types = AuditLog.RESOURCE_TYPES
    severity_levels = AuditLog.SEVERITY_LEVELS
    
    context = {
        'title': 'Audit Logs',
        'company': company,
        'audit_logs': page_obj,
        'search_query': search_query,
        'action_filter': action_filter,
        'resource_filter': resource_filter,
        'severity_filter': severity_filter,
        'success_filter': success_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_logs': total_logs,
        'recent_logs': recent_logs,
        'critical_events': critical_events,
        'failed_actions': failed_actions,
        'action_types': action_types,
        'resource_types': resource_types,
        'severity_levels': severity_levels,
    }
    
    # Add all_companies to context for owners
    if is_owner:
        context['all_companies'] = all_companies
    return render(request, 'core/audit_logs.html', context)


@login_required
def export_audit_logs(request):
    """Export audit logs to CSV"""
    # Allow both system owners and company admins to export audit logs
    is_owner = hasattr(request.user, 'owner_profile')
    is_company_admin = hasattr(request.user, 'company_admin_profile')
    
    if not (is_owner or is_company_admin):
        messages.error(request, 'Access denied. You are not authorized to export audit logs.')
        return redirect('core:home')
    
    # Different query logic for owners vs company admins
    if is_owner:
        # Owners can export all audit logs, with optional company filtering
        audit_logs = AuditLog.objects.all().order_by('-timestamp')
        
        # Apply company filter if specified
        company_filter = request.GET.get('company_filter', '')
        if company_filter:
            try:
                company_id = int(company_filter)
                from .models import Company
                filtered_company = get_object_or_404(Company, id=company_id)
                # Filter logs by the selected company
                audit_logs = audit_logs.filter(
                    Q(company=filtered_company) | 
                    Q(company__isnull=True, user__company_admin__company=filtered_company)
                )
            except ValueError:
                pass
        
        company = None
    else:
        # Company admins can export only their company's logs
        company = request.user.company_admin_profile.company
        audit_logs = AuditLog.objects.filter(
            Q(company=company) | Q(company__isnull=True, user__company_admin__company=company)
        ).order_by('-timestamp')
    
    # Apply filters from request
    search_query = request.GET.get('search', '')
    if search_query:
        audit_logs = audit_logs.filter(
            Q(action_description__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(resource_name__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )
    
    action_filter = request.GET.get('action', '')
    if action_filter:
        audit_logs = audit_logs.filter(action_type=action_filter)
    
    resource_filter = request.GET.get('resource_type', '')
    if resource_filter:
        audit_logs = audit_logs.filter(resource_type=resource_filter)
    
    severity_filter = request.GET.get('severity', '')
    if severity_filter:
        audit_logs = audit_logs.filter(severity=severity_filter)
    
    success_filter = request.GET.get('success', '')
    if success_filter:
        audit_logs = audit_logs.filter(success=(success_filter == 'true'))
    
    # Date range filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            audit_logs = audit_logs.filter(timestamp__gte=from_date)
        except ValueError:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            to_date = to_date + timedelta(days=1)
            audit_logs = audit_logs.filter(timestamp__lt=to_date)
        except ValueError:
            pass
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    
    # Generate appropriate filename based on user type and filters
    if is_owner:
        if 'company_filter' in locals() and company_filter:
            # If owner is exporting filtered company logs
            filename = f'audit_logs_{filtered_company.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:
            # If owner is exporting all logs
            filename = f'audit_logs_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    else:
        # For company admins
        filename = f'audit_logs_{company.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Timestamp',
        'User',
        'Action Type',
        'Resource Type',
        'Resource ID',
        'Resource Name',
        'Description',
        'Severity',
        'Success',
        'Error Message',
        'IP Address',
        'User Agent',
        'Request Path',
        'Request Method',
        'Company',
        'Additional Data'
    ])
    
    # Write data
    for log in audit_logs:
        user_name = f"{log.user.get_full_name()} ({log.user.username})" if log.user else 'System'
        company_name = log.company.name if log.company else ('N/A' if not is_owner else log.user.company_admin_profile.company.name if log.user and hasattr(log.user, 'company_admin_profile') else 'N/A')
        additional_data = json.dumps(log.additional_data) if log.additional_data else ''
        
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            user_name,
            log.get_action_type_display(),
            log.get_resource_type_display(),
            log.resource_id,
            log.resource_name,
            log.action_description,
            log.get_severity_display(),
            'Success' if log.success else 'Failed',
            log.error_message,
            log.ip_address,
            log.user_agent[:100] + '...' if len(log.user_agent) > 100 else log.user_agent,
            log.request_path,
            log.request_method,
            company_name,
            additional_data[:200] + '...' if len(additional_data) > 200 else additional_data
        ])
    
    # Log the export action
    try:
        AuditLog.log_action(
            user=request.user,
            action_type='EXPORT',
            resource_type='SYSTEM',
            description=f"Exported {audit_logs.count()} audit log entries",
            severity='MEDIUM',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_path=request.path,
            request_method=request.method,
            company=company,
            success=True
        )
    except Exception as e:
        # Don't let audit logging break the export
        pass
    
    return response


@login_required
def audit_log_details(request, log_id):
    """
    AJAX view to get detailed information about a specific audit log entry
    """
    # Allow system owners, superusers, and company admins to view audit log details
    is_superuser = request.user.is_superuser
    is_owner = hasattr(request.user, 'owner_profile')
    is_company_admin = hasattr(request.user, 'company_admin_profile')
    
    if not (is_superuser or is_owner or is_company_admin):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        log = get_object_or_404(AuditLog, id=log_id)
        
        # For company admins, ensure they can only view logs related to their company
        if is_company_admin and not is_superuser and not is_owner:
            company = request.user.company_admin_profile.company
            # Check if the log belongs to their company or was created by a user from their company
            if not (log.company == company or (log.company is None and log.user and log.user.company_admin_profile.company == company)):
                return JsonResponse({'success': False, 'error': 'Access denied to this audit log'})
        
        # Format the log data for JSON response
        log_data = {
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user': log.user.get_full_name() if log.user else None,
            'action_type': log.get_action_type_display(),
            'resource_type': log.get_resource_type_display(),
            'resource_name': log.resource_name,
            'resource_id': log.resource_id,
            'action_description': log.action_description,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'success': log.success,
            'severity': log.get_severity_display(),
            'severity_color': log.severity_color,
            'error_message': log.error_message,
            'changes': log.changes,
            'additional_context': log.additional_context,
        }
        
        return JsonResponse({'success': True, 'log': log_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def data_protection(request):
    """Data protection page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get data protection records (using announcements as data protection records)
    data_records = Announcement.objects.filter(
        company=company,
        announcement_type='DATA_PROTECTION'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        data_records = data_records.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by data type
    data_type_filter = request.GET.get('data_type', '')
    if data_type_filter:
        data_records = data_records.filter(content__icontains=data_type_filter)
    
    # Pagination
    paginator = Paginator(data_records, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Data protection statistics
    total_records = data_records.count()
    sensitive_data = data_records.filter(is_active=True).count()
    protected_data = data_records.filter(is_active=False).count()
    
    context = {
        'title': 'Data Protection',
        'company': company,
        'data_records': page_obj,
        'search_query': search_query,
        'data_type_filter': data_type_filter,
        'total_records': total_records,
        'sensitive_data': sensitive_data,
        'protected_data': protected_data,
    }
    return render(request, 'core/data_protection.html', context)

@login_required
def compliance_reports(request):
    """Compliance reports page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get compliance reports (using projects as compliance reports)
    compliance_reports = Project.objects.filter(
        company=company,
        name__icontains='compliance'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        compliance_reports = compliance_reports.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by compliance type
    compliance_type_filter = request.GET.get('compliance_type', '')
    if compliance_type_filter:
        compliance_reports = compliance_reports.filter(description__icontains=compliance_type_filter)
    
    # Pagination
    paginator = Paginator(compliance_reports, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Compliance statistics
    total_reports = compliance_reports.count()
    active_reports = compliance_reports.filter(status='ACTIVE').count()
    completed_reports = compliance_reports.filter(status='COMPLETED').count()
    
    context = {
        'title': 'Compliance Reports',
        'company': company,
        'compliance_reports': page_obj,
        'search_query': search_query,
        'compliance_type_filter': compliance_type_filter,
        'total_reports': total_reports,
        'active_reports': active_reports,
        'completed_reports': completed_reports,
    }
    return render(request, 'core/compliance_reports.html', context)

@login_required
def security_settings(request):
    """Security settings page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get security settings (using announcements as security settings)
    security_settings = Announcement.objects.filter(
        company=company,
        announcement_type='SECURITY'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        security_settings = security_settings.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by setting type
    setting_type_filter = request.GET.get('setting_type', '')
    if setting_type_filter:
        security_settings = security_settings.filter(content__icontains=setting_type_filter)
    
    # Pagination
    paginator = Paginator(security_settings, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Security statistics
    total_settings = security_settings.count()
    active_settings = security_settings.filter(is_active=True).count()
    
    context = {
        'title': 'Security Settings',
        'company': company,
        'security_settings': page_obj,
        'search_query': search_query,
        'setting_type_filter': setting_type_filter,
        'total_settings': total_settings,
        'active_settings': active_settings,
    }
    return render(request, 'core/security_settings.html', context)

@login_required
def access_control(request):
    """Access control page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get access control records (using workflow instances as access records)
    access_records = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='access'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        access_records = access_records.filter(
            Q(template__name__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query)
        )
    
    # Filter by access level
    access_level_filter = request.GET.get('access_level', '')
    if access_level_filter:
        access_records = access_records.filter(status=access_level_filter)
    
    # Pagination
    paginator = Paginator(access_records, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Access control statistics
    total_records = access_records.count()
    active_access = access_records.filter(status='ACTIVE').count()
    revoked_access = access_records.filter(status='REVOKED').count()
    
    context = {
        'title': 'Access Control',
        'company': company,
        'access_records': page_obj,
        'search_query': search_query,
        'access_level_filter': access_level_filter,
        'total_records': total_records,
        'active_access': active_access,
        'revoked_access': revoked_access,
    }
    return render(request, 'core/access_control.html', context)

# Integrations & API Views
@login_required
def third_party_integrations(request):
    """Third-party integrations page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get integrations (using projects as integration records)
    integrations = Project.objects.filter(
        company=company,
        name__icontains='integration'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        integrations = integrations.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by integration type
    integration_type_filter = request.GET.get('integration_type', '')
    if integration_type_filter:
        integrations = integrations.filter(description__icontains=integration_type_filter)
    
    # Pagination
    paginator = Paginator(integrations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Integration statistics
    total_integrations = integrations.count()
    active_integrations = integrations.filter(status='ACTIVE').count()
    pending_integrations = integrations.filter(status='PENDING').count()
    
    context = {
        'title': 'Third-party Integrations',
        'company': company,
        'integrations': page_obj,
        'search_query': search_query,
        'integration_type_filter': integration_type_filter,
        'total_integrations': total_integrations,
        'active_integrations': active_integrations,
        'pending_integrations': pending_integrations,
    }
    return render(request, 'core/third_party_integrations.html', context)

@login_required
def api_management(request):
    """API management page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get API endpoints (using workflow instances as API records)
    api_endpoints = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='api'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        api_endpoints = api_endpoints.filter(
            Q(template__name__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query)
        )
    
    # Filter by API method
    method_filter = request.GET.get('method', '')
    if method_filter:
        api_endpoints = api_endpoints.filter(status=method_filter)
    
    # Pagination
    paginator = Paginator(api_endpoints, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # API statistics
    total_endpoints = api_endpoints.count()
    active_endpoints = api_endpoints.filter(status='ACTIVE').count()
    deprecated_endpoints = api_endpoints.filter(status='DEPRECATED').count()
    
    context = {
        'title': 'API Management',
        'company': company,
        'api_endpoints': page_obj,
        'search_query': search_query,
        'method_filter': method_filter,
        'total_endpoints': total_endpoints,
        'active_endpoints': active_endpoints,
        'deprecated_endpoints': deprecated_endpoints,
    }
    return render(request, 'core/api_management.html', context)

@login_required
def webhook_configuration(request):
    """Webhook configuration page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get webhooks (using announcements as webhook records)
    webhooks = Announcement.objects.filter(
        company=company,
        announcement_type='WEBHOOK'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        webhooks = webhooks.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by webhook type
    webhook_type_filter = request.GET.get('webhook_type', '')
    if webhook_type_filter:
        webhooks = webhooks.filter(content__icontains=webhook_type_filter)
    
    # Pagination
    paginator = Paginator(webhooks, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Webhook statistics
    total_webhooks = webhooks.count()
    active_webhooks = webhooks.filter(is_active=True).count()
    failed_webhooks = webhooks.filter(is_active=False).count()
    
    context = {
        'title': 'Webhook Configuration',
        'company': company,
        'webhooks': page_obj,
        'search_query': search_query,
        'webhook_type_filter': webhook_type_filter,
        'total_webhooks': total_webhooks,
        'active_webhooks': active_webhooks,
        'failed_webhooks': failed_webhooks,
    }
    return render(request, 'core/webhook_configuration.html', context)

@login_required
def integration_analytics(request):
    """Integration analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Integration usage statistics
    integration_usage = Project.objects.filter(
        company=company,
        name__icontains='integration'
    ).values('description').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # API call statistics
    api_calls = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='api'
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at) || '-01'"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Webhook performance
    webhook_performance = Announcement.objects.filter(
        company=company,
        announcement_type='WEBHOOK'
    ).values('is_active').annotate(
        count=Count('id')
    )
    
    context = {
        'title': 'Integration Analytics',
        'company': company,
        'integration_usage': integration_usage,
        'api_calls': api_calls,
        'webhook_performance': webhook_performance,
    }
    return render(request, 'core/integration_analytics.html', context)

# Company Settings Views
@login_required
def company_profile(request):
    """Company profile page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get company information
    company_info = {
        'name': company.name,
        'email': getattr(company, 'email', ''),
        'phone': getattr(company, 'phone', ''),
        'address': getattr(company, 'address', ''),
        'website': getattr(company, 'website', ''),
        'industry': getattr(company, 'industry', ''),
        'size': getattr(company, 'size', ''),
        'description': getattr(company, 'description', ''),
        'logo': getattr(company, 'logo', ''),
        'created_at': company.created_at,
        'domain': company.domain,
        'company_key': company.company_key,
        'max_users': company.max_users,
        'is_active': company.is_active,
    }
    
    context = {
        'title': 'Company Profile',
        'company': company,
        'company_info': company_info,
    }
    return render(request, 'core/company_profile.html', context)

@login_required
def billing_subscriptions(request):
    """Billing and subscriptions page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get subscription information
    try:
        subscription = company.subscription
        subscription_plan = subscription.plan
    except:
        subscription = None
        subscription_plan = None
    
    # Get billing history (using announcements as billing records)
    billing_history = Announcement.objects.filter(
        company=company,
        announcement_type='BILLING'
    ).order_by('-created_at')[:10]
    
    # Get payment methods
    payment_methods = PaymentMethod.objects.filter(company=company, is_active=True)
    
    # Calculate real usage data
    from django.contrib.auth.models import User
    from django.db.models import Sum
    
    # Count actual users in the company
    total_users = User.objects.filter(
        company_admin_profile__company=company
    ).count()
    
    # Count actual projects (assuming you have a Project model)
    try:
        from core.models import Project
        total_projects = Project.objects.filter(company=company).count()
    except:
        total_projects = 0
    
    # Calculate storage usage (assuming you have file/document models)
    try:
        from core.models import Document
        storage_usage_mb = Document.objects.filter(
            company=company
        ).aggregate(total_size=Sum('file_size'))['total_size'] or 0
        storage_usage_gb = round(storage_usage_mb / (1024 * 1024), 2) if storage_usage_mb else 0
    except:
        storage_usage_gb = 0
    
    # Get plan limits
    if subscription_plan:
        user_limit = subscription_plan.max_users
        project_limit = subscription_plan.max_projects
        storage_limit_gb = subscription_plan.max_storage_gb
    else:
        # Free plan limits
        user_limit = 5
        project_limit = 3
        storage_limit_gb = 1
    
    context = {
        'title': 'Billing & Subscriptions',
        'company': company,
        'subscription': subscription,
        'subscription_plan': subscription_plan,
        'billing_history': billing_history,
        'payment_methods': payment_methods,
        # Real usage data
        'total_users': total_users,
        'user_limit': user_limit,
        'total_projects': total_projects,
        'project_limit': project_limit,
        'storage_usage_gb': storage_usage_gb,
        'storage_limit_gb': storage_limit_gb,
    }
    return render(request, 'core/billing_subscriptions.html', context)

@login_required
def add_payment_method_page(request):
    """Add payment method page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    context = {
        'title': 'Add Payment Method',
        'company': company,
        'timestamp': int(timezone.now().timestamp()),
    }
    return render(request, 'core/add_payment_method.html', context)

@login_required
def system_settings(request):
    """System settings page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get system settings (using announcements as system settings)
    system_settings = Announcement.objects.filter(
        company=company,
        announcement_type='SYSTEM'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        system_settings = system_settings.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by setting category
    category_filter = request.GET.get('category', '')
    if category_filter:
        system_settings = system_settings.filter(content__icontains=category_filter)
    
    # Pagination
    paginator = Paginator(system_settings, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # System statistics
    total_settings = system_settings.count()
    active_settings = system_settings.filter(is_active=True).count()
    
    context = {
        'title': 'System Settings',
        'company': company,
        'system_settings': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'total_settings': total_settings,
        'active_settings': active_settings,
    }
    return render(request, 'core/system_settings.html', context)

@login_required
def user_preferences(request):
    """User preferences page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get or create user preferences
    preferences, created = UserPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'theme': 'LIGHT',
            'language': 'en',
            'timezone': 'UTC',
            'email_notifications': True,
            'dashboard_layout': {}
        }
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.theme = request.POST.get('theme', 'LIGHT')
        preferences.language = request.POST.get('language', 'en')
        preferences.timezone = request.POST.get('timezone', 'UTC')
        preferences.email_notifications = request.POST.get('email_notifications') == 'on'
        
        # Update dashboard layout if provided
        dashboard_layout = request.POST.get('dashboard_layout', '{}')
        try:
            preferences.dashboard_layout = json.loads(dashboard_layout)
        except json.JSONDecodeError:
            preferences.dashboard_layout = {}
        
        preferences.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            company=company,
            action='PREFERENCES_UPDATED',
            description='Updated user preferences',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, 'Your preferences have been updated successfully!')
        return redirect('core:user_preferences')
    
    # Get all users in the company for admin view
    company_users = User.objects.filter(
        company_admin_profile__company=company
    ).select_related('preferences')
    
    # Get preference statistics
    total_users = company_users.count()
    users_with_preferences = company_users.filter(preferences__isnull=False).count()
    
    context = {
        'title': 'User Preferences',
        'company': company,
        'preferences': preferences,
        'company_users': company_users,
        'total_users': total_users,
        'users_with_preferences': users_with_preferences,
        'theme_choices': UserPreference._meta.get_field('theme').choices,
        'language_choices': [
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ru', 'Russian'),
            ('zh', 'Chinese'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
        ],
        'timezone_choices': [
            ('UTC', 'UTC'),
            ('America/New_York', 'Eastern Time'),
            ('America/Chicago', 'Central Time'),
            ('America/Denver', 'Mountain Time'),
            ('America/Los_Angeles', 'Pacific Time'),
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Europe/Berlin', 'Berlin'),
            ('Asia/Tokyo', 'Tokyo'),
            ('Asia/Shanghai', 'Shanghai'),
            ('Australia/Sydney', 'Sydney'),
        ]
    }
    return render(request, 'core/user_preferences.html', context)

@login_required
def company_policies(request):
    """Company policies page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get company policies (using projects as policy records)
    company_policies = Project.objects.filter(
        company=company,
        name__icontains='policy'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        company_policies = company_policies.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by policy type
    policy_type_filter = request.GET.get('policy_type', '')
    if policy_type_filter:
        company_policies = company_policies.filter(description__icontains=policy_type_filter)
    
    # Pagination
    paginator = Paginator(company_policies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Policy statistics
    total_policies = company_policies.count()
    active_policies = company_policies.filter(status='ACTIVE').count()
    draft_policies = company_policies.filter(status='DRAFT').count()
    
    context = {
        'title': 'Company Policies',
        'company': company,
        'company_policies': page_obj,
        'search_query': search_query,
        'policy_type_filter': policy_type_filter,
        'total_policies': total_policies,
        'active_policies': active_policies,
        'draft_policies': draft_policies,
    }
    return render(request, 'core/company_policies.html', context)

# Reports & Analytics Views
@login_required
def dashboard_analytics(request):
    """Dashboard analytics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get analytics data
    analytics_data = {
        'total_users': company.employees.count(),
        'total_projects': company.projects.count(),
        'total_departments': company.departments.count(),
        'total_announcements': company.announcements.count(),
        'active_projects': company.projects.filter(status='ACTIVE').count(),
        'completed_projects': company.projects.filter(status='COMPLETED').count(),
        'pending_projects': company.projects.filter(status='PENDING').count(),
    }
    
    # Get recent activity
    recent_activity = WorkflowInstance.objects.filter(
        template__company=company
    ).order_by('-created_at')[:10]
    
    context = {
        'title': 'Dashboard Analytics',
        'company': company,
        'analytics_data': analytics_data,
        'recent_activity': recent_activity,
    }
    return render(request, 'core/dashboard_analytics.html', context)

@login_required
def custom_reports(request):
    """Custom reports page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get custom reports (using projects as report records)
    custom_reports = Project.objects.filter(
        company=company,
        name__icontains='report'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        custom_reports = custom_reports.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by report type
    report_type_filter = request.GET.get('report_type', '')
    if report_type_filter:
        custom_reports = custom_reports.filter(description__icontains=report_type_filter)
    
    # Pagination
    paginator = Paginator(custom_reports, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Report statistics
    total_reports = custom_reports.count()
    active_reports = custom_reports.filter(status='ACTIVE').count()
    scheduled_reports = custom_reports.filter(status='SCHEDULED').count()
    
    context = {
        'title': 'Custom Reports',
        'company': company,
        'custom_reports': page_obj,
        'search_query': search_query,
        'report_type_filter': report_type_filter,
        'total_reports': total_reports,
        'active_reports': active_reports,
        'scheduled_reports': scheduled_reports,
    }
    return render(request, 'core/custom_reports.html', context)

@login_required
def data_export(request):
    """Data export page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get export history (using announcements as export records)
    export_history = Announcement.objects.filter(
        company=company,
        announcement_type='EXPORT'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        export_history = export_history.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by export type
    export_type_filter = request.GET.get('export_type', '')
    if export_type_filter:
        export_history = export_history.filter(content__icontains=export_type_filter)
    
    # Pagination
    paginator = Paginator(export_history, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Export statistics
    total_exports = export_history.count()
    successful_exports = export_history.filter(is_active=True).count()
    failed_exports = export_history.filter(is_active=False).count()
    
    context = {
        'title': 'Data Export',
        'company': company,
        'export_history': page_obj,
        'search_query': search_query,
        'export_type_filter': export_type_filter,
        'total_exports': total_exports,
        'successful_exports': successful_exports,
        'failed_exports': failed_exports,
    }
    return render(request, 'core/data_export.html', context)

@login_required
def performance_metrics(request):
    """Performance metrics page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get performance metrics
    performance_metrics = {
        'project_completion_rate': 85,
        'employee_productivity': 92,
        'customer_satisfaction': 88,
        'system_uptime': 99.5,
        'response_time': 245,
        'error_rate': 0.2,
    }
    
    # Get performance trends
    performance_trends = WorkflowInstance.objects.filter(
        template__company=company,
        template__name__icontains='performance'
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at) || '-01'"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'title': 'Performance Metrics',
        'company': company,
        'performance_metrics': performance_metrics,
        'performance_trends': performance_trends,
    }
    return render(request, 'core/performance_metrics.html', context)

@login_required
def business_intelligence(request):
    """Business intelligence page"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get business intelligence data
    business_intelligence = {
        'revenue_growth': 15.2,
        'customer_acquisition': 23.5,
        'employee_retention': 94.8,
        'market_share': 12.3,
        'operational_efficiency': 87.6,
        'innovation_index': 78.9,
    }
    
    # Get business insights
    business_insights = Announcement.objects.filter(
        company=company,
        announcement_type='INSIGHT'
    ).order_by('-created_at')[:5]
    
    context = {
        'title': 'Business Intelligence',
        'company': company,
        'business_intelligence': business_intelligence,
        'business_insights': business_insights,
    }
    return render(request, 'core/business_intelligence.html', context)

def employee_verification(request):
    """Employee verification page"""
    # Get company from URL parameter, session, or email domain
    company_id = request.GET.get('company') or request.session.get('verification_company_id')
    
    # If no company specified, clear any existing session and show domain verification
    if not company_id:
        # Clear any existing verification session to prevent showing wrong company
        if 'verification_company_id' in request.session:
            del request.session['verification_company_id']
        if request.method == 'POST':
            email_domain = request.POST.get('email_domain', '').strip()
            if email_domain:
                # Remove @ if user included it
                if email_domain.startswith('@'):
                    email_domain = email_domain[1:]
                
                # Find company by domain
                try:
                    company = Company.objects.get(domain=email_domain, is_active=True)
                    request.session['verification_company_id'] = company.id
                    return redirect('core:employee_verification')
                except Company.DoesNotExist:
                    messages.error(request, f'No company found with domain "{email_domain}". Please check with your administrator.')
                except Company.MultipleObjectsReturned:
                    messages.error(request, f'Multiple companies found with domain "{email_domain}". Please contact support.')
        
        context = {
            'title': 'Company Verification',
        }
        return render(request, 'core/company_domain_verification.html', context)
    
    try:
        company = Company.objects.get(id=company_id, is_active=True)
        request.session['verification_company_id'] = company_id
    except Company.DoesNotExist:
        messages.error(request, 'Invalid company selected.')
        return redirect('core:employee_verification')
    
    if request.method == 'POST':
        form = EmployeeVerificationForm(request.POST, company=company)
        if form.is_valid():
            employee = form.cleaned_data.get('employee')
            if employee:
                request.session['verified_employee_id'] = employee.id
                return redirect('core:employee_registration')
            else:
                messages.error(request, 'Employee verification failed. Please check your details.')
    else:
        form = EmployeeVerificationForm(company=company)
    
    context = {
        'title': 'Employee Verification',
        'form': form,
        'company': company,
        'debug_info': {
            'company_id': company_id,
            'company_name': company.name,
            'company_domain': company.domain,
            'session_company_id': request.session.get('verification_company_id'),
        }
    }
    return render(request, 'core/employee_verification.html', context)

def employee_verification_by_slug(request, company_slug):
    """Employee verification page for specific company via slug"""
    try:
        # Find company by slug (domain or name slug)
        company = Company.objects.get(
            Q(domain=company_slug) | Q(name__iexact=company_slug.replace('-', ' ')),
            is_active=True
        )
    except Company.DoesNotExist:
        messages.error(request, f'Company "{company_slug}" not found or inactive.')
        return redirect('core:employee_verification')
    except Company.MultipleObjectsReturned:
        # If multiple companies found, prefer by domain
        company = Company.objects.filter(domain=company_slug, is_active=True).first()
        if not company:
            messages.error(request, f'Multiple companies found for "{company_slug}". Please contact support.')
            return redirect('core:employee_verification')
    
    # Store company in session
    request.session['verification_company_id'] = company.id
    
    if request.method == 'POST':
        form = EmployeeVerificationForm(request.POST, company=company)
        if form.is_valid():
            employee = form.cleaned_data.get('employee')
            if employee:
                request.session['verified_employee_id'] = employee.id
                return redirect('core:employee_registration')
            else:
                messages.error(request, 'Employee verification failed. Please check your details.')
    else:
        form = EmployeeVerificationForm(company=company)
    
    context = {
        'title': 'Employee Verification',
        'form': form,
        'company': company,
    }
    return render(request, 'core/employee_verification.html', context)

def employee_registration(request):
    """Employee registration after verification"""
    verified_employee_id = request.session.get('verified_employee_id')
    if not verified_employee_id:
        messages.error(request, 'Please verify your identity first.')
        return redirect('core:employee_verification')
    
    try:
        employee = Employee.objects.get(id=verified_employee_id)
    except Employee.DoesNotExist:
        messages.error(request, 'Invalid verification. Please try again.')
        return redirect('core:employee_verification')
    
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create user account
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=employee.email,
                    password=form.cleaned_data['password'],
                    first_name=employee.first_name,
                    last_name=employee.last_name
                )
                
                # Link employee to user account
                employee.user_account = user
                employee.save()
                
                # Clear session
                del request.session['verified_employee_id']
                
                messages.success(request, 'Account created successfully! You can now login.')
                return redirect('core:login')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = EmployeeRegistrationForm()
    
    context = {
        'title': 'Create Account',
        'form': form,
        'employee': employee,
    }
    return render(request, 'core/employee_registration.html', context)

@login_required
def employee_dashboard(request):
    """Enhanced Employee dashboard with comprehensive data"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Get employee's tasks
    from datetime import datetime, timedelta
    
    # Task statistics
    my_tasks = Task.objects.filter(assigned_to=employee)
    completed_tasks = my_tasks.filter(status='DONE').count()
    in_progress_tasks = my_tasks.filter(status='IN_PROGRESS').count()
    pending_tasks = my_tasks.filter(status='TODO').count()
    
    # Recent tasks (last 10)
    recent_tasks = my_tasks.order_by('-created_at')[:10]
    
    # Project statistics
    active_projects = Project.objects.filter(
        Q(tasks__assigned_to=employee) | Q(project_manager=employee)
    ).distinct().count()
    
    # Time tracking statistics
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Hours today
    hours_today = Timesheet.objects.filter(
        employee=employee,
        date=today
    ).aggregate(total=Sum('total_hours'))['total'] or 0
    
    # Hours this week
    hours_week = Timesheet.objects.filter(
        employee=employee,
        date__gte=week_start
    ).aggregate(total=Sum('total_hours'))['total'] or 0
    
    # Hours this month
    hours_month = Timesheet.objects.filter(
        employee=employee,
        date__gte=month_start
    ).aggregate(total=Sum('total_hours'))['total'] or 0
    
    # Performance goals
    active_goals = PerformanceGoal.objects.filter(
        employee=employee,
        status__in=['NOT_STARTED', 'IN_PROGRESS']
    ).order_by('-priority', 'target_date')[:5]
    
    # Recent announcements
    recent_announcements = Announcement.objects.filter(
        company=company,
        is_active=True
    ).order_by('-created_at')[:3]
    
    # Leave requests
    pending_leave = LeaveRequest.objects.filter(
        employee=employee,
        status='PENDING'
    ).count()
    
    # Upcoming deadlines
    upcoming_deadlines = my_tasks.filter(
        due_date__gte=datetime.now(),
        status__in=['TODO', 'IN_PROGRESS']
    ).order_by('due_date')[:5]
    
    context = {
        'title': 'Employee Dashboard',
        'employee': employee,
        'company': company,
        'my_tasks': my_tasks.count(),
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'active_projects': active_projects,
        'hours_today': round(float(hours_today), 1),
        'hours_week': round(float(hours_week), 1),
        'hours_month': round(float(hours_month), 1),
        'recent_tasks': recent_tasks,
        'active_goals': active_goals,
        'recent_announcements': recent_announcements,
        'pending_leave': pending_leave,
        'upcoming_deadlines': upcoming_deadlines,
    }
    return render(request, 'core/employee_dashboard.html', context)

@login_required
def employee_tasks(request):
    """Employee task management page"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    # Get tasks with filtering
    tasks = Task.objects.filter(assigned_to=employee)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    # Order by due date and priority
    tasks = tasks.order_by('due_date', '-priority')
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'My Tasks',
        'employee': employee,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'task_statuses': Task._meta.get_field('status').choices,
        'task_priorities': Task._meta.get_field('priority').choices,
    }
    return render(request, 'core/employee_tasks.html', context)

@login_required
def employee_projects(request):
    """Employee projects overview"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    # Get projects where employee is assigned to tasks or is project manager
    projects = Project.objects.filter(
        Q(tasks__assigned_to=employee) | Q(project_manager=employee)
    ).distinct().order_by('-created_at')
    
    # Get project statistics
    project_stats = []
    for project in projects:
        project_tasks = Task.objects.filter(project=project, assigned_to=employee)
        stats = {
            'project': project,
            'total_tasks': project_tasks.count(),
            'completed_tasks': project_tasks.filter(status='DONE').count(),
            'in_progress_tasks': project_tasks.filter(status='IN_PROGRESS').count(),
            'pending_tasks': project_tasks.filter(status='TODO').count(),
            'overdue_tasks': project_tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['TODO', 'IN_PROGRESS']
            ).count(),
        }
        project_stats.append(stats)
    
    context = {
        'title': 'My Projects',
        'employee': employee,
        'project_stats': project_stats,
    }
    return render(request, 'core/employee_projects.html', context)

@login_required
def employee_timesheet(request):
    """Employee timesheet management"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    # Get current week's timesheets
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    timesheets = Timesheet.objects.filter(
        employee=employee,
        date__range=[week_start, week_end]
    ).order_by('date', 'start_time')
    
    # Calculate week totals
    week_total = timesheets.aggregate(total=Sum('total_hours'))['total'] or 0
    
    # Get recent timesheets for history
    recent_timesheets = Timesheet.objects.filter(
        employee=employee
    ).order_by('-date')[:20]
    
    context = {
        'title': 'Time Tracking',
        'employee': employee,
        'timesheets': timesheets,
        'week_total': round(float(week_total), 1),
        'week_start': week_start,
        'week_end': week_end,
        'recent_timesheets': recent_timesheets,
    }
    return render(request, 'core/employee_timesheet.html', context)

@login_required
def employee_edit_timesheet(request, timesheet_id):
    """Edit a specific timesheet entry for employees"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    try:
        timesheet = Timesheet.objects.get(
            id=timesheet_id,
            employee=employee
        )
    except Timesheet.DoesNotExist:
        messages.error(request, 'Timesheet entry not found.')
        return redirect('core:employee_timesheet')
    
    # Only allow editing of draft timesheets
    if timesheet.status != 'DRAFT':
        messages.error(request, 'Only draft timesheet entries can be edited.')
        return redirect('core:employee_timesheet')
    
    if request.method == 'POST':
        # Handle form submission
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        task_description = request.POST.get('task_description', '')
        work_performed = request.POST.get('work_performed', '')
        
        # Validate required fields
        if not all([date_str, start_time_str, end_time_str]):
            messages.error(request, 'Date, start time, and end time are required.')
            return redirect('core:employee_edit_timesheet', timesheet_id=timesheet_id)
        
        # Parse date and times
        from datetime import datetime
        
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, 'Invalid date/time format.')
            return redirect('core:employee_edit_timesheet', timesheet_id=timesheet_id)
        
        # Calculate total hours
        start_datetime = datetime.combine(entry_date, start_time)
        end_datetime = datetime.combine(entry_date, end_time)
        
        if end_datetime <= start_datetime:
            messages.error(request, 'End time must be after start time.')
            return redirect('core:employee_edit_timesheet', timesheet_id=timesheet_id)
        
        duration = end_datetime - start_datetime
        total_hours = duration.total_seconds() / 3600  # Convert to hours
        
        # Update timesheet entry
        timesheet.date = entry_date
        timesheet.start_time = start_time
        timesheet.end_time = end_time
        timesheet.total_hours = total_hours
        timesheet.task_description = task_description
        timesheet.work_performed = work_performed
        timesheet.save()
        
        messages.success(request, 'Timesheet entry updated successfully!')
        return redirect('core:employee_timesheet')
    
    context = {
        'title': f'Edit Timesheet Entry - {timesheet.date}',
        'employee': employee,
        'timesheet': timesheet,
    }
    return render(request, 'core/employee_edit_timesheet.html', context)

@login_required
def employee_chat(request):
    """Employee chat system"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Handle GET requests for loading data
    if request.method == 'GET':
        action = request.GET.get('action')
        
        if action == 'get_employees':
            employees = Employee.objects.filter(company=company).values('id', 'first_name', 'last_name', 'position')
            return JsonResponse({'success': True, 'employees': list(employees)})
        
        elif action == 'get_projects':
            from .models import Project
            projects = Project.objects.filter(company=company).values('id', 'name')
            return JsonResponse({'success': True, 'projects': list(projects)})
    
    # Handle POST request for creating new room
    if request.method == 'POST':
        try:
            room_name = request.POST.get('name')
            room_description = request.POST.get('description', '')
            room_type = request.POST.get('room_type', 'GROUP')
            department = request.POST.get('department', '')
            project_id = request.POST.get('project', '')
            participants = request.POST.getlist('participants')
            
            if not room_name:
                return JsonResponse({'success': False, 'message': 'Room name is required'})
            
            # Create new chat room
            room = ChatRoom.objects.create(
                name=room_name,
                description=room_description,
                room_type=room_type,
                company=company,
                created_by=employee
            )
            
            # Add creator as participant
            room.participants.add(employee)
            
            # Add selected participants
            if participants:
                participant_employees = Employee.objects.filter(
                    id__in=participants,
                    company=company
                )
                room.participants.add(*participant_employees)
            
            # Handle department-specific rooms
            if room_type == 'DEPARTMENT' and department:
                department_employees = Employee.objects.filter(
                    company=company,
                    department=department
                )
                room.participants.add(*department_employees)
                room.description = f"Department chat for {department}"
            
            # Handle project-specific rooms
            if room_type == 'PROJECT' and project_id:
                from .models import Project
                try:
                    project = Project.objects.get(id=project_id, company=company)
                    project_employees = project.team_members.all()
                    room.participants.add(*project_employees)
                    room.description = f"Project chat for {project.name}"
                except Project.DoesNotExist:
                    pass
            
            return JsonResponse({'success': True, 'message': 'Room created successfully', 'room_id': room.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error creating room: {str(e)}'})
    
    # Get chat rooms the employee is part of
    chat_rooms = ChatRoom.objects.filter(
        company=company,
        participants=employee,
        is_active=True
    ).order_by('-updated_at')
    
    # Get recent messages for each room
    for room in chat_rooms:
        room.recent_message = ChatMessage.objects.filter(room=room).last()
        try:
            participant = ChatParticipant.objects.get(room=room, employee=employee)
            room.unread_count = ChatMessage.objects.filter(
                room=room,
                created_at__gt=participant.last_seen
            ).count()
        except ChatParticipant.DoesNotExist:
            room.unread_count = 0
    
    context = {
        'title': 'Team Chat',
        'employee': employee,
        'company': company,
        'chat_rooms': chat_rooms,
    }
    return render(request, 'core/employee_chat.html', context)

@login_required
def employee_chat_room(request, room_id):
    """Individual chat room view"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    try:
        room = ChatRoom.objects.get(
            id=room_id,
            participants=employee,
            is_active=True
        )
    except ChatRoom.DoesNotExist:
        messages.error(request, 'Chat room not found or access denied.')
        return redirect('core:employee_chat')
    
    # Handle POST request for sending messages
    if request.method == 'POST':
        try:
            content = request.POST.get('content', '').strip()
            attachment = request.FILES.get('attachment')
            
            if not content and not attachment:
                return JsonResponse({'success': False, 'message': 'Message content or attachment is required'})
            
            # Create new message
            message = ChatMessage.objects.create(
                room=room,
                sender=employee,
                content=content,
                attachment=attachment
            )
            
            # Update room's updated_at timestamp
            room.updated_at = timezone.now()
            room.save()
            
            return JsonResponse({'success': True, 'message': 'Message sent successfully', 'message_id': message.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error sending message: {str(e)}'})
    
    # Get messages for this room
    messages_list = ChatMessage.objects.filter(room=room).order_by('created_at')[:50]
    
    # Update last read time
    participant, created = ChatParticipant.objects.get_or_create(
        room=room,
        employee=employee
    )
    participant.last_seen = timezone.now()
    participant.save()
    
    context = {
        'title': f'Chat - {room.name}',
        'employee': employee,
        'room': room,
        'messages': messages_list,
    }
    return render(request, 'core/employee_chat_room.html', context)

@login_required
def employee_goals(request):
    """Employee performance goals"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    # Get all goals
    goals = PerformanceGoal.objects.filter(employee=employee).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        goals = goals.filter(status=status_filter)
    
    # Get goal statistics
    total_goals = goals.count()
    completed_goals = goals.filter(status='COMPLETED').count()
    in_progress_goals = goals.filter(status='IN_PROGRESS').count()
    
    context = {
        'title': 'My Goals',
        'employee': employee,
        'goals': goals,
        'status_filter': status_filter,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'in_progress_goals': in_progress_goals,
        'goal_statuses': PerformanceGoal._meta.get_field('status').choices,
    }
    return render(request, 'core/employee_goals.html', context)

@login_required
def employee_leave(request):
    """Employee leave management"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    
    # Get leave requests
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    
    # Calculate actual leave balance based on approved requests
    def calculate_leave_balance():
        # Default annual allocations
        annual_allocation = 20
        sick_allocation = 10
        personal_allocation = 5
        
        # Calculate used leave days for each type
        approved_annual = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='VACATION',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        approved_sick = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='SICK_LEAVE',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        approved_personal = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='PERSONAL',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        return {
            'annual': float(annual_allocation - approved_annual),
            'sick': float(sick_allocation - approved_sick),
            'personal': float(personal_allocation - approved_personal),
            'annual_used': float(approved_annual),
            'sick_used': float(approved_sick),
            'personal_used': float(approved_personal),
        }
    
    leave_balance = calculate_leave_balance()
    
    # Calculate pending requests count
    pending_requests_count = leave_requests.filter(status='PENDING').count()
    
    # Handle AJAX requests for real-time balance updates
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'leave_balance': leave_balance,
            'pending_requests': pending_requests_count,
        })
    
    context = {
        'title': 'Leave Management',
        'employee': employee,
        'leave_requests': leave_requests,
        'leave_balance': leave_balance,
        'pending_requests_count': pending_requests_count,
        'leave_types': LeaveRequest._meta.get_field('leave_type').choices,
        'leave_statuses': LeaveRequest._meta.get_field('status').choices,
    }
    return render(request, 'core/employee_leave.html', context)

@login_required
def employee_analytics(request):
    """Employee Analytics Dashboard with productivity insights"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg, Q
    import json
    
    # Date ranges
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Task Analytics
    my_tasks = Task.objects.filter(assigned_to=employee)
    
    # Task completion trends (last 30 days)
    task_trends = []
    for i in range(30):
        date = today - timedelta(days=i)
        completed = my_tasks.filter(
            status='DONE',
            updated_at__date=date
        ).count()
        task_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'completed': completed
        })
    task_trends.reverse()
    
    # Productivity metrics
    productivity_metrics = {
        'tasks_completed_today': my_tasks.filter(status='DONE', updated_at__date=today).count(),
        'tasks_completed_week': my_tasks.filter(status='DONE', updated_at__date__gte=week_start).count(),
        'tasks_completed_month': my_tasks.filter(status='DONE', updated_at__date__gte=month_start).count(),
        'overdue_tasks': my_tasks.filter(
            due_date__lt=today,
            status__in=['TODO', 'IN_PROGRESS']
        ).count(),
    }
    
    # Time tracking analytics
    timesheets = Timesheet.objects.filter(employee=employee)
    
    # Weekly time distribution
    weekly_hours = []
    for i in range(7):
        date = week_start + timedelta(days=i)
        hours = timesheets.filter(date=date).aggregate(
            total=Sum('total_hours')
        )['total'] or 0
        weekly_hours.append({
            'day': date.strftime('%A'),
            'hours': float(hours)
        })
    
    # Project contribution analytics
    projects = Project.objects.filter(
        Q(tasks__assigned_to=employee) | Q(project_manager=employee)
    ).distinct()
    
    project_contributions = []
    for project in projects:
        task_count = my_tasks.filter(project=project).count()
        completed_tasks = my_tasks.filter(project=project, status='DONE').count()
        project_hours = timesheets.filter(
            task__project=project
        ).aggregate(total=Sum('total_hours'))['total'] or 0
        
        project_contributions.append({
            'project_name': project.name,
            'total_tasks': task_count,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / task_count * 100) if task_count > 0 else 0,
            'hours_logged': float(project_hours),
            'status': project.status
        })
    
    context = {
        'title': 'Analytics Dashboard',
        'employee': employee,
        'company': company,
        'productivity_metrics': productivity_metrics,
        'task_trends': json.dumps(task_trends),
        'weekly_hours': json.dumps(weekly_hours),
        'project_contributions': project_contributions,
    }
    
    return render(request, 'core/employee_analytics.html', context)

@login_required
def employee_notifications(request):
    """Employee Notifications Center"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Get notifications
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(company=company),
        is_read=False
    ).order_by('-created_at')[:50]
    
    context = {
        'title': 'Notifications',
        'employee': employee,
        'company': company,
        'notifications': notifications,
    }
    
    return render(request, 'core/employee_notifications.html', context)

@login_required
def employee_team_directory(request):
    """Employee Team Directory"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Get team members
    team_members = Employee.objects.filter(
        company=company,
        user_account__is_active=True
    ).exclude(id=employee.id).order_by('first_name')
    
    # Group by department
    departments = team_members.values('department').distinct().order_by('department')
    
    context = {
        'title': 'Team Directory',
        'employee': employee,
        'company': company,
        'team_members': team_members,
        'departments': departments,
    }
    
    return render(request, 'core/employee_team_directory.html', context)

@login_required
def employee_calendar(request):
    """Employee Calendar and Scheduling"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    from datetime import datetime, timedelta
    
    # Get upcoming tasks with deadlines
    upcoming_tasks = Task.objects.filter(
        assigned_to=employee,
        due_date__gte=datetime.now().date(),
        status__in=['TODO', 'IN_PROGRESS']
    ).order_by('due_date')[:10]
    
    # Get leave requests
    leave_requests = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]
    
    context = {
        'title': 'Calendar',
        'employee': employee,
        'company': company,
        'upcoming_tasks': upcoming_tasks,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'core/employee_calendar.html', context)

@login_required
def employee_kanban_board(request):
    """Advanced Task Management with Kanban Board"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Get tasks organized by status
    todo_tasks = Task.objects.filter(
        assigned_to=employee,
        status='TODO'
    ).order_by('-priority', 'due_date')
    
    in_progress_tasks = Task.objects.filter(
        assigned_to=employee,
        status='IN_PROGRESS'
    ).order_by('-priority', 'due_date')
    
    review_tasks = Task.objects.filter(
        assigned_to=employee,
        status='REVIEW'
    ).order_by('-priority', 'due_date')
    
    done_tasks = Task.objects.filter(
        assigned_to=employee,
        status='DONE'
    ).order_by('-updated_at')[:10]  # Show only recent completed tasks
    
    context = {
        'title': 'Task Board',
        'employee': employee,
        'company': company,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'done_tasks': done_tasks,
    }
    
    return render(request, 'core/employee_kanban.html', context)

@login_required
def employee_gamification(request):
    """Employee Gamification and Recognition"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Calculate achievements and points
    achievements = []
    total_points = 0
    
    # Task completion achievements
    completed_tasks = Task.objects.filter(assigned_to=employee, status='DONE').count()
    if completed_tasks >= 10:
        achievements.append({
            'name': 'Task Master',
            'description': 'Completed 10+ tasks',
            'icon': 'fas fa-tasks',
            'points': 100,
            'earned': True
        })
        total_points += 100
    
    # Time tracking achievements
    total_hours = Timesheet.objects.filter(employee=employee).aggregate(
        total=Sum('total_hours')
    )['total'] or 0
    if total_hours >= 100:
        achievements.append({
            'name': 'Time Tracker',
            'description': 'Logged 100+ hours',
            'icon': 'fas fa-clock',
            'points': 150,
            'earned': True
        })
        total_points += 150
    
    # Project completion achievements
    completed_projects = Project.objects.filter(
        tasks__assigned_to=employee,
        status='COMPLETED'
    ).distinct().count()
    if completed_projects >= 3:
        achievements.append({
            'name': 'Project Champion',
            'description': 'Completed 3+ projects',
            'icon': 'fas fa-project-diagram',
            'points': 200,
            'earned': True
        })
        total_points += 200
    
    # Leaderboard (team comparison)
    team_members = Employee.objects.filter(company=company)
    leaderboard = []
    for member in team_members:
        member_points = 0
        member_tasks = Task.objects.filter(assigned_to=member, status='DONE').count()
        member_hours = Timesheet.objects.filter(employee=member).aggregate(
            total=Sum('total_hours')
        )['total'] or 0
        
        member_points = member_tasks * 10 + member_hours * 2
        
        leaderboard.append({
            'employee': member,
            'points': member_points,
            'tasks_completed': member_tasks,
            'hours_logged': member_hours
        })
    
    leaderboard.sort(key=lambda x: x['points'], reverse=True)
    
    context = {
        'title': 'Achievements & Recognition',
        'employee': employee,
        'company': company,
        'achievements': achievements,
        'total_points': total_points,
        'leaderboard': leaderboard[:10],  # Top 10
    }
    
    return render(request, 'core/employee_gamification.html', context)

@login_required
def employee_documents(request):
    """Employee Document Management System"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Get document categories
    categories = [
        {'name': 'Personal Documents', 'icon': 'fas fa-user', 'color': 'primary'},
        {'name': 'Project Files', 'icon': 'fas fa-project-diagram', 'color': 'success'},
        {'name': 'Company Policies', 'icon': 'fas fa-building', 'color': 'info'},
        {'name': 'Training Materials', 'icon': 'fas fa-graduation-cap', 'color': 'warning'},
        {'name': 'Templates', 'icon': 'fas fa-file-alt', 'color': 'secondary'},
    ]
    
    # Sample documents (in real implementation, these would come from Document model)
    sample_documents = [
        {
            'name': 'Employee Handbook.pdf',
            'size': '2.5 MB',
            'type': 'PDF',
            'category': 'Company Policies',
            'uploaded_date': '2024-09-20',
            'shared_by': 'HR Department',
            'downloads': 45
        },
        {
            'name': 'Project Requirements.docx',
            'size': '1.2 MB',
            'type': 'DOCX',
            'category': 'Project Files',
            'uploaded_date': '2024-09-18',
            'shared_by': 'Project Manager',
            'downloads': 12
        },
        {
            'name': 'Training Module 1.pptx',
            'size': '5.8 MB',
            'type': 'PPTX',
            'category': 'Training Materials',
            'uploaded_date': '2024-09-15',
            'shared_by': 'Training Team',
            'downloads': 8
        }
    ]
    
    context = {
        'title': 'Document Management',
        'employee': employee,
        'company': company,
        'categories': categories,
        'documents': sample_documents,
    }
    
    return render(request, 'core/employee_documents.html', context)

@login_required
def employee_productivity(request):
    """Employee Productivity Tracking and Insights"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg, Q
    import json
    
    # Productivity metrics
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Focus time analysis
    focus_sessions = [
        {'date': '2024-09-22', 'duration': 120, 'tasks_completed': 3, 'productivity_score': 85},
        {'date': '2024-09-21', 'duration': 90, 'tasks_completed': 2, 'productivity_score': 78},
        {'date': '2024-09-20', 'duration': 150, 'tasks_completed': 4, 'productivity_score': 92},
        {'date': '2024-09-19', 'duration': 75, 'tasks_completed': 1, 'productivity_score': 65},
        {'date': '2024-09-18', 'duration': 180, 'tasks_completed': 5, 'productivity_score': 88},
    ]
    
    # Productivity patterns
    productivity_patterns = {
        'peak_hours': ['10:00-11:00', '14:00-15:00', '16:00-17:00'],
        'most_productive_day': 'Wednesday',
        'average_focus_time': 125,  # minutes
        'distraction_frequency': 3.2,  # per hour
        'break_efficiency': 78,  # percentage
    }
    
    # Work habits analysis
    work_habits = {
        'early_bird': True,
        'night_owl': False,
        'prefers_mornings': True,
        'takes_regular_breaks': True,
        'multitasker': False,
        'deep_worker': True,
    }
    
    # Productivity recommendations
    recommendations = [
        {
            'title': 'Optimize Your Morning Routine',
            'description': 'You\'re most productive in the morning. Schedule your most important tasks between 10-11 AM.',
            'priority': 'high',
            'category': 'Schedule Optimization'
        },
        {
            'title': 'Take More Regular Breaks',
            'description': 'Your break efficiency is 78%. Try taking a 5-minute break every 45 minutes.',
            'priority': 'medium',
            'category': 'Work-Life Balance'
        },
        {
            'title': 'Reduce Distractions',
            'description': 'You get distracted 3.2 times per hour. Consider using focus mode during deep work sessions.',
            'priority': 'high',
            'category': 'Focus Improvement'
        }
    ]
    
    context = {
        'title': 'Productivity Insights',
        'employee': employee,
        'company': company,
        'focus_sessions': json.dumps(focus_sessions),
        'productivity_patterns': productivity_patterns,
        'work_habits': work_habits,
        'recommendations': recommendations,
    }
    
    return render(request, 'core/employee_productivity.html', context)

@login_required
def employee_settings(request):
    """Employee Settings and Personalization"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Dashboard preferences
    dashboard_preferences = {
        'theme': 'light',
        'layout': 'grid',
        'widgets': ['tasks', 'calendar', 'notifications', 'analytics'],
        'auto_refresh': True,
        'refresh_interval': 30,  # seconds
    }
    
    # Notification preferences
    notification_preferences = {
        'email_notifications': True,
        'push_notifications': True,
        'sms_notifications': False,
        'task_reminders': True,
        'deadline_alerts': True,
        'meeting_reminders': True,
        'team_updates': True,
        'quiet_hours_start': '18:00',
        'quiet_hours_end': '08:00',
    }
    
    # Privacy settings
    privacy_settings = {
        'profile_visibility': 'team',
        'activity_status': 'visible',
        'work_hours_visible': True,
        'task_progress_visible': True,
        'achievements_public': True,
    }
    
    context = {
        'title': 'Settings & Preferences',
        'employee': employee,
        'company': company,
        'dashboard_preferences': dashboard_preferences,
        'notification_preferences': notification_preferences,
        'privacy_settings': privacy_settings,
    }
    
    return render(request, 'core/employee_settings.html', context)

@login_required
def employee_search(request):
    """Global Search for Employee Dashboard"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    query = request.GET.get('q', '')
    
    context = {
        'title': 'Global Search',
        'employee': employee,
        'company': company,
        'query': query,
    }
    
    return render(request, 'core/employee_search.html', context)

@login_required
def employee_shortcuts(request):
    """Keyboard Shortcuts Help Page"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    context = {
        'title': 'Keyboard Shortcuts',
        'employee': employee,
        'company': company,
    }
    
    return render(request, 'core/employee_shortcuts.html', context)

@login_required
def employee_onboarding(request):
    """Employee Onboarding Flow"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Check if onboarding was already completed
    onboarding_completed = request.session.get('onboarding_completed', False)
    
    context = {
        'title': 'Welcome to ProjectManager Pro',
        'employee': employee,
        'company': company,
        'onboarding_completed': onboarding_completed,
    }
    
    return render(request, 'core/employee_onboarding.html', context)

def about(request):
    """About page view"""
    context = {
        'title': 'About',
    }
    return render(request, 'core/about.html', context)

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        company = request.POST.get('company')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        messages.success(request, f'Thank you for your message, {name}! We will get back to you soon.')
        return redirect('core:contact')
    
    context = {
        'title': 'Contact',
    }
    return render(request, 'core/contact.html', context)

# Owner Management Pages
@login_required
def all_companies(request):
    """View all companies page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count
    
    companies = Company.objects.annotate(
        employee_count=Count('employees')
    ).order_by('-created_at')
    total_companies = companies.count()
    active_companies = companies.filter(is_active=True).count()
    inactive_companies = total_companies - active_companies
    
    context = {
        'title': 'All Companies',
        'companies': companies,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'inactive_companies': inactive_companies,
    }
    return render(request, 'core/all_companies.html', context)

@login_required
def company_analytics(request):
    """Company analytics page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count, Avg, Q
    from datetime import datetime, timedelta
    
    # Company statistics
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    inactive_companies = total_companies - active_companies
    
    # Company growth over time
    thirty_days_ago = datetime.now() - timedelta(days=30)
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    companies_last_30_days = Company.objects.filter(created_at__gte=thirty_days_ago).count()
    companies_last_7_days = Company.objects.filter(created_at__gte=seven_days_ago).count()
    
    # Employee statistics per company
    companies_with_employees = Company.objects.annotate(
        employee_count=Count('employees'),
        verified_employees=Count('employees', filter=Q(employees__is_verified=True)),
        registered_employees=Count('employees', filter=Q(employees__user_account__isnull=False))
    ).order_by('-employee_count')
    
    # Average employees per company
    avg_employees_per_company = companies_with_employees.aggregate(
        avg_employees=Avg('employee_count')
    )['avg_employees'] or 0
    
    # Company activity metrics
    companies_with_recent_activity = Company.objects.filter(
        updated_at__gte=seven_days_ago
    ).count()
    
    # Top companies by employee count
    top_companies = companies_with_employees[:10]
    
    # Company registration trends (last 12 months)
    monthly_registrations = []
    for i in range(12):
        month_start = datetime.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = Company.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_registrations.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_registrations.reverse()
    
    context = {
        'title': 'Company Analytics',
        'total_companies': total_companies,
        'active_companies': active_companies,
        'inactive_companies': inactive_companies,
        'companies_last_30_days': companies_last_30_days,
        'companies_last_7_days': companies_last_7_days,
        'avg_employees_per_company': round(avg_employees_per_company, 1),
        'companies_with_recent_activity': companies_with_recent_activity,
        'top_companies': top_companies,
        'monthly_registrations': monthly_registrations,
    }
    return render(request, 'core/company_analytics.html', context)

@login_required
def user_stats(request):
    """User statistics page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    total_employees = Employee.objects.count()
    total_admins = CompanyAdmin.objects.count()
    
    context = {
        'title': 'User Statistics',
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_employees': total_employees,
        'total_admins': total_admins,
    }
    return render(request, 'core/user_stats.html', context)

@login_required
def active_users(request):
    """Active users page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    active_users = User.objects.filter(is_active=True).order_by('-last_login')
    context = {
        'title': 'Active Users',
        'active_users': active_users,
    }
    return render(request, 'core/active_users.html', context)

@login_required
def user_activity(request):
    """User activity page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Recent user activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    # User login activity
    recent_logins = User.objects.filter(
        last_login__gte=thirty_days_ago
    ).order_by('-last_login')
    
    # User registration activity
    recent_registrations = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).order_by('-date_joined')
    
    # Employee verification activity
    recent_verifications = Employee.objects.filter(
        updated_at__gte=thirty_days_ago,
        is_verified=True
    ).order_by('-updated_at')
    
    # Activity statistics
    logins_last_7_days = User.objects.filter(
        last_login__gte=seven_days_ago
    ).count()
    
    registrations_last_7_days = User.objects.filter(
        date_joined__gte=seven_days_ago
    ).count()
    
    verifications_last_7_days = Employee.objects.filter(
        updated_at__gte=seven_days_ago,
        is_verified=True
    ).count()
    
    # Most active users (by last login)
    most_active_users = User.objects.filter(
        last_login__isnull=False
    ).order_by('-last_login')[:10]
    
    # User activity by hour (last 7 days)
    hourly_activity = []
    for hour in range(24):
        hour_start = datetime.now() - timedelta(days=7)
        hour_start = hour_start.replace(hour=hour, minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        count = User.objects.filter(
            last_login__gte=hour_start,
            last_login__lt=hour_end
        ).count()
        
        hourly_activity.append({
            'hour': f"{hour:02d}:00",
            'count': count
        })
    
    # Department activity
    department_activity = Employee.objects.values('department').annotate(
        count=Count('id'),
        verified_count=Count('id', filter=Q(is_verified=True))
    ).order_by('-count')
    
    context = {
        'title': 'User Activity',
        'recent_logins': recent_logins[:20],
        'recent_registrations': recent_registrations[:20],
        'recent_verifications': recent_verifications[:20],
        'logins_last_7_days': logins_last_7_days,
        'registrations_last_7_days': registrations_last_7_days,
        'verifications_last_7_days': verifications_last_7_days,
        'most_active_users': most_active_users,
        'hourly_activity': hourly_activity,
        'department_activity': department_activity,
    }
    return render(request, 'core/user_activity.html', context)

@login_required
def user_reports(request):
    """User reports page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count, Avg, Q
    from datetime import datetime, timedelta
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    
    # Employee statistics
    total_employees = Employee.objects.count()
    verified_employees = Employee.objects.filter(is_verified=True).count()
    unverified_employees = total_employees - verified_employees
    registered_employees = Employee.objects.filter(user_account__isnull=False).count()
    
    # User roles breakdown
    system_owners = User.objects.filter(system_owner_profile__isnull=False).count()
    company_admins = User.objects.filter(company_admin_profile__isnull=False).count()
    regular_employees = User.objects.filter(employee_profile__isnull=False).count()
    
    # Registration trends (last 12 months)
    monthly_registrations = []
    for i in range(12):
        month_start = datetime.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = User.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        monthly_registrations.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_registrations.reverse()
    
    # Department statistics
    department_stats = Employee.objects.values('department').annotate(
        total_count=Count('id'),
        verified_count=Count('id', filter=Q(is_verified=True)),
        registered_count=Count('id', filter=Q(user_account__isnull=False))
    ).order_by('-total_count')
    
    # Company user distribution
    company_user_distribution = Company.objects.annotate(
        total_users=Count('employees'),
        verified_users=Count('employees', filter=Q(employees__is_verified=True)),
        registered_users=Count('employees', filter=Q(employees__user_account__isnull=False))
    ).order_by('-total_users')
    
    # User activity metrics
    thirty_days_ago = datetime.now() - timedelta(days=30)
    users_with_recent_login = User.objects.filter(
        last_login__gte=thirty_days_ago
    ).count()
    
    users_never_logged_in = User.objects.filter(
        last_login__isnull=True
    ).count()
    
    # Average users per company
    avg_users_per_company = company_user_distribution.aggregate(
        avg_users=Avg('total_users')
    )['avg_users'] or 0
    
    context = {
        'title': 'User Reports',
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_employees': total_employees,
        'verified_employees': verified_employees,
        'unverified_employees': unverified_employees,
        'registered_employees': registered_employees,
        'system_owners': system_owners,
        'company_admins': company_admins,
        'regular_employees': regular_employees,
        'monthly_registrations': monthly_registrations,
        'department_stats': department_stats,
        'company_user_distribution': company_user_distribution,
        'users_with_recent_login': users_with_recent_login,
        'users_never_logged_in': users_never_logged_in,
        'avg_users_per_company': round(avg_users_per_company, 1),
    }
    return render(request, 'core/user_reports.html', context)

@login_required
def system_stats(request):
    """System statistics page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_health = {
            'cpu_usage': round(cpu_percent, 1),
            'memory_usage': round(memory.percent, 1),
            'disk_usage': round(disk.percent, 1),
            'memory_available': round(memory.available / (1024**3), 2),
            'disk_free': round(disk.free / (1024**3), 2),
        }
    except:
        system_health = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'memory_available': 0,
            'disk_free': 0,
        }
    
    context = {
        'title': 'System Statistics',
        'system_health': system_health,
    }
    return render(request, 'core/system_stats.html', context)

@login_required
def revenue_reports(request):
    """Revenue reports page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count, Sum
    from datetime import datetime, timedelta
    
    # Revenue simulation based on companies and users
    # In a real system, this would come from actual billing/payment data
    
    # Company-based revenue (assuming $100/month per company)
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    
    monthly_revenue_per_company = 100  # $100 per company per month
    total_monthly_revenue = active_companies * monthly_revenue_per_company
    total_annual_revenue = total_monthly_revenue * 12
    
    # User-based revenue (assuming $5/month per active user)
    active_users = User.objects.filter(is_active=True).count()
    monthly_revenue_per_user = 5  # $5 per user per month
    user_monthly_revenue = active_users * monthly_revenue_per_user
    
    # Total revenue
    total_revenue = total_monthly_revenue + user_monthly_revenue
    
    # Revenue trends (last 12 months)
    monthly_revenue_data = []
    for i in range(12):
        month_start = datetime.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        # Companies active in this month
        companies_in_month = Company.objects.filter(
            created_at__lt=month_end,
            is_active=True
        ).count()
        
        # Users active in this month
        users_in_month = User.objects.filter(
            date_joined__lt=month_end,
            is_active=True
        ).count()
        
        month_revenue = (companies_in_month * monthly_revenue_per_company) + (users_in_month * monthly_revenue_per_user)
        
        monthly_revenue_data.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': month_revenue,
            'companies': companies_in_month,
            'users': users_in_month
        })
    
    monthly_revenue_data.reverse()
    
    # Revenue by company size
    revenue_by_company_size = []
    company_sizes = [
        {'min': 1, 'max': 10, 'label': 'Small (1-10 users)'},
        {'min': 11, 'max': 50, 'label': 'Medium (11-50 users)'},
        {'min': 51, 'max': 100, 'label': 'Large (51-100 users)'},
        {'min': 101, 'max': 1000, 'label': 'Enterprise (100+ users)'}
    ]
    
    for size in company_sizes:
        companies_in_range = Company.objects.annotate(
            user_count=Count('employees')
        ).filter(
            user_count__gte=size['min'],
            user_count__lte=size['max'],
            is_active=True
        ).count()
        
        revenue_in_range = companies_in_range * monthly_revenue_per_company
        
        revenue_by_company_size.append({
            'label': size['label'],
            'companies': companies_in_range,
            'revenue': revenue_in_range
        })
    
    # Top revenue generating companies
    top_revenue_companies = Company.objects.annotate(
        user_count=Count('employees')
    ).filter(
        is_active=True
    ).order_by('-user_count')[:10]
    
    # Revenue growth metrics
    current_month_revenue = monthly_revenue_data[-1]['revenue'] if monthly_revenue_data else 0
    previous_month_revenue = monthly_revenue_data[-2]['revenue'] if len(monthly_revenue_data) > 1 else 0
    
    revenue_growth = 0
    if previous_month_revenue > 0:
        revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
    
    # Projected revenue (next 6 months)
    projected_revenue = []
    for i in range(1, 7):
        projected_month = datetime.now() + timedelta(days=30*i)
        projected_companies = active_companies + (i * 2)  # Assuming 2 new companies per month
        projected_users = active_users + (i * 10)  # Assuming 10 new users per month
        projected_rev = (projected_companies * monthly_revenue_per_company) + (projected_users * monthly_revenue_per_user)
        
        projected_revenue.append({
            'month': projected_month.strftime('%b %Y'),
            'revenue': projected_rev,
            'companies': projected_companies,
            'users': projected_users
        })
    
    context = {
        'title': 'Revenue Reports',
        'total_monthly_revenue': total_monthly_revenue,
        'user_monthly_revenue': user_monthly_revenue,
        'total_revenue': total_revenue,
        'total_annual_revenue': total_annual_revenue,
        'monthly_revenue_data': monthly_revenue_data,
        'revenue_by_company_size': revenue_by_company_size,
        'top_revenue_companies': top_revenue_companies,
        'revenue_growth': round(revenue_growth, 1),
        'projected_revenue': projected_revenue,
        'monthly_revenue_per_company': monthly_revenue_per_company,
        'monthly_revenue_per_user': monthly_revenue_per_user,
    }
    return render(request, 'core/revenue_reports.html', context)

@login_required
def growth_analytics(request):
    """Growth analytics page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Growth metrics over different time periods
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    ninety_days_ago = now - timedelta(days=90)
    one_year_ago = now - timedelta(days=365)
    
    # Company growth
    total_companies = Company.objects.count()
    companies_last_7_days = Company.objects.filter(created_at__gte=seven_days_ago).count()
    companies_last_30_days = Company.objects.filter(created_at__gte=thirty_days_ago).count()
    companies_last_90_days = Company.objects.filter(created_at__gte=ninety_days_ago).count()
    companies_last_year = Company.objects.filter(created_at__gte=one_year_ago).count()
    
    # User growth
    total_users = User.objects.count()
    users_last_7_days = User.objects.filter(date_joined__gte=seven_days_ago).count()
    users_last_30_days = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    users_last_90_days = User.objects.filter(date_joined__gte=ninety_days_ago).count()
    users_last_year = User.objects.filter(date_joined__gte=one_year_ago).count()
    
    # Employee growth
    total_employees = Employee.objects.count()
    employees_last_7_days = Employee.objects.filter(created_at__gte=seven_days_ago).count()
    employees_last_30_days = Employee.objects.filter(created_at__gte=thirty_days_ago).count()
    employees_last_90_days = Employee.objects.filter(created_at__gte=ninety_days_ago).count()
    employees_last_year = Employee.objects.filter(created_at__gte=one_year_ago).count()
    
    # Growth rates calculation
    def calculate_growth_rate(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    
    # Monthly growth trends (last 12 months)
    monthly_growth = []
    for i in range(12):
        month_start = now - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        companies_in_month = Company.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        users_in_month = User.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        
        employees_in_month = Employee.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_growth.append({
            'month': month_start.strftime('%b %Y'),
            'companies': companies_in_month,
            'users': users_in_month,
            'employees': employees_in_month
        })
    
    monthly_growth.reverse()
    
    # Weekly growth trends (last 12 weeks)
    weekly_growth = []
    for i in range(12):
        week_start = now - timedelta(days=7*i)
        week_end = week_start + timedelta(days=7)
        
        companies_in_week = Company.objects.filter(
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()
        
        users_in_week = User.objects.filter(
            date_joined__gte=week_start,
            date_joined__lt=week_end
        ).count()
        
        employees_in_week = Employee.objects.filter(
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()
        
        weekly_growth.append({
            'week': f"Week {12-i}",
            'companies': companies_in_week,
            'users': users_in_week,
            'employees': employees_in_week
        })
    
    weekly_growth.reverse()
    
    # Growth projections (next 6 months)
    # Simple linear projection based on recent growth
    avg_monthly_company_growth = companies_last_30_days
    avg_monthly_user_growth = users_last_30_days
    avg_monthly_employee_growth = employees_last_30_days
    
    projected_growth = []
    for i in range(1, 7):
        projected_month = now + timedelta(days=30*i)
        projected_companies = total_companies + (avg_monthly_company_growth * i)
        projected_users = total_users + (avg_monthly_user_growth * i)
        projected_employees = total_employees + (avg_monthly_employee_growth * i)
        
        projected_growth.append({
            'month': projected_month.strftime('%b %Y'),
            'companies': int(projected_companies),
            'users': int(projected_users),
            'employees': int(projected_employees)
        })
    
    # Growth by company size
    company_size_growth = []
    size_ranges = [
        {'min': 1, 'max': 10, 'label': 'Small'},
        {'min': 11, 'max': 50, 'label': 'Medium'},
        {'min': 51, 'max': 100, 'label': 'Large'},
        {'min': 101, 'max': 1000, 'label': 'Enterprise'}
    ]
    
    for size in size_ranges:
        companies_in_range = Company.objects.annotate(
            employee_count=Count('employees')
        ).filter(
            employee_count__gte=size['min'],
            employee_count__lte=size['max']
        ).count()
        
        new_companies_in_range = Company.objects.annotate(
            employee_count=Count('employees')
        ).filter(
            employee_count__gte=size['min'],
            employee_count__lte=size['max'],
            created_at__gte=thirty_days_ago
        ).count()
        
        company_size_growth.append({
            'label': size['label'],
            'total': companies_in_range,
            'new_last_30_days': new_companies_in_range,
            'growth_rate': calculate_growth_rate(new_companies_in_range, companies_in_range - new_companies_in_range)
        })
    
    context = {
        'title': 'Growth Analytics',
        'total_companies': total_companies,
        'total_users': total_users,
        'total_employees': total_employees,
        'companies_last_7_days': companies_last_7_days,
        'companies_last_30_days': companies_last_30_days,
        'companies_last_90_days': companies_last_90_days,
        'companies_last_year': companies_last_year,
        'users_last_7_days': users_last_7_days,
        'users_last_30_days': users_last_30_days,
        'users_last_90_days': users_last_90_days,
        'users_last_year': users_last_year,
        'employees_last_7_days': employees_last_7_days,
        'employees_last_30_days': employees_last_30_days,
        'employees_last_90_days': employees_last_90_days,
        'employees_last_year': employees_last_year,
        'monthly_growth': monthly_growth,
        'weekly_growth': weekly_growth,
        'projected_growth': projected_growth,
        'company_size_growth': company_size_growth,
        'avg_monthly_company_growth': avg_monthly_company_growth,
        'avg_monthly_user_growth': avg_monthly_user_growth,
        'avg_monthly_employee_growth': avg_monthly_employee_growth,
    }
    return render(request, 'core/growth_analytics.html', context)

@login_required
def custom_reports(request):
    """Custom reports page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from django.db.models import Count, Avg, Max, Min
    from datetime import datetime, timedelta
    
    # Custom report categories
    report_categories = [
        'Company Performance',
        'User Engagement',
        'System Usage',
        'Security Metrics',
        'Growth Analysis',
        'Revenue Analysis'
    ]
    
    # Company performance metrics
    company_performance = {
        'total_companies': Company.objects.count(),
        'active_companies': Company.objects.filter(is_active=True).count(),
        'avg_employees_per_company': Company.objects.annotate(
            employee_count=Count('employees')
        ).aggregate(avg=Avg('employee_count'))['avg'] or 0,
        'largest_company': Company.objects.annotate(
            employee_count=Count('employees')
        ).order_by('-employee_count').first(),
        'companies_with_recent_activity': Company.objects.filter(
            updated_at__gte=datetime.now() - timedelta(days=30)
        ).count()
    }
    
    # User engagement metrics
    user_engagement = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'users_with_recent_login': User.objects.filter(
            last_login__gte=datetime.now() - timedelta(days=30)
        ).count(),
        'users_never_logged_in': User.objects.filter(last_login__isnull=True).count(),
        'avg_users_per_company': Company.objects.annotate(
            user_count=Count('employees')
        ).aggregate(avg=Avg('user_count'))['avg'] or 0
    }
    
    # System usage metrics
    total_employees = Employee.objects.count()
    verified_employees = Employee.objects.filter(is_verified=True).count()
    registered_employees = Employee.objects.filter(user_account__isnull=False).count()
    unregistered_employees = total_employees - registered_employees
    
    system_usage = {
        'total_employees': total_employees,
        'verified_employees': verified_employees,
        'registered_employees': registered_employees,
        'unregistered_employees': unregistered_employees,
        'employees_by_department': Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count'),
        'companies_by_size': Company.objects.annotate(
            size=Count('employees')
        ).values('size').annotate(count=Count('id')).order_by('size')
    }
    
    # Security metrics
    security_metrics = {
        'failed_login_attempts': 0,  # Would come from SystemLog in real implementation
        'suspicious_activities': 0,   # Would come from SystemLog
        'password_resets': 0,        # Would come from SystemLog
        'account_locks': 0           # Would come from SystemLog
    }
    
    # Growth analysis
    growth_analysis = {
        'companies_last_30_days': Company.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ).count(),
        'users_last_30_days': User.objects.filter(
            date_joined__gte=datetime.now() - timedelta(days=30)
        ).count(),
        'employees_last_30_days': Employee.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ).count(),
        'growth_rate_companies': 0,  # Would calculate based on historical data
        'growth_rate_users': 0,      # Would calculate based on historical data
        'growth_rate_employees': 0   # Would calculate based on historical data
    }
    
    # Revenue analysis (simulated)
    revenue_analysis = {
        'monthly_revenue': Company.objects.filter(is_active=True).count() * 100,
        'annual_revenue': Company.objects.filter(is_active=True).count() * 100 * 12,
        'revenue_per_company': 100,
        'revenue_per_user': 5,
        'top_revenue_companies': Company.objects.annotate(
            employee_count=Count('employees')
        ).filter(is_active=True).order_by('-employee_count')[:5]
    }
    
    # Custom date range reports
    date_range_reports = []
    for days in [7, 30, 90, 365]:
        start_date = datetime.now() - timedelta(days=days)
        
        companies_in_range = Company.objects.filter(created_at__gte=start_date).count()
        users_in_range = User.objects.filter(date_joined__gte=start_date).count()
        employees_in_range = Employee.objects.filter(created_at__gte=start_date).count()
        
        date_range_reports.append({
            'period': f'Last {days} days',
            'companies': companies_in_range,
            'users': users_in_range,
            'employees': employees_in_range
        })
    
    context = {
        'title': 'Custom Reports',
        'report_categories': report_categories,
        'company_performance': company_performance,
        'user_engagement': user_engagement,
        'system_usage': system_usage,
        'security_metrics': security_metrics,
        'growth_analysis': growth_analysis,
        'revenue_analysis': revenue_analysis,
        'date_range_reports': date_range_reports,
    }
    return render(request, 'core/custom_reports.html', context)

@login_required
def system_settings(request):
    """System settings page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    context = {
        'title': 'System Settings',
    }
    return render(request, 'core/system_settings.html', context)

@login_required
def security_settings(request):
    """Security settings page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    if request.method == 'POST':
        # Handle security settings form submission
        password_policy = request.POST.get('password_policy')
        session_timeout = request.POST.get('session_timeout')
        two_factor_auth = request.POST.get('two_factor_auth') == 'on'
        ip_whitelist = request.POST.get('ip_whitelist')
        login_attempts = request.POST.get('login_attempts')
        
        # Here you would typically save these settings to database
        # For now, we'll just show a success message
        messages.success(request, 'Security settings updated successfully!')
        return redirect('core:security_settings')
    
    context = {
        'title': 'Security Settings',
    }
    return render(request, 'core/security_settings.html', context)

@login_required
def backup_restore(request):
    """Backup and restore page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_backup':
            # Handle backup creation
            backup_name = request.POST.get('backup_name', f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            backup_type = request.POST.get('backup_type', 'full')
            backup_location = request.POST.get('backup_location', '')
            
            try:
                # Create actual backup
                backup_path = create_real_backup(backup_name, backup_type, backup_location)
                messages.success(request, f'Backup "{backup_name}" created successfully at {backup_path}!')
            except Exception as e:
                messages.error(request, f'Backup failed: {str(e)}')
            
        elif action == 'restore_backup':
            # Handle backup restoration
            backup_id = request.POST.get('backup_id')
            if backup_id:
                try:
                    restore_real_backup(backup_id)
                    messages.success(request, f'Backup restored successfully!')
                except Exception as e:
                    messages.error(request, f'Restore failed: {str(e)}')
            else:
                messages.error(request, 'Please select a backup to restore.')
                
        elif action == 'delete_backup':
            # Handle backup deletion
            backup_id = request.POST.get('backup_id')
            if backup_id:
                try:
                    delete_real_backup(backup_id)
                    messages.success(request, 'Backup deleted successfully!')
                except Exception as e:
                    messages.error(request, f'Delete failed: {str(e)}')
            else:
                messages.error(request, 'Please select a backup to delete.')
        
        return redirect('core:backup_restore')
    
    # Get real backup data
    backups = get_real_backups()
    external_drives = get_external_drives()
    storage_info = get_storage_info()
    
    context = {
        'title': 'Backup & Restore',
        'backups': backups,
        'external_drives': external_drives,
        'storage_info': storage_info,
    }
    return render(request, 'core/backup_restore.html', context)

@login_required
def system_logs(request):
    """System logs page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    from .models import SystemLog
    from .logging_utils import SystemLogger
    
    # Get filter parameters
    level_filter = request.GET.get('level', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Start with all logs
    logs = SystemLog.objects.all()
    
    # Apply filters
    if level_filter:
        logs = logs.filter(level=level_filter)
    if category_filter:
        logs = logs.filter(category=category_filter)
    if search_query:
        logs = logs.filter(message__icontains=search_query)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)  # 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get log statistics
    total_logs = SystemLog.objects.count()
    error_logs = SystemLog.objects.filter(level='ERROR').count()
    warning_logs = SystemLog.objects.filter(level='WARNING').count()
    critical_logs = SystemLog.objects.filter(level='CRITICAL').count()
    
    # Get recent activity
    recent_logs = SystemLog.objects.all()[:10]
    
    # Get log levels and categories for filter dropdowns
    log_levels = SystemLog.LOG_LEVELS
    log_categories = SystemLog.LOG_CATEGORIES
    
    context = {
        'title': 'System Logs',
        'page_obj': page_obj,
        'logs': page_obj,
        'total_logs': total_logs,
        'error_logs': error_logs,
        'warning_logs': warning_logs,
        'critical_logs': critical_logs,
        'recent_logs': recent_logs,
        'log_levels': log_levels,
        'log_categories': log_categories,
        'level_filter': level_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'core/system_logs.html', context)

@login_required
def maintenance(request):
    """System maintenance page"""
    if not hasattr(request.user, 'system_owner_profile'):
        messages.error(request, 'Access denied. You are not authorized to view this page.')
        return redirect('core:home')
    
    import psutil
    import os
    from django.db import connection
    from django.core.cache import cache
    from datetime import datetime, timedelta
    
    # System health check
    system_health = {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time()),
    }
    
    # Database health
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM core_company")
            company_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM core_employee")
            employee_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM core_systemlog")
            log_count = cursor.fetchone()[0]
        
        database_health = {
            'status': 'Healthy',
            'migration_count': migration_count,
            'user_count': user_count,
            'company_count': company_count,
            'employee_count': employee_count,
            'log_count': log_count,
        }
    except Exception as e:
        database_health = {
            'status': 'Error',
            'error': str(e)
        }
    
    # Cache health
    try:
        cache.set('health_check', 'ok', 60)
        cache_status = 'Healthy' if cache.get('health_check') == 'ok' else 'Error'
    except Exception as e:
        cache_status = f'Error: {str(e)}'
    
    # File system health
    try:
        static_files_size = 0
        media_files_size = 0
        
        # Calculate static files size
        for root, dirs, files in os.walk('static'):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    static_files_size += os.path.getsize(file_path)
        
        # Calculate media files size
        for root, dirs, files in os.walk('media'):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    media_files_size += os.path.getsize(file_path)
        
        file_system_health = {
            'status': 'Healthy',
            'static_files_size_mb': round(static_files_size / (1024*1024), 2),
            'media_files_size_mb': round(media_files_size / (1024*1024), 2),
            'database_size_mb': round(os.path.getsize('db.sqlite3') / (1024*1024), 2) if os.path.exists('db.sqlite3') else 0,
        }
    except Exception as e:
        file_system_health = {
            'status': 'Error',
            'error': str(e)
        }
    
    # Maintenance tasks
    maintenance_tasks = [
        {
            'name': 'Clear Old Logs',
            'description': 'Remove system logs older than 90 days',
            'status': 'Pending',
            'last_run': None,
            'next_run': 'Weekly'
        },
        {
            'name': 'Database Optimization',
            'description': 'Optimize database tables and indexes',
            'status': 'Pending',
            'last_run': None,
            'next_run': 'Monthly'
        },
        {
            'name': 'Backup Verification',
            'description': 'Verify backup integrity and completeness',
            'status': 'Pending',
            'last_run': None,
            'next_run': 'Weekly'
        },
        {
            'name': 'Cache Cleanup',
            'description': 'Clear expired cache entries',
            'status': 'Pending',
            'last_run': None,
            'next_run': 'Daily'
        },
        {
            'name': 'Security Scan',
            'description': 'Scan for security vulnerabilities',
            'status': 'Pending',
            'last_run': None,
            'next_run': 'Weekly'
        }
    ]
    
    # System alerts
    alerts = []
    
    if system_health['cpu_usage'] > 80:
        alerts.append({
            'level': 'warning',
            'message': f'High CPU usage: {system_health["cpu_usage"]}%',
            'timestamp': datetime.now()
        })
    
    if system_health['memory_usage'] > 85:
        alerts.append({
            'level': 'warning',
            'message': f'High memory usage: {system_health["memory_usage"]}%',
            'timestamp': datetime.now()
        })
    
    if system_health['disk_usage'] > 90:
        alerts.append({
            'level': 'critical',
            'message': f'Low disk space: {system_health["disk_usage"]}% used',
            'timestamp': datetime.now()
        })
    
    # Recent system events
    recent_events = []
    try:
        from .models import SystemLog
        recent_events = SystemLog.objects.filter(
            level__in=['ERROR', 'CRITICAL', 'WARNING']
        ).order_by('-timestamp')[:10]
    except:
        pass
    
    context = {
        'title': 'System Maintenance',
        'system_health': system_health,
        'database_health': database_health,
        'cache_status': cache_status,
        'file_system_health': file_system_health,
        'maintenance_tasks': maintenance_tasks,
        'alerts': alerts,
        'recent_events': recent_events,
    }
    return render(request, 'core/maintenance.html', context)

# Real backup functions
import shutil
import json
import sqlite3
import os
import zipfile
import psutil
from datetime import datetime
from pathlib import Path
from django.conf import settings

def get_external_drives():
    """Detect all drives (internal and external) connected to the system"""
    drives = []
    try:
        # On Windows
        if os.name == 'nt':
            import win32api
            import win32file
            drives_info = win32api.GetLogicalDriveStrings()
            drives_list = drives_info.split('\000')[:-1]
            
            for drive in drives_list:
                try:
                    drive_type = win32file.GetDriveType(drive)
                    free_bytes = win32api.GetDiskFreeSpaceEx(drive)
                    total_bytes = free_bytes[1]
                    free_space = free_bytes[0]
                    used_space = total_bytes - free_space
                    
                    # Determine drive type
                    if drive_type == 2:  # Removable drive
                        drive_type_name = 'External'
                        icon = 'fas fa-usb'
                    elif drive_type == 3:  # Fixed drive
                        drive_type_name = 'Internal'
                        icon = 'fas fa-hdd'
                    elif drive_type == 4:  # Remote drive
                        drive_type_name = 'Network'
                        icon = 'fas fa-network-wired'
                    elif drive_type == 5:  # CD-ROM drive
                        drive_type_name = 'CD/DVD'
                        icon = 'fas fa-compact-disc'
                    else:
                        drive_type_name = 'Other'
                        icon = 'fas fa-hdd'
                    
                    drives.append({
                        'path': drive,
                        'name': f'{drive_type_name} Drive ({drive})',
                        'total_gb': round(total_bytes / (1024**3), 2),
                        'free_gb': round(free_space / (1024**3), 2),
                        'used_gb': round(used_space / (1024**3), 2),
                        'type': drive_type_name,
                        'icon': icon,
                        'usage_percent': round((used_space / total_bytes) * 100, 1)
                    })
                except:
                    continue
        else:
            # On Linux/Mac
            import subprocess
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    mount_point = parts[5]
                    total_size = parts[1]
                    used_size = parts[2]
                    free_size = parts[3]
                    
                    # Determine drive type
                    if '/media/' in mount_point or '/mnt/' in mount_point or '/Volumes/' in mount_point:
                        drive_type_name = 'External'
                        icon = 'fas fa-usb'
                    elif mount_point == '/' or '/home' in mount_point or '/var' in mount_point:
                        drive_type_name = 'Internal'
                        icon = 'fas fa-hdd'
                    elif '/tmp' in mount_point or '/dev' in mount_point:
                        drive_type_name = 'System'
                        icon = 'fas fa-cog'
                    else:
                        drive_type_name = 'Other'
                        icon = 'fas fa-hdd'
                    
                    drives.append({
                        'path': mount_point,
                        'name': f'{drive_type_name} Drive ({mount_point})',
                        'total_gb': total_size,
                        'free_gb': free_size,
                        'used_gb': used_size,
                        'type': drive_type_name,
                        'icon': icon,
                        'usage_percent': 0  # Would need to calculate from df output
                    })
    except Exception as e:
        print(f"Error detecting drives: {e}")
    
    return drives

def get_storage_info():
    """Get real storage information"""
    try:
        # Get system disk usage
        disk_usage = psutil.disk_usage('/')
        total_gb = round(disk_usage.total / (1024**3), 2)
        used_gb = round(disk_usage.used / (1024**3), 2)
        free_gb = round(disk_usage.free / (1024**3), 2)
        
        # Get backup directory size
        backup_dir = Path('backups')
        backup_size = 0
        if backup_dir.exists():
            for file_path in backup_dir.rglob('*'):
                if file_path.is_file():
                    backup_size += file_path.stat().st_size
        backup_size_gb = round(backup_size / (1024**3), 2)
        
        return {
            'total_gb': total_gb,
            'used_gb': used_gb,
            'free_gb': free_gb,
            'backup_size_gb': backup_size_gb,
            'usage_percent': round((used_gb / total_gb) * 100, 1)
        }
    except Exception as e:
        print(f"Error getting storage info: {e}")
        return {
            'total_gb': 0,
            'used_gb': 0,
            'free_gb': 0,
            'backup_size_gb': 0,
            'usage_percent': 0
        }

def get_real_backups():
    """Get real backup files from the system"""
    backups = []
    try:
        backup_dir = Path('backups')
        if not backup_dir.exists():
            backup_dir.mkdir(exist_ok=True)
        
        # Scan for backup files
        for backup_file in backup_dir.glob('*.zip'):
            stat = backup_file.stat()
            size_gb = round(stat.st_size / (1024**3), 2)
            created_time = datetime.fromtimestamp(stat.st_ctime)
            
            backups.append({
                'id': str(backup_file.stem),
                'name': backup_file.name,
                'path': str(backup_file),
                'type': 'Full' if 'full' in backup_file.name.lower() else 'Incremental',
                'size': f'{size_gb} GB',
                'created': created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Completed'
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
    except Exception as e:
        print(f"Error getting backups: {e}")
    
    return backups

def create_real_backup(backup_name, backup_type, backup_location):
    """Create a real backup of the system"""
    try:
        import zipfile
        from django.conf import settings
        
        # Create backup directory if it doesn't exist
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)
        
        # Determine backup location
        if backup_location and Path(backup_location).exists():
            backup_path = Path(backup_location) / f'{backup_name}.zip'
        else:
            backup_path = backup_dir / f'{backup_name}.zip'
        
        # Create ZIP backup
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup database
            db_path = settings.DATABASES['default']['NAME']
            if os.path.exists(db_path):
                zipf.write(db_path, 'database.sqlite3')
            
            # Backup media files
            media_path = settings.MEDIA_ROOT
            if os.path.exists(media_path):
                for root, dirs, files in os.walk(media_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, media_path)
                        zipf.write(file_path, f'media/{arcname}')
            
            # Backup static files
            static_paths = settings.STATICFILES_DIRS
            for static_path in static_paths:
                if os.path.exists(static_path):
                    for root, dirs, files in os.walk(static_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, static_path)
                            zipf.write(file_path, f'static/{arcname}')
            
            # Backup settings and configuration
            settings_info = {
                'backup_type': backup_type,
                'created_at': datetime.now().isoformat(),
                'django_version': '5.2.6',
                'database_engine': settings.DATABASES['default']['ENGINE']
            }
            zipf.writestr('backup_info.json', json.dumps(settings_info, indent=2))
        
        # Log successful backup creation
        log_backup_action(f'Backup "{backup_name}" created successfully at {backup_path}', additional_data={
            'backup_type': backup_type,
            'backup_location': str(backup_location) if backup_location else 'local',
            'backup_size': os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
        })
        
        return str(backup_path)
        
    except Exception as e:
        # Log backup failure
        log_error(f'Backup creation failed: {str(e)}', additional_data={
            'backup_name': backup_name,
            'backup_type': backup_type,
            'backup_location': str(backup_location) if backup_location else 'local',
            'error': str(e)
        })
        raise Exception(f"Failed to create backup: {str(e)}")

def restore_real_backup(backup_id):
    """Restore from a real backup"""
    try:
        import zipfile
        from django.conf import settings
        
        # Find backup file
        backup_dir = Path('backups')
        backup_file = backup_dir / f'{backup_id}.zip'
        
        if not backup_file.exists():
            raise Exception("Backup file not found")
        
        # Extract backup
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            # Restore database
            if 'database.sqlite3' in zipf.namelist():
                db_path = settings.DATABASES['default']['NAME']
                with zipf.open('database.sqlite3') as source, open(db_path, 'wb') as target:
                    target.write(source.read())
            
            # Restore media files
            media_path = settings.MEDIA_ROOT
            media_path.mkdir(exist_ok=True)
            
            for file_info in zipf.infolist():
                if file_info.filename.startswith('media/'):
                    file_path = media_path / file_info.filename[6:]  # Remove 'media/' prefix
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with zipf.open(file_info) as source, open(file_path, 'wb') as target:
                        target.write(source.read())
            
            # Restore static files
            static_paths = settings.STATICFILES_DIRS
            for static_path in static_paths:
                static_path.mkdir(exist_ok=True)
                
                for file_info in zipf.infolist():
                    if file_info.filename.startswith('static/'):
                        file_path = static_path / file_info.filename[7:]  # Remove 'static/' prefix
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with zipf.open(file_info) as source, open(file_path, 'wb') as target:
                            target.write(source.read())
        
        return True
        
    except Exception as e:
        raise Exception(f"Failed to restore backup: {str(e)}")

def delete_real_backup(backup_id):
    """Delete a real backup file"""
    try:
        backup_dir = Path('backups')
        backup_file = backup_dir / f'{backup_id}.zip'
        
        if backup_file.exists():
            backup_file.unlink()
            return True
        else:
            raise Exception("Backup file not found")
            
    except Exception as e:
        raise Exception(f"Failed to delete backup: {str(e)}")

# API endpoints for AJAX requests
@csrf_exempt
def api_stats(request):
    """API endpoint for dashboard statistics"""
    if request.method == 'GET':
        # Placeholder data - replace with actual database queries
        stats = {
            'total_projects': 0,
            'active_projects': 0,
            'completed_projects': 0,
            'total_tasks': 0,
            'completed_tasks': 0,
            'team_members': 0,
        }
        return JsonResponse(stats)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Subscription Management Views
@login_required
def subscription_plans(request):
    """View all subscription plans"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Owner privileges required.')
        return redirect('core:owner_dashboard')
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    # Get subscription statistics
    total_plans = plans.count()
    active_subscriptions = CompanySubscription.objects.filter(status='ACTIVE').count()
    trial_subscriptions = CompanySubscription.objects.filter(status='TRIAL').count()
    expired_subscriptions = CompanySubscription.objects.filter(status='EXPIRED').count()
    
    context = {
        'title': 'Subscription Plans',
        'plans': plans,
        'total_plans': total_plans,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'expired_subscriptions': expired_subscriptions,
    }
    
    return render(request, 'core/subscription_plans.html', context)


@login_required
def create_subscription_plan(request):
    """Create a new subscription plan"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Owner privileges required.')
        return redirect('core:owner_dashboard')
    
    if request.method == 'POST':
        try:
            plan_data = {
                'name': request.POST.get('name'),
                'plan_type': request.POST.get('plan_type'),
                'description': request.POST.get('description'),
                'price': request.POST.get('price'),
                'billing_cycle': request.POST.get('billing_cycle'),
                'max_users': request.POST.get('max_users'),
                'max_projects': request.POST.get('max_projects'),
                'max_storage_gb': request.POST.get('max_storage_gb'),
                'max_api_calls': request.POST.get('max_api_calls'),
                'has_analytics': request.POST.get('has_analytics') == 'on',
                'has_advanced_reporting': request.POST.get('has_advanced_reporting') == 'on',
                'has_api_access': request.POST.get('has_api_access') == 'on',
                'has_priority_support': request.POST.get('has_priority_support') == 'on',
                'has_custom_integrations': request.POST.get('has_custom_integrations') == 'on',
                'has_white_label': request.POST.get('has_white_label') == 'on',
                'is_popular': request.POST.get('is_popular') == 'on',
                'sort_order': request.POST.get('sort_order', 0),
            }
            
            plan = SubscriptionPlan.objects.create(**plan_data)
            
            SystemLogger.log(
                'INFO',
                'SUBSCRIPTION',
                f'Created new subscription plan: {plan.name}',
                user=request.user,
                request=request
            )
            
            messages.success(request, f'Subscription plan "{plan.name}" created successfully!')
            return redirect('core:subscription_plans')
            
        except Exception as e:
            messages.error(request, f'Error creating subscription plan: {str(e)}')
    
    context = {
        'title': 'Create Subscription Plan',
        'plan_types': SubscriptionPlan.PLAN_TYPES,
        'billing_cycles': SubscriptionPlan.BILLING_CYCLES,
    }
    
    return render(request, 'core/create_subscription_plan.html', context)


@login_required
def edit_subscription_plan(request, plan_id):
    """Edit a subscription plan"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Owner privileges required.')
        return redirect('core:owner_dashboard')
    
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        try:
            plan.name = request.POST.get('name')
            plan.plan_type = request.POST.get('plan_type')
            plan.description = request.POST.get('description')
            plan.price = request.POST.get('price')
            plan.billing_cycle = request.POST.get('billing_cycle')
            plan.max_users = request.POST.get('max_users')
            plan.max_projects = request.POST.get('max_projects')
            plan.max_storage_gb = request.POST.get('max_storage_gb')
            plan.max_api_calls = request.POST.get('max_api_calls')
            plan.has_analytics = request.POST.get('has_analytics') == 'on'
            plan.has_advanced_reporting = request.POST.get('has_advanced_reporting') == 'on'
            plan.has_api_access = request.POST.get('has_api_access') == 'on'
            plan.has_priority_support = request.POST.get('has_priority_support') == 'on'
            plan.has_custom_integrations = request.POST.get('has_custom_integrations') == 'on'
            plan.has_white_label = request.POST.get('has_white_label') == 'on'
            plan.is_popular = request.POST.get('is_popular') == 'on'
            plan.sort_order = request.POST.get('sort_order', 0)
            
            plan.save()
            
            SystemLogger.log(
                'INFO',
                'SUBSCRIPTION',
                f'Updated subscription plan: {plan.name}',
                user=request.user,
                request=request
            )
            
            messages.success(request, f'Subscription plan "{plan.name}" updated successfully!')
            return redirect('core:subscription_plans')
            
        except Exception as e:
            messages.error(request, f'Error updating subscription plan: {str(e)}')
    
    context = {
        'title': f'Edit {plan.name}',
        'plan': plan,
        'plan_types': SubscriptionPlan.PLAN_TYPES,
        'billing_cycles': SubscriptionPlan.BILLING_CYCLES,
    }
    
    return render(request, 'core/edit_subscription_plan.html', context)


@login_required
def company_subscriptions(request):
    """View all company subscriptions"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Owner privileges required.')
        return redirect('core:owner_dashboard')
    
    subscriptions = CompanySubscription.objects.select_related('company', 'plan').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(subscriptions, 20)
    page_number = request.GET.get('page')
    subscriptions = paginator.get_page(page_number)
    
    # Statistics
    total_subscriptions = CompanySubscription.objects.count()
    active_subscriptions = CompanySubscription.objects.filter(status='ACTIVE').count()
    trial_subscriptions = CompanySubscription.objects.filter(status='TRIAL').count()
    expired_subscriptions = CompanySubscription.objects.filter(status='EXPIRED').count()
    
    # Revenue calculations
    monthly_revenue = CompanySubscription.objects.filter(
        status='ACTIVE'
    ).aggregate(
        total=Sum('plan__price')
    )['total'] or 0
    
    context = {
        'title': 'Company Subscriptions',
        'subscriptions': subscriptions,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'monthly_revenue': monthly_revenue,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/company_subscriptions.html', context)


@login_required
def assign_subscription(request, company_id):
    """Assign a subscription plan to a company"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Owner privileges required.')
        return redirect('core:owner_dashboard')
    
    company = get_object_or_404(Company, id=company_id)
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    if request.method == 'POST':
        try:
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(SubscriptionPlan, id=plan_id)
            
            # Check if company already has a subscription
            if hasattr(company, 'subscription'):
                subscription = company.subscription
                subscription.plan = plan
                subscription.status = 'ACTIVE'
                subscription.start_date = timezone.now()
                subscription.save()
                
                SystemLogger.log(
                    'INFO',
                    'SUBSCRIPTION',
                    f'Updated subscription for company "{company.name}" to plan "{plan.name}"',
                    user=request.user,
                    request=request
                )
                
                messages.success(request, f'Subscription updated for {company.name}!')
            else:
                subscription = CompanySubscription.objects.create(
                    company=company,
                    plan=plan,
                    status='ACTIVE',
                    start_date=timezone.now()
                )
                
                SystemLogger.log(
                    'INFO',
                    'SUBSCRIPTION',
                    f'Assigned subscription plan "{plan.name}" to company "{company.name}"',
                    user=request.user,
                    request=request
                )
                
                messages.success(request, f'Subscription assigned to {company.name}!')
            
            return redirect('core:company_subscriptions')
            
        except Exception as e:
            messages.error(request, f'Error assigning subscription: {str(e)}')
    
    context = {
        'title': f'Assign Subscription - {company.name}',
        'company': company,
        'plans': plans,
    }
    
    return render(request, 'core/assign_subscription.html', context)


@login_required
def subscription_analytics(request):
    """Subscription analytics and reports"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Owner privileges required.')
        return redirect('core:owner_dashboard')
    
    # Revenue analytics
    monthly_revenue = CompanySubscription.objects.filter(
        status='ACTIVE'
    ).aggregate(
        total=Sum('plan__price')
    )['total'] or 0
    
    annual_revenue = monthly_revenue * 12
    
    # Subscription statistics
    total_subscriptions = CompanySubscription.objects.count()
    active_subscriptions = CompanySubscription.objects.filter(status='ACTIVE').count()
    trial_subscriptions = CompanySubscription.objects.filter(status='TRIAL').count()
    expired_subscriptions = CompanySubscription.objects.filter(status='EXPIRED').count()
    
    # Plan popularity
    plan_stats = SubscriptionPlan.objects.annotate(
        subscription_count=Count('companysubscription')
    ).order_by('-subscription_count')
    
    # Monthly growth
    current_month = timezone.now().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    current_month_subscriptions = CompanySubscription.objects.filter(
        created_at__gte=current_month
    ).count()
    
    last_month_subscriptions = CompanySubscription.objects.filter(
        created_at__gte=last_month,
        created_at__lt=current_month
    ).count()
    
    growth_rate = 0
    if last_month_subscriptions > 0:
        growth_rate = ((current_month_subscriptions - last_month_subscriptions) / last_month_subscriptions) * 100
    
    context = {
        'title': 'Subscription Analytics',
        'monthly_revenue': monthly_revenue,
        'annual_revenue': annual_revenue,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'plan_stats': plan_stats,
        'current_month_subscriptions': current_month_subscriptions,
        'last_month_subscriptions': last_month_subscriptions,
        'growth_rate': growth_rate,
    }
    
    return render(request, 'core/subscription_analytics.html', context)


def debug_company_data(request):
    """Debug view to check company data"""
    if not request.user.is_authenticated:
        return HttpResponse("Not logged in")
    
    debug_info = f"""
    <h2>User Debug Information</h2>
    <p><strong>Username:</strong> {request.user.username}</p>
    <p><strong>Email:</strong> {request.user.email}</p>
    <p><strong>Full Name:</strong> {request.user.get_full_name()}</p>
    <p><strong>Is Superuser:</strong> {request.user.is_superuser}</p>
    <p><strong>Is Staff:</strong> {request.user.is_staff}</p>
    <p><strong>User ID:</strong> {request.user.id}</p>
    <hr>
    <h3>Profile Checks</h3>
    <p><strong>Has Company Admin Profile:</strong> {hasattr(request.user, 'company_admin_profile')}</p>
    <p><strong>Has Employee Profile:</strong> {hasattr(request.user, 'employee_profile')}</p>
    <p><strong>Has System Owner Profile:</strong> {hasattr(request.user, 'system_owner_profile')}</p>
    <hr>
    """
    
    if hasattr(request.user, 'company_admin_profile'):
        try:
            company_admin = request.user.company_admin_profile
            company = company_admin.company
            debug_info += f"""
            <h3>Company Admin Info</h3>
            <p><strong>Company Admin ID:</strong> {company_admin.id}</p>
            <p><strong>Company:</strong> {company.name}</p>
            <p><strong>Company ID:</strong> {company.id}</p>
            <p><strong>License Key:</strong> {company.license_key or 'None'}</p>
            <p><strong>Is Premium:</strong> {company.is_premium}</p>
            <p><strong>Subscription Type:</strong> {company.subscription_type}</p>
            <p><strong>License Expires:</strong> {company.license_expires_at or 'None'}</p>
            <p><strong>Is License Valid:</strong> {company.is_license_valid}</p>
            <p><strong>Company Created:</strong> {company.created_at}</p>
            <p><strong>Company Updated:</strong> {company.updated_at}</p>
            """
        except Exception as e:
            debug_info += f"<p><strong>Error accessing company admin profile:</strong> {str(e)}</p>"
    elif hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        debug_info += f"""
        <h3>Employee Info</h3>
        <p><strong>Company:</strong> {employee.company.name}</p>
        <p><strong>Department:</strong> {employee.department}</p>
        <p><strong>Note:</strong> Employees cannot see activation keys</p>
        """
    elif hasattr(request.user, 'system_owner_profile'):
        debug_info += f"""
        <h3>System Owner Info</h3>
        <p><strong>Note:</strong> System owners manage all companies</p>
        """
    else:
        debug_info += f"""
        <h3>No Profile Found</h3>
        <p><strong>Note:</strong> This user has no associated profile. This might be the issue!</p>
        """
    
    # Check all CompanyAdmin records for this user
    debug_info += f"""
    <hr>
    <h3>Database Check</h3>
    """
    
    try:
        from .models import CompanyAdmin
        company_admins = CompanyAdmin.objects.filter(user=request.user)
        debug_info += f"<p><strong>CompanyAdmin records for this user:</strong> {company_admins.count()}</p>"
        
        for admin in company_admins:
            debug_info += f"""
            <p><strong>Admin ID:</strong> {admin.id}, <strong>Company:</strong> {admin.company.name}</p>
            """
    except Exception as e:
        debug_info += f"<p><strong>Error checking CompanyAdmin records:</strong> {str(e)}</p>"
    
    return HttpResponse(debug_info)

def debug_license_status(request):
    """Debug license status for current user"""
    if not request.user.is_authenticated:
        return HttpResponse("Not logged in")
    
    if not hasattr(request.user, 'company_admin_profile'):
        return HttpResponse("Not a company admin")
    
    company = request.user.company_admin_profile.company
    
    debug_info = f"""
    <h2>License Status Debug</h2>
    <p><strong>Company:</strong> {company.name}</p>
    <p><strong>License Key:</strong> {company.license_key}</p>
    <p><strong>Is Premium:</strong> {company.is_premium}</p>
    <p><strong>Subscription Type:</strong> {company.subscription_type}</p>
    <p><strong>License Expires:</strong> {company.license_expires_at}</p>
    <p><strong>Is License Valid:</strong> {company.is_license_valid}</p>
    <hr>
    <p><a href="/company/dashboard/">Go to Dashboard</a></p>
    <p><a href="/debug/company-data/">Full Debug Info</a></p>
    """
    
    return HttpResponse(debug_info)

def test_activation_key(request):
    """Test view to manually set activation key for debugging"""
    if not request.user.is_authenticated:
        return HttpResponse("Not logged in")
    
    if not hasattr(request.user, 'company_admin_profile'):
        return HttpResponse("Not a company admin")
    
    company = request.user.company_admin_profile.company
    
    # Generate test activation key
    import secrets
    import string
    
    def generate_activation_key():
        prefix = "PM-PRO-"
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        return prefix + suffix
    
    activation_key = generate_activation_key()
    
    # Update company
    company.license_key = activation_key
    company.is_premium = True
    company.subscription_type = 'STARTER'
    company.license_expires_at = timezone.now() + timedelta(days=365)
    
    try:
        company.save()
        return HttpResponse(f"""
        <h2>Test Activation Key Set</h2>
        <p><strong>Company:</strong> {company.name}</p>
        <p><strong>Activation Key:</strong> {activation_key}</p>
        <p><strong>Is Premium:</strong> {company.is_premium}</p>
        <p><strong>Subscription Type:</strong> {company.subscription_type}</p>
        <p><strong>License Expires:</strong> {company.license_expires_at}</p>
        <hr>
        <p><a href="/company/dashboard/">Go to Dashboard</a></p>
        <p><a href="/debug/company-data/">Check Debug Info</a></p>
        """)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def test_payment_flow(request):
    """Test view to simulate payment processing"""
    if not request.user.is_authenticated:
        return HttpResponse("Not logged in")
    
    if not hasattr(request.user, 'company_admin_profile'):
        return HttpResponse("Not a company admin")
    
    company = request.user.company_admin_profile.company
    
    # Get the first available plan
    try:
        plan = SubscriptionPlan.objects.filter(is_active=True).first()
        if not plan:
            return HttpResponse("No active plans found")
    except Exception as e:
        return HttpResponse(f"Error getting plan: {str(e)}")
    
    # Generate activation key
    import secrets
    import string
    
    def generate_activation_key():
        prefix = "PM-PRO-"
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        return prefix + suffix
    
    activation_key = generate_activation_key()
    
    # Update company
    company.license_key = activation_key
    company.is_premium = True
    company.subscription_type = plan.plan_type
    company.license_expires_at = timezone.now() + timedelta(days=365)
    
    try:
        company.save()
        return HttpResponse(f"""
        <h2>Test Payment Flow Completed</h2>
        <p><strong>Company:</strong> {company.name}</p>
        <p><strong>Plan:</strong> {plan.name} ({plan.plan_type})</p>
        <p><strong>Activation Key:</strong> {activation_key}</p>
        <p><strong>Is Premium:</strong> {company.is_premium}</p>
        <p><strong>Subscription Type:</strong> {company.subscription_type}</p>
        <p><strong>License Expires:</strong> {company.license_expires_at}</p>
        <hr>
        <p><a href="/company/dashboard/">Go to Dashboard</a></p>
        <p><a href="/debug/company-data/">Check Debug Info</a></p>
        <p><a href="/payment/">Back to Payment Page</a></p>
        """)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def payment_test(request):
    """Simple payment test page"""
    if request.method == 'POST':
        # Debug: Print all POST data
        print(f"DEBUG: Test form POST data received: {dict(request.POST)}")
        
        # Get form data
        selected_plan_id = request.POST.get('selected_plan_id', '')
        card_number = request.POST.get('cardNumber', '')
        cardholder_name = request.POST.get('cardholderName', '')
        
        print(f"DEBUG: Test form data - Plan ID: {selected_plan_id}, Card: {card_number}, Name: {cardholder_name}")
        
        return HttpResponse(f"""
        <h2>Test Form Submitted Successfully!</h2>
        <p><strong>Plan ID:</strong> {selected_plan_id}</p>
        <p><strong>Card Number:</strong> {card_number}</p>
        <p><strong>Cardholder Name:</strong> {cardholder_name}</p>
        <p><strong>All POST Data:</strong> {dict(request.POST)}</p>
        <hr>
        <p><a href="/payment-test/">Try Again</a></p>
        <p><a href="/payment/">Go to Real Payment Page</a></p>
        """)
    
    return render(request, 'core/payment_test.html')

def payment_page(request):
    """Payment page for free trial signup"""
    # Allow both authenticated and unauthenticated users
    # If user is authenticated and is superuser, redirect to owner dashboard
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.is_superuser:
            messages.error(request, 'System owners cannot subscribe to plans.')
            return redirect('core:owner_dashboard')
        elif hasattr(request.user, 'employee_profile'):
            # Employees should not be on the payment page to subscribe
            messages.warning(request, 'Employees cannot subscribe to plans. Please contact your company admin.')
            return redirect('core:employee_dashboard')
        # If it's a CompanyAdmin, they can proceed to select/manage subscriptions
        # The template will show the payment form for them
    
    # Handle POST request (payment processing)
    if request.method == 'POST':
        # Debug: Print all POST data
        print(f"DEBUG: POST data received: {dict(request.POST)}")
        
        # Get form data
        selected_plan_id = request.POST.get('selected_plan_id', '')
        card_number = request.POST.get('cardNumber', '')
        cardholder_name = request.POST.get('cardholderName', '')
        expiry_date = request.POST.get('expiryDate', '')
        cvv = request.POST.get('cvv', '')
        
        print(f"DEBUG: Form data - Plan ID: {selected_plan_id}, Card: {card_number}, Name: {cardholder_name}")
        
        # For testing purposes, we'll simulate a successful payment
        # In a real application, you would integrate with a payment processor like Stripe
        
        if request.user.is_authenticated and hasattr(request.user, 'company_admin_profile'):
            company = request.user.company_admin_profile.company
            
            # Check if plan ID is provided
            if not selected_plan_id:
                messages.error(request, 'Please select a plan before proceeding.')
                return redirect('core:payment')
            
            # Get the selected plan
            try:
                selected_plan = SubscriptionPlan.objects.get(id=selected_plan_id)
                print(f"DEBUG: Selected plan: {selected_plan.name} (ID: {selected_plan.id})")
            except SubscriptionPlan.DoesNotExist:
                messages.error(request, 'Invalid plan selected. Please try again.')
                return redirect('core:payment')
            
            # Generate activation key
            import secrets
            import string
            
            def generate_activation_key():
                """Generate a unique activation key"""
                prefix = "PM-PRO-"
                suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
                return prefix + suffix
            
            activation_key = generate_activation_key()
            
            # Update company with premium status and activation key
            print(f"DEBUG: Before update - Company: {company.name}, Current license_key: {company.license_key}")
            
            company.license_key = activation_key
            company.is_premium = True
            company.subscription_type = selected_plan.plan_type
            company.license_expires_at = timezone.now() + timedelta(days=365)  # 1 year
            
            print(f"DEBUG: After setting values - license_key: {company.license_key}, is_premium: {company.is_premium}")
            
            try:
                company.save()
                print(f"DEBUG: Company saved successfully")
                
                # Verify the save worked by reloading from database
                company.refresh_from_db()
                print(f"DEBUG: After refresh - license_key: {company.license_key}, is_premium: {company.is_premium}")
                
            except Exception as e:
                print(f"DEBUG: Error saving company: {str(e)}")
                messages.error(request, f'Error saving company data: {str(e)}')
                return redirect('core:payment')
            
            # Add success message
            messages.success(request, f'Payment successful! Your activation key has been generated and your premium features are now active.')
            
            # Redirect to dashboard
            return redirect('core:company_dashboard')
        else:
            messages.error(request, 'Please log in as a company admin to complete the payment.')
            return redirect('core:login')
    
    # Get available subscription plans
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
    
    context = {
        'title': 'Choose Your Plan',
        'plans': plans,
        'user': request.user if hasattr(request, 'user') else None,
        'is_authenticated': hasattr(request, 'user') and request.user.is_authenticated,
        'timestamp': int(timezone.now().timestamp()),  # Cache busting
    }
    
    return render(request, 'core/payment_page.html', context)

# Performance Management Views
@login_required
def performance_dashboard(request):
    """Performance management dashboard"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get performance overview data
    total_employees = Employee.objects.filter(company=company).count()
    active_reviews = PerformanceReview.objects.filter(
        employee__company=company,
        status__in=['DRAFT', 'IN_PROGRESS', 'EMPLOYEE_REVIEW', 'MANAGER_REVIEW']
    ).count()
    
    completed_reviews = PerformanceReview.objects.filter(
        employee__company=company,
        status='COMPLETED'
    ).count()
    
    active_goals = PerformanceGoal.objects.filter(
        employee__company=company,
        status__in=['NOT_STARTED', 'IN_PROGRESS']
    ).count()
    
    completed_goals = PerformanceGoal.objects.filter(
        employee__company=company,
        status='COMPLETED'
    ).count()
    
    overdue_goals = PerformanceGoal.objects.filter(
        employee__company=company,
        status__in=['NOT_STARTED', 'IN_PROGRESS'],
        target_date__lt=timezone.now().date()
    ).count()
    
    # Recent performance reviews
    recent_reviews = PerformanceReview.objects.filter(
        employee__company=company
    ).order_by('-created_at')[:5]
    
    # Recent goals
    recent_goals = PerformanceGoal.objects.filter(
        employee__company=company
    ).order_by('-created_at')[:5]
    
    # Performance metrics by department
    department_performance = PerformanceMetric.objects.filter(
        employee__company=company
    ).values('employee__department').annotate(
        avg_value=Avg('value'),
        total_metrics=Count('id')
    ).order_by('-avg_value')
    
    context = {
        'title': 'Performance Dashboard',
        'company': company,
        'total_employees': total_employees,
        'active_reviews': active_reviews,
        'completed_reviews': completed_reviews,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'overdue_goals': overdue_goals,
        'recent_reviews': recent_reviews,
        'recent_goals': recent_goals,
        'department_performance': department_performance,
    }
    
    return render(request, 'core/performance_dashboard.html', context)

@login_required
def performance_reviews(request):
    """Performance reviews management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
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
    
    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)
    
    # Get employees for filter dropdown
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Performance Reviews',
        'company': company,
        'reviews': reviews,
        'employees': employees,
        'status_filter': status_filter,
        'review_type_filter': review_type_filter,
        'employee_filter': employee_filter,
        'review_status_choices': PerformanceReview.REVIEW_STATUS,
        'review_type_choices': PerformanceReview.REVIEW_TYPES,
    }
    
    return render(request, 'core/performance_reviews.html', context)

@login_required
def performance_goals(request):
    """Performance goals management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
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
    
    # Pagination
    paginator = Paginator(goals, 20)
    page_number = request.GET.get('page')
    goals = paginator.get_page(page_number)
    
    # Get employees for filter dropdown
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Performance Goals',
        'company': company,
        'goals': goals,
        'employees': employees,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'employee_filter': employee_filter,
        'overdue_filter': overdue_filter,
        'goal_status_choices': PerformanceGoal.GOAL_STATUS,
        'priority_choices': PerformanceGoal.PRIORITY_LEVELS,
    }
    
    return render(request, 'core/performance_goals.html', context)

@login_required
def performance_feedback(request):
    """360-degree feedback management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
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
    
    # Pagination
    paginator = Paginator(feedback, 20)
    page_number = request.GET.get('page')
    feedback = paginator.get_page(page_number)
    
    # Get employees for filter dropdown
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    context = {
        'title': '360-Degree Feedback',
        'company': company,
        'feedback': feedback,
        'employees': employees,
        'feedback_type_filter': feedback_type_filter,
        'status_filter': status_filter,
        'employee_filter': employee_filter,
        'feedback_type_choices': Feedback.FEEDBACK_TYPES,
        'feedback_status_choices': Feedback.FEEDBACK_STATUS,
    }
    
    return render(request, 'core/performance_feedback.html', context)

@login_required
def performance_reports(request):
    """Performance reports and analytics"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
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
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)
    
    context = {
        'title': 'Performance Reports',
        'company': company,
        'reports': reports,
        'report_type_filter': report_type_filter,
        'period_filter': period_filter,
        'report_type_choices': PerformanceReport.REPORT_TYPES,
        'period_choices': PerformanceReport.REPORT_PERIODS,
    }
    
    return render(request, 'core/performance_reports.html', context)

@login_required
def employee_performance_detail(request, employee_id):
    """Individual employee performance detail"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    employee = get_object_or_404(Employee, id=employee_id, company=company)
    
    # Get employee's performance data
    reviews = PerformanceReview.objects.filter(employee=employee).order_by('-review_period_end')
    goals = PerformanceGoal.objects.filter(employee=employee).order_by('-target_date')
    feedback = Feedback.objects.filter(employee=employee).order_by('-created_at')
    metrics = PerformanceMetric.objects.filter(employee=employee).order_by('-period_end')
    
    # Calculate performance statistics
    total_reviews = reviews.count()
    completed_reviews = reviews.filter(status='COMPLETED').count()
    avg_score = reviews.filter(status='COMPLETED').aggregate(avg=Avg('overall_score'))['avg']
    
    total_goals = goals.count()
    completed_goals = goals.filter(status='COMPLETED').count()
    overdue_goals = goals.filter(
        status__in=['NOT_STARTED', 'IN_PROGRESS'],
        target_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'title': f'Performance - {employee.first_name} {employee.last_name}',
        'company': company,
        'employee': employee,
        'reviews': reviews,
        'goals': goals,
        'feedback': feedback,
        'metrics': metrics,
        'total_reviews': total_reviews,
        'completed_reviews': completed_reviews,
        'avg_score': avg_score,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'overdue_goals': overdue_goals,
    }
    
    return render(request, 'core/employee_performance_detail.html', context)

# Attendance Management Views
@login_required
def attendance_dashboard(request):
    """Attendance management dashboard"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get attendance overview data
    total_employees = Employee.objects.filter(company=company).count()
    today = timezone.now().date()
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(
        employee__company=company,
        date=today
    )
    
    present_today = today_attendance.filter(status='PRESENT').count()
    absent_today = today_attendance.filter(status='ABSENT').count()
    late_today = today_attendance.filter(status='LATE').count()
    on_leave_today = today_attendance.filter(status='ON_LEAVE').count()
    
    # Currently clocked in employees
    clocked_in_employees = today_attendance.filter(
        clock_in__isnull=False,
        clock_out__isnull=True
    )
    
    # Recent attendance records
    recent_attendance = Attendance.objects.filter(
        employee__company=company
    ).order_by('-date', '-clock_in')[:10]
    
    # Attendance statistics for the month
    month_start = today.replace(day=1)
    month_attendance = Attendance.objects.filter(
        employee__company=company,
        date__gte=month_start,
        date__lte=today
    )
    
    total_working_days = month_attendance.count()
    total_hours_worked = month_attendance.aggregate(
        total=Sum('total_hours')
    )['total'] or 0
    
    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        employee__company=company,
        status='PENDING'
    ).count()
    
    # Upcoming leaves
    upcoming_leaves = LeaveRequest.objects.filter(
        employee__company=company,
        status='APPROVED',
        start_date__gte=today
    ).order_by('start_date')[:5]
    
    context = {
        'title': 'Attendance Dashboard',
        'company': company,
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_today': late_today,
        'on_leave_today': on_leave_today,
        'clocked_in_employees': clocked_in_employees,
        'recent_attendance': recent_attendance,
        'total_working_days': total_working_days,
        'total_hours_worked': total_hours_worked,
        'pending_leaves': pending_leaves,
        'upcoming_leaves': upcoming_leaves,
    }
    
    return render(request, 'core/attendance_dashboard.html', context)

@login_required
def attendance_records(request):
    """Attendance records management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    employee_filter = request.GET.get('employee', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    attendance_records = Attendance.objects.filter(employee__company=company)
    
    # Apply filters
    if employee_filter:
        attendance_records = attendance_records.filter(employee__id=employee_filter)
    if status_filter:
        attendance_records = attendance_records.filter(status=status_filter)
    if date_from:
        attendance_records = attendance_records.filter(date__gte=date_from)
    if date_to:
        attendance_records = attendance_records.filter(date__lte=date_to)
    
    # Pagination
    paginator = Paginator(attendance_records, 20)
    page_number = request.GET.get('page')
    attendance_records = paginator.get_page(page_number)
    
    # Get employees for filter dropdown
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Attendance Records',
        'company': company,
        'attendance_records': attendance_records,
        'employees': employees,
        'employee_filter': employee_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'attendance_status_choices': Attendance.ATTENDANCE_STATUS,
    }
    
    return render(request, 'core/attendance_records.html', context)

@login_required
def leave_management(request):
    """Leave management system"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    employee_filter = request.GET.get('employee', '')
    leave_type_filter = request.GET.get('leave_type', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Force fresh database query - no caching for real-time data
    # Base queryset - always fresh from database
    leave_requests = LeaveRequest.objects.filter(employee__company=company).select_related('employee')
    
    # Apply filters
    if employee_filter:
        leave_requests = leave_requests.filter(employee__id=employee_filter)
    if leave_type_filter:
        leave_requests = leave_requests.filter(leave_type=leave_type_filter)
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    if date_from:
        leave_requests = leave_requests.filter(start_date__gte=date_from)
    if date_to:
        leave_requests = leave_requests.filter(end_date__lte=date_to)
    
    # Order by most recent first
    leave_requests = leave_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(leave_requests, 20)
    page_number = request.GET.get('page')
    leave_requests = paginator.get_page(page_number)
    
    # Get employees for filter dropdown
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    # Calculate statistics
    all_leave_requests = LeaveRequest.objects.filter(employee__company=company)
    total_requests = all_leave_requests.count()
    pending_requests = all_leave_requests.filter(status='PENDING').count()
    approved_requests = all_leave_requests.filter(status='APPROVED').count()
    
    # Handle AJAX requests for polling
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        recent_requests = all_leave_requests.filter(
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).order_by('-created_at')[:10]
        
        new_requests_data = []
        for req in recent_requests:
            new_requests_data.append({
                'id': req.id,
                'employee_name': f"{req.employee.first_name} {req.employee.last_name}",
                'leave_type': req.get_leave_type_display(),
                'start_date': req.start_date.strftime('%Y-%m-%d'),
                'end_date': req.end_date.strftime('%Y-%m-%d'),
                'total_days': str(req.total_days),
                'reason': req.reason,
                'status': req.status,
                'created_at': req.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'new_requests': new_requests_data,
            'total_requests': total_requests,
            'pending_requests': pending_requests,
        })
    
    context = {
        'title': 'Leave Management',
        'company': company,
        'leave_requests': leave_requests,
        'employees': employees,
        'employee_filter': employee_filter,
        'leave_type_filter': leave_type_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'leave_type_choices': LeaveRequest.LEAVE_TYPES,
        'leave_status_choices': LeaveRequest.LEAVE_STATUS,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
    }
    
    return render(request, 'core/leave_management.html', context)

@login_required
def leave_request_details(request, request_id):
    """View detailed information about a specific leave request"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    try:
        leave_request = LeaveRequest.objects.get(
            id=request_id,
            employee__company=company
        )
        
        context = {
            'title': f'Leave Request Details - {leave_request.employee.first_name} {leave_request.employee.last_name}',
            'company': company,
            'leave_request': leave_request,
        }
        return render(request, 'core/leave_request_details.html', context)
        
    except LeaveRequest.DoesNotExist:
        messages.error(request, 'Leave request not found.')
        return redirect('core:leave_management')

@login_required
def edit_leave_request(request, request_id):
    """Edit a specific leave request"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    try:
        leave_request = LeaveRequest.objects.get(
            id=request_id,
            employee__company=company
        )
    except LeaveRequest.DoesNotExist:
        messages.error(request, 'Leave request not found.')
        return redirect('core:leave_management')
    
    if request.method == 'POST':
        # Handle form submission
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        emergency_contact = request.POST.get('emergency_contact')
        emergency_phone = request.POST.get('emergency_phone')
        
        # Update the leave request
        leave_request.leave_type = leave_type
        leave_request.start_date = start
        leave_request.end_date = end
        leave_request.reason = reason
        leave_request.emergency_contact = emergency_contact
        leave_request.emergency_phone = emergency_phone
        
        # Convert string dates to date objects and set them
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            leave_request.start_date = start
            leave_request.end_date = end
            # The model's save method will automatically calculate total_days
        
        leave_request.save()
        
        messages.success(request, 'Leave request updated successfully!')
        return redirect('core:leave_request_details', request_id=request_id)
    
    # Get all employees for the company (for potential reassignment)
    employees = Employee.objects.filter(company=company)
    
    context = {
        'title': f'Edit Leave Request - {leave_request.employee.first_name} {leave_request.employee.last_name}',
        'company': company,
        'leave_request': leave_request,
        'employees': employees,
        'leave_types': LeaveRequest.LEAVE_TYPES,
    }
    return render(request, 'core/edit_leave_request.html', context)

@login_required
def timesheet_management(request):
    """Timesheet management system"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
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
    
    # Pagination
    paginator = Paginator(timesheets, 20)
    page_number = request.GET.get('page')
    timesheets = paginator.get_page(page_number)
    
    # Get employees and projects for filter dropdowns
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    projects = Project.objects.filter(company=company).order_by('name')
    
    context = {
        'title': 'Timesheet Management',
        'company': company,
        'timesheets': timesheets,
        'employees': employees,
        'projects': projects,
        'employee_filter': employee_filter,
        'project_filter': project_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'timesheet_status_choices': Timesheet.TIMESHEET_STATUS,
    }
    
    return render(request, 'core/timesheet_management.html', context)

@login_required
def shift_management(request):
    """Shift management system"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get shifts
    shifts = Shift.objects.filter(company=company).order_by('start_time')
    
    # Get employee shift assignments
    employee_shifts = EmployeeShift.objects.filter(
        shift__company=company,
        is_active=True
    ).order_by('-start_date')
    
    # Get employees for assignment dropdown
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Shift Management',
        'company': company,
        'shifts': shifts,
        'employee_shifts': employee_shifts,
        'employees': employees,
        'shift_type_choices': Shift.SHIFT_TYPES,
    }
    
    return render(request, 'core/shift_management.html', context)

@login_required
def employee_attendance_detail(request, employee_id):
    """Individual employee attendance detail"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    employee = get_object_or_404(Employee, id=employee_id, company=company)
    
    # Get employee's attendance data
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-requested_at')
    timesheets = Timesheet.objects.filter(employee=employee).order_by('-date')
    
    # Calculate attendance statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='PRESENT').count()
    absent_days = attendance_records.filter(status='ABSENT').count()
    late_days = attendance_records.filter(status='LATE').count()
    
    # Calculate total hours worked
    total_hours = attendance_records.aggregate(
        total=Sum('total_hours')
    )['total'] or 0
    
    overtime_hours = attendance_records.aggregate(
        total=Sum('overtime_hours')
    )['total'] or 0
    
    # Get current shift assignment
    current_shift = EmployeeShift.objects.filter(
        employee=employee,
        is_active=True,
        start_date__lte=timezone.now().date()
    ).first()
    
    context = {
        'title': f'Attendance - {employee.first_name} {employee.last_name}',
        'company': company,
        'employee': employee,
        'attendance_records': attendance_records,
        'leave_requests': leave_requests,
        'timesheets': timesheets,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'total_hours': total_hours,
        'overtime_hours': overtime_hours,
        'current_shift': current_shift,
    }
    
    return render(request, 'core/employee_attendance_detail.html', context)

# Notification Management Views
@login_required
def notification_center(request):
    """Notification center for managing all notifications"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    notification_type_filter = request.GET.get('type', '')
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    notifications = Notification.objects.filter(company=company)
    
    # Apply filters
    if notification_type_filter:
        notifications = notifications.filter(notification_type=notification_type_filter)
    if priority_filter:
        notifications = notifications.filter(priority=priority_filter)
    if status_filter == 'read':
        notifications = notifications.filter(is_read=True)
    elif status_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status_filter == 'archived':
        notifications = notifications.filter(is_archived=True)
    if date_from:
        notifications = notifications.filter(created_at__gte=date_from)
    if date_to:
        notifications = notifications.filter(created_at__lte=date_to)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # Get notification statistics
    total_notifications = Notification.objects.filter(company=company).count()
    unread_notifications = Notification.objects.filter(company=company, is_read=False).count()
    critical_notifications = Notification.objects.filter(company=company, priority='CRITICAL', is_read=False).count()
    
    # Get recent notifications for sidebar
    recent_notifications = Notification.objects.filter(company=company).order_by('-created_at')[:5]
    
    context = {
        'title': 'Notification Center',
        'company': company,
        'notifications': notifications,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'critical_notifications': critical_notifications,
        'recent_notifications': recent_notifications,
        'notification_type_filter': notification_type_filter,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'notification_type_choices': Notification.NOTIFICATION_TYPES,
        'priority_choices': Notification.PRIORITY_LEVELS,
    }
    
    return render(request, 'core/notification_center.html', context)

@login_required
def notification_templates(request):
    """Notification templates management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get templates
    templates = NotificationTemplate.objects.all().order_by('template_type')
    
    # Get template usage statistics
    template_stats = []
    for template in templates:
        usage_count = Notification.objects.filter(
            company=company,
            notification_type=template.template_type
        ).count()
        template_stats.append({
            'template': template,
            'usage_count': usage_count
        })
    
    context = {
        'title': 'Notification Templates',
        'company': company,
        'template_stats': template_stats,
        'template_type_choices': NotificationTemplate.TEMPLATE_TYPES,
    }
    
    return render(request, 'core/notification_templates.html', context)

@login_required
def notification_preferences(request):
    """User notification preferences"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get or create user preferences
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        company=company,
        defaults={
            'email_enabled': True,
            'push_enabled': True,
            'browser_enabled': True,
            'in_app_enabled': True,
        }
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.email_enabled = request.POST.get('email_enabled') == 'on'
        preferences.sms_enabled = request.POST.get('sms_enabled') == 'on'
        preferences.push_enabled = request.POST.get('push_enabled') == 'on'
        preferences.browser_enabled = request.POST.get('browser_enabled') == 'on'
        preferences.in_app_enabled = request.POST.get('in_app_enabled') == 'on'
        
        # Type preferences
        preferences.system_notifications = request.POST.get('system_notifications') == 'on'
        preferences.performance_notifications = request.POST.get('performance_notifications') == 'on'
        preferences.attendance_notifications = request.POST.get('attendance_notifications') == 'on'
        preferences.leave_notifications = request.POST.get('leave_notifications') == 'on'
        preferences.timesheet_notifications = request.POST.get('timesheet_notifications') == 'on'
        preferences.shift_notifications = request.POST.get('shift_notifications') == 'on'
        preferences.project_notifications = request.POST.get('project_notifications') == 'on'
        preferences.task_notifications = request.POST.get('task_notifications') == 'on'
        preferences.deadline_notifications = request.POST.get('deadline_notifications') == 'on'
        preferences.birthday_notifications = request.POST.get('birthday_notifications') == 'on'
        preferences.anniversary_notifications = request.POST.get('anniversary_notifications') == 'on'
        preferences.training_notifications = request.POST.get('training_notifications') == 'on'
        preferences.meeting_notifications = request.POST.get('meeting_notifications') == 'on'
        preferences.payroll_notifications = request.POST.get('payroll_notifications') == 'on'
        preferences.benefits_notifications = request.POST.get('benefits_notifications') == 'on'
        preferences.policy_notifications = request.POST.get('policy_notifications') == 'on'
        preferences.emergency_notifications = request.POST.get('emergency_notifications') == 'on'
        
        # Frequency preferences
        preferences.digest_frequency = request.POST.get('digest_frequency', 'IMMEDIATE')
        
        # Quiet hours
        preferences.quiet_hours_enabled = request.POST.get('quiet_hours_enabled') == 'on'
        if request.POST.get('quiet_hours_start'):
            preferences.quiet_hours_start = request.POST.get('quiet_hours_start')
        if request.POST.get('quiet_hours_end'):
            preferences.quiet_hours_end = request.POST.get('quiet_hours_end')
        
        preferences.save()
        messages.success(request, 'Notification preferences updated successfully!')
        return redirect('core:notification_preferences')
    
    context = {
        'title': 'Notification Preferences',
        'company': company,
        'preferences': preferences,
        'digest_frequency_choices': [
            ('IMMEDIATE', 'Immediate'),
            ('HOURLY', 'Hourly'),
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('NEVER', 'Never'),
        ],
    }
    
    return render(request, 'core/notification_preferences.html', context)

@login_required
def notification_digests(request):
    """Notification digests management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    digest_type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    digests = NotificationDigest.objects.filter(company=company)
    
    # Apply filters
    if digest_type_filter:
        digests = digests.filter(digest_type=digest_type_filter)
    if status_filter == 'sent':
        digests = digests.filter(is_sent=True)
    elif status_filter == 'pending':
        digests = digests.filter(is_sent=False)
    if date_from:
        digests = digests.filter(created_at__gte=date_from)
    if date_to:
        digests = digests.filter(created_at__lte=date_to)
    
    # Pagination
    paginator = Paginator(digests, 20)
    page_number = request.GET.get('page')
    digests = paginator.get_page(page_number)
    
    # Get digest statistics
    total_digests = NotificationDigest.objects.filter(company=company).count()
    sent_digests = NotificationDigest.objects.filter(company=company, is_sent=True).count()
    pending_digests = NotificationDigest.objects.filter(company=company, is_sent=False).count()
    
    context = {
        'title': 'Notification Digests',
        'company': company,
        'digests': digests,
        'total_digests': total_digests,
        'sent_digests': sent_digests,
        'pending_digests': pending_digests,
        'digest_type_filter': digest_type_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'digest_type_choices': NotificationDigest.DIGEST_TYPES,
    }
    
    return render(request, 'core/notification_digests.html', context)

@login_required
def create_notification(request):
    """Create new notification"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    if request.method == 'POST':
        # Create notification
        notification = Notification.objects.create(
            company=company,
            notification_type=request.POST.get('notification_type'),
            title=request.POST.get('title'),
            message=request.POST.get('message'),
            priority=request.POST.get('priority', 'MEDIUM'),
            channel=request.POST.get('channel', 'IN_APP'),
            action_url=request.POST.get('action_url', ''),
            action_text=request.POST.get('action_text', ''),
            scheduled_at=request.POST.get('scheduled_at') or None,
            expires_at=request.POST.get('expires_at') or None,
        )
        
        # Add metadata
        metadata = {}
        if request.POST.get('target_employees'):
            employee_ids = request.POST.get('target_employees').split(',')
            metadata['target_employees'] = employee_ids
        if request.POST.get('target_departments'):
            departments = request.POST.get('target_departments').split(',')
            metadata['target_departments'] = departments
        
        notification.metadata = metadata
        notification.save()
        
        messages.success(request, 'Notification created successfully!')
        return redirect('core:notification_center')
    
    # Get employees and departments for targeting
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    departments = Employee.objects.filter(company=company).values_list('department', flat=True).distinct()
    departments = [dept for dept in departments if dept]
    
    context = {
        'title': 'Create Notification',
        'company': company,
        'employees': employees,
        'departments': departments,
        'notification_type_choices': Notification.NOTIFICATION_TYPES,
        'priority_choices': Notification.PRIORITY_LEVELS,
        'channel_choices': Notification.NOTIFICATION_CHANNELS,
    }
    
    return render(request, 'core/create_notification.html', context)

@login_required
def notification_analytics(request):
    """Notification analytics and insights"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get analytics data
    total_notifications = Notification.objects.filter(company=company).count()
    read_notifications = Notification.objects.filter(company=company, is_read=True).count()
    unread_notifications = Notification.objects.filter(company=company, is_read=False).count()
    
    # Notification types distribution
    type_distribution = Notification.objects.filter(company=company).values('notification_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Priority distribution
    priority_distribution = Notification.objects.filter(company=company).values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Channel distribution
    channel_distribution = Notification.objects.filter(company=company).values('channel').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly trends
    monthly_trends = Notification.objects.filter(company=company).extra(
        select={'month': "strftime('%%Y-%%m', created_at) || '-01'"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Read rate by type
    read_rate_by_type = []
    for notification_type in Notification.NOTIFICATION_TYPES:
        type_code = notification_type[0]
        total = Notification.objects.filter(company=company, notification_type=type_code).count()
        read = Notification.objects.filter(company=company, notification_type=type_code, is_read=True).count()
        read_rate = (read / total * 100) if total > 0 else 0
        read_rate_by_type.append({
            'type': notification_type[1],
            'total': total,
            'read': read,
            'read_rate': read_rate
        })
    
    context = {
        'title': 'Notification Analytics',
        'company': company,
        'total_notifications': total_notifications,
        'read_notifications': read_notifications,
        'unread_notifications': unread_notifications,
        'type_distribution': type_distribution,
        'priority_distribution': priority_distribution,
        'channel_distribution': channel_distribution,
        'monthly_trends': monthly_trends,
        'read_rate_by_type': read_rate_by_type,
    }
    
    return render(request, 'core/notification_analytics.html', context)

# Onboarding Management Views
@login_required
def onboarding_dashboard(request):
    """Onboarding management dashboard"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get onboarding overview data
    total_workflows = OnboardingWorkflow.objects.filter(company=company).count()
    active_assignments = OnboardingAssignment.objects.filter(
        workflow__company=company,
        status__in=['NOT_STARTED', 'IN_PROGRESS', 'PENDING_APPROVAL']
    ).count()
    completed_assignments = OnboardingAssignment.objects.filter(
        workflow__company=company,
        status='COMPLETED'
    ).count()
    overdue_assignments = OnboardingAssignment.objects.filter(
        workflow__company=company,
        status__in=['NOT_STARTED', 'IN_PROGRESS', 'PENDING_APPROVAL']
    ).filter(due_date__lt=timezone.now()).count()
    
    # Recent onboarding assignments
    recent_assignments = OnboardingAssignment.objects.filter(
        workflow__company=company
    ).order_by('-assigned_at')[:10]
    
    # Onboarding statistics
    onboarding_stats = {
        'total_workflows': total_workflows,
        'active_assignments': active_assignments,
        'completed_assignments': completed_assignments,
        'overdue_assignments': overdue_assignments,
    }
    
    # Workflow performance
    workflow_performance = []
    for workflow in OnboardingWorkflow.objects.filter(company=company, status='ACTIVE'):
        assignments = OnboardingAssignment.objects.filter(workflow=workflow)
        total_assigned = assignments.count()
        completed = assignments.filter(status='COMPLETED').count()
        completion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
        
        workflow_performance.append({
            'workflow': workflow,
            'total_assigned': total_assigned,
            'completed': completed,
            'completion_rate': completion_rate,
            'avg_duration': workflow.estimated_duration_days,
        })
    
    # Pending approvals
    pending_approvals = OnboardingTaskAssignment.objects.filter(
        onboarding_assignment__workflow__company=company,
        status='PENDING_APPROVAL'
    ).order_by('-created_at')[:5]
    
    # Pending document reviews
    pending_documents = OnboardingDocumentSubmission.objects.filter(
        onboarding_assignment__workflow__company=company,
        status='PENDING'
    ).order_by('-submitted_at')[:5]
    
    context = {
        'title': 'Onboarding Dashboard',
        'company': company,
        'onboarding_stats': onboarding_stats,
        'recent_assignments': recent_assignments,
        'workflow_performance': workflow_performance,
        'pending_approvals': pending_approvals,
        'pending_documents': pending_documents,
    }
    
    return render(request, 'core/onboarding_dashboard.html', context)

@login_required
def onboarding_workflows(request):
    """Onboarding workflows management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    workflow_type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    workflows = OnboardingWorkflow.objects.filter(company=company)
    
    # Apply filters
    if workflow_type_filter:
        workflows = workflows.filter(workflow_type=workflow_type_filter)
    if status_filter:
        workflows = workflows.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(workflows, 20)
    page_number = request.GET.get('page')
    workflows = paginator.get_page(page_number)
    
    # Get workflow statistics
    workflow_stats = []
    for workflow in workflows:
        assignments = OnboardingAssignment.objects.filter(workflow=workflow)
        total_assigned = assignments.count()
        completed = assignments.filter(status='COMPLETED').count()
        in_progress = assignments.filter(status='IN_PROGRESS').count()
        
        workflow_stats.append({
            'workflow': workflow,
            'total_assigned': total_assigned,
            'completed': completed,
            'in_progress': in_progress,
            'completion_rate': (completed / total_assigned * 100) if total_assigned > 0 else 0,
        })
    
    context = {
        'title': 'Onboarding Workflows',
        'company': company,
        'workflows': workflows,
        'workflow_stats': workflow_stats,
        'workflow_type_filter': workflow_type_filter,
        'status_filter': status_filter,
        'workflow_type_choices': OnboardingWorkflow.WORKFLOW_TYPES,
        'workflow_status_choices': OnboardingWorkflow.WORKFLOW_STATUS,
    }
    
    return render(request, 'core/onboarding_workflows.html', context)

@login_required
def onboarding_assignments(request):
    """Onboarding assignments management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    employee_filter = request.GET.get('employee', '')
    workflow_filter = request.GET.get('workflow', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    assignments = OnboardingAssignment.objects.filter(workflow__company=company)
    
    # Apply filters
    if employee_filter:
        assignments = assignments.filter(employee__id=employee_filter)
    if workflow_filter:
        assignments = assignments.filter(workflow__id=workflow_filter)
    if status_filter:
        assignments = assignments.filter(status=status_filter)
    if date_from:
        assignments = assignments.filter(assigned_at__gte=date_from)
    if date_to:
        assignments = assignments.filter(assigned_at__lte=date_to)
    
    # Pagination
    paginator = Paginator(assignments, 20)
    page_number = request.GET.get('page')
    assignments = paginator.get_page(page_number)
    
    # Get employees and workflows for filter dropdowns
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    workflows = OnboardingWorkflow.objects.filter(company=company).order_by('name')
    
    context = {
        'title': 'Onboarding Assignments',
        'company': company,
        'assignments': assignments,
        'employees': employees,
        'workflows': workflows,
        'employee_filter': employee_filter,
        'workflow_filter': workflow_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'assignment_status_choices': OnboardingAssignment.ASSIGNMENT_STATUS,
    }
    
    return render(request, 'core/onboarding_assignments.html', context)

@login_required
def onboarding_tasks(request):
    """Onboarding tasks management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    workflow_filter = request.GET.get('workflow', '')
    task_type_filter = request.GET.get('task_type', '')
    priority_filter = request.GET.get('priority', '')
    
    # Base queryset
    tasks = OnboardingTask.objects.filter(workflow__company=company)
    
    # Apply filters
    if workflow_filter:
        tasks = tasks.filter(workflow__id=workflow_filter)
    if task_type_filter:
        tasks = tasks.filter(task_type=task_type_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(tasks, 20)
    page_number = request.GET.get('page')
    tasks = paginator.get_page(page_number)
    
    # Get workflows for filter dropdown
    workflows = OnboardingWorkflow.objects.filter(company=company).order_by('name')
    
    context = {
        'title': 'Onboarding Tasks',
        'company': company,
        'tasks': tasks,
        'workflows': workflows,
        'workflow_filter': workflow_filter,
        'task_type_filter': task_type_filter,
        'priority_filter': priority_filter,
        'task_type_choices': OnboardingTask.TASK_TYPES,
        'task_priority_choices': OnboardingTask.TASK_PRIORITY,
    }
    
    return render(request, 'core/onboarding_tasks.html', context)

@login_required
def onboarding_documents(request):
    """Onboarding documents management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    document_type_filter = request.GET.get('document_type', '')
    workflow_filter = request.GET.get('workflow', '')
    
    # Base queryset
    documents = OnboardingDocument.objects.filter(company=company)
    
    # Apply filters
    if document_type_filter:
        documents = documents.filter(document_type=document_type_filter)
    if workflow_filter:
        documents = documents.filter(workflows__id=workflow_filter)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)
    
    # Get workflows for filter dropdown
    workflows = OnboardingWorkflow.objects.filter(company=company).order_by('name')
    
    context = {
        'title': 'Onboarding Documents',
        'company': company,
        'documents': documents,
        'workflows': workflows,
        'document_type_filter': document_type_filter,
        'workflow_filter': workflow_filter,
        'document_type_choices': OnboardingDocument.DOCUMENT_TYPES,
    }
    
    return render(request, 'core/onboarding_documents.html', context)

@login_required
def onboarding_assign_workflow(request):
    """Assign onboarding workflow to employee"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        workflow_id = request.POST.get('workflow')
        due_date = request.POST.get('due_date')
        notes = request.POST.get('notes', '')
        
        try:
            employee = Employee.objects.get(id=employee_id, company=company)
            workflow = OnboardingWorkflow.objects.get(id=workflow_id, company=company)
            
            # Check if employee already has this workflow assigned
            existing_assignment = OnboardingAssignment.objects.filter(
                employee=employee,
                workflow=workflow
            ).first()
            
            if existing_assignment:
                messages.warning(request, f'{employee.first_name} {employee.last_name} already has this workflow assigned.')
                return redirect('core:onboarding_assign_workflow')
            
            # Create assignment
            assignment = OnboardingAssignment.objects.create(
                employee=employee,
                workflow=workflow,
                assigned_by=request.user,
                due_date=due_date or None,
                notes=notes,
            )
            
            # Create task assignments
            for task in workflow.workflow_tasks.all():
                OnboardingTaskAssignment.objects.create(
                    onboarding_assignment=assignment,
                    task=task,
                    due_date=due_date or None,
                )
            
            messages.success(request, f'Onboarding workflow assigned to {employee.first_name} {employee.last_name} successfully!')
            return redirect('core:onboarding_assignments')
            
        except (Employee.DoesNotExist, OnboardingWorkflow.DoesNotExist):
            messages.error(request, 'Invalid employee or workflow selected.')
    
    # Get employees and workflows for assignment
    employees = Employee.objects.filter(company=company).order_by('first_name', 'last_name')
    workflows = OnboardingWorkflow.objects.filter(company=company, status='ACTIVE').order_by('name')
    
    context = {
        'title': 'Assign Onboarding Workflow',
        'company': company,
        'employees': employees,
        'workflows': workflows,
    }
    
    return render(request, 'core/onboarding_assign_workflow.html', context)

@login_required
def employee_onboarding_detail(request, employee_id):
    """Individual employee onboarding detail"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    employee = get_object_or_404(Employee, id=employee_id, company=company)
    
    # Get employee's onboarding assignments
    assignments = OnboardingAssignment.objects.filter(employee=employee).order_by('-assigned_at')
    
    # Get task assignments
    task_assignments = OnboardingTaskAssignment.objects.filter(
        onboarding_assignment__employee=employee
    ).order_by('task__order')
    
    # Get document submissions
    document_submissions = OnboardingDocumentSubmission.objects.filter(
        employee=employee
    ).order_by('-submitted_at')
    
    # Calculate overall progress
    total_tasks = task_assignments.count()
    completed_tasks = task_assignments.filter(status='COMPLETED').count()
    overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get pending approvals
    pending_approvals = task_assignments.filter(status='PENDING_APPROVAL')
    
    # Get overdue tasks
    overdue_tasks = task_assignments.filter(
        due_date__lt=timezone.now(),
        status__in=['NOT_STARTED', 'IN_PROGRESS']
    )
    
    context = {
        'title': f'Onboarding - {employee.first_name} {employee.last_name}',
        'company': company,
        'employee': employee,
        'assignments': assignments,
        'task_assignments': task_assignments,
        'document_submissions': document_submissions,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overall_progress': overall_progress,
        'pending_approvals': pending_approvals,
        'overdue_tasks': overdue_tasks,
    }
    
    return render(request, 'core/employee_onboarding_detail.html', context)

# Document Management Views
@login_required
def document_library(request):
    """Document library management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    document_type_filter = request.GET.get('document_type', '')
    access_level_filter = request.GET.get('access_level', '')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset
    documents = Document.objects.filter(company=company, is_archived=False)
    
    # Apply filters
    if category_filter:
        documents = documents.filter(category__id=category_filter)
    if document_type_filter:
        documents = documents.filter(document_type=document_type_filter)
    if access_level_filter:
        documents = documents.filter(access_level=access_level_filter)
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(keywords__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Apply sorting
    documents = documents.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)
    
    # Get categories and other filter options
    categories = DocumentCategory.objects.filter(company=company, is_active=True).order_by('sort_order', 'name')
    departments = Employee.objects.filter(company=company).values_list('department', flat=True).distinct()
    departments = [dept for dept in departments if dept]
    
    # Get document statistics
    total_documents = Document.objects.filter(company=company, is_archived=False).count()
    total_size = Document.objects.filter(company=company, is_archived=False).aggregate(
        total_size=Sum('file_size')
    )['total_size'] or 0
    
    # Recent documents
    recent_documents = Document.objects.filter(company=company, is_archived=False).order_by('-created_at')[:5]
    
    # Most accessed documents
    most_accessed = Document.objects.filter(company=company, is_archived=False).order_by('-last_accessed')[:5]
    
    context = {
        'title': 'Document Library',
        'company': company,
        'documents': documents,
        'categories': categories,
        'departments': departments,
        'total_documents': total_documents,
        'total_size': total_size,
        'recent_documents': recent_documents,
        'most_accessed': most_accessed,
        'category_filter': category_filter,
        'document_type_filter': document_type_filter,
        'access_level_filter': access_level_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'document_type_choices': Document.DOCUMENT_TYPES,
        'access_level_choices': Document.ACCESS_LEVELS,
    }
    
    return render(request, 'core/document_library.html', context)

@login_required
def document_categories(request):
    """Document categories management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get categories with document counts
    categories = DocumentCategory.objects.filter(company=company).order_by('sort_order', 'name')
    
    # Get category statistics
    category_stats = []
    for category in categories:
        document_count = category.documents.count()
        total_size = category.documents.aggregate(total_size=Sum('file_size'))['total_size'] or 0
        
        category_stats.append({
            'category': category,
            'document_count': document_count,
            'total_size': total_size,
        })
    
    context = {
        'title': 'Document Categories',
        'company': company,
        'category_stats': category_stats,
    }
    
    return render(request, 'core/document_categories.html', context)

@login_required
def document_templates(request):
    """Document templates management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    template_type_filter = request.GET.get('template_type', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    templates = DocumentTemplate.objects.filter(company=company)
    
    # Apply filters
    if template_type_filter:
        templates = templates.filter(template_type=template_type_filter)
    if status_filter == 'active':
        templates = templates.filter(is_active=True)
    elif status_filter == 'inactive':
        templates = templates.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page')
    templates = paginator.get_page(page_number)
    
    # Get template statistics
    template_stats = {
        'total_templates': DocumentTemplate.objects.filter(company=company).count(),
        'active_templates': DocumentTemplate.objects.filter(company=company, is_active=True).count(),
        'public_templates': DocumentTemplate.objects.filter(company=company, is_public=True).count(),
        'total_usage': DocumentTemplate.objects.filter(company=company).aggregate(
            total_usage=Sum('usage_count')
        )['total_usage'] or 0,
    }
    
    context = {
        'title': 'Document Templates',
        'company': company,
        'templates': templates,
        'template_stats': template_stats,
        'template_type_filter': template_type_filter,
        'status_filter': status_filter,
        'template_type_choices': DocumentTemplate.TEMPLATE_TYPES,
    }
    
    return render(request, 'core/document_templates.html', context)

@login_required
def document_sharing(request):
    """Document sharing management"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get filter parameters
    document_filter = request.GET.get('document', '')
    share_type_filter = request.GET.get('share_type', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    shares = DocumentShare.objects.filter(document__company=company)
    
    # Apply filters
    if document_filter:
        shares = shares.filter(document__id=document_filter)
    if share_type_filter:
        shares = shares.filter(share_type=share_type_filter)
    if status_filter == 'expired':
        shares = shares.filter(expires_at__lt=timezone.now())
    elif status_filter == 'active':
        shares = shares.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
    
    # Pagination
    paginator = Paginator(shares, 20)
    page_number = request.GET.get('page')
    shares = paginator.get_page(page_number)
    
    # Get documents for filter dropdown
    documents = Document.objects.filter(company=company).order_by('title')
    
    # Get sharing statistics
    sharing_stats = {
        'total_shares': DocumentShare.objects.filter(document__company=company).count(),
        'active_shares': DocumentShare.objects.filter(
            document__company=company,
            expires_at__isnull=True
        ).count() + DocumentShare.objects.filter(
            document__company=company,
            expires_at__gt=timezone.now()
        ).count(),
        'expired_shares': DocumentShare.objects.filter(
            document__company=company,
            expires_at__lt=timezone.now()
        ).count(),
    }
    
    context = {
        'title': 'Document Sharing',
        'company': company,
        'shares': shares,
        'documents': documents,
        'sharing_stats': sharing_stats,
        'document_filter': document_filter,
        'share_type_filter': share_type_filter,
        'status_filter': status_filter,
        'share_type_choices': DocumentShare.SHARE_TYPES,
    }
    
    return render(request, 'core/document_sharing.html', context)

@login_required
def document_analytics(request):
    """Document analytics and insights"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    # Get analytics data
    total_documents = Document.objects.filter(company=company, is_archived=False).count()
    total_size = Document.objects.filter(company=company, is_archived=False).aggregate(
        total_size=Sum('file_size')
    )['total_size'] or 0
    
    # Document types distribution
    type_distribution = Document.objects.filter(company=company, is_archived=False).values('document_type').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Access levels distribution
    access_distribution = Document.objects.filter(company=company, is_archived=False).values('access_level').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Category distribution
    category_distribution = Document.objects.filter(company=company, is_archived=False).values('category__name').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Monthly upload trends
    monthly_uploads = Document.objects.filter(company=company, is_archived=False).extra(
        select={'month': "strftime('%%Y-%%m', created_at) || '-01'"}
    ).values('month').annotate(
        count=models.Count('id')
    ).order_by('month')
    
    # Most accessed documents
    most_accessed = Document.objects.filter(company=company, is_archived=False).order_by('-last_accessed')[:10]
    
    # Recent uploads
    recent_uploads = Document.objects.filter(company=company, is_archived=False).order_by('-created_at')[:10]
    
    # Document access analytics
    access_analytics = DocumentAccess.objects.filter(document__company=company).values('access_type').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    context = {
        'title': 'Document Analytics',
        'company': company,
        'total_documents': total_documents,
        'total_size': total_size,
        'type_distribution': type_distribution,
        'access_distribution': access_distribution,
        'category_distribution': category_distribution,
        'monthly_uploads': monthly_uploads,
        'most_accessed': most_accessed,
        'recent_uploads': recent_uploads,
        'access_analytics': access_analytics,
    }
    
    return render(request, 'core/document_analytics.html', context)

@login_required
def upload_document(request):
    """Upload new document"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        document_type = request.POST.get('document_type')
        access_level = request.POST.get('access_level')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags', '')
        keywords = request.POST.get('keywords', '')
        expires_at = request.POST.get('expires_at')
        
        # Get uploaded file
        file = request.FILES.get('file')
        
        if not file or not title:
            messages.error(request, 'Please provide a title and select a file.')
            return redirect('core:upload_document')
        
        try:
            # Create document
            document = Document.objects.create(
                company=company,
                title=title,
                description=description,
                document_type=document_type,
                access_level=access_level,
                file=file,
                file_name=file.name,
                file_size=file.size,
                file_type=file.content_type,
                uploaded_by=request.user,
                keywords=keywords,
                expires_at=expires_at or None,
            )
            
            # Set category
            if category_id:
                try:
                    category = DocumentCategory.objects.get(id=category_id, company=company)
                    document.category = category
                except DocumentCategory.DoesNotExist:
                    pass
            
            # Set tags
            if tags:
                document.tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            document.save()
            
            # Log access
            DocumentAccess.objects.create(
                document=document,
                user=request.user,
                access_type='UPLOAD',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            messages.success(request, f'Document "{title}" uploaded successfully!')
            return redirect('core:document_library')
            
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')
    
    # Get categories for dropdown
    categories = DocumentCategory.objects.filter(company=company, is_active=True).order_by('sort_order', 'name')
    
    context = {
        'title': 'Upload Document',
        'company': company,
        'categories': categories,
        'document_type_choices': Document.DOCUMENT_TYPES,
        'access_level_choices': Document.ACCESS_LEVELS,
    }
    
    return render(request, 'core/upload_document.html', context)

@login_required
def document_detail(request, document_id):
    """Document detail view"""
    if not hasattr(request.user, 'company_admin_profile'):
        messages.error(request, 'Access denied. Company admin access required.')
        return redirect('core:home')
    
    company = request.user.company_admin_profile.company
    document = get_object_or_404(Document, id=document_id, company=company)
    
    # Check access permissions
    if not document.can_access(request.user):
        messages.error(request, 'You do not have permission to access this document.')
        return redirect('core:document_library')
    
    # Log view access
    DocumentAccess.objects.create(
        document=document,
        user=request.user,
        access_type='VIEW',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    
    # Update last accessed
    document.last_accessed = timezone.now()
    document.save()
    
    # Get document versions
    versions = DocumentVersion.objects.filter(document=document).order_by('-created_at')
    
    # Get document comments
    comments = DocumentComment.objects.filter(document=document, parent__isnull=True).order_by('created_at')
    
    # Get document shares
    shares = DocumentShare.objects.filter(document=document).order_by('-shared_at')
    
    # Get recent access
    recent_access = DocumentAccess.objects.filter(document=document).order_by('-accessed_at')[:10]
    
    context = {
        'title': f'Document - {document.title}',
        'company': company,
        'document': document,
        'versions': versions,
        'comments': comments,
        'shares': shares,
        'recent_access': recent_access,
    }
    
    return render(request, 'core/document_detail.html', context)


# Dashboard Widget Views
@login_required
def dashboard_notifications(request):
    """Get real-time notifications for dashboard"""
    if not hasattr(request.user, 'system_owner_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get recent system logs (errors and warnings)
    recent_logs = SystemLog.objects.filter(
        level__in=['ERROR', 'WARNING', 'CRITICAL']
    ).order_by('-timestamp')[:10]
    
    # Get recent announcements
    recent_announcements = Announcement.objects.filter(
        is_active=True,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')[:5]
    
    # Get subscription alerts (expiring soon)
    expiring_subscriptions = CompanySubscription.objects.filter(
        end_date__lte=timezone.now() + timedelta(days=7),
        status='ACTIVE'
    ).select_related('company')[:5]
    
    # Get failed payments
    failed_payments = SubscriptionPayment.objects.filter(
        status='FAILED',
        created_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('subscription__company')[:5]
    
    notifications = []
    
    # Add system log notifications
    for log in recent_logs:
        notifications.append({
            'type': 'system_log',
            'level': log.level.lower(),
            'title': f'{log.level} - {log.category}',
            'message': log.message[:100] + '...' if len(log.message) > 100 else log.message,
            'timestamp': log.timestamp.isoformat(),
            'icon': 'fas fa-exclamation-triangle' if log.level == 'WARNING' else 'fas fa-times-circle'
        })
    
    # Add announcement notifications
    for announcement in recent_announcements:
        notifications.append({
            'type': 'announcement',
            'level': 'info',
            'title': announcement.title,
            'message': announcement.content[:100] + '...' if len(announcement.content) > 100 else announcement.content,
            'timestamp': announcement.created_at.isoformat(),
            'icon': 'fas fa-bullhorn'
        })
    
    # Add subscription alerts
    for subscription in expiring_subscriptions:
        days_left = (subscription.end_date - timezone.now()).days
        notifications.append({
            'type': 'subscription_expiring',
            'level': 'warning',
            'title': f'Subscription Expiring - {subscription.company.name}',
            'message': f'Subscription expires in {days_left} days',
            'timestamp': subscription.end_date.isoformat(),
            'icon': 'fas fa-calendar-times'
        })
    
    # Add failed payment alerts
    for payment in failed_payments:
        notifications.append({
            'type': 'payment_failed',
            'level': 'error',
            'title': f'Payment Failed - {payment.subscription.company.name}',
            'message': f'Payment of ${payment.amount} failed',
            'timestamp': payment.created_at.isoformat(),
            'icon': 'fas fa-credit-card'
        })
    
    # Sort by timestamp (newest first)
    notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return JsonResponse({
        'notifications': notifications[:20],  # Limit to 20 most recent
        'count': len(notifications)
    })


@login_required
def dashboard_system_performance(request):
    """Get system performance metrics for dashboard"""
    if not hasattr(request.user, 'system_owner_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Calculate performance metrics
    now = timezone.now()
    
    # Database performance (simulated - in real app, use actual DB metrics)
    total_records = (
        Company.objects.count() +
        Employee.objects.count() +
        User.objects.count() +
        SystemLog.objects.count()
    )
    
    # System load metrics (simulated)
    performance_data = {
        'cpu_usage': min(85, max(15, (total_records % 100) + 20)),  # Simulated CPU usage
        'memory_usage': min(90, max(20, (total_records % 80) + 30)),  # Simulated memory usage
        'disk_usage': min(95, max(10, (total_records % 60) + 25)),  # Simulated disk usage
        'database_size': total_records,
        'active_sessions': User.objects.filter(
            last_login__gte=now - timedelta(hours=1)
        ).count(),
        'response_time': round(0.1 + (total_records % 50) / 1000, 3),  # Simulated response time
        'uptime_hours': 24 * 7,  # Simulated uptime
        'error_rate': SystemLog.objects.filter(
            level='ERROR',
            timestamp__gte=now - timedelta(hours=24)
        ).count()
    }
    
    # Historical data for charts (last 24 hours)
    hourly_data = []
    for i in range(24):
        hour_start = now - timedelta(hours=i)
        hourly_data.append({
            'hour': hour_start.strftime('%H:00'),
            'cpu': min(100, max(0, performance_data['cpu_usage'] + (i % 20) - 10)),
            'memory': min(100, max(0, performance_data['memory_usage'] + (i % 15) - 7)),
            'active_users': User.objects.filter(
                last_login__gte=hour_start - timedelta(hours=1),
                last_login__lt=hour_start
            ).count()
        })
    
    hourly_data.reverse()  # Oldest to newest
    
    return JsonResponse({
        'performance': performance_data,
        'hourly_data': hourly_data
    })


@login_required
def dashboard_subscription_overview(request):
    """Get subscription overview for dashboard"""
    if not hasattr(request.user, 'system_owner_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Subscription statistics
    total_subscriptions = CompanySubscription.objects.count()
    active_subscriptions = CompanySubscription.objects.filter(status='ACTIVE').count()
    trial_subscriptions = CompanySubscription.objects.filter(status='TRIAL').count()
    expired_subscriptions = CompanySubscription.objects.filter(status='EXPIRED').count()
    
    # Revenue calculations
    monthly_revenue = SubscriptionPayment.objects.filter(
        status='COMPLETED',
        payment_date__gte=timezone.now().replace(day=1)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Plan distribution
    plan_distribution = CompanySubscription.objects.filter(
        status__in=['ACTIVE', 'TRIAL']
    ).values('plan__name').annotate(count=Count('id')).order_by('-count')
    
    # Recent payments
    recent_payments = SubscriptionPayment.objects.filter(
        payment_date__gte=timezone.now() - timedelta(days=30)
    ).select_related('subscription__company').order_by('-payment_date')[:10]
    
    # Upcoming renewals
    upcoming_renewals = CompanySubscription.objects.filter(
        end_date__lte=timezone.now() + timedelta(days=30),
        status='ACTIVE'
    ).select_related('company').order_by('end_date')[:10]
    
    subscription_data = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'monthly_revenue': float(monthly_revenue),
        'plan_distribution': list(plan_distribution),
        'recent_payments': [
            {
                'company': payment.subscription.company.name,
                'amount': float(payment.amount),
                'date': payment.payment_date.isoformat(),
                'status': payment.status
            }
            for payment in recent_payments
        ],
        'upcoming_renewals': [
            {
                'company': subscription.company.name,
                'plan': subscription.plan.name,
                'end_date': subscription.end_date.isoformat(),
                'days_left': (subscription.end_date - timezone.now()).days
            }
            for subscription in upcoming_renewals
        ]
    }
    
    return JsonResponse(subscription_data)


@login_required
def dashboard_api_usage(request):
    """Get API usage statistics for dashboard"""
    if not hasattr(request.user, 'system_owner_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # API usage from system logs
    now = timezone.now()
    
    # Get API-related logs from the last 24 hours
    api_logs = SystemLog.objects.filter(
        category='API',
        timestamp__gte=now - timedelta(hours=24)
    )
    
    # Calculate API metrics
    total_requests = api_logs.count()
    successful_requests = api_logs.filter(response_status__lt=400).count()
    failed_requests = api_logs.filter(response_status__gte=400).count()
    
    # Average response time
    avg_response_time = api_logs.aggregate(
        avg_time=Avg('execution_time')
    )['avg_time'] or 0
    
    # Hourly API usage
    hourly_usage = []
    for i in range(24):
        hour_start = now - timedelta(hours=i)
        hour_end = hour_start + timedelta(hours=1)
        
        hour_requests = api_logs.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        
        hourly_usage.append({
            'hour': hour_start.strftime('%H:00'),
            'requests': hour_requests
        })
    
    hourly_usage.reverse()  # Oldest to newest
    
    # Top API endpoints
    top_endpoints = api_logs.values('request_path').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    api_data = {
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'failed_requests': failed_requests,
        'success_rate': round((successful_requests / total_requests * 100) if total_requests > 0 else 0, 2),
        'avg_response_time': round(avg_response_time, 3) if avg_response_time else 0,
        'hourly_usage': hourly_usage,
        'top_endpoints': list(top_endpoints)
    }
    
    return JsonResponse(api_data)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def bulk_company_operations(request):
    """Handle bulk operations on companies"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        operation = data.get('operation')
        company_ids = data.get('company_ids', [])
        params = data.get('params', {})
        
        if not operation or not company_ids:
            return JsonResponse({'error': 'Missing operation or company IDs'}, status=400)
        
        companies = Company.objects.filter(id__in=company_ids)
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for company in companies:
            try:
                if operation == 'activate':
                    company.is_active = True
                    company.save()
                    results['success'] += 1
                    
                elif operation == 'deactivate':
                    company.is_active = False
                    company.save()
                    results['success'] += 1
                    
                elif operation == 'suspend':
                    company.status = 'suspended'
                    company.save()
                    results['success'] += 1
                    
                elif operation == 'change_plan':
                    new_plan = params.get('plan')
                    if new_plan:
                        company.subscription_plan = new_plan
                        company.save()
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f'No plan specified for {company.name}')
                        
                elif operation == 'extend_trial':
                    days = params.get('days', 30)
                    if hasattr(company, 'trial_end_date') and company.trial_end_date:
                        company.trial_end_date += timedelta(days=days)
                    else:
                        company.trial_end_date = timezone.now().date() + timedelta(days=days)
                    company.save()
                    results['success'] += 1
                    
                elif operation == 'apply_discount':
                    discount = params.get('discount', 0)
                    # Apply discount logic here
                    # This would typically involve creating a discount record
                    results['success'] += 1
                    
                elif operation == 'send_notification':
                    subject = params.get('subject', '')
                    message = params.get('message', '')
                    notification_type = params.get('type', 'info')
                    
                    # Create notification for company admin
                    admin_user = company.admin_user if hasattr(company, 'admin_user') else None
                    if admin_user:
                        # Create notification logic here
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f'No admin user for {company.name}')
                        
                elif operation == 'delete':
                    company_name = company.name
                    company.delete()
                    results['success'] += 1
                    
                else:
                    results['failed'] += 1
                    results['errors'].append(f'Unknown operation: {operation}')
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f'Error processing {company.name}: {str(e)}')
        
        return JsonResponse({
            'success': True,
            'results': results,
            'message': f'Operation completed: {results["success"]} successful, {results["failed"]} failed'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to perform bulk operation: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_companies_filtered(request):
    """Export companies with filters applied"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        plan_filter = request.GET.get('plan', '')
        date_filter = request.GET.get('date', '')
        size_filter = request.GET.get('size', '')
        search_filter = request.GET.get('search', '')
        
        # Start with all companies
        companies = Company.objects.all()
        
        # Apply filters
        if status_filter:
            if status_filter == 'active':
                companies = companies.filter(is_active=True)
            elif status_filter == 'inactive':
                companies = companies.filter(is_active=False)
            elif status_filter == 'suspended':
                companies = companies.filter(status='suspended')
            elif status_filter == 'trial':
                companies = companies.filter(status='trial')
        
        if plan_filter:
            companies = companies.filter(subscription_plan__icontains=plan_filter)
        
        if search_filter:
            companies = companies.filter(
                Q(name__icontains=search_filter) |
                Q(domain__icontains=search_filter) |
                Q(admin_email__icontains=search_filter)
            )
        
        if date_filter:
            now = timezone.now()
            if date_filter == 'today':
                companies = companies.filter(created_at__date=now.date())
            elif date_filter == 'week':
                week_ago = now - timedelta(days=7)
                companies = companies.filter(created_at__gte=week_ago)
            elif date_filter == 'month':
                companies = companies.filter(
                    created_at__month=now.month,
                    created_at__year=now.year
                )
            elif date_filter == 'quarter':
                quarter_start = now.replace(month=((now.month-1)//3)*3+1, day=1)
                companies = companies.filter(created_at__gte=quarter_start)
            elif date_filter == 'year':
                companies = companies.filter(created_at__year=now.year)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="companies_filtered.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Company Name', 'Domain', 'Admin Email', 'Status', 
            'Subscription Plan', 'Employees', 'Created Date', 'Last Login'
        ])
        
        for company in companies:
            writer.writerow([
                company.name,
                company.domain,
                company.admin_email,
                'Active' if company.is_active else 'Inactive',
                company.subscription_plan or 'N/A',
                company.employee_count if hasattr(company, 'employee_count') else 0,
                company.created_at.strftime('%Y-%m-%d'),
                company.last_activity.strftime('%Y-%m-%d') if hasattr(company, 'last_activity') and company.last_activity else 'Never'
            ])
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to export companies: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_selected_companies(request):
    """Export specific selected companies"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        company_ids = request.POST.getlist('company_ids')
        
        if not company_ids:
            return JsonResponse({'error': 'No companies selected'}, status=400)
        
        companies = Company.objects.filter(id__in=company_ids)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="selected_companies.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Company Name', 'Domain', 'Admin Email', 'Status', 
            'Subscription Plan', 'Employees', 'Created Date', 'Last Login'
        ])
        
        for company in companies:
            writer.writerow([
                company.name,
                company.domain,
                company.admin_email,
                'Active' if company.is_active else 'Inactive',
                company.subscription_plan or 'N/A',
                company.employee_count if hasattr(company, 'employee_count') else 0,
                company.created_at.strftime('%Y-%m-%d'),
                company.last_activity.strftime('%Y-%m-%d') if hasattr(company, 'last_activity') and company.last_activity else 'Never'
            ])
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to export selected companies: {str(e)}'
        }, status=500)

# Advanced Analytics Views
@login_required
@user_passes_test(lambda u: u.is_superuser)
def analytics_growth_data(request):
    """Get growth analytics data for the specified date range"""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            return JsonResponse({'error': 'Start date and end date are required'}, status=400)
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get daily company registrations
        company_data = []
        user_data = []
        labels = []
        
        current_date = start_date
        while current_date <= end_date:
            # Count companies registered on this date
            companies_count = Company.objects.filter(
                created_at__date=current_date
            ).count()
            
            # Count users registered on this date
            users_count = User.objects.filter(
                date_joined__date=current_date
            ).count()
            
            labels.append(current_date.strftime('%Y-%m-%d'))
            company_data.append(companies_count)
            user_data.append(users_count)
            
            current_date += timedelta(days=1)
        
        # Calculate growth rates
        total_companies = Company.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count()
        
        total_users = User.objects.filter(
            date_joined__date__range=[start_date, end_date]
        ).count()
        
        # Calculate previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        prev_companies = Company.objects.filter(
            created_at__date__range=[prev_start, prev_end]
        ).count()
        
        prev_users = User.objects.filter(
            date_joined__date__range=[prev_start, prev_end]
        ).count()
        
        # Calculate growth percentages
        company_growth = ((total_companies - prev_companies) / max(prev_companies, 1)) * 100
        user_growth = ((total_users - prev_users) / max(prev_users, 1)) * 100
        
        # Calculate churn rate (simplified)
        active_companies = Company.objects.filter(is_active=True).count()
        total_companies_all = Company.objects.count()
        churn_rate = ((total_companies_all - active_companies) / max(total_companies_all, 1)) * 100
        
        response_data = {
            'company_growth': round(company_growth, 1),
            'user_growth': round(user_growth, 1),
            'churn_rate': round(churn_rate, 1),
            'chart_data': {
                'labels': labels,
                'companies': company_data,
                'users': user_data
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def analytics_revenue_data(request):
    """Get revenue analytics data for the specified date range"""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            return JsonResponse({'error': 'Start date and end date are required'}, status=400)
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get daily revenue data (simplified calculation)
        revenue_data = []
        labels = []
        
        current_date = start_date
        while current_date <= end_date:
            # Calculate daily revenue based on active subscriptions
            daily_revenue = 0
            active_companies = Company.objects.filter(
                is_active=True,
                created_at__date__lte=current_date
            )
            
            for company in active_companies:
                # Simplified revenue calculation
                if company.subscription_plan == 'basic':
                    daily_revenue += 29  # $29/month
                elif company.subscription_plan == 'premium':
                    daily_revenue += 99  # $99/month
                elif company.subscription_plan == 'enterprise':
                    daily_revenue += 299  # $299/month
            
            labels.append(current_date.strftime('%Y-%m-%d'))
            revenue_data.append(daily_revenue)
            
            current_date += timedelta(days=1)
        
        # Calculate metrics
        total_revenue = sum(revenue_data)
        active_companies_count = Company.objects.filter(is_active=True).count()
        
        # Calculate ARPU (Average Revenue Per User)
        arpu = total_revenue / max(active_companies_count, 1) if active_companies_count > 0 else 0
        
        # Calculate MRR growth (simplified)
        current_mrr = revenue_data[-1] * 30 if revenue_data else 0
        previous_mrr = revenue_data[0] * 30 if revenue_data else 0
        mrr_growth = current_mrr - previous_mrr
        
        # Calculate LTV (simplified)
        ltv = arpu * 12  # Assuming 12 month average lifetime
        
        response_data = {
            'mrr_growth': round(mrr_growth, 0),
            'arpu': round(arpu, 0),
            'ltv': round(ltv, 0),
            'chart_data': {
                'labels': labels,
                'revenue': revenue_data
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def analytics_predictive_data(request):
    """Get predictive analytics data"""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            return JsonResponse({'error': 'Start date and end date are required'}, status=400)
        
        # Get historical data for the last 6 months
        historical_data = []
        predicted_data = []
        labels = []
        
        # Generate historical data (last 6 months)
        for i in range(6):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            companies_count = Company.objects.filter(
                created_at__date__range=[month_start.date(), month_end.date()]
            ).count()
            
            labels.insert(0, month_start.strftime('%B %Y'))
            historical_data.insert(0, companies_count)
        
        # Simple prediction based on trend
        if len(historical_data) >= 2:
            trend = (historical_data[-1] - historical_data[-2])
            predicted_growth = historical_data[-1] + trend
            predicted_revenue = predicted_growth * 150  # Assuming $150 average per company
        else:
            predicted_growth = 0
            predicted_revenue = 0
        
        # Add predicted data points
        predicted_data = [None] * 4 + [historical_data[-1] + trend, historical_data[-1] + trend * 2]
        
        # Calculate risk score based on growth trend
        if len(historical_data) >= 3:
            recent_trend = sum(historical_data[-3:]) / 3
            overall_trend = sum(historical_data) / len(historical_data)
            risk_ratio = recent_trend / max(overall_trend, 1)
            
            if risk_ratio > 1.2:
                risk_score = 'Low'
            elif risk_ratio > 0.8:
                risk_score = 'Medium'
            else:
                risk_score = 'High'
        else:
            risk_score = 'Medium'
        
        response_data = {
            'predicted_growth': round(abs(trend), 1) if trend else 0,
            'predicted_revenue': round(predicted_revenue, 0),
            'risk_score': risk_score,
            'chart_data': {
                'labels': labels,
                'historical': historical_data,
                'predicted': predicted_data
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def analytics_comparative_data(request):
    """Get comparative analytics data"""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            return JsonResponse({'error': 'Start date and end date are required'}, status=400)
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Calculate period length
        period_length = (end_date - start_date).days
        
        # Current period data
        current_companies = Company.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count()
        
        current_users = User.objects.filter(
            date_joined__date__range=[start_date, end_date]
        ).count()
        
        # Calculate current revenue
        current_revenue = 0
        active_companies = Company.objects.filter(
            is_active=True,
            created_at__date__range=[start_date, end_date]
        )
        
        for company in active_companies:
            if company.subscription_plan == 'basic':
                current_revenue += 29 * period_length
            elif company.subscription_plan == 'premium':
                current_revenue += 99 * period_length
            elif company.subscription_plan == 'enterprise':
                current_revenue += 299 * period_length
        
        # Previous period data
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        previous_companies = Company.objects.filter(
            created_at__date__range=[prev_start, prev_end]
        ).count()
        
        previous_users = User.objects.filter(
            date_joined__date__range=[prev_start, prev_end]
        ).count()
        
        # Calculate previous revenue
        previous_revenue = 0
        prev_active_companies = Company.objects.filter(
            is_active=True,
            created_at__date__range=[prev_start, prev_end]
        )
        
        for company in prev_active_companies:
            if company.subscription_plan == 'basic':
                previous_revenue += 29 * period_length
            elif company.subscription_plan == 'premium':
                previous_revenue += 99 * period_length
            elif company.subscription_plan == 'enterprise':
                previous_revenue += 299 * period_length
        
        # Calculate percentage changes
        companies_change = ((current_companies - previous_companies) / max(previous_companies, 1)) * 100
        users_change = ((current_users - previous_users) / max(previous_users, 1)) * 100
        revenue_change = ((current_revenue - previous_revenue) / max(previous_revenue, 1)) * 100
        
        response_data = {
            'current': {
                'companies': current_companies,
                'users': current_users,
                'revenue': round(current_revenue, 0)
            },
            'previous': {
                'companies': previous_companies,
                'users': previous_users,
                'revenue': round(previous_revenue, 0)
            },
            'changes': {
                'companies': round(companies_change, 1),
                'users': round(users_change, 1),
                'revenue': round(revenue_change, 1)
            },
            'chart_data': {
                'labels': ['Companies', 'Users', 'Revenue'],
                'values': [current_companies, current_users, current_revenue / 1000]  # Revenue in thousands
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)# Chat System Views
@login_required
def chat_dashboard(request):
    """Main chat dashboard for employees"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    # Get all chat rooms for the employee
    chat_rooms = ChatRoom.objects.filter(
        Q(participants=employee) | Q(created_by=employee),
        company=company,
        is_active=True
    ).distinct().order_by('-updated_at')
    
    # Get recent messages for preview
    for room in chat_rooms:
        room.last_message = room.get_last_message()
        room.unread_count = room.get_unread_count(employee)
    
    # Get online employees
    online_employees = Employee.objects.filter(
        company=company
    ).exclude(id=employee.id)[:10]
    
    context = {
        'title': 'Chat Dashboard',
        'company': company,
        'employee': employee,
        'chat_rooms': chat_rooms,
        'online_employees': online_employees,
    }
    return render(request, 'core/chat_dashboard.html', context)

@login_required
def chat_room(request, room_id):
    """Individual chat room view"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    try:
        room = ChatRoom.objects.get(
            id=room_id,
            company=company,
            participants=employee
        )
    except ChatRoom.DoesNotExist:
        messages.error(request, 'Chat room not found.')
        return redirect('core:chat_dashboard')
    
    # Get messages for this room
    messages = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).order_by('created_at')
    
    # Get participants
    participants = room.participants.all()
    
    # Mark messages as read (update last_seen)
    ChatParticipant.objects.filter(
        room=room,
        employee=employee
    ).update(last_seen=timezone.now())
    
    context = {
        'title': f'Chat - {room.name}',
        'company': company,
        'employee': employee,
        'room': room,
        'messages': messages,
        'participants': participants,
    }
    return render(request, 'core/chat_room.html', context)

@login_required
def create_chat_room(request):
    """Create a new chat room"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_type = request.POST.get('room_type', 'GROUP')
        description = request.POST.get('description', '')
        participant_ids = request.POST.getlist('participants')
        
        if not room_name:
            messages.error(request, 'Room name is required.')
            return redirect('core:create_chat_room')
        
        # Create the room
        room = ChatRoom.objects.create(
            name=room_name,
            room_type=room_type,
            company=company,
            created_by=employee,
            description=description
        )
        
        # Add participants
        room.participants.add(employee)  # Add creator
        if participant_ids:
            participants = Employee.objects.filter(
                id__in=participant_ids,
                company=company
            )
            room.participants.add(*participants)
        
        # Create participant records
        for participant in room.participants.all():
            ChatParticipant.objects.get_or_create(
                room=room,
                employee=participant
            )
        
        messages.success(request, f'Chat room "{room_name}" created successfully!')
        return redirect('core:chat_room', room_id=room.id)
    
    # Get available employees for the company
    available_employees = Employee.objects.filter(company=company).exclude(id=employee.id)
    
    context = {
        'title': 'Create Chat Room',
        'company': company,
        'employee': employee,
        'available_employees': available_employees,
        'room_types': ChatRoom.ROOM_TYPES,
    }
    return render(request, 'core/create_chat_room.html', context)

@login_required
def send_message(request, room_id):
    """API endpoint to send a message"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    company = employee.company
    
    try:
        room = ChatRoom.objects.get(
            id=room_id,
            company=company,
            participants=employee
        )
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Room not found'})
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        message_type = request.POST.get('message_type', 'TEXT')
        reply_to_id = request.POST.get('reply_to')
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Message content is required'})
        
        # Create the message
        message = ChatMessage.objects.create(
            room=room,
            sender=employee,
            message_type=message_type,
            content=content
        )
        
        # Handle reply
        if reply_to_id:
            try:
                reply_to = ChatMessage.objects.get(id=reply_to_id, room=room)
                message.reply_to = reply_to
                message.save()
            except ChatMessage.DoesNotExist:
                pass
        
        # Update room's updated_at
        room.updated_at = timezone.now()
        room.save()
        
        # Create notifications for offline participants
        for participant in room.participants.exclude(id=employee.id):
            ChatNotification.objects.create(
                recipient=participant,
                sender=employee,
                room=room,
                message=message,
                notification_type='NEW_MESSAGE',
                title=f'New message in {room.name}',
                content=f'{employee.first_name}: {content[:100]}...'
            )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'sender_name': employee.first_name,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_messages(request, room_id):
    """API endpoint to get messages for a room"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    company = employee.company
    
    try:
        room = ChatRoom.objects.get(
            id=room_id,
            company=company,
            participants=employee
        )
    except ChatRoom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Room not found'})
    
    # Get messages
    messages = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).order_by('created_at')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender_name': msg.sender.first_name,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'message_type': msg.message_type,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_edited': msg.is_edited,
            'reply_to': msg.reply_to.id if msg.reply_to else None,
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_data
    })

@login_required
def edit_message(request, message_id):
    """API endpoint to edit a message"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    
    try:
        message = ChatMessage.objects.get(
            id=message_id,
            sender=employee,
            is_deleted=False
        )
    except ChatMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})
    
    if request.method == 'POST':
        new_content = request.POST.get('content', '').strip()
        
        if not new_content:
            return JsonResponse({'success': False, 'error': 'Message content is required'})
        
        message.content = new_content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def delete_message(request, message_id):
    """API endpoint to delete a message"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    
    try:
        message = ChatMessage.objects.get(
            id=message_id,
            sender=employee,
            is_deleted=False
        )
    except ChatMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})
    
    if request.method == 'POST':
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def chat_notifications(request):
    """Get chat notifications for the current employee"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    
    notifications = ChatNotification.objects.filter(
        recipient=employee,
        is_read=False
    ).order_by('-created_at')[:20]
    
    notifications_data = []
    for notif in notifications:
        notifications_data.append({
            'id': notif.id,
            'title': notif.title,
            'content': notif.content,
            'room_name': notif.room.name,
            'sender_name': notif.sender.first_name if notif.sender else 'System',
            'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'notification_type': notif.notification_type,
        })
    
    return JsonResponse({
        'success': True,
        'notifications': notifications_data
    })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    
    try:
        notification = ChatNotification.objects.get(
            id=notification_id,
            recipient=employee
        )
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True})
    except ChatNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

# Employee Leave Request Details View
@login_required
def employee_leave_details(request, request_id):
    """Display detailed information about a specific leave request for employees"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    try:
        leave_request = LeaveRequest.objects.get(
            id=request_id,
            employee=employee,
            employee__company=company
        )
    except LeaveRequest.DoesNotExist:
        messages.error(request, 'Leave request not found.')
        return redirect('core:employee_leave')
    
    # Get related leave requests for context
    related_requests = LeaveRequest.objects.filter(
        employee=employee
    ).exclude(id=request_id).order_by('-created_at')[:5]
    
    # Calculate leave balance
    def calculate_leave_balance():
        annual_allocation = 20
        sick_allocation = 10
        personal_allocation = 5
        
        approved_annual = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='VACATION',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        approved_sick = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='SICK_LEAVE',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        approved_personal = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='PERSONAL',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        return {
            'annual': float(annual_allocation - approved_annual),
            'sick': float(sick_allocation - approved_sick),
            'personal': float(personal_allocation - approved_personal),
            'annual_used': float(approved_annual),
            'sick_used': float(approved_sick),
            'personal_used': float(approved_personal),
        }
    
    leave_balance = calculate_leave_balance()
    
    context = {
        'title': f'Leave Request Details - {leave_request.leave_type}',
        'company': company,
        'employee': employee,
        'leave_request': leave_request,
        'related_requests': related_requests,
        'leave_balance': leave_balance,
    }
    return render(request, 'core/employee_leave_details.html', context)

# Employee Edit Leave Request View
@login_required
def employee_edit_leave_request(request, request_id):
    """Edit a specific leave request for employees"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('core:home')
    
    employee = request.user.employee_profile
    company = employee.company
    
    try:
        leave_request = LeaveRequest.objects.get(
            id=request_id,
            employee=employee,
            employee__company=company
        )
    except LeaveRequest.DoesNotExist:
        messages.error(request, 'Leave request not found.')
        return redirect('core:employee_leave')
    
    # Only allow editing of pending requests
    if leave_request.status != 'PENDING':
        messages.error(request, 'Only pending leave requests can be edited.')
        return redirect('core:employee_leave_details', request_id=request_id)
    
    if request.method == 'POST':
        # Handle form submission
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        emergency_contact = request.POST.get('emergency_contact')
        emergency_phone = request.POST.get('emergency_phone')
        
        # Validate dates
        if start_date and end_date:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                messages.error(request, 'Start date cannot be after end date.')
                return redirect('core:employee_edit_leave_request', request_id=request_id)
            
            if start < timezone.now().date():
                messages.error(request, 'Start date cannot be in the past.')
                return redirect('core:employee_edit_leave_request', request_id=request_id)
        
        # Update the leave request
        leave_request.leave_type = leave_type
        leave_request.start_date = start
        leave_request.end_date = end
        leave_request.reason = reason
        leave_request.emergency_contact = emergency_contact
        leave_request.emergency_phone = emergency_phone
        
        # Convert string dates to date objects and set them
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            leave_request.start_date = start
            leave_request.end_date = end
            # The model's save method will automatically calculate total_days
        
        leave_request.save()
        
        messages.success(request, 'Leave request updated successfully!')
        return redirect('core:employee_leave_details', request_id=request_id)
    
    # Calculate leave balance
    def calculate_leave_balance():
        annual_allocation = 20
        sick_allocation = 10
        personal_allocation = 5
        
        approved_annual = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='VACATION',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        approved_sick = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='SICK_LEAVE',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        approved_personal = LeaveRequest.objects.filter(
            employee=employee,
            leave_type='PERSONAL',
            status='APPROVED'
        ).aggregate(total=Sum('total_days'))['total'] or 0
        
        return {
            'annual': float(annual_allocation - approved_annual),
            'sick': float(sick_allocation - approved_sick),
            'personal': float(personal_allocation - approved_personal),
            'annual_used': float(approved_annual),
            'sick_used': float(approved_sick),
            'personal_used': float(approved_personal),
        }
    
    leave_balance = calculate_leave_balance()
    
    context = {
        'title': f'Edit Leave Request - {leave_request.leave_type}',
        'company': company,
        'employee': employee,
        'leave_request': leave_request,
        'leave_types': LeaveRequest.LEAVE_TYPES,
        'leave_balance': leave_balance,
    }
    return render(request, 'core/employee_edit_leave_request.html', context)

# Leave Request API Endpoints
@login_required
def cancel_leave_request_api(request, request_id):
    """API endpoint to cancel a leave request"""
    if not hasattr(request.user, 'employee_profile'):
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    employee = request.user.employee_profile
    company = employee.company
    
    try:
        leave_request = LeaveRequest.objects.get(
            id=request_id,
            employee=employee,
            employee__company=company
        )
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Leave request not found'})
    
    if leave_request.status != 'PENDING':
        return JsonResponse({'success': False, 'error': 'Only pending leave requests can be cancelled'})
    
    if request.method == 'POST':
        leave_request.status = 'CANCELLED'
        leave_request.save()
        
        return JsonResponse({'success': True, 'message': 'Leave request cancelled successfully'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
