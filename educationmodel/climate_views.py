from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Max, Min
from django.utils import timezone
from django.conf import settings
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.offline as pyo
from plotly.utils import PlotlyJSONEncoder

from .models import (
    ClimateUser, UserRole, DataSource, ClimateData, ClimateAlert, 
    MLModel, SupportTicket, SystemMetrics
)

logger = logging.getLogger(__name__)

# Utility functions for role-based access
def is_admin(user):
    return user.is_authenticated and user.has_admin_access()

def is_analyst_or_admin(user):
    return user.is_authenticated and user.has_analyst_access()

# Home View
def home_view(request):
    """Home page with overview of EarthScape Climate Agency"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get some basic stats for the home page
    context = {
        'total_data_sources': DataSource.objects.filter(is_active=True).count(),
        'total_climate_data': ClimateData.objects.count(),
        'active_alerts': ClimateAlert.objects.filter(is_active=True).count(),
        'recent_data': ClimateData.objects.select_related('data_source').order_by('-timestamp')[:5]
    }
    return render(request, 'pages/home.html', context)

# Authentication Views
def login_view(request):
    """Secure login with role-based redirection and security logging"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Get client IP for security logging
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                user.last_login_ip = client_ip
                user.is_active_session = True
                user.save()
                
                logger.info(f"Successful login for user {username} from IP {client_ip}")
                
                # Role-based redirection
                if user.has_admin_access():
                    return redirect('admin_dashboard')
                elif user.has_analyst_access():
                    return redirect('analyst_dashboard')
                else:
                    return redirect('viewer_dashboard')
            else:
                messages.error(request, "Your account has been deactivated. Please contact support.")
                logger.warning(f"Login attempt with deactivated account: {username} from IP {client_ip}")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            logger.warning(f"Failed login attempt for username: {username} from IP {client_ip}")
    
    return render(request, 'auth/login.html')

def register_view(request):
    """User registration with role assignment"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        organization = request.POST.get('organization', '')
        phone = request.POST.get('phone', '')
        
        # Check if user already exists
        if ClimateUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'auth/register.html')
        
        if ClimateUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'auth/register.html')
        
        # Create new user (default role is VIEWER)
        user = ClimateUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            organization=organization,
            phone=phone,
            role=UserRole.VIEWER
        )
        
        messages.success(request, "Account created successfully! Please log in.")
        logger.info(f"New user registered: {username} ({email})")
        return redirect('login')
    
    return render(request, 'auth/register.html')

@login_required
def logout_view(request):
    """Secure logout with session cleanup"""
    user = request.user
    user.is_active_session = False
    user.save()
    
    logger.info(f"User {user.username} logged out")
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

def forgot_password_view(request):
    """Password reset request view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        # In a real application, this would send a password reset email
        messages.success(request, 'If an account with that email exists, we have sent you a password reset link.')
        logger.info(f"Password reset requested for email: {email}")
        return redirect('login')
    
    return render(request, 'auth/forgot_password.html')

