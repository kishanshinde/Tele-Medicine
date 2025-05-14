from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=7, choices=USER_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'user_type']

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    estimated_cost = models.FloatField(null=True, blank=True)
    estimate_comment = models.TextField(blank=True, null=True)  # New field for estimate comment
    shared_records = models.ManyToManyField('MedicalRecord', blank=True)

class MedicalRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='medical_records/')
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile', limit_choices_to={'user_type': 'patient'})
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # in cm
    weight = models.FloatField(null=True, blank=True)  # in kg
    address = models.CharField(max_length=255, null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name}'s Patient Profile"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', limit_choices_to={'user_type': 'doctor'})
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # in cm
    weight = models.FloatField(null=True, blank=True)  # in kg

    def __str__(self):
        return f"{self.user.name}'s Doctor Profile"