"""Seed sample Task records for local development."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand

from tasks.models import Task

if TYPE_CHECKING:
    from argparse import ArgumentParser

SAMPLE_TITLES = [
    "Prepare sprint planning",
    "Review pull requests",
    "Write API documentation",
    "Fix login bug",
    "Update dependencies",
    "Plan database migration",
    "Create frontend wireframe",
    "Validate report endpoint",
    "Refactor task serializer",
    "Deploy staging build",
]

SAMPLE_CONTENTS = [
    "Break down work into small actionable steps.",
    "Add tests and verify edge cases before merge.",
    "Coordinate with teammates and share status update.",
    "Document assumptions and expected behavior.",
    "Prioritize based on urgency and user impact.",
]


class Command(BaseCommand):
    """Create fake task rows to speed up local testing."""

    help = "Seed sample tasks into the database."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Register command line arguments."""
        parser.add_argument("--count", type=int, default=20, help="Number of tasks to create.")
        parser.add_argument(
            "--completed-ratio",
            type=float,
            default=0.35,
            help="Ratio of completed tasks between 0.0 and 1.0.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing tasks before seeding.",
        )

    def handle(self, *args: object, **options: object) -> str:
        """Create the requested amount of tasks and print a summary."""
        count = int(options["count"])
        completed_ratio = float(options["completed_ratio"])
        reset = bool(options["reset"])

        if count < 1:
            self.stderr.write(self.style.ERROR("count must be >= 1"))
            return ""
        if completed_ratio < 0.0 or completed_ratio > 1.0:
            self.stderr.write(self.style.ERROR("completed-ratio must be between 0.0 and 1.0"))
            return ""

        if reset:
            deleted_count, _ = Task.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted_count} existing tasks."))

        tasks_to_create: list[Task] = []
        for index in range(count):
            title_seed = SAMPLE_TITLES[index % len(SAMPLE_TITLES)]
            content_seed = SAMPLE_CONTENTS[index % len(SAMPLE_CONTENTS)]
            is_completed = random.random() < completed_ratio

            tasks_to_create.append(
                Task(
                    title=f"{title_seed} #{index + 1}",
                    content=content_seed,
                    completed=is_completed,
                )
            )

        Task.objects.bulk_create(tasks_to_create)

        completed = sum(1 for task in tasks_to_create if task.completed)
        pending = count - completed

        self.stdout.write(self.style.SUCCESS(f"Created {count} tasks (completed={completed}, pending={pending})."))
        return ""
