#!/usr/bin/env python
"""
Script to create sample climate data for EarthScape Climate Agency
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPredict.settings')
django.setup()

from educationmodel.models import (
    ClimateUser, UserRole, DataSource, ClimateData, ClimateAlert, 
    MLModel, SupportTicket, SystemMetrics
)
from django.utils import timezone

def create_sample_users():
    """Create sample users with different roles"""
    print("Creating sample users...")
    
    # Create analyst user
    if not ClimateUser.objects.filter(username='analyst').exists():
        analyst = ClimateUser.objects.create_user(
            username='analyst',
            email='analyst@earthscape.org',
            password='climate123',
            first_name='Dr. Sarah',
            last_name='Johnson',
            role=UserRole.ANALYST,
            organization='Climate Research Institute'
        )
        print(f"Created analyst user: {analyst.username}")
    
    # Create viewer user
    if not ClimateUser.objects.filter(username='viewer').exists():
        viewer = ClimateUser.objects.create_user(
            username='viewer',
            email='viewer@earthscape.org',
            password='climate123',
            first_name='Mike',
            last_name='Chen',
            role=UserRole.VIEWER,
            organization='Environmental Monitoring Corp'
        )
        print(f"Created viewer user: {viewer.username}")

def create_sample_data_sources():
    """Create sample data sources"""
    print("Creating sample data sources...")
    
    sources = [
        {
            'name': 'Arctic Research Station Alpha',
            'source_type': 'weather_station',
            'location_lat': 71.0,
            'location_lon': -8.0,
            'altitude': 15.0,
            'installation_date': timezone.now() - timedelta(days=365*3)
        },
        {
            'name': 'NOAA Satellite GOES-16',
            'source_type': 'satellite',
            'location_lat': 0.0,
            'location_lon': -75.2,
            'altitude': 35786000.0,  # Geostationary orbit
            'installation_date': timezone.now() - timedelta(days=365*5)
        },
        {
            'name': 'Pacific Ocean Buoy 46001',
            'source_type': 'ocean_buoy',
            'location_lat': 56.3,
            'location_lon': -148.0,
            'altitude': 0.0,
            'installation_date': timezone.now() - timedelta(days=365*2)
        },
        {
            'name': 'Amazon Rainforest Sensor Network',
            'source_type': 'sensor',
            'location_lat': -3.4,
            'location_lon': -62.2,
            'altitude': 100.0,
            'installation_date': timezone.now() - timedelta(days=365*1)
        },
        {
            'name': 'Beijing Air Quality Monitor',
            'source_type': 'air_quality',
            'location_lat': 39.9,
            'location_lon': 116.4,
            'altitude': 50.0,
            'installation_date': timezone.now() - timedelta(days=365*4)
        }
    ]
    
    created_sources = []
    for source_data in sources:
        source, created = DataSource.objects.get_or_create(
            name=source_data['name'],
            defaults=source_data
        )
        if created:
            print(f"Created data source: {source.name}")
        created_sources.append(source)
    
    return created_sources

def create_sample_climate_data(data_sources):
    """Create sample climate data"""
    print("Creating sample climate data...")
    
    data_types = [
        ('temperature', '°C'),
        ('humidity', '%'),
        ('pressure', 'hPa'),
        ('wind_speed', 'm/s'),
        ('precipitation', 'mm'),
        ('co2_level', 'ppm'),
        ('ozone_level', 'DU'),
    ]
    
    # Create data for the last 30 days
    for days_ago in range(30):
        date = timezone.now() - timedelta(days=days_ago)
        
        for source in data_sources:
            # Create 2-4 data points per day per source
            for _ in range(random.randint(2, 4)):
                data_type, unit = random.choice(data_types)
                
                # Generate realistic values based on data type
                if data_type == 'temperature':
                    value = random.uniform(-20, 35)
                elif data_type == 'humidity':
                    value = random.uniform(20, 95)
                elif data_type == 'pressure':
                    value = random.uniform(980, 1030)
                elif data_type == 'wind_speed':
                    value = random.uniform(0, 25)
                elif data_type == 'precipitation':
                    value = random.uniform(0, 50)
                elif data_type == 'co2_level':
                    value = random.uniform(410, 430)
                elif data_type == 'ozone_level':
                    value = random.uniform(250, 350)
                else:
                    value = random.uniform(0, 100)
                
                # 5% chance of anomaly
                is_anomaly = random.random() < 0.05
                if is_anomaly:
                    value *= random.uniform(1.5, 3.0)  # Make it anomalous
                
                ClimateData.objects.create(
                    data_source=source,
                    data_type=data_type,
                    value=round(value, 2),
                    unit=unit,
                    timestamp=date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                    quality_score=random.uniform(0.8, 1.0),
                    is_anomaly=is_anomaly
                )
    
    print(f"Created {ClimateData.objects.count()} climate data records")

def create_sample_alerts():
    """Create sample climate alerts"""
    print("Creating sample climate alerts...")
    
    alerts = [
        {
            'alert_type': 'temperature_anomaly',
            'severity': 'high',
            'title': 'Unusual Temperature Spike in Arctic',
            'description': 'Temperature readings from Arctic Research Station Alpha show values 15°C above seasonal average.',
            'threshold_value': -10.0,
            'actual_value': 5.0,
            'is_active': True
        },
        {
            'alert_type': 'air_quality',
            'severity': 'medium',
            'title': 'Elevated CO2 Levels Detected',
            'description': 'CO2 concentrations have exceeded 425 ppm in multiple monitoring stations.',
            'threshold_value': 420.0,
            'actual_value': 427.5,
            'is_active': True
        },
        {
            'alert_type': 'extreme_weather',
            'severity': 'critical',
            'title': 'Hurricane Formation Alert',
            'description': 'Satellite imagery shows rapid cyclone development in the Atlantic basin.',
            'threshold_value': 25.0,
            'actual_value': 45.0,
            'is_active': False  # Resolved
        },
        {
            'alert_type': 'sea_level_rise',
            'severity': 'low',
            'title': 'Gradual Sea Level Increase',
            'description': 'Ocean buoy data indicates continued sea level rise at 3.2mm/year rate.',
            'threshold_value': 3.0,
            'actual_value': 3.2,
            'is_active': True
        }
    ]
    
    data_sources = list(DataSource.objects.all())
    
    for alert_data in alerts:
        alert_data['data_source'] = random.choice(data_sources)
        alert_data['created_at'] = timezone.now() - timedelta(days=random.randint(1, 10))
        
        ClimateAlert.objects.create(**alert_data)
    
    print(f"Created {ClimateAlert.objects.count()} climate alerts")

def create_sample_ml_models():
    """Create sample ML models"""
    print("Creating sample ML models...")
    
    admin_user = ClimateUser.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("No admin user found, skipping ML models")
        return
    
    models = [
        {
            'name': 'Temperature Anomaly Detector v2.1',
            'model_type': 'anomaly_detection',
            'version': '2.1.0',
            'description': 'Advanced neural network for detecting temperature anomalies using historical data patterns.',
            'accuracy_score': 0.94,
            'is_active': True,
            'training_data_period_start': timezone.now() - timedelta(days=365*5),
            'training_data_period_end': timezone.now() - timedelta(days=30),
            'created_by': admin_user
        },
        {
            'name': 'Climate Trend Predictor',
            'model_type': 'trend_prediction',
            'version': '1.3.2',
            'description': 'Long-term climate trend prediction model using ensemble methods.',
            'accuracy_score': 0.87,
            'is_active': True,
            'training_data_period_start': timezone.now() - timedelta(days=365*10),
            'training_data_period_end': timezone.now() - timedelta(days=60),
            'created_by': admin_user
        },
        {
            'name': 'Weather Pattern Correlator',
            'model_type': 'correlation_analysis',
            'version': '1.0.5',
            'description': 'Identifies correlations between different climate variables across regions.',
            'accuracy_score': 0.91,
            'is_active': False,  # Under maintenance
            'training_data_period_start': timezone.now() - timedelta(days=365*3),
            'training_data_period_end': timezone.now() - timedelta(days=90),
            'created_by': admin_user
        }
    ]
    
    for model_data in models:
        MLModel.objects.create(**model_data)
    
    print(f"Created {MLModel.objects.count()} ML models")

def create_sample_support_tickets():
    """Create sample support tickets"""
    print("Creating sample support tickets...")
    
    users = list(ClimateUser.objects.all())
    if not users:
        print("No users found, skipping support tickets")
        return
    
    tickets = [
        {
            'title': 'Data Export Feature Request',
            'description': 'Would like to export climate data in CSV format for external analysis.',
            'priority': 'medium',
            'status': 'open',
            'created_by': random.choice(users)
        },
        {
            'title': 'Alert Notification Not Working',
            'description': 'Not receiving email notifications for high-severity climate alerts.',
            'priority': 'high',
            'status': 'in_progress',
            'created_by': random.choice(users)
        },
        {
            'title': 'Dashboard Loading Slowly',
            'description': 'The main dashboard takes more than 30 seconds to load climate data charts.',
            'priority': 'low',
            'status': 'resolved',
            'created_by': random.choice(users),
            'resolved_at': timezone.now() - timedelta(days=2)
        }
    ]
    
    for ticket_data in tickets:
        SupportTicket.objects.create(**ticket_data)
    
    print(f"Created {SupportTicket.objects.count()} support tickets")

def create_sample_system_metrics():
    """Create sample system metrics"""
    print("Creating sample system metrics...")
    
    # Create metrics for the last 24 hours
    for hours_ago in range(24):
        timestamp = timezone.now() - timedelta(hours=hours_ago)
        
        SystemMetrics.objects.create(
            cpu_usage=random.uniform(20, 80),
            memory_usage=random.uniform(40, 90),
            disk_usage=random.uniform(30, 70),
            network_io=random.uniform(10, 100),
            active_users=random.randint(5, 25),
            data_processing_rate=random.uniform(100, 1000),
            timestamp=timestamp
        )
    
    print(f"Created {SystemMetrics.objects.count()} system metrics records")

def main():
    """Main function to create all sample data"""
    print("Creating sample data for EarthScape Climate Agency...")
    print("=" * 50)
    
    create_sample_users()
    data_sources = create_sample_data_sources()
    create_sample_climate_data(data_sources)
    create_sample_alerts()
    create_sample_ml_models()
    create_sample_support_tickets()
    create_sample_system_metrics()
    
    print("=" * 50)
    print("Sample data creation completed!")
    print("\nLogin credentials:")
    print("Admin: admin / climate123")
    print("Analyst: analyst / climate123")
    print("Viewer: viewer / climate123")

if __name__ == '__main__':
    main()