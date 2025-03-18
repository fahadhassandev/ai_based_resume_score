from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from tests.test_utils import TestCaseWithSetup
from .models import Task, TaskComment, TaskHistory

class TaskModelTests(TestCase, TestCaseWithSetup):
    def setUp(self):
        self.user = self.create_test_user()
        self.project = self.create_test_project(self.user)
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

class TaskAPITests(APITestCase, TestCaseWithSetup):
    def setUp(self):
        self.user = self.create_test_user()
        self.client.force_authenticate(user=self.user)
        self.project = self.create_test_project(self.user)
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
