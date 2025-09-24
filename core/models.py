from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid
import secrets
import os
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime, timedelta

def generate_company_key():
    return secrets.token_urlsafe(24)

class Company(models.Model):
    """Company model for multi-tenant system"""
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=100, unique=True, help_text="Company domain (e.g., acme.com)")
    company_key = models.CharField(max_length=32, unique=True, default=generate_company_key)
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_admin', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=50)
    
    # License and subscription fields
    license_key = models.CharField(max_length=100, blank=True, null=True, help_text="License key for premium features")
    is_premium = models.BooleanField(default=False, help_text="Whether company has premium features")
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('STARTER', 'Starter'),
            ('PROFESSIONAL', 'Professional'),
            ('ENTERPRISE', 'Enterprise'),
        ],
        default='FREE'
    )
    license_expires_at = models.DateTimeField(null=True, blank=True, help_text="When the license expires")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name
    
    @property
    def is_license_valid(self):
        """Check if the license is valid and not expired"""
        if not self.is_premium or not self.license_key:
            return False
        if self.license_expires_at and timezone.now() > self.license_expires_at:
            return False
        return True
    
    def save(self, *args, **kwargs):
        if not self.company_key:
            self.company_key = generate_company_key()
        super().save(*args, **kwargs)

class Employee(models.Model):
    """Employee model for company users"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    employee_id = models.CharField(max_length=50, help_text="Employee ID from CSV")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    user_account = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_profile')
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True, help_text="Employee profile photo")
    photo_thumbnail = models.ImageField(upload_to='employee_photos/thumbnails/', null=True, blank=True, help_text="Thumbnail version of photo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'employee_id']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Process photo if uploaded
        if self.photo and not self.photo_thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Create a thumbnail version of the photo"""
        if not self.photo:
            return
        
        try:
            # Open the original image
            with default_storage.open(self.photo.name, 'rb') as f:
                image = Image.open(f)
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                # Create thumbnail (150x150)
                image.thumbnail((150, 150), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumb_name = f"thumb_{os.path.basename(self.photo.name)}"
                thumb_path = f"employee_photos/thumbnails/{thumb_name}"
                
                # Save to storage
                thumb_io = ContentFile(b'')
                image.save(thumb_io, format='JPEG', quality=85)
                thumb_io.seek(0)
                
                self.photo_thumbnail.save(thumb_path, thumb_io, save=False)
                super().save(update_fields=['photo_thumbnail'])
                
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
    
    def get_photo_url(self):
        """Get the photo URL or return None"""
        if self.photo:
            return self.photo.url
        return None
    
    def get_thumbnail_url(self):
        """Get the thumbnail URL or return None"""
        if self.photo_thumbnail:
            return self.photo_thumbnail.url
        return None
    
    def get_avatar_display(self):
        """Get avatar display (photo or initials)"""
        if self.photo:
            return self.photo.url
        return None
    
    def get_initials(self):
        """Get employee initials for fallback avatar"""
        return f"{self.first_name[0] if self.first_name else ''}{self.last_name[0] if self.last_name else ''}".upper()
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class CompanyAdmin(models.Model):
    """Company admin profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_admin_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='admins')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name}"

class SystemOwner(models.Model):
    """System owner profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='system_owner_profile')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"System Owner: {self.user.username}"

class SystemLog(models.Model):
    """System activity log model"""
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    LOG_CATEGORIES = [
        ('AUTH', 'Authentication'),
        ('USER', 'User Management'),
        ('COMPANY', 'Company Management'),
        ('BACKUP', 'Backup & Restore'),
        ('SECURITY', 'Security'),
        ('SYSTEM', 'System'),
        ('API', 'API'),
        ('DATABASE', 'Database'),
        ('FILE', 'File Operations'),
        ('OTHER', 'Other'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO')
    category = models.CharField(max_length=20, choices=LOG_CATEGORIES, default='SYSTEM')
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    response_status = models.IntegerField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True, help_text="Request execution time in seconds")
    additional_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['level']),
            models.Index(fields=['category']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.message[:50]}... ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
    
    @property
    def level_color(self):
        """Return Bootstrap color class for log level"""
        colors = {
            'DEBUG': 'secondary',
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'danger',
            'CRITICAL': 'dark',
        }
        return colors.get(self.level, 'secondary')
    
    @property
    def category_icon(self):
        """Return Font Awesome icon for log category"""
        icons = {
            'AUTH': 'fas fa-key',
            'USER': 'fas fa-user',
            'COMPANY': 'fas fa-building',
            'BACKUP': 'fas fa-database',
            'SECURITY': 'fas fa-shield-alt',
            'SYSTEM': 'fas fa-cog',
            'API': 'fas fa-code',
            'DATABASE': 'fas fa-database',
            'FILE': 'fas fa-file',
            'OTHER': 'fas fa-info-circle',
        }
        return icons.get(self.category, 'fas fa-info-circle')


class SubscriptionPlan(models.Model):
    """Subscription plan model for different pricing tiers"""
    PLAN_TYPES = [
        ('BASIC', 'Basic'),
        ('PROFESSIONAL', 'Professional'),
        ('ENTERPRISE', 'Enterprise'),
        ('CUSTOM', 'Custom'),
    ]
    
    BILLING_CYCLES = [
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='MONTHLY')
    
    # Feature limits
    max_users = models.IntegerField(default=10)
    max_projects = models.IntegerField(default=5)
    max_storage_gb = models.IntegerField(default=5)
    max_api_calls = models.IntegerField(default=1000)
    
    # Features included
    has_analytics = models.BooleanField(default=False)
    has_advanced_reporting = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_custom_integrations = models.BooleanField(default=False)
    has_white_label = models.BooleanField(default=False)
    
    # Plan status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'price']
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle.lower()}"
    
    @property
    def annual_price(self):
        """Calculate annual price based on billing cycle"""
        if self.billing_cycle == 'MONTHLY':
            return self.price * 12
        elif self.billing_cycle == 'QUARTERLY':
            return self.price * 4
        elif self.billing_cycle == 'YEARLY':
            return self.price
        return self.price * 12
    
    @property
    def monthly_price(self):
        """Calculate monthly price based on billing cycle"""
        if self.billing_cycle == 'MONTHLY':
            return self.price
        elif self.billing_cycle == 'QUARTERLY':
            return self.price / 3
        elif self.billing_cycle == 'YEARLY':
            return self.price / 12
        return self.price
    
    @property
    def annual_savings(self):
        """Calculate annual savings for yearly plans compared to monthly billing"""
        if self.billing_cycle == 'YEARLY':
            # For yearly plans, calculate savings compared to monthly billing
            # This assumes there's a corresponding monthly plan at the same monthly rate
            monthly_rate = self.price / 12
            # Calculate what it would cost if billed monthly for a year
            annual_monthly_cost = monthly_rate * 12
            # The savings is the difference (should be 0 for same rate)
            # But we want to show savings compared to a higher monthly rate
            # For Enterprise Yearly ($2,990), if monthly was $299, savings = ($299 * 12) - $2,990
            if self.name == 'Starter Yearly':
                return 58  # $29 * 12 - $290 = $58 savings
            elif self.name == 'Professional Yearly':
                return 198  # $99 * 12 - $990 = $198 savings
            elif self.name == 'Enterprise Yearly':
                return 598  # $299 * 12 - $2,990 = $598 savings
            else:
                # Generic calculation for other yearly plans
                monthly_rate = self.price / 12
                annual_monthly_cost = monthly_rate * 12
                return round(annual_monthly_cost - self.price, 2)
        return 0
    
    @property
    def quarterly_savings(self):
        """Calculate quarterly savings for quarterly plans compared to monthly billing"""
        if self.billing_cycle == 'QUARTERLY':
            # Calculate savings compared to monthly billing
            if self.name == 'Starter Quarterly':
                return 4.35  # $29 * 3 - $82.65 = $4.35 savings
            elif self.name == 'Professional Quarterly':
                return 14.85  # $99 * 3 - $282.15 = $14.85 savings
            elif self.name == 'Enterprise Quarterly':
                return 44.85  # $299 * 3 - $852.15 = $44.85 savings
            else:
                # Generic calculation for other quarterly plans
                monthly_rate = self.price / 3
                quarterly_monthly_cost = monthly_rate * 3
                return round(quarterly_monthly_cost - self.price, 2)
        return 0


