import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Department, Job, Event, EventRegistration, DirectMessage, Announcement

def home(request):
    events = Event.objects.all().order_by('-date')[:3]
    jobs = Job.objects.all().order_by('-created_at')[:3]
    announcements = Announcement.objects.all().order_by('-created_at')[:3]
    alumni_count = UserProfile.objects.filter(role='alumni', is_approved=True).count()
    return render(request, 'home.html', {
        'events': events, 'jobs': jobs, 'announcements': announcements, 'alumni_count': alumni_count
    })

def alumni_login(request):
    if request.user.is_authenticated and not (request.user.is_superuser or request.user.is_staff):
        return redirect('alumni_dashboard')

    if request.method == 'POST':
        u_in = request.POST.get('username')
        p_in = request.POST.get('password')
        user = authenticate(request, username=u_in, password=p_in)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is pending approval by Admin/Faculty.')
                return render(request, 'login.html')

            login(request, user)
            messages.success(request, 'Login Successful!')
            
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
            return redirect('alumni_dashboard')
        else:
            messages.error(request, 'Invalid Username/ID or Password.')

    return render(request, 'login.html')

def alumni_register(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        role = request.POST.get('role')
        name = request.POST.get('name')
        email = request.POST.get('email')
        register_no = request.POST.get('register_no')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dept_id = request.POST.get('department')
        password = request.POST.get('password')

        if User.objects.filter(username=register_no).exists():
            messages.error(request, 'Register No / ID is already registered.')
            return render(request, 'register.html', {'departments': departments})

        dept = get_object_or_404(Department, id=dept_id)
        is_active = True if role == 'faculty' else False

        user = User.objects.create_user(username=register_no, email=email, password=password)
        user.first_name = name
        user.is_active = is_active
        user.save()

        profile = UserProfile.objects.create(
            user=user, role=role, register_no=register_no, phone=phone,
            gender=gender, department=dept, is_approved=is_active
        )

        if role == 'alumni':
            profile.batch = request.POST.get('batch', '')
            grad_year = request.POST.get('graduation_year')
            profile.graduation_year = int(grad_year) if grad_year and grad_year.isdigit() else 2024
            profile.company = request.POST.get('company', '')
            profile.designation = request.POST.get('designation', '')
        elif role == 'student':
            profile.current_semester = request.POST.get('current_semester', '')

        profile.save()
        logout(request)

        if is_active:
            messages.success(request, 'Registration Successful! You can login now.')
        else:
            messages.info(request, 'Registration Successful! Sent for Faculty/Admin approval.')

        return redirect('alumni_login')

    return render(request, 'register.html', {'departments': departments})

def alumni_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required(login_url='alumni_login')
def alumni_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    jobs_count = Job.objects.count()
    events_count = Event.objects.count()
    
    alumni_count = UserProfile.objects.filter(role='alumni', is_approved=True).count()
    students_count = UserProfile.objects.filter(role='student', is_approved=True).count()
    unread_messages = DirectMessage.objects.filter(receiver=request.user).count()
    announcements = Announcement.objects.all().order_by('-created_at')[:3]
    recent_jobs = Job.objects.all().order_by('-created_at')[:3]
    
    pending_students = []
    department_students_count = 0
    
    if profile and profile.role == 'faculty':
        pending_students = UserProfile.objects.filter(role='student', is_approved=False)
        department_students_count = UserProfile.objects.filter(role='student', is_approved=True).count()

    return render(request, 'dashboard.html', {
        'profile': profile, 
        'jobs_count': jobs_count,
        'events_count': events_count, 
        'alumni_count': alumni_count,
        'students_count': students_count,
        'messages_count': unread_messages,
        'pending_students': pending_students,
        'department_students_count': department_students_count,
        'announcements': announcements,
        'recent_jobs': recent_jobs,
    })

@login_required(login_url='alumni_login')
def approve_student(request, profile_id):
    if request.user.profile.role == 'faculty':
        prof = get_object_or_404(UserProfile, id=profile_id)
        prof.is_approved = True
        prof.save()
        prof.user.is_active = True
        prof.user.save()
        messages.success(request, f"Student {prof.user.first_name} has been approved successfully!")
    return redirect('alumni_dashboard')

@login_required(login_url='alumni_login')
def add_event(request):
    if request.method == 'POST':
        Event.objects.create(
            title=request.POST.get('title'),
            date=request.POST.get('date'),
            location=request.POST.get('location'),
            description=request.POST.get('description')
        )
        messages.success(request, "New event hosted successfully!")
        return redirect('event_list')
    return render(request, 'add_event.html')

@login_required(login_url='alumni_login')
def add_announcement(request):
    if request.method == 'POST':
        Announcement.objects.create(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            posted_by=request.user,
            department=request.user.profile.department
        )
        messages.success(request, "Announcement published successfully!")
        return redirect('alumni_dashboard')
    return render(request, 'add_announcement.html')

@login_required(login_url='alumni_login')
def export_alumni_csv(request):
    if request.user.profile.role == 'faculty':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="alumni_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Register No', 'Department', 'Company', 'Designation', 'Graduation Year'])
        
        alumnis = UserProfile.objects.filter(role='alumni', is_approved=True)
        for a in alumnis:
            writer.writerow([a.user.first_name, a.user.email, a.register_no, a.department.name if a.department else '', a.company, a.designation, a.graduation_year])
            
        return response
    return redirect('alumni_dashboard')

@login_required(login_url='alumni_login')
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    profile = getattr(request.user, 'profile', None)
    return render(request, 'job.html', {'jobs': jobs, 'profile': profile})

@login_required(login_url='alumni_login')
def add_job(request):
    if request.method == 'POST':
        Job.objects.create(
            title=request.POST.get('title'),
            company=request.POST.get('company'),
            location=request.POST.get('location'),
            description=request.POST.get('description'),
            contact_email=request.POST.get('contact_email'),
            posted_by=request.user
        )
        messages.success(request, "Job posting added successfully!")
        return redirect('job_list')
    return render(request, 'add_job.html')

@login_required(login_url='alumni_login')
def event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'events.html', {'events': events})

