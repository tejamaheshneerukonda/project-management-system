#!/usr/bin/env python3
"""
Employee Dashboard Link Diagnostic Script
Checks which templates exist and identifies missing ones
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

def check_templates():
    """Check which employee dashboard templates exist"""
    print("🔍 Checking Employee Dashboard Templates...")
    print("="*60)
    
    templates_dir = "templates/core"
    employee_templates = [
        "employee_dashboard.html",
        "employee_tasks.html", 
        "employee_projects.html",
        "employee_timesheet.html",
        "employee_goals.html",
        "employee_leave.html",
        "employee_analytics.html",
        "employee_notifications.html",
        "employee_team_directory.html",
        "employee_calendar.html",
        "employee_kanban.html",
        "employee_gamification.html",
        "employee_documents.html",
        "employee_productivity.html",
        "employee_settings.html",
        "employee_search.html",
        "employee_shortcuts.html",
        "employee_onboarding.html"
    ]
    
    missing_templates = []
    existing_templates = []
    
    for template in employee_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            existing_templates.append(template)
            print(f"✅ {template}")
        else:
            missing_templates.append(template)
            print(f"❌ {template} - MISSING")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"Total Templates: {len(employee_templates)}")
    print(f"Existing: {len(existing_templates)}")
    print(f"Missing: {len(missing_templates)}")
    
    if missing_templates:
        print(f"\n❌ MISSING TEMPLATES:")
        for template in missing_templates:
            print(f"   - {template}")
    else:
        print(f"\n🎉 All templates exist!")
    
    return missing_templates

def check_views():
    """Check which employee dashboard views exist"""
    print("\n🔍 Checking Employee Dashboard Views...")
    print("="*60)
    
    from core import views
    
    employee_views = [
        "employee_dashboard",
        "employee_tasks", 
        "employee_projects",
        "employee_timesheet",
        "employee_goals",
        "employee_leave",
        "employee_analytics",
        "employee_notifications",
        "employee_team_directory",
        "employee_calendar",
        "employee_kanban_board",
        "employee_gamification",
        "employee_documents",
        "employee_productivity",
        "employee_settings",
        "employee_search",
        "employee_shortcuts",
        "employee_onboarding"
    ]
    
    missing_views = []
    existing_views = []
    
    for view_name in employee_views:
        if hasattr(views, view_name):
            existing_views.append(view_name)
            print(f"✅ {view_name}")
        else:
            missing_views.append(view_name)
            print(f"❌ {view_name} - MISSING")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"Total Views: {len(employee_views)}")
    print(f"Existing: {len(existing_views)}")
    print(f"Missing: {len(missing_views)}")
    
    if missing_views:
        print(f"\n❌ MISSING VIEWS:")
        for view in missing_views:
            print(f"   - {view}")
    else:
        print(f"\n🎉 All views exist!")
    
    return missing_views

def check_urls():
    """Check which employee dashboard URLs exist"""
    print("\n🔍 Checking Employee Dashboard URLs...")
    print("="*60)
    
    from django.urls import reverse
    
    employee_urls = [
        "core:employee_dashboard",
        "core:employee_tasks", 
        "core:employee_projects",
        "core:employee_timesheet",
        "core:employee_goals",
        "core:employee_leave",
        "core:employee_analytics",
        "core:employee_notifications",
        "core:employee_team_directory",
        "core:employee_calendar",
        "core:employee_kanban_board",
        "core:employee_gamification",
        "core:employee_documents",
        "core:employee_productivity",
        "core:employee_settings",
        "core:employee_search",
        "core:employee_shortcuts",
        "core:employee_onboarding"
    ]
    
    missing_urls = []
    existing_urls = []
    
    for url_name in employee_urls:
        try:
            url = reverse(url_name)
            existing_urls.append(url_name)
            print(f"✅ {url_name}: {url}")
        except Exception as e:
            missing_urls.append(url_name)
            print(f"❌ {url_name} - MISSING: {e}")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY:")
    print(f"Total URLs: {len(employee_urls)}")
    print(f"Existing: {len(existing_urls)}")
    print(f"Missing: {len(missing_urls)}")
    
    if missing_urls:
        print(f"\n❌ MISSING URLS:")
        for url in missing_urls:
            print(f"   - {url}")
    else:
        print(f"\n🎉 All URLs exist!")
    
    return missing_urls

def main():
    """Main diagnostic function"""
    print("🔧 Employee Dashboard Link Diagnostic")
    print("="*60)
    
    missing_templates = check_templates()
    missing_views = check_views()
    missing_urls = check_urls()
    
    print("\n" + "="*60)
    print("🎯 FINAL DIAGNOSIS")
    print("="*60)
    
    if not missing_templates and not missing_views and not missing_urls:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("All templates, views, and URLs are working correctly.")
        print("If links are still not working, the issue might be:")
        print("1. Authentication/authorization issues")
        print("2. Template rendering errors")
        print("3. JavaScript errors")
        print("4. Server configuration issues")
    else:
        print("❌ ISSUES FOUND:")
        if missing_templates:
            print(f"   - {len(missing_templates)} missing templates")
        if missing_views:
            print(f"   - {len(missing_views)} missing views")
        if missing_urls:
            print(f"   - {len(missing_urls)} missing URLs")
    
    return len(missing_templates) + len(missing_views) + len(missing_urls) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
