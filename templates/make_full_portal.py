import os

# 1. Models Update
models_code = """from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self): return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('faculty', 'Faculty'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    register_no = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    batch = models.CharField(max_length=50, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    current_semester = models.CharField(max_length=20, blank=True, null=True)
    employee_id = models.CharField(max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} ({self.role.capitalize()})"

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    contact_email = models.EmailField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.title} - {self.company}"

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
"""
with open('alumni/models.py', 'w') as f: f.write(models_code)

# 2. Views Update
views_code = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Department, Job, Event, EventRegistration

def home(request):
    return render(request, 'home.html')

def alumni_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
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
        elif role == 'faculty':
            profile.employee_id = request.POST.get('employee_id', '')

        profile.save()

        if is_active:
            messages.success(request, 'Registration Successful! You can login now.')
        else:
            messages.info(request, 'Registration Successful! Your account is sent for approval.')

        return redirect('alumni_login')

    return render(request, 'register.html', {'departments': departments})

def alumni_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('alumni_login')

@login_required(login_url='alumni_login')
def alumni_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    jobs_count = Job.objects.count()
    events_count = Event.objects.count()
    alumni_count = UserProfile.objects.filter(role='alumni', is_approved=True).count()
    return render(request, 'dashboard.html', {
        'profile': profile, 'jobs_count': jobs_count,
        'events_count': events_count, 'alumni_count': alumni_count
    })

@login_required(login_url='alumni_login')
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs.html', {'jobs': jobs})

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

@login_required(login_url='alumni_login')
def alumni_directory(request):
    profiles = UserProfile.objects.filter(is_approved=True).select_related('user', 'department')
    return render(request, 'directory.html', {'profiles': profiles})
