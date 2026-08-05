"""Django models for the Task application."""

from django.db import models


class Task(models.Model):
    """Model representing a task.

    Attributes:
        title (str): The title of the task.
        content (str): The content or description of the task.
        done (bool): The done of the task, indicating whether it is completed or not.
        created_at (datetime): The timestamp when the task was created.
    """

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for the Task model.

        Defines the ordering of Task instances when queried from the database.
        """

        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Return a string representation of the Task instance."""
        return f"{self.id} - {self.title}"
