# PythonAnywhere Deployment Guide

This guide will help you deploy your Django Project Management System to PythonAnywhere's free tier.

## 🚀 Prerequisites

- PythonAnywhere account (free tier)
- Your project code ready for deployment
- Basic understanding of Django deployment

## 📋 Step-by-Step Deployment

### 1. Prepare Your Project Locally

```bash
# Run the deployment preparation script
python deploy_to_pythonanywhere.py

# Or manually:
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py check --deploy
```

### 2. Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account
3. Verify your email address

### 3. Upload Your Project

**Option A: Using Git (Recommended)**
```bash
# On PythonAnywhere console
git clone https://github.com/tejamaheshneerukonda/project-management-system.git
cd project-management-system
```

**Option B: Using File Upload**
1. Zip your project folder
2. Upload via PythonAnywhere Files tab
3. Extract the zip file

### 4. Install Dependencies

```bash
# Install Python packages (PythonAnywhere compatible)
pip3.10 install --user -r requirements-pythonanywhere.txt

# Or for minimal installation (no WebSocket features):
pip3.10 install --user -r requirements-pythonanywhere-minimal.txt
```

### 5. Configure Database

```bash
# Run migrations (use PythonAnywhere-specific manage.py)
python3.10 manage_pythonanywhere.py migrate

# Create superuser
python3.10 manage_pythonanywhere.py createsuperuser

# Collect static files
python3.10 manage_pythonanywhere.py collectstatic --noinput
```

### 6. Configure Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual Configuration**
4. Select **Python 3.10** (or latest available)

### 7. Configure WSGI File

1. In the **Web** tab, find **WSGI configuration file**
2. Replace the content with:

```python
import os
import sys

# Add your project directory to the Python path
path = '/home/YOUR_USERNAME/project-management-system'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings_pythonanywhere')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace `YOUR_USERNAME` with your PythonAnywhere username**

### 8. Configure Static Files

1. In the **Web** tab, find **Static files** section
2. Add static file mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/YOUR_USERNAME/project-management-system/staticfiles`

### 9. Configure Media Files (Optional)

1. Add media file mapping:
   - **URL**: `/media/`
   - **Directory**: `/home/YOUR_USERNAME/project-management-system/media`

### 10. Reload Web App

1. Click **Reload** button in the Web tab
2. Your app should now be live at `YOUR_USERNAME.pythonanywhere.com`

## 🔧 Configuration Files

### WSGI Configuration (`pythonanywhere_wsgi.py`)
```python
import os
import sys

path = '/home/YOUR_USERNAME/project-management-system'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings_production')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Production Settings (`settings_production.py`)
- Debug mode disabled
- Allowed hosts configured
- Static files configured
- Security settings enabled
- Database configured for SQLite

## 🚨 Free Tier Limitations

### Resource Limits
- **CPU seconds**: 100,000 per month
- **Disk space**: 512 MB
- **Always-on tasks**: 1 (for web app)
- **Custom domains**: Not available
- **HTTPS**: Not available

### Recommended Optimizations
1. **Disable WebSocket features** (comment out channels in INSTALLED_APPS)
2. **Use SQLite database** (included in free tier)
3. **Minimize static files** (compress images, CSS, JS)
4. **Use minimal requirements** (`requirements-minimal.txt`)

## 🐛 Troubleshooting

### Common Issues

**1. Dependency Conflicts**
```bash
# If you get Django version conflicts, use PythonAnywhere-specific requirements:
pip3.10 install --user -r requirements-pythonanywhere-minimal.txt

# This resolves conflicts between Django 5.2.6 and django-celery-beat
```

**2. ModuleNotFoundError: No module named 'channels'**
```bash
# Use the PythonAnywhere-specific manage.py file:
python3.10 manage_pythonanywhere.py migrate
python3.10 manage_pythonanywhere.py createsuperuser

# This uses settings_pythonanywhere.py which removes channels dependency
```

**3. Import Errors**
```bash
# Check Python path in WSGI file
# Ensure all dependencies are installed
pip3.10 install --user -r requirements-pythonanywhere.txt
```

**2. Static Files Not Loading**
```bash
# Collect static files
python3.10 manage.py collectstatic --noinput

# Check static file mapping in Web tab
```

**3. Database Errors**
```bash
# Run migrations
python3.10 manage.py migrate

# Check database permissions
```

**4. Memory Issues**
- Use `requirements-minimal.txt` instead of full requirements
- Disable unused features in settings
- Optimize static files

### Debug Mode
```python
# Temporarily enable debug mode for troubleshooting
DEBUG = True
ALLOWED_HOSTS = ['*']
```

## 📊 Monitoring

### Check Logs
1. Go to **Tasks** tab
2. Click **Errors** to view error logs
3. Check **Web** tab for web app logs

### Performance Monitoring
- Monitor CPU usage in **Account** tab
- Check disk usage regularly
- Optimize queries to reduce CPU usage

## 🔄 Updates

### Updating Your App
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip3.10 install --user -r requirements.txt

# Run migrations
python3.10 manage.py migrate

# Collect static files
python3.10 manage.py collectstatic --noinput

# Reload web app
```

## 🎯 Best Practices

1. **Use Git** for version control
2. **Test locally** before deploying
3. **Monitor resource usage**
4. **Keep dependencies minimal**
5. **Regular backups** of database
6. **Optimize static files**

## 📞 Support

- PythonAnywhere Documentation: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- Django Deployment Guide: [docs.djangoproject.com](https://docs.djangoproject.com/en/stable/howto/deployment/)
- Project Issues: [GitHub Issues](https://github.com/tejamaheshneerukonda/project-management-system/issues)

---

**Your Django Project Management System should now be live on PythonAnywhere!** 🚀
