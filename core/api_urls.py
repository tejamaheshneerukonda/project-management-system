from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Project Management API
    path('projects/create/', api_views.create_project, name='create_project'),
    path('projects/<int:project_id>/', api_views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/tasks/', api_views.project_tasks, name='project_tasks'),
    
    # Task Management API
    path('tasks/create/', api_views.create_task, name='create_task'),
    path('task/<int:task_id>/', api_views.get_task, name='get_task'),
    path('update_task/<int:task_id>/', api_views.update_task, name='update_task'),
    path('delete_task/<int:task_id>/', api_views.delete_task, name='delete_task'),
    
    # Notifications API
    path('notifications/unread/', api_views.unread_notifications, name='unread_notifications'),
    path('notifications/<int:notification_id>/mark-read/', api_views.mark_notification_read, name='mark_notification_read'),
    
    # Announcements API
    path('announcements/create/', api_views.create_announcement, name='create_announcement'),
    path('announcements/', api_views.list_announcements, name='list_announcements'),
    
    # Analytics API
    path('analytics/dashboard/', api_views.dashboard_analytics, name='dashboard_analytics'),
    path('analytics/performance/', api_views.performance_analytics, name='performance_analytics'),
    
    # Employee Management API
    path('employees/create/', api_views.create_employee, name='create_employee'),
    path('employees/search/', api_views.search_employees, name='search_employees'),
    path('employees/bulk-operations/', api_views.bulk_employee_operations, name='bulk_employee_operations'),
    path('employees/<int:employee_id>/', api_views.get_employee, name='get_employee'),
    path('employees/<int:employee_id>/update/', api_views.update_employee, name='update_employee'),
    path('employees/<int:employee_id>/photo/', api_views.upload_employee_photo, name='upload_employee_photo'),
    path('employees/<int:employee_id>/photo/delete/', api_views.delete_employee_photo, name='delete_employee_photo'),
    path('employees/<int:employee_id>/performance/', api_views.employee_performance, name='employee_performance'),
    path('employees/<int:employee_id>/delete/', api_views.delete_employee, name='delete_employee'),
    
    # Company Settings API
    path('settings/update/', api_views.update_company_settings, name='update_company_settings'),
    # Payment Method URLs
    path('payment-methods/add/', api_views.add_payment_method, name='add_payment_method'),
    path('payment-methods/update/', api_views.update_payment_method, name='update_payment_method'),
    path('payment-methods/remove/', api_views.remove_payment_method, name='remove_payment_method'),
    path('payment-methods/get/', api_views.get_payment_methods, name='get_payment_methods'),
    
    # Workflow API
    path('workflows/create/', api_views.create_workflow, name='create_workflow'),
    path('workflows/<int:workflow_id>/execute/', api_views.execute_workflow, name='execute_workflow'),
    
    # Additional API endpoints for templates
    path('employees/verify/', api_views.verify_employee, name='verify_employee'),
    path('departments/create/', api_views.create_department, name='create_department'),
    path('departments/<int:department_id>/', api_views.get_department, name='get_department'),
    path('departments/<int:department_id>/update/', api_views.update_department, name='update_department'),
    path('departments/<int:department_id>/delete/', api_views.delete_department, name='delete_department'),
    path('performance/create/', api_views.create_performance, name='create_performance'),
    path('performance/<int:performance_id>/', api_views.get_performance, name='get_performance'),
    path('performance/<int:performance_id>/update/', api_views.update_performance, name='update_performance'),
    path('performance/<int:performance_id>/delete/', api_views.delete_performance, name='delete_performance'),
    path('messages/send/', api_views.send_message, name='send_message'),
    path('chat/send/', api_views.send_chat_message, name='send_chat_message'),
    path('chat/clear/', api_views.clear_chat, name='clear_chat'),
    path('files/upload/', api_views.upload_file, name='upload_file'),
    path('tickets/create/', api_views.create_ticket, name='create_ticket'),
    path('customers/create/', api_views.create_customer, name='create_customer'),
    path('attendance/create/', api_views.create_attendance, name='create_attendance'),
    path('benefits/create/', api_views.create_benefit, name='create_benefit'),
    path('leave/create/', api_views.create_leave, name='create_leave'),
    path('timesheets/create/', api_views.create_timesheet, name='create_timesheet'),
    path('timesheets/<int:timesheet_id>/update/', api_views.update_timesheet, name='update_timesheet'),
    path('assets/create/', api_views.create_asset, name='create_asset'),
    path('security-settings/create/', api_views.create_security_setting, name='create_security_setting'),
    path('integrations/create/', api_views.create_integration, name='create_integration'),
    path('endpoints/create/', api_views.create_endpoint, name='create_endpoint'),
    path('company-profile/update/', api_views.update_company_profile, name='update_company_profile'),
    path('logo/upload/', api_views.upload_logo, name='upload_logo'),
    
    # Performance Reports API
    path('performance/generate-report/', api_views.generate_performance_report, name='generate_performance_report'),
    path('performance/export-reviews/', api_views.export_performance_reviews, name='export_performance_reviews'),
    path('performance/export-goals/', api_views.export_performance_goals, name='export_performance_goals'),
    path('performance/export-feedback/', api_views.export_performance_feedback, name='export_performance_feedback'),
    path('performance/export-reports/', api_views.export_performance_reports, name='export_performance_reports'),
    path('performance/download-report/', api_views.download_performance_report, name='download_performance_report'),
    
    # Attendance Reports API
    path('attendance/generate-report/', api_views.generate_attendance_report, name='generate_attendance_report'),
    path('attendance/export/', api_views.export_attendance_data, name='export_attendance_data'),
    path('attendance/download-report/', api_views.download_attendance_report, name='download_attendance_report'),
    
    # Timesheet Management API
    path('timesheet/export/', api_views.export_timesheet_data, name='export_timesheet_data'),
    
    # Shift Management API
    path('shift/export/', api_views.export_shift_data, name='export_shift_data'),
]
