"""Django URL configuration for the Task application."""

from typing import TYPE_CHECKING

from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter

from .views import TaskReportAPIView, TaskViewSet

if TYPE_CHECKING:
    from rest_framework.request import Request

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")


@api_view(["GET"])
def api_root(request: Request) -> Response:
    """Return root links for core API endpoints."""
    return Response(
        {
            "tasks": reverse("task-list", request=request),
            "report": reverse("report", request=request),
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("report/", TaskReportAPIView.as_view(), name="report"),
    path("tasks/report/", TaskReportAPIView.as_view(), name="tasks-report"),
    path("", include(router.urls)),
]