@login_required(login_url='alumni_login')
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reg, created = EventRegistration.objects.get_or_create(event=event, user=request.user)
    if created:
        messages.success(request, f"Registered for {event.title}!")
    else:
        messages.info(request, "You are already registered.")
    return redirect('event_list')

# Role-Based Institutional Directory View
@login_required(login_url='alumni_login')
def alumni_directory(request):
    user_role = getattr(request.user.profile, 'role', 'student')
    
    # 1. Alumni can message Alumni, Students, and Faculty
    if user_role == 'alumni':
        alumni_profiles = UserProfile.objects.filter(role='alumni', is_approved=True).exclude(user=request.user).select_related('user', 'department')
        student_profiles = UserProfile.objects.filter(role='student', is_approved=True).select_related('user', 'department')
        faculty_profiles = UserProfile.objects.filter(role='faculty', is_approved=True).select_related('user', 'department')
    
    # 2. Student can message Alumni and Faculty
    elif user_role == 'student':
        alumni_profiles = UserProfile.objects.filter(role='alumni', is_approved=True).select_related('user', 'department')
        student_profiles = UserProfile.objects.none()
        faculty_profiles = UserProfile.objects.filter(role='faculty', is_approved=True).select_related('user', 'department')
        
    # 3. Faculty can message Alumni
    elif user_role == 'faculty':
        alumni_profiles = UserProfile.objects.filter(role='alumni', is_approved=True).select_related('user', 'department')
        student_profiles = UserProfile.objects.none()
        faculty_profiles = UserProfile.objects.none()

    return render(request, 'directory.html', {
        'alumni_profiles': alumni_profiles,
        'student_profiles': student_profiles,
        'faculty_profiles': faculty_profiles,
        'user_role': user_role,
    })

# Dedicated Student Directory View
@login_required(login_url='alumni_login')
def student_directory(request):
    student_profiles = UserProfile.objects.filter(role='student', is_approved=True).select_related('user', 'department')
    return render(request, 'student_directory.html', {'student_profiles': student_profiles})

@login_required(login_url='alumni_login')
def send_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        DirectMessage.objects.create(
            sender=request.user, receiver=receiver,
            subject=subject, message=message_text
        )
        messages.success(request, f"Message sent successfully to {receiver.first_name}!")
        return redirect('alumni_directory')
    return render(request, 'send_message.html', {'receiver': receiver})

@login_required(login_url='alumni_login')
def inbox(request):
    received = DirectMessage.objects.filter(receiver=request.user).order_by('-sent_at')
    return render(request, 'inbox.html', {'received_messages': received})

@login_required(login_url='alumni_login')
def edit_profile(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        if profile:
            profile.phone = request.POST.get('phone', profile.phone)
            if profile.role == 'alumni':
                profile.company = request.POST.get('company', profile.company)
                profile.designation = request.POST.get('designation', profile.designation)
            
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {'profile': profile})