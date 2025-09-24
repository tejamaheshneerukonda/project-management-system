from django.urls import path, include
from . import views
from . import api_views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('terms/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('debug/company-data/', views.debug_company_data, name='debug_company_data'),
    path('debug/license-status/', views.debug_license_status, name='debug_license_status'),
    path('test/activation-key/', views.test_activation_key, name='test_activation_key'),
    path('test/payment-flow/', views.test_payment_flow, name='test_payment_flow'),
    path('payment-test/', views.payment_test, name='payment_test'),
    path('payment/', views.payment_page, name='payment'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('registration-selection/', views.registration_selection, name='registration_selection'),
    path('company-admin-register/', views.company_admin_registration, name='company_admin_registration'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Owner URLs
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/profile-settings/', views.owner_profile_settings, name='owner_profile_settings'),
    path('owner/register-company/', views.register_company, name='register_company'),
    path('owner/company/<int:company_id>/', views.company_details, name='company_details'),
    path('owner/company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('owner/company/<int:company_id>/toggle/', views.toggle_company_status, name='toggle_company_status'),
    path('owner/company/<int:company_id>/delete/', views.delete_company, name='delete_company'),
    
    # Subscription Management URLs
    path('owner/subscriptions/plans/', views.subscription_plans, name='subscription_plans'),
    path('owner/subscriptions/plans/create/', views.create_subscription_plan, name='create_subscription_plan'),
    path('owner/subscriptions/plans/<int:plan_id>/edit/', views.edit_subscription_plan, name='edit_subscription_plan'),
    path('owner/subscriptions/companies/', views.company_subscriptions, name='company_subscriptions'),
    path('owner/subscriptions/assign/<int:company_id>/', views.assign_subscription, name='assign_subscription'),
    path('owner/subscriptions/analytics/', views.subscription_analytics, name='subscription_analytics'),
    path('owner/export-companies/', views.export_companies, name='export_companies'),
    
    # Owner Management Pages
    path('owner/companies/bulk-delete/', views.bulk_delete_companies, name='bulk_delete_companies'),
    path('owner/companies/', views.all_companies, name='all_companies'),
    path('owner/company-analytics/', views.company_analytics, name='company_analytics'),
    path('owner/user-stats/', views.user_stats, name='user_stats'),
    path('owner/active-users/', views.active_users, name='active_users'),
    path('owner/user-activity/', views.user_activity, name='user_activity'),
    path('owner/user-reports/', views.user_reports, name='user_reports'),
    path('owner/system-stats/', views.system_stats, name='system_stats'),
    path('owner/revenue-reports/', views.revenue_reports, name='revenue_reports'),
    path('owner/growth-analytics/', views.growth_analytics, name='growth_analytics'),
    path('owner/custom-reports/', views.custom_reports, name='owner_custom_reports'),
    path('owner/system-settings/', views.system_settings, name='owner_system_settings'),
    path('owner/security-settings/', views.security_settings, name='owner_security_settings'),
    path('owner/backup-restore/', views.backup_restore, name='backup_restore'),
    path('owner/system-logs/', views.system_logs, name='system_logs'),
    path('owner/maintenance/', views.maintenance, name='maintenance'),
    path('owner/audit-logs/', views.audit_logs, name='audit_logs'),
    
    # Company Admin URLs
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/license-activation/', views.license_activation, name='license_activation'),
    path('company/import-employees/', views.import_employees, name='import_employees'),
    
    # Team Management URLs
    path('company/employee-directory/', views.employee_directory, name='employee_directory'),
    path('company/employee-profile/<int:employee_id>/', views.employee_profile, name='employee_profile'),
    path('company/department-management/', views.department_management, name='department_management'),
    path('company/team-performance/', views.team_performance, name='team_performance'),
    path('company/employee-onboarding/', views.company_employee_onboarding, name='company_employee_onboarding'),
    
    # Performance Management URLs
    path('company/performance-dashboard/', views.performance_dashboard, name='performance_dashboard'),
    path('company/performance-reviews/', views.performance_reviews, name='performance_reviews'),
    path('company/performance-goals/', views.performance_goals, name='performance_goals'),
    path('company/performance-feedback/', views.performance_feedback, name='performance_feedback'),
    path('company/performance-reports/', views.performance_reports, name='performance_reports'),
    path('company/employee-performance/<int:employee_id>/', views.employee_performance_detail, name='employee_performance_detail'),
    
    # Attendance Management URLs
    path('company/attendance-dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('company/attendance-records/', views.attendance_records, name='attendance_records'),
    path('company/leave-management/', views.leave_management, name='leave_management'),
    path('company/leave-management/<int:request_id>/details/', views.leave_request_details, name='leave_request_details'),
    path('company/leave-management/<int:request_id>/edit/', views.edit_leave_request, name='edit_leave_request'),
    path('company/timesheet-management/', views.timesheet_management, name='timesheet_management'),
    path('company/shift-management/', views.shift_management, name='shift_management'),
    path('company/employee-attendance/<int:employee_id>/', views.employee_attendance_detail, name='employee_attendance_detail'),
    
    # Notification Management URLs
    path('company/notification-center/', views.notification_center, name='notification_center'),
    path('company/notification-templates/', views.notification_templates, name='notification_templates'),
    path('company/notification-preferences/', views.notification_preferences, name='notification_preferences'),
    path('company/notification-digests/', views.notification_digests, name='notification_digests'),
    path('company/create-notification/', views.create_notification, name='create_notification'),
    path('company/notification-analytics/', views.notification_analytics, name='notification_analytics'),
    
    # Onboarding Management URLs
    path('company/onboarding-dashboard/', views.onboarding_dashboard, name='onboarding_dashboard'),
    path('company/onboarding-workflows/', views.onboarding_workflows, name='onboarding_workflows'),
    path('company/onboarding-assignments/', views.onboarding_assignments, name='onboarding_assignments'),
    path('company/onboarding-tasks/', views.onboarding_tasks, name='onboarding_tasks'),
    path('company/onboarding-documents/', views.onboarding_documents, name='onboarding_documents'),
    path('company/onboarding-assign-workflow/', views.onboarding_assign_workflow, name='onboarding_assign_workflow'),
    path('company/employee-onboarding/<int:employee_id>/', views.employee_onboarding_detail, name='employee_onboarding_detail'),
    
    # Document Management URLs
    path('company/document-library/', views.document_library, name='document_library'),
    path('company/document-categories/', views.document_categories, name='document_categories'),
    path('company/document-templates/', views.document_templates, name='document_templates'),
    path('company/document-sharing/', views.document_sharing, name='document_sharing'),
    path('company/document-analytics/', views.document_analytics, name='document_analytics'),
    path('company/upload-document/', views.upload_document, name='upload_document'),
    path('company/document-detail/<int:document_id>/', views.document_detail, name='document_detail'),
    
    # Project Management URLs
    path('company/project-list/', views.project_list, name='project_list'),
    path('company/task-management/', views.task_management, name='task_management'),
    path('company/project-analytics/', views.project_analytics, name='project_analytics'),
    path('company/resource-planning/', views.resource_planning, name='resource_planning'),
    path('company/project-templates/', views.project_templates, name='project_templates'),
    
    # Communication & Collaboration URLs
    path('company/internal-messaging/', views.internal_messaging, name='internal_messaging'),
    path('company/team-chat/', views.team_chat, name='team_chat'),
    path('company/meeting-scheduler/', views.meeting_scheduler, name='meeting_scheduler'),
    path('company/announcements/', views.announcements, name='announcements'),
    path('company/video-meetings/', views.video_meetings, name='video_meetings'),
    
    # Document Management URLs
    path('company/file-sharing/', views.file_sharing, name='file_sharing'),
    path('company/version-control/', views.version_control, name='version_control'),
    path('company/archive-management/', views.archive_management, name='archive_management'),
    
    # HR & Payroll URLs
    path('company/attendance-tracking/', views.attendance_tracking, name='attendance_tracking'),
    path('company/payroll-processing/', views.payroll_processing, name='payroll_processing'),
    path('company/employee-benefits/', views.employee_benefits, name='employee_benefits'),
    
    # Customer Management URLs
    path('company/crm-dashboard/', views.crm_dashboard, name='crm_dashboard'),
    path('company/support-tickets/', views.support_tickets, name='support_tickets'),
    path('company/client-portal/', views.client_portal, name='client_portal'),
    path('company/customer-analytics/', views.customer_analytics, name='customer_analytics'),
    path('company/contact-management/', views.contact_management, name='contact_management'),
    
    # Inventory & Assets URLs
    path('company/asset-tracking/', views.asset_tracking, name='asset_tracking'),
    path('company/procurement-management/', views.procurement_management, name='procurement_management'),
    path('company/maintenance-scheduling/', views.maintenance_scheduling, name='maintenance_scheduling'),
    path('company/inventory-reports/', views.inventory_reports, name='inventory_reports'),
    path('company/asset-analytics/', views.asset_analytics, name='asset_analytics'),
    
    # Security & Compliance URLs
    path('company/audit-logs/', views.audit_logs, name='audit_logs'),
    path('company/export-audit-logs/', views.export_audit_logs, name='export_audit_logs'),
    path('company/audit-log-details/<int:log_id>/', views.audit_log_details, name='audit_log_details'),
    path('company/data-protection/', views.data_protection, name='data_protection'),
    path('company/compliance-reports/', views.compliance_reports, name='compliance_reports'),
    path('company/security-settings/', views.security_settings, name='company_security_settings'),
    path('company/access-control/', views.access_control, name='access_control'),
    
    # Integrations & API URLs
    path('company/third-party-integrations/', views.third_party_integrations, name='third_party_integrations'),
    path('company/api-management/', views.api_management, name='api_management'),
    path('company/webhook-configuration/', views.webhook_configuration, name='webhook_configuration'),
    path('company/integration-analytics/', views.integration_analytics, name='integration_analytics'),
    
    # Company Settings URLs
    path('company/company-profile/', views.company_profile, name='company_profile'),
    path('company/billing-subscriptions/', views.billing_subscriptions, name='billing_subscriptions'),
    path('company/add-payment-method/', views.add_payment_method_page, name='add_payment_method_page'),
    path('company/system-settings/', views.system_settings, name='company_system_settings'),
    path('company/user-preferences/', views.user_preferences, name='user_preferences'),
    path('company/company-policies/', views.company_policies, name='company_policies'),
    
    # Reports & Analytics URLs
    path('company/dashboard-analytics/', views.dashboard_analytics, name='dashboard_analytics'),
    path('company/custom-reports/', views.custom_reports, name='company_custom_reports'),
    path('company/data-export/', views.data_export, name='data_export'),
    path('company/performance-metrics/', views.performance_metrics, name='performance_metrics'),
    path('company/business-intelligence/', views.business_intelligence, name='business_intelligence'),
    
    # Employee URLs
    path('employee/verification/', views.employee_verification, name='employee_verification'),
    path('employee/verification/<str:company_slug>/', views.employee_verification_by_slug, name='employee_verification_by_slug'),
    path('employee/registration/', views.employee_registration, name='employee_registration'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/tasks/', views.employee_tasks, name='employee_tasks'),
    path('employee/projects/', views.employee_projects, name='employee_projects'),
    path('employee/timesheet/', views.employee_timesheet, name='employee_timesheet'),
    path('employee/timesheet/<int:timesheet_id>/edit/', views.employee_edit_timesheet, name='employee_edit_timesheet'),
    path('employee/goals/', views.employee_goals, name='employee_goals'),
    path('employee/leave/', views.employee_leave, name='employee_leave'),
    path('employee/leave/<int:request_id>/details/', views.employee_leave_details, name='employee_leave_details'),
    path('employee/leave/<int:request_id>/edit/', views.employee_edit_leave_request, name='employee_edit_leave_request'),
    path('employee/analytics/', views.employee_analytics, name='employee_analytics'),
    path('employee/notifications/', views.employee_notifications, name='employee_notifications'),
    path('employee/team/', views.employee_team_directory, name='employee_team_directory'),
    path('employee/calendar/', views.employee_calendar, name='employee_calendar'),
    path('employee/kanban/', views.employee_kanban_board, name='employee_kanban_board'),
    path('employee/gamification/', views.employee_gamification, name='employee_gamification'),
    path('employee/documents/', views.employee_documents, name='employee_documents'),
    path('employee/productivity/', views.employee_productivity, name='employee_productivity'),
    path('employee/settings/', views.employee_settings, name='employee_settings'),
    path('employee/search/', views.employee_search, name='employee_search'),
    path('employee/shortcuts/', views.employee_shortcuts, name='employee_shortcuts'),
    path('employee/onboarding/', views.employee_onboarding, name='employee_onboarding'),
    
    # General URLs
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('api/stats/', views.api_stats, name='api_stats'),
    
    # Dashboard Widget APIs
    path('api/dashboard/notifications/', views.dashboard_notifications, name='dashboard_notifications'),
    path('api/dashboard/system-performance/', views.dashboard_system_performance, name='dashboard_system_performance'),
    path('api/dashboard/subscription-overview/', views.dashboard_subscription_overview, name='dashboard_subscription_overview'),
    path('api/dashboard/api-usage/', views.dashboard_api_usage, name='dashboard_api_usage'),
    
    # Bulk Operations APIs
    path('api/bulk-operations/', views.bulk_company_operations, name='bulk_company_operations'),
    path('api/export/companies/filtered/', views.export_companies_filtered, name='export_companies_filtered'),
    path('api/export/companies/selected/', views.export_selected_companies, name='export_selected_companies'),
    
    # Analytics APIs
    path('api/analytics/growth-data/', views.analytics_growth_data, name='analytics_growth_data'),
    path('api/analytics/revenue-data/', views.analytics_revenue_data, name='analytics_revenue_data'),
    path('api/analytics/predictive-data/', views.analytics_predictive_data, name='analytics_predictive_data'),
    path('api/analytics/comparative-data/', views.analytics_comparative_data, name='analytics_comparative_data'),
    
    # Chat System URLs
    path('employee/chat/', views.chat_dashboard, name='chat_dashboard'),
    path('employee/chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('employee/chat/create/', views.create_chat_room, name='create_chat_room'),
    path('employee/chat/room/<int:room_id>/send/', views.send_message, name='send_message'),
    path('employee/chat/room/<int:room_id>/messages/', views.get_messages, name='get_messages'),
    path('employee/chat/message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('employee/chat/message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('employee/chat/notifications/', views.chat_notifications, name='chat_notifications'),
    path('employee/chat/notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Leave Request API URLs
    path('api/leave/<int:request_id>/cancel/', views.cancel_leave_request_api, name='cancel_leave_request_api'),
    path('api/leave/<int:request_id>/approve/', api_views.approve_leave, name='approve_leave'),
    path('api/leave/<int:request_id>/reject/', api_views.reject_leave, name='reject_leave'),
    
    # API URLs
    path('api/', include('core.api_urls', namespace='api')),
]
