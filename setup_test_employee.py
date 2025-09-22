#!/usr/bin/env python3
"""
Quick Employee Dashboard Test Setup
Creates a test employee for testing the dashboard
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Company, Employee

def create_test_employee():
    """Create a test employee for dashboard testing"""
    print("🔧 Creating Test Employee for Dashboard Testing...")
    print("="*60)
    
    try:
        # Get or create test company
        test_company, created = Company.objects.get_or_create(
            domain='testcompany.com',
            defaults={
                'name': 'Test Company',
                'is_premium': True
            }
        )
        
        if created:
            print("✅ Created test company: Test Company")
        else:
            print("✅ Using existing test company: Test Company")
        
        # Check if test employee already exists
        existing_employee = Employee.objects.filter(
            company=test_company,
            employee_id='TEST001'
        ).first()
        
        if existing_employee:
            print("✅ Test employee already exists")
            if existing_employee.user_account:
                print(f"   Username: {existing_employee.user_account.username}")
                print("   Password: testpass123")
            else:
                print("   Creating user account...")
                user = User.objects.create_user(
                    username='testemployee',
                    email='test@testcompany.com',
                    password='testpass123',
                    first_name='Test',
                    last_name='Employee'
                )
                existing_employee.user_account = user
                existing_employee.save()
                print("✅ User account created")
        else:
            # Create new test employee
            print("Creating new test employee...")
            
            # Create user account first
            user = User.objects.create_user(
                username='testemployee',
                email='test@testcompany.com',
                password='testpass123',
                first_name='Test',
                last_name='Employee'
            )
            
            # Create employee profile
            employee = Employee.objects.create(
                user_account=user,
                company=test_company,
                employee_id='TEST001',
                first_name='Test',
                last_name='Employee',
                email='test@testcompany.com',
                department='Engineering',
                position='Software Developer',
                is_verified=True
            )
            
            print("✅ Test employee created successfully!")
        
        print("\n" + "="*60)
        print("🎉 TEST EMPLOYEE READY!")
        print("="*60)
        print("You can now test the employee dashboard with:")
        print("Username: testemployee")
        print("Password: testpass123")
        print("URL: http://localhost:8080/employee/dashboard/")
        print("\nAll employee dashboard links should now work!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test employee: {e}")
        return False

def check_existing_employees():
    """Check if there are any existing employees"""
    print("\n🔍 Checking Existing Employees...")
    print("="*60)
    
    employees = Employee.objects.filter(user_account__isnull=False)
    
    if employees.exists():
        print(f"Found {employees.count()} employees with user accounts:")
        for emp in employees[:5]:  # Show first 5
            print(f"  - {emp.user_account.username} ({emp.first_name} {emp.last_name})")
        if employees.count() > 5:
            print(f"  ... and {employees.count() - 5} more")
    else:
        print("No employees with user accounts found.")
        print("This is why the dashboard links don't work!")
        print("You need to create an employee profile first.")

def main():
    """Main function"""
    print("🚀 Employee Dashboard Test Setup")
    print("="*60)
    
    check_existing_employees()
    
    if create_test_employee():
        print("\n✅ Setup complete! You can now test the employee dashboard.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