"""
with open('alumni/views.py', 'w') as f: f.write(views_code)

# 3. URLs Update
urls_code = """from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.alumni_login, name='alumni_login'),
    path('register/', views.alumni_register, name='alumni_register'),
    path('logout/', views.alumni_logout, name='alumni_logout'),
    path('dashboard/', views.alumni_dashboard, name='alumni_dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('events/', views.event_list, name='event_list'),
    path('events/register/<int:event_id>/', views.register_event, name='register_event'),
    path('directory/', views.alumni_directory, name='alumni_directory'),
]
"""
with open('alumni/urls.py', 'w') as f: f.write(urls_code)

# 4. HTML Templates Generation
os.makedirs('templates', exist_ok=True)

with open('templates/dashboard.html', 'w') as f:
    f.write("""{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - MACFAST Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>:root { --macfast-maroon: #800000; } body { background-color: #f4f5f7; } .bg-maroon { background-color: var(--macfast-maroon); color: white; }</style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-maroon px-4 shadow">
    <a class="navbar-brand fw-bold" href="{% url 'alumni_dashboard' %}"><i class="fa-solid fa-graduation-cap text-warning me-2"></i>MACFAST Portal</a>
    <div class="ms-auto d-flex gap-2">
        <a href="{% url 'alumni_directory' %}" class="btn btn-outline-light btn-sm">Directory</a>
        <a href="{% url 'job_list' %}" class="btn btn-outline-light btn-sm">Jobs</a>
        <a href="{% url 'event_list' %}" class="btn btn-outline-light btn-sm">Events</a>
        <a href="{% url 'alumni_logout' %}" class="btn btn-warning btn-sm fw-bold">Logout</a>
    </div>
</nav>
<div class="container my-5">
    {% if messages %}{% for message in messages %}<div class="alert alert-{{ message.tags }}">{{ message }}</div>{% endfor %}{% endif %}
    <div class="card shadow-sm border-0 mb-4 p-4 border-start border-danger border-5">
        <h2 class="fw-bold mb-1">Welcome, {{ user.first_name }}! 👋</h2>
        <p class="text-muted m-0">Role: <strong class="text-capitalize text-danger">{{ profile.role }}</strong> | Department: {{ profile.department.name }}</p>
    </div>
    <div class="row g-4">
        <div class="col-md-4"><div class="card bg-white shadow-sm p-4 text-center"><i class="fa-solid fa-users fs-1 text-danger mb-2"></i><h3 class="fw-bold">{{ alumni_count }}</h3><p class="text-muted">Approved Members</p><a href="{% url 'alumni_directory' %}" class="btn btn-outline-danger btn-sm rounded-pill">View Directory</a></div></div>
        <div class="col-md-4"><div class="card bg-white shadow-sm p-4 text-center"><i class="fa-solid fa-briefcase fs-1 text-warning mb-2"></i><h3 class="fw-bold">{{ jobs_count }}</h3><p class="text-muted">Job Openings</p><a href="{% url 'job_list' %}" class="btn btn-outline-warning text-dark btn-sm rounded-pill">Explore Jobs</a></div></div>
        <div class="col-md-4"><div class="card bg-white shadow-sm p-4 text-center"><i class="fa-solid fa-calendar-days fs-1 text-primary mb-2"></i><h3 class="fw-bold">{{ events_count }}</h3><p class="text-muted">Upcoming Events</p><a href="{% url 'event_list' %}" class="btn btn-outline-primary btn-sm rounded-pill">View Events</a></div></div>
    </div>
</div>
</body>
</html>""")

with open('templates/jobs.html', 'w') as f:
    f.write("""<!DOCTYPE html><html><head><title>Jobs</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head><body class="bg-light"><div class="container my-5"><div class="d-flex justify-content-between mb-4"><h2 class="fw-bold text-danger">Job Opportunities</h2><div><a href="{% url 'add_job' %}" class="btn btn-danger fw-bold">+ Post Job</a> <a href="{% url 'alumni_dashboard' %}" class="btn btn-secondary">Dashboard</a></div></div>{% if messages %}{% for message in messages %}<div class="alert alert-{{ message.tags }}">{{ message }}</div>{% endfor %}{% endif %}<div class="row g-4">{% for job in jobs %}<div class="col-md-6"><div class="card shadow-sm p-4"><h4 class="fw-bold">{{ job.title }}</h4><h6 class="text-danger">{{ job.company }} - {{ job.location }}</h6><p class="text-muted">{{ job.description }}</p><hr><div class="d-flex justify-content-between align-items-center"><small>Posted by: {{ job.posted_by.first_name }}</small><a href="mailto:{{ job.contact_email }}" class="btn btn-outline-danger btn-sm">Apply / Email</a></div></div></div>{% empty %}<p>No jobs listed.</p>{% endfor %}</div></div></body></html>""")

with open('templates/add_job.html', 'w') as f:
    f.write("""<!DOCTYPE html><html><head><title>Post Job</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head><body class="bg-light py-5"><div class="container" style="max-width:600px;"><div class="card shadow p-4"><h3 class="fw-bold text-danger mb-3">Post a Job</h3><form method="POST">{% csrf_token %}<div class="mb-3"><label>Title</label><input type="text" name="title" class="form-control" required></div><div class="mb-3"><label>Company</label><input type="text" name="company" class="form-control" required></div><div class="mb-3"><label>Location</label><input type="text" name="location" class="form-control" required></div><div class="mb-3"><label>Email</label><input type="email" name="contact_email" class="form-control" required></div><div class="mb-3"><label>Description</label><textarea name="description" class="form-control" rows="4" required></textarea></div><button type="submit" class="btn btn-danger w-100 fw-bold">Post</button></form></div></div></body></html>""")

with open('templates/events.html', 'w') as f:
    f.write("""<!DOCTYPE html><html><head><title>Events</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head><body class="bg-light"><div class="container my-5"><div class="d-flex justify-content-between mb-4"><h2 class="fw-bold text-danger">Events</h2><a href="{% url 'alumni_dashboard' %}" class="btn btn-secondary">Dashboard</a></div>{% if messages %}{% for message in messages %}<div class="alert alert-{{ message.tags }}">{{ message }}</div>{% endfor %}{% endif %}<div class="row g-4">{% for event in events %}<div class="col-md-6"><div class="card shadow-sm p-4"><h4 class="fw-bold">{{ event.title }}</h4><p class="text-danger">Date: {{ event.date }} | Location: {{ event.location }}</p><p class="text-muted">{{ event.description }}</p><a href="{% url 'register_event' event.id %}" class="btn btn-warning fw-bold text-dark w-100">RSVP / Register</a></div></div>{% empty %}<p>No events announced.</p>{% endfor %}</div></div></body></html>""")

with open('templates/directory.html', 'w') as f:
    f.write("""<!DOCTYPE html><html><head><title>Directory</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head><body class="bg-light"><div class="container my-5"><div class="d-flex justify-content-between mb-4"><h2 class="fw-bold text-danger">Directory</h2><a href="{% url 'alumni_dashboard' %}" class="btn btn-secondary">Dashboard</a></div><div class="card shadow-sm p-3"><table class="table table-hover"><thead><tr><th>Name</th><th>Role</th><th>Dept</th><th>Email/Phone</th><th>Info</th></tr></thead><tbody>{% for p in profiles %}<tr><td class="fw-bold">{{ p.user.first_name }}</td><td><span class="badge bg-danger text-capitalize">{{ p.role }}</span></td><td>{{ p.department.name }}</td><td>{{ p.user.email }}<br><small class="text-muted">{{ p.phone }}</small></td><td>{% if p.role == 'alumni' %}{{ p.company }} ({{ p.designation }}){% elif p.role == 'student' %}Sem: {{ p.current_semester }}{% elif p.role == 'faculty' %}ID: {{ p.employee_id }}{% endif %}</td></tr>{% endfor %}</tbody></table></div></div></body></html>""")

print("ALL PORTAL FEATURES UPDATED SUCCESSFULLY!")