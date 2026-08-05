"""Django app configuration for tasks."""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Configuration class for the tasks Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"
