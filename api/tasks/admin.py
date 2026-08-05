"""Admin configuration for task models."""

from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for listing and searching tasks."""

    list_display = ("id", "title", "done", "created_at")
    list_filter = ("done", "created_at")
    search_fields = ("title", "content")
