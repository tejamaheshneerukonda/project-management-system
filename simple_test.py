#!/usr/bin/env python3
"""
Simple Employee Dashboard Test
Tests all employee dashboard URLs and basic functionality
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

def test_employee_urls():
    """Test all employee dashboard URLs"""
    print("🧪 Testing Employee Dashboard URLs...")
    print("="*50)
    
    client = Client()
    
    # Employee URLs to test
    employee_urls = [
        ('core:employee_dashboard', 'Dashboard'),
        ('core:employee_tasks', 'Tasks'),
        ('core:employee_projects', 'Projects'),
        ('core:employee_timesheet', 'Timesheet'),
        ('core:employee_goals', 'Goals'),
        ('core:employee_leave', 'Leave'),
        ('core:employee_analytics', 'Analytics'),
        ('core:employee_notifications', 'Notifications'),
        ('core:employee_team_directory', 'Team Directory'),
        ('core:employee_calendar', 'Calendar'),
        ('core:employee_kanban_board', 'Kanban Board'),
        ('core:employee_gamification', 'Gamification'),
        ('core:employee_documents', 'Documents'),
        ('core:employee_productivity', 'Productivity'),
        ('core:employee_settings', 'Settings'),
        ('core:employee_search', 'Search'),
        ('core:employee_shortcuts', 'Shortcuts'),
        ('core:employee_onboarding', 'Onboarding'),
    ]
    
    results = []
    
    for url_name, page_name in employee_urls:
        try:
            # Test URL resolution
            url = reverse(url_name)
            print(f"✅ {page_name}: {url}")
            results.append((page_name, "PASS", f"URL resolved: {url}"))
        except Exception as e:
            print(f"❌ {page_name}: {e}")
            results.append((page_name, "FAIL", str(e)))
    
    return results

def test_system_check():
    """Test Django system check"""
    print("\n🔍 Running Django System Check...")
    print("="*50)
    
    try:
        from django.core.management import execute_from_command_line
        from django.core.management.commands.check import Command as CheckCommand
        
        # Run system check
        check_command = CheckCommand()
        check_command.handle()
        
        print("✅ Django system check passed")
        return [("System Check", "PASS", "No issues found")]
        
    except Exception as e:
        print(f"❌ Django system check failed: {e}")
        return [("System Check", "FAIL", str(e))]

def test_models():
    """Test model imports"""
    print("\n📊 Testing Model Imports...")
    print("="*50)
    
    models_to_test = [
        ('core.models', 'Company'),
        ('core.models', 'Employee'),
        ('core.models', 'Project'),
        ('core.models', 'Task'),
        ('core.models', 'Timesheet'),
        ('core.models', 'PerformanceGoal'),
        ('core.models', 'LeaveRequest'),
        ('core.models', 'Announcement'),
        ('core.models', 'Notification'),
    ]
    
    results = []
    
    for module_name, model_name in models_to_test:
        try:
            module = __import__(module_name, fromlist=[model_name])
            model = getattr(module, model_name)
            print(f"✅ {model_name} model imported successfully")
            results.append((f"{model_name} Model", "PASS", "Import successful"))
        except Exception as e:
            print(f"❌ {model_name} model import failed: {e}")
            results.append((f"{model_name} Model", "FAIL", str(e)))
    
    return results

def generate_report(all_results):
    """Generate test report"""
    print("\n📊 TEST REPORT")
    print("="*60)
    
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r[1] == "PASS"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print("="*60)
    
    print("\n📋 DETAILED RESULTS:")
    print("-"*60)
    for test_name, result, details in all_results:
        status_icon = "✅" if result == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {result}")
        if details and len(details) > 0:
            print(f"   Details: {details}")
    
    print("\n" + "="*60)
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! Employee dashboard is ready!")
    else:
        print(f"⚠️  {failed_tests} tests failed. Please review issues.")
    
    return passed_tests == total_tests

def main():
    """Main test function"""
    print("🧪 Employee Dashboard Simple Test Suite")
    print("="*60)
    
    all_results = []
    
    # Run tests
    all_results.extend(test_employee_urls())
    all_results.extend(test_system_check())
    all_results.extend(test_models())
    
    # Generate report
    success = generate_report(all_results)
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        return 0
    else:
        print("\n❌ Test suite completed with failures!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
