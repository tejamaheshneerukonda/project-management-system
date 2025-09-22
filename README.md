# Project Management System

A comprehensive Django-based project management system with real-time features, employee management, and leave tracking capabilities.

## 🚀 Features

### Core Functionality
- **Company Management**: Multi-company support with admin dashboards
- **Employee Management**: Complete employee lifecycle management
- **Project Management**: Project creation, task assignment, and tracking
- **Leave Management**: Real-time leave request and approval system
- **Time Tracking**: Employee timesheet management
- **Performance Goals**: Goal setting and tracking system

### Real-Time Features
- **Live Updates**: WebSocket-powered real-time notifications
- **Leave Balance**: Automatic balance updates when requests are approved
- **Cross-Browser Sync**: Updates across multiple browser sessions
- **Instant Notifications**: Toast notifications for all actions

### Advanced Features
- **Document Management**: File upload and sharing system
- **Chat System**: Employee-to-employee communication
- **Analytics Dashboard**: Performance insights and reporting
- **Mobile Responsive**: Works seamlessly on all devices

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6, Django Channels
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Real-time**: WebSocket (Django Channels)
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: Django's built-in authentication system

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tejamaheshneerukonda/project-management-system.git
   cd project-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Login with your superuser credentials

## 🎯 Usage

### Company Admin Dashboard
- Manage employees and projects
- Approve/reject leave requests
- View analytics and reports
- Handle document management

### Employee Dashboard
- Submit leave requests
- Track time and tasks
- View performance goals
- Access company announcements

### Real-Time Features
- Leave requests update instantly across all browsers
- Balance calculations happen automatically
- Notifications appear without page refresh

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

### WebSocket Configuration
The system uses Django Channels with InMemoryChannelLayer for development and RedisChannelLayer for production.

## 📁 Project Structure

```
project-management-system/
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── api_views.py        # API endpoints
│   ├── consumers.py        # WebSocket consumers
│   └── urls.py             # URL patterns
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── project_manager/        # Django project settings
└── requirements.txt        # Python dependencies
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Check system configuration:
```bash
python manage.py check
```

## 🚀 Deployment

### Production Settings
1. Set `DEBUG=False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up Redis for WebSocket channels
4. Configure static file serving
5. Set up SSL certificates

### Docker Deployment
```bash
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Teja Mahesh Neerukonda**
- GitHub: [@tejamaheshneerukonda](https://github.com/tejamaheshneerukonda)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive UI components
- Chart.js for data visualization capabilities

## 📞 Support

If you have any questions or need help, please open an issue on GitHub or contact the author.

---

**Made with ❤️ using Django and modern web technologies**