from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

# User Roles
class UserRole(models.TextChoices):
    ADMINISTRATOR = 'admin', 'Administrator'
    ANALYST = 'analyst', 'Climate Analyst'
    VIEWER = 'viewer', 'Data Viewer'

# Extended User Model with Role-based Access
class ClimateUser(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.VIEWER)
    organization = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_active_session = models.BooleanField(default=False)
    
    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='climate_users',
        related_query_name='climate_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='climate_users',
        related_query_name='climate_user',
    )

    def has_admin_access(self):
        return self.role == UserRole.ADMINISTRATOR
    
    def has_analyst_access(self):
        return self.role in [UserRole.ADMINISTRATOR, UserRole.ANALYST]

# Climate Data Sources
class DataSource(models.Model):
    SOURCE_TYPES = [
        ('satellite', 'Satellite Imagery'),
        ('weather_station', 'Weather Station'),
        ('sensor', 'Environmental Sensor'),
        ('ocean_buoy', 'Ocean Buoy'),
        ('air_quality', 'Air Quality Monitor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    installation_date = models.DateTimeField()
    last_maintenance = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

# Climate Data Records
class ClimateData(models.Model):
    DATA_TYPES = [
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('pressure', 'Atmospheric Pressure'),
        ('wind_speed', 'Wind Speed'),
        ('wind_direction', 'Wind Direction'),
        ('precipitation', 'Precipitation'),
        ('co2_level', 'CO2 Concentration'),
        ('ozone_level', 'Ozone Level'),
        ('sea_level', 'Sea Level'),
        ('ice_coverage', 'Ice Coverage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    quality_score = models.FloatField(default=1.0)  # 0.0 to 1.0
    is_anomaly = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['data_source', 'timestamp']),
            models.Index(fields=['data_type', 'timestamp']),
            models.Index(fields=['is_anomaly']),
        ]

    def __str__(self):
        return f"{self.data_type}: {self.value} {self.unit} at {self.timestamp}"

# Climate Alerts and Notifications
class ClimateAlert(models.Model):
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_TYPES = [
        ('temperature_anomaly', 'Temperature Anomaly'),
        ('extreme_weather', 'Extreme Weather Event'),
        ('air_quality', 'Air Quality Alert'),
        ('sea_level_rise', 'Sea Level Rise'),
        ('system_failure', 'System/Sensor Failure'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    actual_value = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    acknowledged_by = models.ForeignKey(ClimateUser, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_severity_display()} Alert: {self.title}"

# Machine Learning Models Registry
class MLModel(models.Model):
    MODEL_TYPES = [
        ('anomaly_detection', 'Anomaly Detection'),
        ('trend_prediction', 'Trend Prediction'),
        ('correlation_analysis', 'Correlation Analysis'),
        ('weather_forecast', 'Weather Forecasting'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    description = models.TextField()
    accuracy_score = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    training_data_period_start = models.DateTimeField()
    training_data_period_end = models.DateTimeField()
    created_by = models.ForeignKey(ClimateUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

# Support Tickets
class SupportTicket(models.Model):
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(ClimateUser, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(ClimateUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id.hex[:8]}: {self.title}"

# System Performance Monitoring
class SystemMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_io = models.FloatField()
    active_users = models.IntegerField()
    data_processing_rate = models.FloatField()  # records per minute
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

# Legacy model for backward compatibility (will be deprecated)
class Signup(models.Model):
    name = models.CharField(max_length=100) 
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'educationmodel_signup'  # Keep original table name