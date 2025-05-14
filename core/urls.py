from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/complete-profile/', views.complete_patient_profile, name='complete_patient_profile'),
    path('doctor/complete-profile/', views.complete_doctor_profile, name='complete_doctor_profile'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('upload-medical-record/', views.upload_medical_record, name='upload_medical_record'),
    path('update-estimate/', views.update_estimate, name='update_estimate'),
    path('delete-record/<int:record_id>/', views.delete_medical_record, name='delete_record'),
    path('download-record/<int:record_id>/', views.download_record, name='download_record'),
    path('view-record/<int:record_id>/', views.view_record, name='view_record'),  # New URL for viewing records
    path('update-appointment-status/', views.update_appointment_status, name='update_appointment_status'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
]