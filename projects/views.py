from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Project, ProjectMember
from .serializers import ProjectSerializer, ProjectMemberSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        ProjectMember.objects.create(project=project, user=self.request.user)

    def get_queryset(self):
        return Project.objects.filter(
            Q(created_by=self.request.user) |
            Q(members__user=self.request.user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def add_member(self, request, *args, **kwargs):
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            ProjectMember.objects.create(project=project, user=user)
            return Response({'status': 'Member added successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True)
    def statistics(self, request, *args, **kwargs):
        project = self.get_object()
        stats = {
            'total_tasks': project.tasks.count(),
            'completed_tasks': project.tasks.filter(
                status=Task.STATUS_COMPLETED
            ).count(),
            'in_progress_tasks': project.tasks.filter(
                status=Task.STATUS_IN_PROGRESS
            ).count(),
            'todo_tasks': project.tasks.filter(status=Task.STATUS_TODO).count(),
            'team_members': project.members.count()
        }
        return Response(stats)
