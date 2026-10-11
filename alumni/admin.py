from django.contrib import admin
from .models import (
    Department, Job, Event, EventRegistration, DirectMessage,
    AlumniUser, FacultyUser, StudentUser
)

# Base Admin configuration
class BaseProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'register_no', 'department', 'phone', 'is_approved')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'department', 'gender')
    search_fields = ('user__first_name', 'register_no', 'phone', 'company', 'employee_id')

    def get_full_name(self, obj):
        return obj.user.first_name or obj.user.username
    get_full_name.short_description = 'Name'

@admin.register(AlumniUser)
class AlumniUserAdmin(BaseProfileAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='alumni')

@admin.register(FacultyUser)
class FacultyUserAdmin(BaseProfileAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='faculty')

@admin.register(StudentUser)
class StudentUserAdmin(BaseProfileAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='student')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_by', 'created_at')
    list_filter = ('company', 'created_at')
    search_fields = ('title', 'company', 'description')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'created_at')
    list_filter = ('date',)
    search_fields = ('title', 'location')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registered_at')
    list_filter = ('event', 'registered_at')

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'subject', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('subject', 'message')