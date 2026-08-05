from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskViewSet, TaskReportAPIView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path("", include(router.urls)),
    path("report/", TaskReportAPIView.as_view(), name="task-report"),
]