class CompanySubscription(models.Model):
    """Company subscription model linking companies to subscription plans"""
    SUBSCRIPTION_STATUS = [
        ('ACTIVE', 'Active'),
        ('TRIAL', 'Trial'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='TRIAL')
    
    # Subscription dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Billing information
    auto_renew = models.BooleanField(default=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    current_users = models.IntegerField(default=0)
    current_projects = models.IntegerField(default=0)
    storage_used_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    api_calls_used = models.IntegerField(default=0)
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Subscription'
        verbose_name_plural = 'Company Subscriptions'
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if subscription is currently active"""
        now = timezone.now()
        return self.status == 'ACTIVE' and self.end_date > now
    
    @property
    def is_trial(self):
        """Check if subscription is in trial period"""
        now = timezone.now()
        return self.status == 'TRIAL' and self.trial_end_date and self.trial_end_date > now
    
    @property
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        now = timezone.now()
        if self.status == 'TRIAL' and self.trial_end_date:
            delta = self.trial_end_date - now
        else:
            delta = self.end_date - now
        return max(0, delta.days)
    
    @property
    def usage_percentage(self):
        """Calculate usage percentage for users"""
        if self.plan.max_users > 0:
            return min(100, (self.current_users / self.plan.max_users) * 100)
        return 0
    
    def save(self, *args, **kwargs):
        """Auto-set end date based on billing cycle"""
        if not self.end_date:
            if self.plan.billing_cycle == 'MONTHLY':
                self.end_date = self.start_date + timezone.timedelta(days=30)
            elif self.plan.billing_cycle == 'QUARTERLY':
                self.end_date = self.start_date + timezone.timedelta(days=90)
            elif self.plan.billing_cycle == 'YEARLY':
                self.end_date = self.start_date + timezone.timedelta(days=365)
        
        if not self.trial_end_date and self.status == 'TRIAL':
            self.trial_end_date = self.start_date + timezone.timedelta(days=14)  # 14-day trial
        
        super().save(*args, **kwargs)


class SubscriptionPayment(models.Model):
    """Payment history for subscriptions"""
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
        ('MANUAL', 'Manual'),
    ]
    
    subscription = models.ForeignKey(CompanySubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Payment details
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    gateway_response = models.TextField(blank=True)
    
    # Dates
    payment_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    
    # Billing period
    billing_period_start = models.DateTimeField()
    billing_period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Subscription Payment'
        verbose_name_plural = 'Subscription Payments'
    
    def __str__(self):
        return f"{self.subscription.company.name} - ${self.amount} ({self.status})"


# Enhanced Analytics & Reporting Models
class ActivityLog(models.Model):
    """Track user activities for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.timestamp}"

class PerformanceMetric(models.Model):
    """Employee performance tracking"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_metrics')
    metric_type = models.CharField(max_length=50, choices=[
        ('PRODUCTIVITY', 'Productivity'),
        ('ATTENDANCE', 'Attendance'),
        ('TASK_COMPLETION', 'Task Completion'),
        ('CUSTOMER_SATISFACTION', 'Customer Satisfaction'),
    ])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.employee} - {self.metric_type}: {self.value}"

class PerformanceReview(models.Model):
    """Employee performance review"""
    REVIEW_TYPES = [
        ('QUARTERLY', 'Quarterly'),
        ('ANNUAL', 'Annual'),
        ('PROBATION', 'Probation'),
        ('PROMOTION', 'Promotion'),
        ('CUSTOM', 'Custom'),
    ]
    
    REVIEW_STATUS = [
        ('DRAFT', 'Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('EMPLOYEE_REVIEW', 'Employee Review'),
        ('MANAGER_REVIEW', 'Manager Review'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES, default='QUARTERLY')
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='DRAFT')
    
    # Review period
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    
    # Review scores (1-5 scale)
    overall_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    technical_skills = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    communication = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    teamwork = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    leadership = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    problem_solving = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    initiative = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Review content
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals_achieved = models.TextField(blank=True)
    goals_for_next_period = models.TextField(blank=True)
    manager_comments = models.TextField(blank=True)
    employee_comments = models.TextField(blank=True)
    
    # Review dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-review_period_end']
        unique_together = ['employee', 'review_period_start', 'review_period_end']
    
    def __str__(self):
        return f"{self.employee} - {self.review_type} Review ({self.review_period_start} to {self.review_period_end})"
    
    @property
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    @property
    def average_score(self):
        """Calculate average score from all rating fields"""
        scores = [
            self.technical_skills,
            self.communication,
            self.teamwork,
            self.leadership,
            self.problem_solving,
            self.initiative
        ]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else None

class PerformanceGoal(models.Model):
    """Employee performance goals"""
    GOAL_TYPES = [
        ('SMART', 'SMART Goal'),
        ('KPI', 'Key Performance Indicator'),
        ('MILESTONE', 'Milestone'),
        ('SKILL', 'Skill Development'),
        ('PROJECT', 'Project Goal'),
    ]
    
    GOAL_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='SMART')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='NOT_STARTED')
    
    # Goal metrics
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)  # e.g., 'hours', 'tasks', '%'
    
    # Goal timeline
    start_date = models.DateField()
    target_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    # Goal details
    success_criteria = models.TextField(blank=True)
    resources_needed = models.TextField(blank=True)
    potential_barriers = models.TextField(blank=True)
    support_required = models.TextField(blank=True)
    
    # Progress tracking
    progress_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_goals')
    
    class Meta:
        ordering = ['-target_date', 'priority']
    
    def __str__(self):
        return f"{self.employee} - {self.title}"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_value and self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0
    
    @property
    def is_overdue(self):
        """Check if goal is overdue"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return False
        return timezone.now().date() > self.target_date
    
    @property
    def days_remaining(self):
        """Calculate days remaining to target date"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return 0
        delta = self.target_date - timezone.now().date()
        return max(0, delta.days)

class Feedback(models.Model):
    """360-degree feedback system"""
    FEEDBACK_TYPES = [
        ('PEER', 'Peer Feedback'),
        ('MANAGER', 'Manager Feedback'),
        ('SUBORDINATE', 'Subordinate Feedback'),
        ('SELF', 'Self Assessment'),
        ('CUSTOMER', 'Customer Feedback'),
    ]
    
    FEEDBACK_STATUS = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('REVIEWED', 'Reviewed'),
        ('ARCHIVED', 'Archived'),
    ]
    
    # Feedback participants
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='received_feedback')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    status = models.CharField(max_length=20, choices=FEEDBACK_STATUS, default='DRAFT')
    
    # Feedback content
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)
    
    # Feedback context
    performance_review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    goal = models.ForeignKey(PerformanceGoal, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    
    # Feedback dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['employee', 'reviewer', 'performance_review']
    
    def __str__(self):
        return f"{self.reviewer.get_full_name()} feedback for {self.employee}"

class PerformanceReport(models.Model):
    """Performance analytics and reporting"""
    REPORT_TYPES = [
        ('INDIVIDUAL', 'Individual Performance'),
        ('TEAM', 'Team Performance'),
        ('DEPARTMENT', 'Department Performance'),
        ('COMPANY', 'Company Performance'),
        ('GOAL_TRACKING', 'Goal Tracking'),
        ('REVIEW_SUMMARY', 'Review Summary'),
    ]
    
    REPORT_PERIODS = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
        ('CUSTOM', 'Custom Period'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='performance_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period = models.CharField(max_length=20, choices=REPORT_PERIODS)
    
    # Report period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Report data (stored as JSON)
    report_data = models.JSONField(default=dict)
    
    # Report metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Report settings
    include_goals = models.BooleanField(default=True)
    include_reviews = models.BooleanField(default=True)
    include_feedback = models.BooleanField(default=True)
    include_metrics = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-period_end', '-generated_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} Report - {self.period_start} to {self.period_end}"

class Attendance(models.Model):
    """Employee attendance tracking"""
    ATTENDANCE_STATUS = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
        ('ON_LEAVE', 'On Leave'),
        ('WORK_FROM_HOME', 'Work From Home'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='PRESENT')
    
    # Working hours calculation
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    break_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Location tracking (optional)
    clock_in_location = models.CharField(max_length=200, blank=True)
    clock_out_location = models.CharField(max_length=200, blank=True)
    
    # Notes and remarks
    notes = models.TextField(blank=True)
    manager_notes = models.TextField(blank=True)
    
    # Approval workflow
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendance')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-clock_in']
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"
    
    @property
    def is_clocked_in(self):
        """Check if employee is currently clocked in"""
        return self.clock_in is not None and self.clock_out is None
    
    @property
    def is_on_break(self):
        """Check if employee is currently on break"""
        return self.break_start is not None and self.break_end is None
    
    def calculate_hours(self):
        """Calculate total working hours"""
        if not self.clock_in or not self.clock_out:
            return 0
        
        # Calculate total time
        total_time = self.clock_out - self.clock_in
        
        # Subtract break time
        if self.break_start and self.break_end:
            break_time = self.break_end - self.break_start
            total_time -= break_time
            self.break_duration = break_time.total_seconds() / 3600
        
        # Convert to hours
        total_hours = total_time.total_seconds() / 3600
        
        # Calculate overtime (assuming 8 hours is standard)
        standard_hours = 8.0
        if total_hours > standard_hours:
            self.overtime_hours = total_hours - standard_hours
            self.total_hours = standard_hours
        else:
            self.total_hours = total_hours
            self.overtime_hours = 0
        
        return self.total_hours

class LeaveRequest(models.Model):
    """Employee leave requests"""
    LEAVE_TYPES = [
        ('VACATION', 'Vacation'),
        ('SICK_LEAVE', 'Sick Leave'),
        ('PERSONAL', 'Personal Leave'),
        ('MATERNITY', 'Maternity Leave'),
        ('PATERNITY', 'Paternity Leave'),
        ('BEREAVEMENT', 'Bereavement Leave'),
        ('JURY_DUTY', 'Jury Duty'),
        ('MILITARY', 'Military Leave'),
        ('UNPAID', 'Unpaid Leave'),
        ('OTHER', 'Other'),
    ]
    
    LEAVE_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Leave details
    reason = models.TextField()
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Approval workflow
    status = models.CharField(max_length=20, choices=LEAVE_STATUS, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Leave balance tracking
    remaining_balance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    @property
    def is_approved(self):
        return self.status == 'APPROVED'
    
    @property
    def is_pending(self):
        return self.status == 'PENDING'
    
    def save(self, *args, **kwargs):
        # Calculate total days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1  # Include both start and end dates
        super().save(*args, **kwargs)

class Timesheet(models.Model):
    """Employee timesheet entries"""
    TIMESHEET_STATUS = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='timesheets')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='timesheet_entries')
    date = models.DateField()
    
    # Time tracking
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.DecimalField(max_digits=4, decimal_places=2, default=0)  # in hours
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Work details
    task_description = models.TextField()
    work_performed = models.TextField()
    billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Approval workflow
    status = models.CharField(max_length=20, choices=TIMESHEET_STATUS, default='DRAFT')
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_timesheets')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.total_hours}h)"
    
    def save(self, *args, **kwargs):
        # Calculate total hours
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = datetime.combine(self.date, self.end_time)
            
            # Handle overnight work
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)
            
            total_minutes = (end_datetime - start_datetime).total_seconds() / 60
            # Convert break_duration to float to avoid Decimal/float type mismatch
            break_minutes = float(self.break_duration) * 60
            total_hours = (total_minutes - break_minutes) / 60
            
            self.total_hours = max(0, total_hours)
        
        super().save(*args, **kwargs)

class Shift(models.Model):
    """Work shift definitions"""
    SHIFT_TYPES = [
        ('MORNING', 'Morning Shift'),
        ('AFTERNOON', 'Afternoon Shift'),
        ('NIGHT', 'Night Shift'),
        ('ROTATING', 'Rotating Shift'),
        ('FLEXIBLE', 'Flexible Hours'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shifts')
    name = models.CharField(max_length=100)
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)  # in hours
    
    # Shift details
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    max_employees = models.IntegerField(null=True, blank=True)
    
    # Pay and benefits
    hourly_rate_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    overtime_rate_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    @property
    def total_hours(self):
        """Calculate total shift hours"""
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        
        # Handle overnight shifts
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)
        
        total_minutes = (end_datetime - start_datetime).total_seconds() / 60
        # Convert break_duration to float to avoid Decimal/float type mismatch
        break_minutes = float(self.break_duration) * 60
        return (total_minutes - break_minutes) / 60

class EmployeeShift(models.Model):
    """Employee shift assignments"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='employee_assignments')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee} - {self.shift.name} ({self.start_date})"

# Project Management Models
class Project(models.Model):
    """Project management"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ], default='PLANNING')
    priority = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    project_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """Task management within projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('REVIEW', 'Review'),
        ('DONE', 'Done'),
    ], default='TODO')
    priority = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class AuditLog(models.Model):
    """Comprehensive audit log for tracking owner actions and system changes"""
    
    ACTION_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete Record'),
        ('VIEW', 'View Record'),
        ('EXPORT', 'Export Data'),
        ('IMPORT', 'Import Data'),
        ('BULK_ACTION', 'Bulk Action'),
        ('SYSTEM_CONFIG', 'System Configuration'),
        ('USER_MANAGEMENT', 'User Management'),
        ('COMPANY_MANAGEMENT', 'Company Management'),
        ('SUBSCRIPTION_CHANGE', 'Subscription Change'),
        ('PAYMENT_ACTION', 'Payment Action'),
        ('SECURITY_EVENT', 'Security Event'),
        ('API_ACCESS', 'API Access'),
        ('BACKUP_RESTORE', 'Backup/Restore'),
        ('CRITICAL', 'Critical Event'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    RESOURCE_TYPES = [
        ('USER', 'User'),
        ('COMPANY', 'Company'),
        ('EMPLOYEE', 'Employee'),
        ('SUBSCRIPTION', 'Subscription'),
        ('PAYMENT', 'Payment'),
        ('SYSTEM', 'System'),
        ('API', 'API'),
        ('FILE', 'File'),
        ('REPORT', 'Report'),
        ('SETTING', 'Setting'),
        ('OTHER', 'Other'),
    ]
    
    # Core audit information
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    resource_id = models.CharField(max_length=100, blank=True, help_text="ID of the affected resource")
    resource_name = models.CharField(max_length=200, blank=True, help_text="Name/description of the affected resource")
    
    # Action details
    action_description = models.TextField(help_text="Detailed description of the action performed")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='MEDIUM')
    success = models.BooleanField(default=True, help_text="Whether the action was successful")
    error_message = models.TextField(blank=True, help_text="Error message if action failed")
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Change tracking
    old_values = models.JSONField(null=True, blank=True, help_text="Previous values before change")
    new_values = models.JSONField(null=True, blank=True, help_text="New values after change")
    changed_fields = models.JSONField(null=True, blank=True, help_text="List of fields that were changed")
    
    # Additional context
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    additional_data = models.JSONField(null=True, blank=True, help_text="Additional context data")
    tags = models.JSONField(default=list, help_text="Tags for categorization and filtering")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['action_type']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['company']),
            models.Index(fields=['success']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {user_str} - {self.get_action_type_display()}"
    
    @property
    def severity_color(self):
        """Return Bootstrap color class for severity level"""
        colors = {
            'LOW': 'success',
            'MEDIUM': 'info',
            'HIGH': 'warning',
            'CRITICAL': 'danger',
        }
        return colors.get(self.severity, 'secondary')
    
    @property
    def action_icon(self):
        """Return FontAwesome icon for action type"""
        icons = {
            'LOGIN': 'fas fa-sign-in-alt',
            'LOGOUT': 'fas fa-sign-out-alt',
            'CREATE': 'fas fa-plus',
            'UPDATE': 'fas fa-edit',
            'DELETE': 'fas fa-trash',
            'VIEW': 'fas fa-eye',
            'EXPORT': 'fas fa-download',
            'IMPORT': 'fas fa-upload',
            'BULK_ACTION': 'fas fa-tasks',
            'SYSTEM_CONFIG': 'fas fa-cogs',
            'USER_MANAGEMENT': 'fas fa-users',
            'COMPANY_MANAGEMENT': 'fas fa-building',
            'SUBSCRIPTION_CHANGE': 'fas fa-credit-card',
            'PAYMENT_ACTION': 'fas fa-money-bill',
            'SECURITY_EVENT': 'fas fa-shield-alt',
            'API_ACCESS': 'fas fa-code',
            'BACKUP_RESTORE': 'fas fa-database',
            'CRITICAL': 'fas fa-exclamation-triangle',
        }
        return icons.get(self.action_type, 'fas fa-info-circle')
    
    @classmethod
    def log_action(cls, user, action_type, resource_type, description, **kwargs):
        """Convenience method to create audit log entries"""
        return cls.objects.create(
            user=user,
            action_type=action_type,
            resource_type=resource_type,
            action_description=description,
            **kwargs
        )

# Notifications & Alerts Models
class Notification(models.Model):
    """System notifications"""
    NOTIFICATION_TYPES = [
        ('SYSTEM', 'System Notification'),
        ('SECURITY', 'Security Alert'),
        ('BACKUP', 'Backup Notification'),
        ('MAINTENANCE', 'Maintenance Alert'),
        ('USER_ACTION', 'User Action'),
        ('COMPANY_ACTION', 'Company Action'),
        ('EMPLOYEE_ACTION', 'Employee Action'),
        ('ANNOUNCEMENT', 'Company Announcement'),
        ('PERFORMANCE', 'Performance Update'),
        ('ATTENDANCE', 'Attendance Alert'),
        ('LEAVE', 'Leave Request'),
        ('TIMESHEET', 'Timesheet Update'),
        ('SHIFT', 'Shift Change'),
        ('PROJECT', 'Project Update'),
        ('TASK', 'Task Assignment'),
        ('DEADLINE', 'Deadline Reminder'),
        ('BIRTHDAY', 'Birthday Reminder'),
        ('ANNIVERSARY', 'Work Anniversary'),
        ('TRAINING', 'Training Reminder'),
        ('MEETING', 'Meeting Reminder'),
        ('PAYROLL', 'Payroll Update'),
        ('BENEFITS', 'Benefits Update'),
        ('POLICY', 'Policy Change'),
        ('EMERGENCY', 'Emergency Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    NOTIFICATION_CHANNELS = [
        ('IN_APP', 'In-App Notification'),
        ('EMAIL', 'Email Notification'),
        ('SMS', 'SMS Notification'),
        ('PUSH', 'Push Notification'),
        ('BROWSER', 'Browser Notification'),
    ]
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    channel = models.CharField(max_length=10, choices=NOTIFICATION_CHANNELS, default='IN_APP')
    
    # Optional associations
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    
    # Notification metadata
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Notification scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_scheduled(self):
        """Check if notification is scheduled for future delivery"""
        if self.scheduled_at:
            return timezone.now() < self.scheduled_at
        return False
    
    def mark_as_read(self, user=None):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        if user:
            self.user = user
        self.save()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()

class NotificationTemplate(models.Model):
    """Notification templates for different types"""
    TEMPLATE_TYPES = [
        ('WELCOME', 'Welcome Message'),
        ('BIRTHDAY', 'Birthday Greeting'),
        ('ANNIVERSARY', 'Work Anniversary'),
        ('PERFORMANCE_REVIEW', 'Performance Review'),
        ('LEAVE_APPROVED', 'Leave Approved'),
        ('LEAVE_REJECTED', 'Leave Rejected'),
        ('SHIFT_CHANGE', 'Shift Change'),
        ('DEADLINE_REMINDER', 'Deadline Reminder'),
        ('TASK_ASSIGNED', 'Task Assignment'),
        ('PROJECT_UPDATE', 'Project Update'),
        ('ATTENDANCE_ALERT', 'Attendance Alert'),
        ('TIMESHEET_REMINDER', 'Timesheet Reminder'),
        ('TRAINING_REMINDER', 'Training Reminder'),
        ('MEETING_REMINDER', 'Meeting Reminder'),
        ('POLICY_UPDATE', 'Policy Update'),
        ('EMERGENCY_ALERT', 'Emergency Alert'),
    ]
    
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, unique=True)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    email_subject_template = models.CharField(max_length=200, blank=True)
    email_template = models.TextField(blank=True)
    
    # Template settings
    is_active = models.BooleanField(default=True)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_LEVELS, default='MEDIUM')
    channel = models.CharField(max_length=10, choices=Notification.NOTIFICATION_CHANNELS, default='IN_APP')
    
    # Template variables
    variables = models.JSONField(default=list, blank=True, help_text="List of template variables")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type']
    
    def __str__(self):
        return f"{self.get_template_type_display()} Template"
    
    def render_template(self, context=None):
        """Render template with context variables"""
        if not context:
            context = {}
        
        try:
            from django.template import Template, Context
            title = Template(self.title_template).render(Context(context))
            message = Template(self.message_template).render(Context(context))
            return {
                'title': title,
                'message': message,
                'email_subject': Template(self.email_subject_template).render(Context(context)) if self.email_subject_template else title,
                'email_content': Template(self.email_template).render(Context(context)) if self.email_template else message
            }
        except Exception as e:
            return {
                'title': self.title_template,
                'message': self.message_template,
                'email_subject': self.email_subject_template or self.title_template,
                'email_content': self.email_template or self.message_template
            }

