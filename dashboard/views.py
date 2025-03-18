from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from projects.models import Project
from tasks.models import Task
from .serializers import DashboardSerializer

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        projects_count = Project.objects.filter(
            Q(created_by=user) | Q(members__user=user)
        ).distinct().count()

        tasks = Task.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).distinct()

        task_stats = {
            'total': tasks.count(),
            'todo': tasks.filter(status=Task.STATUS_TODO).count(),
            'in_progress': tasks.filter(status=Task.STATUS_IN_PROGRESS).count(),
            'completed': tasks.filter(status=Task.STATUS_COMPLETED).count()
        }

        recent_tasks = tasks.order_by('-updated_at')[:5]
        urgent_tasks = tasks.filter(
            priority=Task.PRIORITY_HIGH,
            status__in=[Task.STATUS_TODO, Task.STATUS_IN_PROGRESS]
        )[:5]

        data = {
            'projects_count': projects_count,
            'task_stats': task_stats,
            'recent_tasks': recent_tasks,
            'urgent_tasks': urgent_tasks
        }
        serializer = DashboardSerializer(data)
        return Response(serializer.data)
