from django.contrib.auth import get_user_model
from django.utils import timezone
from projects.models import Project

User = get_user_model()

class TestCaseWithSetup:
    def create_test_user(self):
        return User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def create_test_project(self, user):
        return Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            created_by=user
        )