from django import forms
from django.contrib.auth.models import User
from .models import Company, CompanyAdmin, SystemOwner, Employee

class CompanyRegistrationForm(forms.ModelForm):
    """Form for system owner to register a new company"""
    
    class Meta:
        model = Company
        fields = ['name', 'domain', 'max_users']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'domain': forms.TextInput(attrs={'class': 'form-control'}),
            'max_users': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean_domain(self):
        domain = self.cleaned_data.get('domain')
        if Company.objects.filter(domain=domain).exists():
            raise forms.ValidationError("A company with this domain already exists.")
        return domain

class CompanyAdminRegistrationForm(forms.Form):
    """Form for company admin to register and create new company"""
    company_name = forms.CharField(
        max_length=200,
        help_text="Enter your company name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    company_domain = forms.CharField(
        max_length=100,
        help_text="Enter your company domain (e.g., yourcompany.com)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        help_text="Choose your username",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        help_text="Your email address",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Choose a secure password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Confirm your password"
    )
    first_name = forms.CharField(
        max_length=30,
        help_text="Your first name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        help_text="Your last name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        help_text="Your phone number (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_company_domain(self):
        domain = self.cleaned_data.get('company_domain')
        if Company.objects.filter(domain=domain).exists():
            raise forms.ValidationError("A company with this domain already exists.")
        return domain
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class EmployeeCSVImportForm(forms.Form):
    """Form for importing employees from CSV"""
    csv_file = forms.FileField(
        help_text="Upload CSV file with columns: employee_id, first_name, last_name, email, department, position",
        widget=forms.FileInput(attrs={'accept': '.csv', 'class': 'form-control'})
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise forms.ValidationError("File must be a CSV file.")
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be less than 5MB.")
        return csv_file

class EmployeeVerificationForm(forms.Form):
    """Form for employees to verify their identity"""
    employee_id = forms.CharField(
        max_length=50, 
        help_text="Your Employee ID",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        help_text="Your company email address",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        employee_id = cleaned_data.get('employee_id')
        email = cleaned_data.get('email')
        
        if employee_id and email:
            if not self.company:
                raise forms.ValidationError("Company context is required for verification.")
            
            try:
                # Find employee by ID, email, and company combination
                employee = Employee.objects.get(
                    employee_id=employee_id,
                    email=email,
                    company=self.company
                )
                
                # Check if employee already has an account
                if employee.user_account:
                    raise forms.ValidationError("This employee already has an account.")
                
                cleaned_data['employee'] = employee
            except Employee.DoesNotExist:
                raise forms.ValidationError("Employee not found. Please check your Employee ID and email.")
            except Employee.MultipleObjectsReturned:
                raise forms.ValidationError(
                    "Multiple employees found with this information. Please contact your administrator."
                )
        
        return cleaned_data

class EmployeeRegistrationForm(forms.ModelForm):
    """Form for employees to create their account after verification"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
