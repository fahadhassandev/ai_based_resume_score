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

    def test_task_priority_choices(self):
        self.task.priority = Task.PRIORITY_HIGH
        self.task.save()
        self.assertEqual(self.task.priority, Task.PRIORITY_HIGH)

        self.task.priority = Task.PRIORITY_MEDIUM
        self.task.save()
        self.assertEqual(self.task.priority, Task.PRIORITY_MEDIUM)

        self.task.priority = Task.PRIORITY_LOW
        self.task.save()
        self.assertEqual(self.task.priority, Task.PRIORITY_LOW)

    def test_task_status_choices(self):
        self.task.status = Task.STATUS_TODO
        self.task.save()
        self.assertEqual(self.task.status, Task.STATUS_TODO)

        self.task.status = Task.STATUS_IN_PROGRESS
        self.task.save()
        self.assertEqual(self.task.status, Task.STATUS_IN_PROGRESS)

        self.task.status = Task.STATUS_COMPLETED
        self.task.save()
        self.assertEqual(self.task.status, Task.STATUS_COMPLETED)

    def test_task_assignment(self):
        new_user = User.objects.create_user(
            username='assignee',
            password='testpass123'
        )
        self.task.assigned_to = new_user
        self.task.save()
        self.assertEqual(self.task.assigned_to, new_user)

    def test_task_attachment(self):
        attachment = TaskAttachment.objects.create(
            task=self.task,
            file='test.txt',
            uploaded_by=self.user
        )
        self.assertEqual(
            str(attachment),
            f"Attachment for {self.task.title}"
        )
        self.assertEqual(attachment.uploaded_by, self.user)

    def test_task_comment(self):
        comment = TaskComment.objects.create(
            task=self.task,
            author=self.user,
            content='Test comment content'
        )
        self.assertEqual(comment.content, 'Test comment content')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(
            str(comment),
            f"Comment by {self.user.username} on {self.task.title}"
        )

    def test_task_history(self):
        new_user = User.objects.create_user(
            username='new_assignee',
            password='testpass123'
        )
        history = TaskHistory.objects.create(
            task=self.task,
            changed_by=self.user,
            old_status=Task.STATUS_TODO,
            new_status=Task.STATUS_IN_PROGRESS,
            old_assigned_to=self.user,
            new_assigned_to=new_user,
            notes='Status and assignee changed'
        )
        self.assertEqual(history.old_status, Task.STATUS_TODO)
        self.assertEqual(history.new_status, Task.STATUS_IN_PROGRESS)
        self.assertEqual(history.old_assigned_to, self.user)
        self.assertEqual(history.new_assigned_to, new_user)
        self.assertEqual(history.notes, 'Status and assignee changed')

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