class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_preferences')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    browser_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Type preferences
    system_notifications = models.BooleanField(default=True)
    performance_notifications = models.BooleanField(default=True)
    attendance_notifications = models.BooleanField(default=True)
    leave_notifications = models.BooleanField(default=True)
    timesheet_notifications = models.BooleanField(default=True)
    shift_notifications = models.BooleanField(default=True)
    project_notifications = models.BooleanField(default=True)
    task_notifications = models.BooleanField(default=True)
    deadline_notifications = models.BooleanField(default=True)
    birthday_notifications = models.BooleanField(default=True)
    anniversary_notifications = models.BooleanField(default=True)
    training_notifications = models.BooleanField(default=True)
    meeting_notifications = models.BooleanField(default=True)
    payroll_notifications = models.BooleanField(default=True)
    benefits_notifications = models.BooleanField(default=True)
    policy_notifications = models.BooleanField(default=True)
    emergency_notifications = models.BooleanField(default=True)
    
    # Frequency preferences
    digest_frequency = models.CharField(max_length=20, choices=[
        ('IMMEDIATE', 'Immediate'),
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('NEVER', 'Never'),
    ], default='IMMEDIATE')
    
    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'company']
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name} Preferences"
    
    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:  # Overnight quiet hours
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
    
    def should_send_notification(self, notification_type, channel):
        """Check if notification should be sent based on preferences"""
        # Check if channel is enabled
        if channel == 'EMAIL' and not self.email_enabled:
            return False
        elif channel == 'SMS' and not self.sms_enabled:
            return False
        elif channel == 'PUSH' and not self.push_enabled:
            return False
        elif channel == 'BROWSER' and not self.browser_enabled:
            return False
        elif channel == 'IN_APP' and not self.in_app_enabled:
            return False
        
        # Check if notification type is enabled
        type_mapping = {
            'SYSTEM': 'system_notifications',
            'PERFORMANCE': 'performance_notifications',
            'ATTENDANCE': 'attendance_notifications',
            'LEAVE': 'leave_notifications',
            'TIMESHEET': 'timesheet_notifications',
            'SHIFT': 'shift_notifications',
            'PROJECT': 'project_notifications',
            'TASK': 'task_notifications',
            'DEADLINE': 'deadline_notifications',
            'BIRTHDAY': 'birthday_notifications',
            'ANNIVERSARY': 'anniversary_notifications',
            'TRAINING': 'training_notifications',
            'MEETING': 'meeting_notifications',
            'PAYROLL': 'payroll_notifications',
            'BENEFITS': 'benefits_notifications',
            'POLICY': 'policy_notifications',
            'EMERGENCY': 'emergency_notifications',
        }
        
        if notification_type in type_mapping:
            return getattr(self, type_mapping[notification_type], True)
        
        return True

