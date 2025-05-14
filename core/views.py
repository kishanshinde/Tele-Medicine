from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse
from django.utils import timezone
from django.conf import settings
from .models import User, Appointment, MedicalRecord, PatientProfile, DoctorProfile
from .forms import PatientProfileForm, DoctorProfileForm
import os
from datetime import datetime
from django.urls import reverse
import logging

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html', {'is_dashboard': False})

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            if user.user_type == 'patient':
                return redirect('patient_dashboard')
            else:
                return redirect('doctor_dashboard')
        messages.error(request, 'Invalid email or password')
    return render(request, 'login.html', {'is_dashboard': False})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('index')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        user_type = request.POST.get('user_type')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('register')

        base_username = name.lower().replace(" ", "")
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(email=email, name=name, user_type=user_type, username=username)
        user.set_password(password)
        if user_type == 'doctor':
            user.specialization = request.POST.get('specialization')
        user.save()

        # Create profile for new user
        if user_type == 'patient':
            PatientProfile.objects.create(user=user)
        else:
            DoctorProfile.objects.create(user=user)

        messages.success(request, 'Registration successful')
        return redirect('login')

    return render(request, 'register.html', {'is_dashboard': False})

@login_required
def patient_dashboard(request):
    if request.user.user_type != 'patient':
        return redirect('index')

    try:
        profile = request.user.patient_profile
        if not (profile.age is not None and profile.height is not None and profile.weight is not None and profile.address and profile.medical_history):
            return redirect('complete_patient_profile')
    except PatientProfile.DoesNotExist:
        return redirect('complete_patient_profile')

    appointments = Appointment.objects.filter(patient=request.user)
    medical_records = MedicalRecord.objects.filter(patient=request.user, is_deleted=False)
    doctors = User.objects.filter(user_type='doctor')

    return render(request, 'patient/dashboard.html', {
        'appointments': appointments,
        'doctors': doctors,
        'medical_records': medical_records,
        'is_dashboard': True,
    })

@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'doctor':
        return redirect('index')

    try:
        profile = request.user.doctor_profile
        if not (profile.age is not None and profile.height is not None and profile.weight is not None):
            return redirect('complete_doctor_profile')
    except DoctorProfile.DoesNotExist:
        return redirect('complete_doctor_profile')

    appointments = Appointment.objects.filter(doctor=request.user)
    pending_estimates = appointments.filter(estimated_cost__isnull=True).count()
    pending_appointments = appointments.filter(status='pending').count()
    for appointment in appointments:
        appointment.medical_records = appointment.shared_records.all()

    return render(request, 'doctor/dashboard.html', {
        'appointments': appointments,
        'pending_estimates': pending_estimates,
        'pending_appointments': pending_appointments,
        'is_dashboard': True,
    })

@login_required
def complete_patient_profile(request):
    try:
        profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        profile = PatientProfile(user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=profile)
        if 'remove_profile_picture' in request.POST:
            # Handle profile picture removal
            profile.profile_picture = None
            profile.save()
            messages.success(request, 'Profile picture removed successfully.')
            form = PatientProfileForm(instance=profile)
        else:
            # Handle profile save
            logger.debug(f"Form data: {request.POST}, Files: {request.FILES}")
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile completed successfully.')
                logger.debug("Form saved, redirecting to patient_dashboard")
                return redirect('patient_dashboard')
            else:
                logger.error(f"Form errors: {form.errors}")
                messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientProfileForm(instance=profile)
    
    return render(request, 'patient/complete_profile.html', {'form': form, 'is_dashboard': False})

@login_required
def complete_doctor_profile(request):
    try:
        profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        profile = DoctorProfile(user=request.user)
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=profile)
        if 'remove_profile_picture' in request.POST:
            # Handle profile picture removal
            profile.profile_picture = None
            profile.save()
            messages.success(request, 'Profile picture removed successfully.')
            form = DoctorProfileForm(instance=profile)
        else:
            # Handle profile save
            logger.debug(f"Form data: {request.POST}, Files: {request.FILES}")
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile completed successfully.')
                logger.debug("Form saved, redirecting to doctor_dashboard")
                return redirect('doctor_dashboard')
            else:
                logger.error(f"Form errors: {form.errors}")
                messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorProfileForm(instance=profile)
    
    return render(request, 'doctor/complete_profile.html', {'form': form, 'is_dashboard': False})

