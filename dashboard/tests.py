from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status as http_status
from tests.test_utils import TestCaseWithSetup
from tasks.models import Task

class DashboardAPITests(APITestCase, TestCaseWithSetup):
    def setUp(self):
        self.user = self.create_test_user()
        self.client.force_authenticate(user=self.user)
        self.project = self.create_test_project(self.user)
        self.create_test_tasks()

    def create_test_tasks(self):
        statuses = [Task.STATUS_TODO, Task.STATUS_IN_PROGRESS, Task.STATUS_COMPLETED]
        for task_status in statuses:
            Task.objects.create(
                title=f'Test Task {task_status}',
                description='Test Description',
                project=self.project,
                created_by=self.user,
                status=task_status,
                priority=Task.PRIORITY_HIGH,
                due_date=timezone.now()
            )

    def test_dashboard_access(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_dashboard_content(self):
        response = self.client.get('/api/dashboard/')
        data = response.data
        self.assertEqual(data['projects_count'], 1)
        self.assertEqual(data['task_stats']['total'], 3)
        self.assertEqual(len(data['recent_tasks']), 3)
        self.assertEqual(len(data['urgent_tasks']), 2)