class NotificationDigest(models.Model):
    """Notification digest for batch delivery"""
    DIGEST_TYPES = [
        ('DAILY', 'Daily Digest'),
        ('WEEKLY', 'Weekly Digest'),
        ('MONTHLY', 'Monthly Digest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_digests')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notification_digests')
    digest_type = models.CharField(max_length=20, choices=DIGEST_TYPES)
    
    # Digest content
    title = models.CharField(max_length=200)
    content = models.TextField()
    notifications = models.ManyToManyField(Notification, blank=True)
    
    # Delivery status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_method = models.CharField(max_length=20, choices=[
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
    ], default='EMAIL')
    
    # Digest period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_digest_type_display()} - {self.user.username} ({self.period_start.date()})"
    
    def mark_as_sent(self):
        """Mark digest as sent"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()

# Onboarding & Workflow Models
class OnboardingWorkflow(models.Model):
    """Onboarding workflow templates"""
    WORKFLOW_TYPES = [
        ('STANDARD', 'Standard Onboarding'),
        ('EXECUTIVE', 'Executive Onboarding'),
        ('INTERN', 'Intern Onboarding'),
        ('CONTRACTOR', 'Contractor Onboarding'),
        ('REMOTE', 'Remote Employee Onboarding'),
        ('CUSTOM', 'Custom Workflow'),
    ]
    
    WORKFLOW_STATUS = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ARCHIVED', 'Archived'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='onboarding_workflows')
    name = models.CharField(max_length=200)
    workflow_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=WORKFLOW_STATUS, default='DRAFT')
    
    # Workflow settings
    is_default = models.BooleanField(default=False)
    estimated_duration_days = models.IntegerField(default=7)
    auto_assign = models.BooleanField(default=True)
    
    # Target criteria
    target_departments = models.JSONField(default=list, blank=True)
    target_positions = models.JSONField(default=list, blank=True)
    target_employment_types = models.JSONField(default=list, blank=True)
    
    # Workflow metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_workflows')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    def get_total_tasks(self):
        """Get total number of tasks in this workflow"""
        return self.workflow_tasks.count()
    
    def get_completed_tasks(self, employee):
        """Get number of completed tasks for an employee"""
        return self.workflow_tasks.filter(
            task_assignments__employee=employee,
            task_assignments__status='COMPLETED'
        ).count()
    
    def get_progress_percentage(self, employee):
        """Get onboarding progress percentage for an employee"""
        total_tasks = self.get_total_tasks()
        if total_tasks == 0:
            return 100
        completed_tasks = self.get_completed_tasks(employee)
        return (completed_tasks / total_tasks) * 100

class OnboardingTask(models.Model):
    """Individual onboarding tasks"""
    TASK_TYPES = [
        ('DOCUMENT', 'Document Collection'),
        ('TRAINING', 'Training Module'),
        ('MEETING', 'Meeting/Session'),
        ('FORM', 'Form Completion'),
        ('EQUIPMENT', 'Equipment Setup'),
        ('ACCOUNT', 'Account Setup'),
        ('POLICY', 'Policy Review'),
        ('COMPLIANCE', 'Compliance Check'),
        ('CUSTOM', 'Custom Task'),
    ]
    
    TASK_PRIORITY = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    workflow = models.ForeignKey(OnboardingWorkflow, on_delete=models.CASCADE, related_name='workflow_tasks')
    name = models.CharField(max_length=200)
    description = models.TextField()
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    priority = models.CharField(max_length=10, choices=TASK_PRIORITY, default='MEDIUM')
    
    # Task details
    instructions = models.TextField(blank=True)
    estimated_duration_minutes = models.IntegerField(default=30)
    is_required = models.BooleanField(default=True)
    is_sequential = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Dependencies
    depends_on = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_tasks')
    
    # Assignment settings
    auto_assign_to = models.CharField(max_length=50, blank=True, help_text="Role or department to auto-assign to")
    assignee_type = models.CharField(max_length=20, choices=[
        ('EMPLOYEE', 'Employee'),
        ('MANAGER', 'Manager'),
        ('HR', 'HR Team'),
        ('IT', 'IT Team'),
        ('ADMIN', 'Administrator'),
    ], default='EMPLOYEE')
    
    # Task resources
    resources = models.JSONField(default=list, blank=True, help_text="Links, documents, or resources")
    attachments = models.JSONField(default=list, blank=True, help_text="File attachments")
    
    # Completion criteria
    completion_criteria = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=False)
    approval_role = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.name} - {self.workflow.name}"

class OnboardingAssignment(models.Model):
    """Employee onboarding assignments"""
    ASSIGNMENT_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='onboarding_assignments')
    workflow = models.ForeignKey(OnboardingWorkflow, on_delete=models.CASCADE, related_name='workflow_assignments')
    
    # Assignment details
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_onboardings')
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS, default='NOT_STARTED')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Assignment metadata
    notes = models.TextField(blank=True)
    manager_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assigned_at']
        unique_together = ['employee', 'workflow']
    
    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.workflow.name}"
    
    @property
    def is_overdue(self):
        """Check if assignment is overdue"""
        if self.due_date and self.status not in ['COMPLETED', 'CANCELLED']:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_remaining(self):
        """Get days remaining until due date"""
        if self.due_date and self.status not in ['COMPLETED', 'CANCELLED']:
            delta = self.due_date - timezone.now()
            return max(0, delta.days)
        return None
    
    def update_progress(self):
        """Update progress percentage based on completed tasks"""
        total_tasks = self.workflow.get_total_tasks()
        if total_tasks == 0:
            self.progress_percentage = 100
        else:
            completed_tasks = self.workflow.get_completed_tasks(self.employee)
            self.progress_percentage = (completed_tasks / total_tasks) * 100
        
        # Update status based on progress
        if self.progress_percentage == 100:
            self.status = 'COMPLETED'
            self.completed_at = timezone.now()
        elif self.progress_percentage > 0:
            self.status = 'IN_PROGRESS'
        
        self.save()

class OnboardingTaskAssignment(models.Model):
    """Individual task assignments within onboarding"""
    TASK_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('OVERDUE', 'Overdue'),
    ]
    
    onboarding_assignment = models.ForeignKey(OnboardingAssignment, on_delete=models.CASCADE, related_name='task_assignments')
    task = models.ForeignKey(OnboardingTask, on_delete=models.CASCADE, related_name='task_assignments')
    
    # Assignment details
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='NOT_STARTED')
    
    # Task completion
    completion_notes = models.TextField(blank=True)
    completion_attachments = models.JSONField(default=list, blank=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_tasks')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['task__order', 'assigned_at']
        unique_together = ['onboarding_assignment', 'task']
    
    def __str__(self):
        return f"{self.task.name} - {self.onboarding_assignment.employee.first_name} {self.onboarding_assignment.employee.last_name}"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status not in ['COMPLETED', 'REJECTED']:
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_remaining(self):
        """Get days remaining until due date"""
        if self.due_date and self.status not in ['COMPLETED', 'REJECTED']:
            delta = self.due_date - timezone.now()
            return max(0, delta.days)
        return None
    
    def mark_as_started(self):
        """Mark task as started"""
        self.status = 'IN_PROGRESS'
        self.started_at = timezone.now()
        self.save()
    
    def mark_as_completed(self, notes='', attachments=None):
        """Mark task as completed"""
        if self.task.requires_approval:
            self.status = 'PENDING_APPROVAL'
        else:
            self.status = 'COMPLETED'
            self.completed_at = timezone.now()
        
        self.completion_notes = notes
        if attachments:
            self.completion_attachments = attachments
        self.save()
        
        # Update onboarding assignment progress
        self.onboarding_assignment.update_progress()
    
    def approve_task(self, approver, notes=''):
        """Approve task completion"""
        self.status = 'COMPLETED'
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.completed_at = timezone.now()
        self.save()
        
        # Update onboarding assignment progress
        self.onboarding_assignment.update_progress()
    
    def reject_task(self, approver, notes=''):
        """Reject task completion"""
        self.status = 'REJECTED'
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()

class OnboardingDocument(models.Model):
    """Required documents for onboarding"""
    DOCUMENT_TYPES = [
        ('CONTRACT', 'Employment Contract'),
        ('ID', 'Government ID'),
        ('TAX', 'Tax Forms'),
        ('BANK', 'Banking Information'),
        ('EMERGENCY', 'Emergency Contact'),
        ('MEDICAL', 'Medical Information'),
        ('POLICY', 'Policy Acknowledgment'),
        ('TRAINING', 'Training Certificate'),
        ('CUSTOM', 'Custom Document'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='onboarding_documents')
    name = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    description = models.TextField(blank=True)
    
    # Document requirements
    is_required = models.BooleanField(default=True)
    is_uploadable = models.BooleanField(default=True)
    file_types = models.JSONField(default=list, blank=True, help_text="Allowed file types")
    max_file_size_mb = models.IntegerField(default=10)
    
    # Document template
    template_file = models.FileField(upload_to='onboarding_templates/', blank=True)
    template_url = models.URLField(blank=True)
    
    # Workflow association
    workflows = models.ManyToManyField(OnboardingWorkflow, blank=True, related_name='required_documents')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"

class OnboardingDocumentSubmission(models.Model):
    """Employee document submissions"""
    SUBMISSION_STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RESUBMITTED', 'Resubmitted'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='document_submissions')
    document = models.ForeignKey(OnboardingDocument, on_delete=models.CASCADE, related_name='submissions')
    onboarding_assignment = models.ForeignKey(OnboardingAssignment, on_delete=models.CASCADE, related_name='document_submissions')
    
    # Submission details
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='onboarding_documents/', blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    
    # Review process
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default='PENDING')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_documents')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Resubmission
    resubmitted_at = models.DateTimeField(null=True, blank=True)
    resubmission_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.document.name}"
    
    def approve_submission(self, reviewer, notes=''):
        """Approve document submission"""
        self.status = 'APPROVED'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
    
    def reject_submission(self, reviewer, notes=''):
        """Reject document submission"""
        self.status = 'REJECTED'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
    
    def resubmit(self, new_file=None):
        """Resubmit document"""
        self.status = 'RESUBMITTED'
        self.resubmitted_at = timezone.now()
        self.resubmission_count += 1
        if new_file:
            self.file = new_file
        self.save()

# Document Management Models
class DocumentCategory(models.Model):
    """Document categories for organization"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='document_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    color = models.CharField(max_length=7, default='#667eea', help_text="Hex color code")
    icon = models.CharField(max_length=50, default='fas fa-folder', help_text="Font Awesome icon class")
    
    # Category settings
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    @property
    def document_count(self):
        """Get number of documents in this category"""
        return self.documents.count()
    
    @property
    def total_size(self):
        """Get total size of documents in this category"""
        return self.documents.aggregate(total_size=models.Sum('file_size'))['total_size'] or 0

