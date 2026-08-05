"""Console entrypoints for common Django management commands."""

from __future__ import annotations

import os
import sys

from django.core.management import execute_from_command_line


def _run(command: str | None = None) -> None:
    """Execute a Django management command with passthrough arguments."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    argv = ["manage"]
    if command is not None:
        argv.append(command)
    argv.extend(sys.argv[1:])

    execute_from_command_line(argv)


def manage() -> None:
    """Run generic Django management commands.

    Example:
        uv run dj-manage migrate
    """
    _run()


def migrate() -> None:
    """Run Django migrate command."""
    _run("migrate")


def makemigrations() -> None:
    """Run Django makemigrations command."""
    _run("makemigrations")


def runserver() -> None:
    """Run Django development server."""
    _run("runserver")


def seed_tasks() -> None:
    """Run custom seed_tasks command."""
    _run("seed_tasks")
