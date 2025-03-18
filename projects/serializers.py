from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, ProjectMember

User = get_user_model()

class ProjectMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'username', 'joined_at']
        read_only_fields = ['joined_at']

class ProjectSerializer(serializers.ModelSerializer):
    members = ProjectMemberSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    total_tasks = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'status', 'members', 'total_tasks'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
