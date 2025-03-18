from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Project
from .models import Task, TaskComment, TaskAttachment, TaskHistory

User = get_user_model()

class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            created_by=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            due_date=timezone.now()
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.created_by, self.user)
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_comment_creation(self):
        comment = TaskComment.objects.create(
            task=self.task,
            author=self.user,
            content='Test Comment'
        )
        self.assertEqual(
            str(comment),
            f"Comment by {self.user.username} on {self.task.title}"
        )

    def test_task_history_creation(self):
        history = TaskHistory.objects.create(
            task=self.task,
            changed_by=self.user,
            old_status=Task.STATUS_TODO,
            new_status=Task.STATUS_IN_PROGRESS
        )
        self.assertEqual(history.old_status, Task.STATUS_TODO)
        self.assertEqual(history.new_status, Task.STATUS_IN_PROGRESS)

class TaskAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            created_by=self.user
        )
        self.task_data = {
            'title': 'API Test Task',
            'description': 'API Test Description',
            'project': self.project.id,
            'priority': Task.PRIORITY_HIGH,
            'status': Task.STATUS_TODO,
            'due_date': timezone.now()
        }

    def test_create_task(self):
        response = self.client.post('/api/tasks/', self.task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'API Test Task')

    def test_change_task_status(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            due_date=timezone.now()
        )
        response = self.client.post(
            f'/api/tasks/{task.id}/change_status/',
            {'status': Task.STATUS_IN_PROGRESS}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.STATUS_IN_PROGRESS)
