from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status as http_status
from tests.test_utils import TestCaseWithSetup
from tasks.models import Task
from projects.models import Project

class DashboardAPITests(APITestCase, TestCaseWithSetup):
    def setUp(self):
        self.user = self.create_test_user('testuser1')
        self.other_user = self.create_test_user('testuser2')
        self.client.force_authenticate(user=self.user)
        self.project = self.create_test_project(self.user)
        self.create_test_tasks()

    def create_test_tasks(self):
        statuses = [Task.STATUS_TODO, Task.STATUS_IN_PROGRESS, Task.STATUS_COMPLETED]
        priorities = [Task.PRIORITY_HIGH, Task.PRIORITY_MEDIUM, Task.PRIORITY_LOW]

        for task_status in statuses:
            for priority in priorities:
                Task.objects.create(
                    title=f'Test Task {task_status} {priority}',
                    description='Test Description',
                    project=self.project,
                    created_by=self.user,
                    status=task_status,
                    priority=priority,
                    due_date=timezone.now()
                )

    def test_dashboard_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, http_status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_authorized_access(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_dashboard_content_structure(self):
        response = self.client.get('/api/dashboard/')
        data = response.data
        expected_keys = {'projects_count', 'task_stats', 'recent_tasks', 'urgent_tasks'}
        self.assertEqual(set(data.keys()), expected_keys)

    def test_dashboard_task_stats(self):
        response = self.client.get('/api/dashboard/')
        stats = response.data['task_stats']
        expected_stats = {
            'total': 9,
            'todo': 3,
            'in_progress': 3,
            'completed': 3
        }
        self.assertEqual(stats, expected_stats)

    def test_dashboard_project_count(self):
        Project.objects.create(
            name='Second Project',
            description='Test Description',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            created_by=self.user
        )
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.data['projects_count'], 2)

    def test_dashboard_urgent_tasks(self):
        response = self.client.get('/api/dashboard/')
        urgent_tasks = response.data['urgent_tasks']
        self.assertTrue(all(
            task['priority'] == Task.PRIORITY_HIGH
            for task in urgent_tasks
        ))
        self.assertTrue(all(
            task['status'] in [Task.STATUS_TODO, Task.STATUS_IN_PROGRESS]
            for task in urgent_tasks
        ))

    def test_dashboard_recent_tasks(self):
        response = self.client.get('/api/dashboard/')
        recent_tasks = response.data['recent_tasks']
        self.assertLessEqual(len(recent_tasks), 5)

        # Verify tasks are ordered by updated_a
        dates = [task['due_date'] for task in recent_tasks]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_dashboard_task_visibility(self):
        # Create task assigned to other user
        other_project = self.create_test_project(self.other_user)
        Task.objects.create(
            title='Other User Task',
            description='Test Description',
            project=other_project,
            created_by=self.other_user,
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_HIGH,
            due_date=timezone.now()
        )

        response = self.client.get('/api/dashboard/')
        task_titles = [
            task['title'] for task in response.data['recent_tasks']
        ]
        self.assertNotIn('Other User Task', task_titles)
