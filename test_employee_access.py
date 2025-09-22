#!/usr/bin/env python3
"""
Employee Dashboard Access Test
Tests if users can access employee dashboard features
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Company, Employee

def test_employee_access():
    """Test employee dashboard access"""
    print("🔍 Testing Employee Dashboard Access...")
    print("="*60)
    
    client = Client()
    
    # Test 1: Unauthenticated user
    print("\n1. Testing unauthenticated user...")
    response = client.get('/employee/dashboard/')
    if response.status_code == 302:  # Redirect to login
        print("✅ Unauthenticated user redirected to login")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
    
    # Test 2: User without employee profile
    print("\n2. Testing user without employee profile...")
    try:
        # Create a regular user (not an employee)
        test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        client.login(username='testuser', password='testpass123')
        response = client.get('/employee/dashboard/')
        
        if response.status_code == 302:  # Redirect to home
            print("✅ User without employee profile redirected to home")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
        
        # Clean up
        test_user.delete()
        
    except Exception as e:
        print(f"❌ Error testing user without employee profile: {e}")
    
    # Test 3: User with employee profile
    print("\n3. Testing user with employee profile...")
    try:
        # Create test company
        test_company = Company.objects.create(
            name="Test Company",
            domain="testcompany.com",
            is_premium=True
        )
        
        # Create employee user
        employee_user = User.objects.create_user(
            username='testemployee',
            email='employee@testcompany.com',
            password='testpass123',
            first_name='Test',
            last_name='Employee'
        )
        
        # Create employee profile
        employee = Employee.objects.create(
            user_account=employee_user,
            company=test_company,
            employee_id='EMP001',
            first_name='Test',
            last_name='Employee',
            email='employee@testcompany.com',
            department='Engineering',
            position='Software Developer',
            is_active=True
        )
        
        client.login(username='testemployee', password='testpass123')
        response = client.get('/employee/dashboard/')
        
        if response.status_code == 200:
            print("✅ User with employee profile can access dashboard")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
        
        # Clean up
        employee.delete()
        employee_user.delete()
        test_company.delete()
        
    except Exception as e:
        print(f"❌ Error testing user with employee profile: {e}")
    
    print("\n" + "="*60)
    print("🎯 DIAGNOSIS COMPLETE")
    print("="*60)
    print("If links are not working, the most likely causes are:")
    print("1. User is not logged in")
    print("2. User doesn't have an employee profile")
    print("3. User's employee profile is inactive")
    print("4. User is logged in as company admin instead of employee")

def create_test_employee():
    """Create a test employee for testing purposes"""
    print("\n🔧 Creating Test Employee...")
    print("="*60)
    
    try:
        # Check if test company exists
        test_company, created = Company.objects.get_or_create(
            name="Test Company",
            defaults={
                'domain': 'testcompany.com',
                'is_premium': True
            }
        )
        
        if created:
            print("✅ Created test company")
        else:
            print("✅ Test company already exists")
        
        # Check if test employee exists
        test_employee, created = Employee.objects.get_or_create(
            employee_id='TEST001',
            defaults={
                'user_account': None,  # Will be created below
                'company': test_company,
                'first_name': 'Test',
                'last_name': 'Employee',
                'email': 'test@testcompany.com',
                'department': 'Engineering',
                'position': 'Software Developer',
                'is_verified': True
            }
        )
        
        if created:
            print("✅ Created test employee")
        else:
            print("✅ Test employee already exists")
        
        # Create user account if it doesn't exist
        if not test_employee.user_account:
            test_user = User.objects.create_user(
                username='testemployee',
                email='test@testcompany.com',
                password='testpass123',
                first_name='Test',
                last_name='Employee'
            )
            test_employee.user_account = test_user
            test_employee.save()
            print("✅ Created user account for test employee")
        else:
            print("✅ User account already exists for test employee")
        
        print("\n🎉 Test employee created successfully!")
        print("You can now login with:")
        print("Username: testemployee")
        print("Password: testpass123")
        print("URL: http://localhost:8080/employee/dashboard/")
        
    except Exception as e:
        print(f"❌ Error creating test employee: {e}")

def main():
    """Main function"""
    print("🔧 Employee Dashboard Access Test")
    print("="*60)
    
    test_employee_access()
    create_test_employee()

if __name__ == "__main__":
    main()
