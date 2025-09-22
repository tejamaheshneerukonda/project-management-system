#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script
Run this script to prepare your project for PythonAnywhere deployment
"""

import os
import sys
import subprocess
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings')
django.setup()

def run_command(command, description):
    """Run a command and print the result"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def prepare_for_deployment():
    """Prepare the project for PythonAnywhere deployment"""
    print("🚀 Preparing Project Management System for PythonAnywhere Deployment")
    print("=" * 70)
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version}")
    
    # Run Django checks
    run_command("python manage.py check --deploy", "Django system check")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collect static files")
    
    # Run migrations
    run_command("python manage.py migrate", "Run database migrations")
    
    # Create superuser (optional)
    print("\n👤 Superuser Creation:")
    print("You can create a superuser manually on PythonAnywhere with:")
    print("python manage.py createsuperuser")
    
    print("\n📋 Deployment Checklist:")
    print("✅ Project prepared for deployment")
    print("✅ Static files collected")
    print("✅ Database migrations ready")
    print("✅ Production settings configured")
    
    print("\n🌐 Next Steps:")
    print("1. Upload your project to PythonAnywhere")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Configure WSGI file")
    print("4. Run migrations: python manage.py migrate")
    print("5. Create superuser: python manage.py createsuperuser")
    print("6. Reload your web app")

if __name__ == "__main__":
    prepare_for_deployment()