# Dashboard Views
@login_required
def admin_dashboard(request):
    """Administrator dashboard with system overview"""
    if not request.user.has_admin_access():
        messages.error(request, "Access denied. Administrator privileges required.")
        return redirect('viewer_dashboard')
    
    # System metrics
    latest_metrics = SystemMetrics.objects.first()
    
    # Recent alerts
    recent_alerts = ClimateAlert.objects.filter(is_active=True)[:10]
    
    # User statistics
    user_stats = {
        'total_users': ClimateUser.objects.count(),
        'active_sessions': ClimateUser.objects.filter(is_active_session=True).count(),
        'admin_users': ClimateUser.objects.filter(role=UserRole.ADMINISTRATOR).count(),
        'analyst_users': ClimateUser.objects.filter(role=UserRole.ANALYST).count(),
    }
    
    # Data source statistics
    data_source_stats = {
        'total_sources': DataSource.objects.count(),
        'active_sources': DataSource.objects.filter(is_active=True).count(),
        'satellite_sources': DataSource.objects.filter(source_type='satellite').count(),
        'weather_stations': DataSource.objects.filter(source_type='weather_station').count(),
    }
    
    # Recent data ingestion
    recent_data = ClimateData.objects.order_by('-created_at')[:100]
    data_ingestion_rate = recent_data.count() if recent_data else 0
    
    context = {
        'user_stats': user_stats,
        'data_source_stats': data_source_stats,
        'recent_alerts': recent_alerts,
        'latest_metrics': latest_metrics,
        'data_ingestion_rate': data_ingestion_rate,
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
@user_passes_test(is_analyst_or_admin)
def analyst_dashboard(request):
    """Climate analyst dashboard with data analysis tools"""
    
    # Climate data summary
    data_summary = ClimateData.objects.aggregate(
        total_records=Count('id'),
        avg_temperature=Avg('value', filter=Q(data_type='temperature')),
        max_co2=Max('value', filter=Q(data_type='co2_level')),
        anomaly_count=Count('id', filter=Q(is_anomaly=True))
    )
    
    # Recent anomalies
    recent_anomalies = ClimateData.objects.filter(
        is_anomaly=True
    ).order_by('-timestamp')[:20]
    
    # Active ML models
    active_models = MLModel.objects.filter(is_active=True)
    
    # Data sources by type
    source_distribution = DataSource.objects.values('source_type').annotate(
        count=Count('id')
    )
    
    context = {
        'data_summary': data_summary,
        'recent_anomalies': recent_anomalies,
        'active_models': active_models,
        'source_distribution': source_distribution,
    }
    
    return render(request, 'dashboards/analyst_dashboard.html', context)

@login_required
def viewer_dashboard(request):
    """General user dashboard with climate data visualization"""
    
    # Recent climate data trends
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    temperature_data = ClimateData.objects.filter(
        data_type='temperature',
        timestamp__range=[start_date, end_date]
    ).order_by('timestamp')
    
    # Active alerts (non-critical only for viewers)
    active_alerts = ClimateAlert.objects.filter(
        is_active=True,
        severity__in=['low', 'medium']
    )[:5]
    
    # Data source locations for map
    data_sources = DataSource.objects.filter(is_active=True)
    
    context = {
        'temperature_data': temperature_data,
        'active_alerts': active_alerts,
        'data_sources': data_sources,
    }
    
    return render(request, 'dashboards/viewer_dashboard.html', context)

# Data Management Views
@login_required
@user_passes_test(is_analyst_or_admin)
def data_sources_view(request):
    """Manage climate data sources"""
    sources = DataSource.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(sources, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_sources': sources.count(),
    }
    
    return render(request, 'data/data_sources.html', context)

@login_required
@user_passes_test(is_analyst_or_admin)
def climate_data_view(request):
    """View and analyze climate data"""
    
    # Filters
    data_type = request.GET.get('data_type', '')
    source_id = request.GET.get('source_id', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Base queryset
    climate_data = ClimateData.objects.all()
    
    # Apply filters
    if data_type:
        climate_data = climate_data.filter(data_type=data_type)
    if source_id:
        climate_data = climate_data.filter(data_source_id=source_id)
    if start_date:
        climate_data = climate_data.filter(timestamp__gte=start_date)
    if end_date:
        climate_data = climate_data.filter(timestamp__lte=end_date)
    
    climate_data = climate_data.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(climate_data, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Available filters
    data_types = ClimateData.DATA_TYPES
    data_sources = DataSource.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'data_types': data_types,
        'data_sources': data_sources,
        'current_filters': {
            'data_type': data_type,
            'source_id': source_id,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    
    return render(request, 'data/climate_data.html', context)

# Alert Management Views
@login_required
def alerts_view(request):
    """View climate alerts based on user role"""
    
    # Filter alerts based on user role
    if request.user.has_admin_access():
        alerts = ClimateAlert.objects.all()
    elif request.user.has_analyst_access():
        alerts = ClimateAlert.objects.filter(severity__in=['low', 'medium', 'high'])
    else:
        alerts = ClimateAlert.objects.filter(severity__in=['low', 'medium'])
    
    # Filter by status
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        alerts = alerts.filter(is_active=True)
    elif status_filter == 'resolved':
        alerts = alerts.filter(is_active=False)
    
    alerts = alerts.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'alerts/alerts.html', context)

@login_required
@user_passes_test(is_analyst_or_admin)
def acknowledge_alert(request, alert_id):
    """Acknowledge a climate alert"""
    if request.method == 'POST':
        alert = get_object_or_404(ClimateAlert, id=alert_id)
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        logger.info(f"Alert {alert_id} acknowledged by {request.user.username}")
        messages.success(request, "Alert acknowledged successfully.")
    
    return redirect('alerts')

# Support System Views
@login_required
def support_tickets_view(request):
    """View support tickets"""
    
    if request.user.has_admin_access():
        tickets = SupportTicket.objects.all()
    else:
        tickets = SupportTicket.objects.filter(created_by=request.user)
    
    tickets = tickets.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'support/tickets.html', context)

@login_required
def create_support_ticket(request):
    """Create a new support ticket"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'medium')
        
        ticket = SupportTicket.objects.create(
            title=title,
            description=description,
            priority=priority,
            created_by=request.user
        )
        
        logger.info(f"Support ticket created by {request.user.username}: {title}")
        messages.success(request, "Support ticket created successfully.")
        return redirect('support_tickets')
    
    return render(request, 'support/create_ticket.html')

# API Views for AJAX requests
@login_required
def api_climate_data_chart(request):
    """API endpoint for climate data charts"""
    data_type = request.GET.get('data_type', 'temperature')
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    data = ClimateData.objects.filter(
        data_type=data_type,
        timestamp__range=[start_date, end_date]
    ).order_by('timestamp')
    
    # Prepare data for chart
    timestamps = [d.timestamp.isoformat() for d in data]
    values = [d.value for d in data]
    
    chart_data = {
        'timestamps': timestamps,
        'values': values,
        'data_type': data_type,
        'unit': data[0].unit if data else ''
    }
    
    return JsonResponse(chart_data)

@login_required
@user_passes_test(is_admin)
def api_system_metrics(request):
    """API endpoint for system metrics"""
    hours = int(request.GET.get('hours', 24))
    
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours)
    
    metrics = SystemMetrics.objects.filter(
        timestamp__range=[start_time, end_time]
    ).order_by('timestamp')
    
    data = {
        'timestamps': [m.timestamp.isoformat() for m in metrics],
        'cpu_usage': [m.cpu_usage for m in metrics],
        'memory_usage': [m.memory_usage for m in metrics],
        'disk_usage': [m.disk_usage for m in metrics],
        'active_users': [m.active_users for m in metrics],
    }
    
    return JsonResponse(data)

# Utility Views
def about_view(request):
    """About EarthScape Climate Agency"""
    return render(request, 'pages/about.html')

def contact_view(request):
    """Contact information and support"""
    return render(request, 'pages/contact.html')

@login_required
def profile_view(request):
    """User profile management"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.organization = request.POST.get('organization', user.organization)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    
    return render(request, 'auth/profile.html')

@login_required
def ml_models_view(request):
    """ML Models page"""
    models = MLModel.objects.all().order_by('-created_at')
    
    context = {
        'models': models,
        'total_models': models.count(),
        'active_models': models.filter(is_active=True).count(),
    }
    
    return render(request, 'ml/models.html', context)