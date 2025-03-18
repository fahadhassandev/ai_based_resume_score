from rest_framework import serializers
from .models import Task, TaskAttachment, TaskComment, TaskHistory

class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_by']

class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'content', 'author', 'author_name', 'created_at', 'updated_at']
        read_only_fields = ['author']

class TaskSerializer(serializers.ModelSerializer):
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name', 'priority', 'status', 'due_date',
            'created_at', 'updated_at', 'attachments', 'comments'
        ]
        read_only_fields = ['created_by']

class TaskHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    old_assigned_to_name = serializers.CharField(
        source='old_assigned_to.username',
        read_only=True
    )
    new_assigned_to_name = serializers.CharField(
        source='new_assigned_to.username',
        read_only=True
    )

    class Meta:
        model = TaskHistory
        fields = [
            'id', 'changed_by', 'changed_by_name', 'old_status', 'new_status',
            'old_assigned_to', 'old_assigned_to_name', 'new_assigned_to',
            'new_assigned_to_name', 'changed_at', 'notes'
        ]
        read_only_fields = ['changed_by']
