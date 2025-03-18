from rest_framework import serializers
from tasks.models import Task
from projects.models import Project

class TaskOverviewSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority',
            'due_date', 'project_name'
        ]

class DashboardSerializer(serializers.Serializer):
    projects_count = serializers.IntegerField()
    task_stats = serializers.DictField()
    recent_tasks = TaskOverviewSerializer(many=True)
    urgent_tasks = TaskOverviewSerializer(many=True)
