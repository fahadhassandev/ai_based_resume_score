from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status
from .models import Task, TaskHistory
from .serializers import TaskSerializer, TaskHistorySerializer

class TaskViewSet(viewsets.ModelViewSet):
    def perform_update(self, serializer):
        task = self.get_object()
        old_status = task.status
        old_assigned_to = task.assigned_to
        
        updated_task = serializer.save()
        
        if (old_status != updated_task.status or 
            old_assigned_to != updated_task.assigned_to):
            TaskHistory.objects.create(
                task=updated_task,
                changed_by=self.request.user,
                old_status=old_status,
                new_status=updated_task.status,
                old_assigned_to=old_assigned_to,
                new_assigned_to=updated_task.assigned_to,
                notes=f"Status changed from {old_status} to {updated_task.status}"
            )

    @action(detail=True)
    def history(self, request, *args, **kwargs):
        task = self.get_object()
        history = task.history.all().order_by('-changed_at')
        serializer = TaskHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_status(self, request, *args, **kwargs):
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        old_status = task.status
        task.status = new_status
        task.save()
        
        TaskHistory.objects.create(
            task=task,
            changed_by=request.user,
            old_status=old_status,
            new_status=new_status,
            notes=f"Status manually changed to {new_status}"
        )
        
        return Response({'status': 'Status updated successfully'})
