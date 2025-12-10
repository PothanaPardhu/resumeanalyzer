from django.contrib import admin
from .models import Profile, Resume, JobDescription, Analysis

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'github_username')
    search_fields = ('user__username', 'github_username')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at')
    search_fields = ('user__username',)
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at',)


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'jd', 'score', 'created_at')
    search_fields = ('resume_userusername', 'jd_title')
    list_filter = ('created_at', 'score')
    readonly_fields = ('created_at', 'github_matches')