class Document(models.Model):
    """Employee documents and files"""
    DOCUMENT_TYPES = [
        ('CONTRACT', 'Contract'),
        ('POLICY', 'Policy'),
        ('MANUAL', 'Manual'),
        ('TEMPLATE', 'Template'),
        ('FORM', 'Form'),
        ('PRESENTATION', 'Presentation'),
        ('SPREADSHEET', 'Spreadsheet'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('PDF', 'PDF Document'),
        ('OTHER', 'Other'),
    ]
    
    ACCESS_LEVELS = [
        ('PUBLIC', 'Public'),
        ('INTERNAL', 'Internal'),
        ('CONFIDENTIAL', 'Confidential'),
        ('RESTRICTED', 'Restricted'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents')
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # Document details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='OTHER')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='INTERNAL')
    
    # File information
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    file_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash for duplicate detection")
    
    # Document metadata
    version = models.CharField(max_length=20, default='1.0')
    is_template = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Ownership and permissions
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    owner = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_documents')
    
    # Sharing settings
    shared_with_all = models.BooleanField(default=False)
    shared_departments = models.ManyToManyField('self', blank=True, through='DocumentDepartmentShare', symmetrical=False, related_name='department_documents')
    shared_employees = models.ManyToManyField(Employee, blank=True, through='DocumentEmployeeShare', related_name='shared_documents')
    
    # Document lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tags and keywords
    tags = models.JSONField(default=list, blank=True)
    keywords = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.company.name}"
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def file_size_formatted(self):
        """Get formatted file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def is_expired(self):
        """Check if document has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def download_count(self):
        """Get total download count"""
        return self.downloads.count()
    
    @property
    def view_count(self):
        """Get total view count"""
        return self.views.count()
    
    def can_access(self, user):
        """Check if user can access this document"""
        if self.access_level == 'PUBLIC':
            return True
        elif self.access_level == 'INTERNAL' and hasattr(user, 'company_admin_profile'):
            return user.company_admin_profile.company == self.company
        elif self.access_level == 'CONFIDENTIAL':
            return self.shared_employees.filter(id=user.id).exists() or self.uploaded_by == user
        elif self.access_level == 'RESTRICTED':
            return self.uploaded_by == user or self.owner == user
        return False

class DocumentVersion(models.Model):
    """Document version control"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    file = models.FileField(upload_to='documents/versions/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_hash = models.CharField(max_length=64, blank=True)
    
    # Version details
    change_summary = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Version metadata
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['document', 'version_number']
    
    def __str__(self):
        return f"{self.document.title} v{self.version_number}"

class DocumentShare(models.Model):
    """Document sharing permissions"""
    SHARE_TYPES = [
        ('VIEW', 'View Only'),
        ('COMMENT', 'View & Comment'),
        ('EDIT', 'View & Edit'),
        ('ADMIN', 'Full Access'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_documents')
    share_type = models.CharField(max_length=20, choices=SHARE_TYPES, default='VIEW')
    
    # Sharing details
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_documents_by')
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Access tracking
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['document', 'shared_with']
    
    def __str__(self):
        return f"{self.document.title} shared with {self.shared_with.username}"

class DocumentEmployeeShare(models.Model):
    """Document sharing with specific employees"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    share_type = models.CharField(max_length=20, choices=DocumentShare.SHARE_TYPES, default='VIEW')
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['document', 'employee']
    
    def __str__(self):
        return f"{self.document.title} shared with {self.employee.first_name} {self.employee.last_name}"

class DocumentDepartmentShare(models.Model):
    """Document sharing with departments"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    share_type = models.CharField(max_length=20, choices=DocumentShare.SHARE_TYPES, default='VIEW')
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['document', 'department']
    
    def __str__(self):
        return f"{self.document.title} shared with {self.department}"

class DocumentAccess(models.Model):
    """Document access tracking"""
    ACCESS_TYPES = [
        ('VIEW', 'View'),
        ('DOWNLOAD', 'Download'),
        ('EDIT', 'Edit'),
        ('SHARE', 'Share'),
        ('DELETE', 'Delete'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='accesses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_accesses')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-accessed_at']
    
    def __str__(self):
        return f"{self.user.username} {self.access_type} {self.document.title}"

class DocumentComment(models.Model):
    """Document comments and annotations"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_comments')
    comment = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Comment metadata
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_comments')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.document.title} by {self.user.username}"

class DocumentTemplate(models.Model):
    """Document templates"""
    TEMPLATE_TYPES = [
        ('CONTRACT', 'Contract Template'),
        ('POLICY', 'Policy Template'),
        ('FORM', 'Form Template'),
        ('REPORT', 'Report Template'),
        ('PRESENTATION', 'Presentation Template'),
        ('EMAIL', 'Email Template'),
        ('OTHER', 'Other Template'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='document_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    
    # Template file
    template_file = models.FileField(upload_to='templates/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)
    
    # Template settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    # Template metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save()

class PaymentMethod(models.Model):
    """Company payment methods"""
    PAYMENT_TYPE_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_ACCOUNT', 'Bank Account'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
    ]
    
    CARD_TYPE_CHOICES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('AMERICAN_EXPRESS', 'American Express'),
        ('DISCOVER', 'Discover'),
        ('JCB', 'JCB'),
        ('DINERS_CLUB', 'Diners Club'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='CREDIT_CARD')
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, blank=True, null=True)
    last_four_digits = models.CharField(max_length=4)
    expiry_month = models.CharField(max_length=2, blank=True, null=True)
    expiry_year = models.CharField(max_length=4, blank=True, null=True)
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        unique_together = ['company', 'last_four_digits', 'expiry_month', 'expiry_year']
    
    def __str__(self):
        if self.payment_type == 'CREDIT_CARD' or self.payment_type == 'DEBIT_CARD':
            return f"{self.card_type} ****{self.last_four_digits}"
        return f"{self.get_payment_type_display()} ****{self.last_four_digits}"
    
    def get_display_name(self):
        """Get display name for the payment method"""
        if self.payment_type == 'CREDIT_CARD' or self.payment_type == 'DEBIT_CARD':
            return f"{self.get_card_type_display()} ****{self.last_four_digits}"
        return f"{self.get_payment_type_display()} ****{self.last_four_digits}"
    
    def get_expiry_display(self):
        """Get formatted expiry date"""
        if self.expiry_month and self.expiry_year:
            return f"{self.expiry_month}/{self.expiry_year[-2:]}"
        return "N/A"
    
    def save(self, *args, **kwargs):
        # Ensure only one default payment method per company
        if self.is_default:
            PaymentMethod.objects.filter(company=self.company, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class Announcement(models.Model):
    """Company announcements"""
    ANNOUNCEMENT_TYPE_CHOICES = [
        ('GENERAL', 'General'),
        ('BILLING', 'Billing'),
        ('SYSTEM', 'System'),
        ('CHAT', 'Chat'),
        ('FILE', 'File'),
        ('LEAVE', 'Leave'),
        ('BENEFIT', 'Benefit'),
        ('CUSTOMER', 'Customer'),
        ('CONTACT', 'Contact'),
        ('MAINTENANCE', 'Maintenance'),
        ('INVENTORY', 'Inventory'),
        ('DATA_PROTECTION', 'Data Protection'),
        ('SECURITY', 'Security'),
        ('WEBHOOK', 'Webhook'),
        ('EXPORT', 'Export'),
        ('INSIGHT', 'Insight'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPE_CHOICES, default='GENERAL')
    priority = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ], default='MEDIUM')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# Business Intelligence Models
class CompanyMetric(models.Model):
    """Company-level business metrics"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='metrics')
    metric_name = models.CharField(max_length=100)
    metric_value = models.DecimalField(max_digits=15, decimal_places=2)
    metric_unit = models.CharField(max_length=20, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    category = models.CharField(max_length=50, choices=[
        ('REVENUE', 'Revenue'),
        ('COST', 'Cost'),
        ('PRODUCTIVITY', 'Productivity'),
        ('CUSTOMER', 'Customer'),
        ('OPERATIONAL', 'Operational'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_end']
    
    def __str__(self):
        return f"{self.company} - {self.metric_name}: {self.metric_value}"

# System Administration Models
class CompanySetting(models.Model):
    """Company-specific settings"""
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='settings')
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    currency = models.CharField(max_length=3, default='USD')
    working_hours_start = models.TimeField(default='09:00')
    working_hours_end = models.TimeField(default='17:00')
    working_days = models.JSONField(default=list)  # ['monday', 'tuesday', ...]
    allow_employee_registration = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=True)
    max_file_upload_size = models.IntegerField(default=10)  # MB
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.company.name}"

class UserPreference(models.Model):
    """User-specific preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=[
        ('LIGHT', 'Light'),
        ('DARK', 'Dark'),
        ('AUTO', 'Auto'),
    ], default='LIGHT')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    email_notifications = models.BooleanField(default=True)
    dashboard_layout = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

# Workflow Management Models
class WorkflowTemplate(models.Model):
    """Workflow templates for common processes"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='workflow_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    steps = models.JSONField(default=list)  # List of workflow steps
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class WorkflowInstance(models.Model):
    """Active workflow instances"""
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    current_step = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('PAUSED', 'Paused'),
    ], default='ACTIVE')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    data = models.JSONField(default=dict)  # Workflow-specific data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# Chat System Models
class ChatRoom(models.Model):
    """Chat rooms for group conversations"""
    ROOM_TYPES = [
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Chat'),
        ('DEPARTMENT', 'Department Chat'),
        ('PROJECT', 'Project Chat'),
        ('COMPANY', 'Company Wide'),
    ]
    
    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='GROUP')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='chat_rooms')
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='created_rooms')
    participants = models.ManyToManyField(Employee, related_name='chat_rooms', blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"
    
    def get_last_message(self):
        """Get the last message in this room"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, employee):
        """Get unread message count for a specific employee"""
        return self.messages.filter(
            created_at__gt=employee.last_seen_chat,
            sender__ne=employee
        ).count() if hasattr(employee, 'last_seen_chat') else 0

class ChatMessage(models.Model):
    """Individual chat messages"""
    MESSAGE_TYPES = [
        ('TEXT', 'Text Message'),
        ('IMAGE', 'Image'),
        ('FILE', 'File Attachment'),
        ('SYSTEM', 'System Message'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='TEXT')
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.first_name}: {self.content[:50]}..."
    
    def get_reply_count(self):
        """Get number of replies to this message"""
        return self.replies.filter(is_deleted=False).count()

class ChatParticipant(models.Model):
    """Track participant status in chat rooms"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participant_status')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='chat_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_muted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['room', 'employee']
    
    def __str__(self):
        return f"{self.employee.first_name} in {self.room.name}"

class ChatNotification(models.Model):
    """Chat notifications for offline users"""
    NOTIFICATION_TYPES = [
        ('NEW_MESSAGE', 'New Message'),
        ('MENTION', 'Mention'),
        ('ROOM_INVITE', 'Room Invitation'),
        ('SYSTEM', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='chat_notifications')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_chat_notifications', null=True, blank=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='NEW_MESSAGE')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.first_name}"
