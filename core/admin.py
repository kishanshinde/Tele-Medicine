from django.contrib import admin
from .models import User, Appointment, MedicalRecord, PatientProfile, DoctorProfile

admin.site.register(User)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)