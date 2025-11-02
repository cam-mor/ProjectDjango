from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.http import FileResponse, Http404
from django.urls import path
from django.conf import settings
import shutil
from pathlib import Path
from .models import (
    Profile, Subject, StudyGroup, GroupMembership,
    StudySession, StudyMaterial, Comment, Notification
)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'get_study_hours')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def get_study_hours(self, obj):
        # Calculate total study hours from attended sessions
        total_hours = StudySession.objects.filter(
            group__members=obj,
            status='completed'
        ).extra(
            select={'duration': "ROUND(CAST((JULIANDAY(end_time) - JULIANDAY(start_time)) * 24 AS NUMERIC), 2)"}
        ).aggregate(total=models.Sum('duration'))['total'] or 0
        return f"{total_hours:.2f} hours"
    get_study_hours.short_description = 'Total Study Hours'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'major', 'created_at', 'get_groups_count', 'get_study_hours')
    search_fields = ('user__username', 'major', 'interests')
    list_filter = ('major', 'created_at')
    
    def get_groups_count(self, obj):
        return obj.user.study_groups.count()
    get_groups_count.short_description = 'Groups'
    
    def get_study_hours(self, obj):
        total_hours = StudySession.objects.filter(
            group__members=obj.user,
            status='completed'
        ).extra(
            select={'duration': "ROUND(CAST((JULIANDAY(end_time) - JULIANDAY(start_time)) * 24 AS NUMERIC), 2)"}
        ).aggregate(total=models.Sum('duration'))['total'] or 0
        return f"{total_hours:.2f} hours"
    get_study_hours.short_description = 'Study Hours'

    def get_urls(self):
        """Add custom admin URL for downloading the local SQLite database."""
        urls = super().get_urls()
        custom_urls = [
            path('<int:profile_id>/download_db/', self.admin_site.admin_view(self.download_db_view), name='core_profile_download_db'),
            path('<int:profile_id>/download_exports/', self.admin_site.admin_view(self.download_exports_zip_view), name='core_profile_download_exports'),
        ]
        return custom_urls + urls

    def download_db_view(self, request, profile_id, *args, **kwargs):
        """Return the project's SQLite database file as a downloadable attachment.

        Only staff users can access this view (enforced by admin_view).
        """
        # Optional: verify profile exists (gives nicer 404 if not)
        try:
            profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            raise Http404('Profile not found')

        # Only allow staff (admin) users to download
        if not request.user.is_staff:
            raise Http404('Not allowed')

        db_path = settings.BASE_DIR / 'db.sqlite3'
        if not db_path.exists():
            raise Http404('Database file not found')

        # Serve the file
        try:
            response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename='project_db.sqlite3')
            return response
        except Exception:
            raise Http404('Could not read database file')

    def download_exports_zip_view(self, request, profile_id, *args, **kwargs):
        """Create (or refresh) a zip of the exports/ folder and return it as attachment.

        Only staff users can access this view (enforced by admin_view).
        """
        # Verify profile exists
        try:
            profile = Profile.objects.get(pk=profile_id)
        except Profile.DoesNotExist:
            raise Http404('Profile not found')

        if not request.user.is_staff:
            raise Http404('Not allowed')

        exports_dir = Path(settings.BASE_DIR) / 'exports'
        if not exports_dir.exists():
            raise Http404('Exports directory not found')

        # Create zip at project root: exports.zip (overwrite if exists)
        base_name = str(Path(settings.BASE_DIR) / 'exports')
        try:
            # shutil.make_archive will create base_name + .zip
            shutil.make_archive(base_name, 'zip', root_dir=str(exports_dir))
            zip_path = Path(base_name + '.zip')
            response = FileResponse(open(zip_path, 'rb'), as_attachment=True, filename='exports.zip')
            return response
        except Exception:
            raise Http404('Could not create exports zip')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_by', 'is_active', 'created_at')
    list_filter = ('subject', 'is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__username', 'group__name')

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'is_online')
    search_fields = ('title', 'description', 'location')

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'uploaded_by', 'created_at', 'has_file', 'has_link')
    list_filter = ('created_at', 'group')
    search_fields = ('title', 'description')
    
    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    
    def has_link(self, obj):
        return bool(obj.link)
    has_link.boolean = True

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'group', 'content_preview', 'created_at', 'is_edited')
    list_filter = ('created_at', 'is_edited', 'group')
    search_fields = ('content', 'author__username', 'group__name')
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    date_hierarchy = 'created_at'