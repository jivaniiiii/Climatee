from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    ClimateUser, DataSource, ClimateData, ClimateAlert, 
    MLModel, SupportTicket, SystemMetrics, Signup
)

# Custom User Admin
@admin.register(ClimateUser)
class ClimateUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'organization', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'organization')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Climate Agency Info', {
            'fields': ('role', 'organization', 'phone', 'last_login_ip', 'is_active_session')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Climate Agency Info', {
            'fields': ('role', 'organization', 'phone')
        }),
    )

# Data Source Admin
@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'location_lat', 'location_lon', 'is_active', 'created_at')
    list_filter = ('source_type', 'is_active', 'created_at')
    search_fields = ('name', 'source_type')
    readonly_fields = ('id', 'created_at')

# Climate Data Admin
@admin.register(ClimateData)
class ClimateDataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'value', 'unit', 'data_source', 'timestamp', 'is_anomaly', 'quality_score')
    list_filter = ('data_type', 'is_anomaly', 'processed', 'timestamp', 'data_source__source_type')
    search_fields = ('data_type', 'data_source__name')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'timestamp'

# Climate Alert Admin
@admin.register(ClimateAlert)
class ClimateAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'severity', 'is_active', 'created_at', 'acknowledged_by')
    list_filter = ('alert_type', 'severity', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'

# ML Model Admin
@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'version', 'accuracy_score', 'is_active', 'created_by')
    list_filter = ('model_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'last_updated')

# Support Ticket Admin
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

# System Metrics Admin
@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'cpu_usage', 'memory_usage', 'disk_usage', 'active_users', 'data_processing_rate')
    list_filter = ('timestamp',)
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'

# Legacy Signup Admin (for backward compatibility)
@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')
    readonly_fields = ('password',)  # Don't allow editing passwords in plain text