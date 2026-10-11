from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

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
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True, null=True)

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

    def __str__(self):
        return f"{self.title} - {self.company}"

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.subject}"

# Proxy Models Admin Panel-il Student, Faculty, Alumni ennivayee alavaniyal section aayi kanikkan
class AdminUser(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

class AlumniUser(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Alumni'
        verbose_name_plural = 'Alumnis'

class FacultyUser(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'

class StudentUser(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Student'
        verbose_name_plural = 'Students'



class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title        