"""
URL configuration for EduPredict project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from educationmodel import climate_views
from EduPredict import auth  # Keep for backward compatibility

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home and Authentication
    path('', climate_views.home_view, name='home'),
    path('login/', climate_views.login_view, name='login'),
    path('register/', climate_views.register_view, name='register'),
    path('logout/', climate_views.logout_view, name='logout'),
    path('forgot-password/', climate_views.forgot_password_view, name='forgot-password'),
    
    # Dashboards (Role-based)
    path('dashboard/admin/', climate_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/analyst/', climate_views.analyst_dashboard, name='analyst_dashboard'),
    path('dashboard/viewer/', climate_views.viewer_dashboard, name='viewer_dashboard'),
    path('dashboard/', climate_views.viewer_dashboard, name='dashboard'),  # Default dashboard
    
    # Data Management
    path('data/sources/', climate_views.data_sources_view, name='data_sources'),
    path('data/climate/', climate_views.climate_data_view, name='climate_data'),
    
    # Alerts and Notifications
    path('alerts/', climate_views.alerts_view, name='alerts'),
    path('alerts/acknowledge/<uuid:alert_id>/', climate_views.acknowledge_alert, name='acknowledge_alert'),
    
    # Support System
    path('support/', climate_views.support_tickets_view, name='support_tickets'),
    path('support/create/', climate_views.create_support_ticket, name='create_support_ticket'),
    
    # API Endpoints
    path('api/climate-data-chart/', climate_views.api_climate_data_chart, name='api_climate_data_chart'),
    path('api/system-metrics/', climate_views.api_system_metrics, name='api_system_metrics'),
    
    # User Profile
    path('profile/', climate_views.profile_view, name='profile'),
    
    # Information Pages
    path('about/', climate_views.about_view, name='about'),
    path('contact/', climate_views.contact_view, name='contact'),
    
    # ML Models
    path('models/', climate_views.ml_models_view, name='ml_models'),
    
    # Legacy URLs (for backward compatibility)
    path('signup/', auth.SignupPage, name='legacy_signup'),
    path('signupinserted/', auth.signupPageinserted, name='legacy_signupinserted'),
    path('loginresult/', auth.loginpage, name='legacy_loginresult'),
    path('forgot-password/', auth.forgotPasswordPage, name='forgot-password'),
    path('home/', auth.homePage, name='legacy_home'),
]
