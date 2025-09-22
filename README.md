# ProjectManager Pro

A professional, offline project management system built with Django. Perfect for companies that value data privacy and security.

## Features

- **100% Offline**: Your data never leaves your server
- **Enterprise Ready**: Scalable architecture for teams of any size
- **Modern UI**: Beautiful, responsive interface built with Bootstrap 5
- **User Authentication**: Secure login and registration system
- **Project Management**: Complete project lifecycle management
- **Team Collaboration**: Multi-user support with role-based permissions
- **Analytics & Reporting**: Comprehensive project insights
- **One-Time Purchase**: No monthly subscriptions

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   # If you have the project files, navigate to the project directory
   cd "E:\project management system"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

9. **Open your browser and visit**
   ```
   http://127.0.0.1:8000
   ```

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

## Project Structure

```
project management system/
├── core/                    # Main application
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   └── urls.py            # URL patterns
├── project_manager/        # Django project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
├── templates/             # Global templates
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Features Overview

### Home Page
- Professional landing page with modern design
- Feature highlights and benefits
- Call-to-action sections
- Responsive design for all devices

### Authentication
- Secure user registration and login
- Password validation and security
- Session management
- User profile management

### Navigation
- Fixed navigation bar with responsive design
- User authentication status display
- Dropdown menus for user actions
- Mobile-friendly navigation

## Customization

### Styling
- Modify `static/css/style.css` for custom styling
- Bootstrap 5 framework for responsive design
- Font Awesome icons for enhanced UI
- Custom CSS variables for easy theming

### Templates
- Base template in `templates/base.html`
- Page-specific templates in `templates/core/`
- Django template inheritance for consistency

## Production Deployment

For production deployment:

1. **Update settings.py**
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Set up proper database (PostgreSQL recommended)
   - Configure static file serving

2. **Security**
   - Generate a new `SECRET_KEY`
   - Set up HTTPS
   - Configure proper file permissions
   - Set up regular backups

3. **Performance**
   - Use a production WSGI server (Gunicorn)
   - Set up reverse proxy (Nginx)
   - Configure caching
   - Optimize static file serving

## Support

For technical support or questions:
- Email: support@projectmanagerpro.com
- Documentation: Available in the admin panel
- Updates: Regular updates provided

## License

This software is proprietary. All rights reserved.

## Version

Current Version: 1.0.0
Last Updated: January 2025
