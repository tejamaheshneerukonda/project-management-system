#!/usr/bin/env python3
"""
Employee Dashboard Testing Suite
Comprehensive testing for all employee dashboard features
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

from core.models import Company, Employee, Project, Task, Timesheet, PerformanceGoal, LeaveRequest, Announcement, Notification

class EmployeeDashboardTestSuite:
    """Comprehensive test suite for employee dashboard features"""
    
    def __init__(self):
        self.client = Client()
        self.test_user = None
        self.test_company = None
        self.test_employee = None
        self.test_results = []
        
    def setup_test_data(self):
        """Create test data for testing"""
        print("🔧 Setting up test data...")
        
        try:
            # Create test company
            self.test_company = Company.objects.create(
                name="Test Company",
                domain="testcompany.com",
                is_premium=True
            )
            
            # Create test user
            self.test_user = User.objects.create_user(
                username='testemployee',
                email='test@testcompany.com',
                password='testpass123',
                first_name='Test',
                last_name='Employee'
            )
            
            # Create test employee
            self.test_employee = Employee.objects.create(
                user_account=self.test_user,
                company=self.test_company,
                employee_id='EMP001',
                first_name='Test',
                last_name='Employee',
                email='test@testcompany.com',
                department='Engineering',
                position='Software Developer',
                is_active=True
            )
            
            # Create test projects
            self.test_project = Project.objects.create(
                name='Test Project',
                description='A test project for testing',
                company=self.test_company,
                project_manager=self.test_employee,
                status='ACTIVE'
            )
            
            # Create test tasks
            self.test_task = Task.objects.create(
                title='Test Task',
                description='A test task for testing',
                project=self.test_project,
                assigned_to=self.test_employee,
                priority='HIGH',
                status='TODO',
                due_date='2024-12-31'
            )
            
            print("✅ Test data setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up test data: {e}")
            return False
    
    def test_authentication(self):
        """Test employee authentication"""
        print("\n🔐 Testing authentication...")
        
        try:
            # Test login
            login_success = self.client.login(username='testemployee', password='testpass123')
            if login_success:
                print("✅ Login successful")
                self.test_results.append(("Authentication", "PASS", "Login successful"))
            else:
                print("❌ Login failed")
                self.test_results.append(("Authentication", "FAIL", "Login failed"))
                return False
            
            # Test logout
            self.client.logout()
            print("✅ Logout successful")
            self.test_results.append(("Authentication", "PASS", "Logout successful"))
            
            return True
            
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            self.test_results.append(("Authentication", "FAIL", str(e)))
            return False
    
    def test_dashboard_access(self):
        """Test employee dashboard access"""
        print("\n📊 Testing dashboard access...")
        
        try:
            self.client.login(username='testemployee', password='testpass123')
            
            # Test main dashboard
            response = self.client.get(reverse('core:employee_dashboard'))
            if response.status_code == 200:
                print("✅ Main dashboard accessible")
                self.test_results.append(("Dashboard Access", "PASS", "Main dashboard accessible"))
            else:
                print(f"❌ Main dashboard failed: {response.status_code}")
                self.test_results.append(("Dashboard Access", "FAIL", f"Status code: {response.status_code}"))
            
            self.client.logout()
            return True
            
        except Exception as e:
            print(f"❌ Dashboard access test failed: {e}")
            self.test_results.append(("Dashboard Access", "FAIL", str(e)))
            return False
    
    def test_all_employee_pages(self):
        """Test all employee dashboard pages"""
        print("\n📄 Testing all employee pages...")
        
        pages_to_test = [
            ('employee_tasks', 'Tasks'),
            ('employee_projects', 'Projects'),
            ('employee_timesheet', 'Timesheet'),
            ('employee_goals', 'Goals'),
            ('employee_leave', 'Leave'),
            ('employee_analytics', 'Analytics'),
            ('employee_notifications', 'Notifications'),
            ('employee_team_directory', 'Team Directory'),
            ('employee_calendar', 'Calendar'),
            ('employee_kanban_board', 'Kanban Board'),
            ('employee_gamification', 'Gamification'),
            ('employee_documents', 'Documents'),
            ('employee_productivity', 'Productivity'),
            ('employee_settings', 'Settings'),
            ('employee_search', 'Search'),
            ('employee_shortcuts', 'Shortcuts'),
            ('employee_onboarding', 'Onboarding'),
        ]
        
        try:
            self.client.login(username='testemployee', password='testpass123')
            
            for url_name, page_name in pages_to_test:
                try:
                    response = self.client.get(reverse(f'core:{url_name}'))
                    if response.status_code == 200:
                        print(f"✅ {page_name} page accessible")
                        self.test_results.append((f"{page_name} Page", "PASS", "Page accessible"))
                    else:
                        print(f"❌ {page_name} page failed: {response.status_code}")
                        self.test_results.append((f"{page_name} Page", "FAIL", f"Status code: {response.status_code}"))
                except Exception as e:
                    print(f"❌ {page_name} page error: {e}")
                    self.test_results.append((f"{page_name} Page", "FAIL", str(e)))
            
            self.client.logout()
            return True
            
        except Exception as e:
            print(f"❌ Page testing failed: {e}")
            self.test_results.append(("Page Testing", "FAIL", str(e)))
            return False
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print("\n🔍 Testing data integrity...")
        
        try:
            # Test employee-company relationship
            if self.test_employee.company == self.test_company:
                print("✅ Employee-company relationship intact")
                self.test_results.append(("Data Integrity", "PASS", "Employee-company relationship"))
            else:
                print("❌ Employee-company relationship broken")
                self.test_results.append(("Data Integrity", "FAIL", "Employee-company relationship"))
            
            # Test task-project relationship
            if self.test_task.project == self.test_project:
                print("✅ Task-project relationship intact")
                self.test_results.append(("Data Integrity", "PASS", "Task-project relationship"))
            else:
                print("❌ Task-project relationship broken")
                self.test_results.append(("Data Integrity", "FAIL", "Task-project relationship"))
            
            # Test task-employee relationship
            if self.test_task.assigned_to == self.test_employee:
                print("✅ Task-employee relationship intact")
                self.test_results.append(("Data Integrity", "PASS", "Task-employee relationship"))
            else:
                print("❌ Task-employee relationship broken")
                self.test_results.append(("Data Integrity", "FAIL", "Task-employee relationship"))
            
            return True
            
        except Exception as e:
            print(f"❌ Data integrity test failed: {e}")
            self.test_results.append(("Data Integrity", "FAIL", str(e)))
            return False
    
    def test_performance(self):
        """Test page load performance"""
        print("\n⚡ Testing performance...")
        
        try:
            self.client.login(username='testemployee', password='testpass123')
            
            import time
            
            # Test main dashboard performance
            start_time = time.time()
            response = self.client.get(reverse('core:employee_dashboard'))
            load_time = time.time() - start_time
            
            if response.status_code == 200 and load_time < 2.0:  # Less than 2 seconds
                print(f"✅ Dashboard loads in {load_time:.2f}s")
                self.test_results.append(("Performance", "PASS", f"Dashboard: {load_time:.2f}s"))
            else:
                print(f"❌ Dashboard slow: {load_time:.2f}s")
                self.test_results.append(("Performance", "FAIL", f"Dashboard: {load_time:.2f}s"))
            
            # Test analytics page performance
            start_time = time.time()
            response = self.client.get(reverse('core:employee_analytics'))
            load_time = time.time() - start_time
            
            if response.status_code == 200 and load_time < 3.0:  # Less than 3 seconds
                print(f"✅ Analytics loads in {load_time:.2f}s")
                self.test_results.append(("Performance", "PASS", f"Analytics: {load_time:.2f}s"))
            else:
                print(f"❌ Analytics slow: {load_time:.2f}s")
                self.test_results.append(("Performance", "FAIL", f"Analytics: {load_time:.2f}s"))
            
            self.client.logout()
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.test_results.append(("Performance", "FAIL", str(e)))
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order to avoid foreign key constraints
            if hasattr(self, 'test_task'):
                self.test_task.delete()
            if hasattr(self, 'test_project'):
                self.test_project.delete()
            if hasattr(self, 'test_employee'):
                self.test_employee.delete()
            if hasattr(self, 'test_user'):
                self.test_user.delete()
            if hasattr(self, 'test_company'):
                self.test_company.delete()
            
            print("✅ Test data cleaned up")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False
    
    def generate_report(self):
        """Generate test report"""
        print("\n📊 Generating test report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("🧪 EMPLOYEE DASHBOARD TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("="*60)
        
        print("\n📋 DETAILED RESULTS:")
        print("-"*60)
        for test_name, result, details in self.test_results:
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result}")
            if details:
                print(f"   Details: {details}")
        
        print("\n" + "="*60)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Employee dashboard is ready for production!")
        else:
            print(f"⚠️  {failed_tests} tests failed. Please review and fix issues.")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Employee Dashboard Test Suite...")
        print("="*60)
        
        success = True
        
        # Setup
        if not self.setup_test_data():
            success = False
        
        # Run tests
        if success:
            success &= self.test_authentication()
            success &= self.test_dashboard_access()
            success &= self.test_all_employee_pages()
            success &= self.test_data_integrity()
            success &= self.test_performance()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate report
        final_success = self.generate_report()
        
        return final_success

def main():
    """Main function to run the test suite"""
    print("🧪 Employee Dashboard Testing Suite")
    print("="*50)
    
    test_suite = EmployeeDashboardTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test suite completed with failures!")
        sys.exit(1)

if __name__ == "__main__":
    main()
