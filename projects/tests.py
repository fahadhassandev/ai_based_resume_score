from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from tests.test_utils import TestCaseWithSetup
from .models import Project, ProjectMember

class ProjectModelTests(TestCase, TestCaseWithSetup):
    def setUp(self):
        self.user = self.create_test_user()
        self.project = self.create_test_project(self.user)

    def test_project_creation(self):
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.created_by, self.user)
        self.assertEqual(str(self.project), 'Test Project')

    def test_project_member_creation(self):
        member = ProjectMember.objects.create(
            project=self.project,
            user=self.user
        )
        self.assertEqual(str(member), f"{self.user.username} - {self.project.name}")
        self.assertTrue(
            ProjectMember.objects.filter(
                project=self.project,
                user=self.user
            ).exists()
        )

class ProjectAPITests(APITestCase, TestCaseWithSetup):
    def setUp(self):
        self.user = self.create_test_user()
        self.client.force_authenticate(user=self.user)
        self.project_data = {
            'name': 'API Test Project',
            'description': 'API Test Description',
            'start_date': timezone.now().date().isoformat(),
            'end_date': timezone.now().date().isoformat(),
            'status': Project.STATUS_ACTIVE
        }

    def test_create_project(self):
        response = self.client.post('/api/projects/', self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'API Test Project')

    def test_list_projects(self):
        self.create_test_project(self.user)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