@login_required
def book_appointment(request):
    if request.user.user_type != 'patient':
        return redirect('index')
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date_str = request.POST.get('appointment_date')
        description = request.POST.get('description')
        shared_record_ids = request.POST.getlist('shared_records')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            if date < datetime.now():
                messages.error(request, 'Cannot book an appointment in the past')
                return redirect('patient_dashboard')

            doctor = User.objects.get(id=doctor_id, user_type='doctor')
            appointment = Appointment(
                patient=request.user,
                doctor=doctor,
                date=date,
                description=description,
                status='pending'
            )
            appointment.save()
            records = MedicalRecord.objects.filter(id__in=shared_record_ids, patient=request.user, is_deleted=False)
            appointment.shared_records.set(records)
            messages.success(request, 'Appointment request sent')
        except User.DoesNotExist:
            messages.error(request, 'Doctor not found')
        except ValueError:
            messages.error(request, 'Invalid date format')
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
    return redirect('patient_dashboard')

@login_required
def upload_medical_record(request):
    if request.user.user_type != 'patient':
        return redirect('index')
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file or not file.name.endswith('.pdf'):
            messages.error(request, 'Please upload a PDF file')
            return redirect('patient_dashboard')

        record = MedicalRecord(
            patient=request.user,
            file=file,
            description=request.POST.get('description', ''),
            upload_date=timezone.now()
        )
        record.save()
        messages.success(request, 'Medical record uploaded successfully')
    return redirect('patient_dashboard')

@login_required
def update_estimate(request):
    if request.user.user_type != 'doctor':
        return redirect('index')
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        estimated_cost = request.POST.get('estimated_cost')
        estimate_comment = request.POST.get('estimate_comment')  # Get the comment

        if not appointment_id or not appointment_id.isdigit():
            messages.error(request, 'Invalid appointment ID')
            return redirect('doctor_dashboard')

        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
        try:
            appointment.estimated_cost = float(estimated_cost)
            appointment.estimate_comment = estimate_comment  # Save the comment
            appointment.save()
            messages.success(request, 'Estimate updated successfully')
        except ValueError:
            messages.error(request, 'Invalid estimated cost')
    return redirect('doctor_dashboard')

@login_required
def delete_medical_record(request, record_id):
    if request.user.user_type != 'patient':
        return redirect('index')
    record = get_object_or_404(MedicalRecord, id=record_id, patient=request.user)
    if request.method == 'POST':
        record.is_deleted = True
        record.save()
        messages.success(request, 'Medical record deleted successfully')
    return redirect('patient_dashboard')

@login_required
def download_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.user.user_type == 'patient' and record.is_deleted:
        messages.error(request, 'This record has been deleted')
        return redirect('patient_dashboard')

    if request.user.user_type == 'patient' and record.patient == request.user:
        return FileResponse(open(record.file.path, 'rb'), as_attachment=True)

    elif request.user.user_type == 'doctor':
        appointment = Appointment.objects.filter(
            doctor=request.user,
            shared_records=record
        ).first()
        if appointment:
            return FileResponse(open(record.file.path, 'rb'), as_attachment=True)

    messages.error(request, 'You do not have permission to access this record')
    return redirect('index')

@login_required
def view_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.user.user_type == 'patient' and record.is_deleted:
        messages.error(request, 'This record has been deleted')
        return redirect('patient_dashboard')

    if request.user.user_type == 'patient' and record.patient == request.user:
        return FileResponse(open(record.file.path, 'rb'), content_type='application/pdf')

    elif request.user.user_type == 'doctor':
        appointment = Appointment.objects.filter(
            doctor=request.user,
            shared_records=record
        ).first()
        if appointment:
            return FileResponse(open(record.file.path, 'rb'), content_type='application/pdf')

    messages.error(request, 'You do not have permission to access this record')
    return redirect('index')

@login_required
def update_appointment_status(request):
    if request.user.user_type != 'doctor':
        return redirect('index')
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        status = request.POST.get('status')
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
        appointment.status = status
        appointment.save()
        messages.success(request, 'Appointment status updated successfully')
    return redirect('doctor_dashboard')

@login_required
def appointment_detail(request, appointment_id):
    if request.user.user_type != 'patient':
        return redirect('index')
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    return render(request, 'patient/appointment_detail.html', {'appointment': appointment, 'is_dashboard': False})