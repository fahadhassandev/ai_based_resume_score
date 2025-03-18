from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as http_status
from django.shortcuts import get_object_or_404
from .models import Task, TaskAttachment, TaskComment
from .serializers import TaskSerializer, TaskAttachmentSerializer, TaskCommentSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        queryset = Task.objects.all()
        project_id = self.request.query_params.get('project', None)
        task_status = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if task_status:
            queryset = queryset.filter(status=task_status)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskAttachmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(task=task, uploaded_by=request.user)
            return Response(serializer.data, status=http_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=http_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
