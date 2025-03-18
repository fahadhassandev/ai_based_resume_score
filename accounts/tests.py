from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Role, UserProfile

User = get_user_model()

class RoleModelTest(TestCase):
    """Test cases for Role model"""

    def setUp(self):
        self.role = Role.objects.create(name=Role.ADMIN)

    def test_role_creation(self):
        """Test role creation"""
        self.assertEqual(self.role.name, Role.ADMIN)
        self.assertEqual(str(self.role), Role.ADMIN)

    def test_role_choices(self):
        """Test role choices validation"""
        roles = [role[0] for role in Role.ROLE_CHOICES]
        self.assertIn(Role.ADMIN, roles)
        self.assertIn(Role.PROJECT_MANAGER, roles)
        self.assertIn(Role.TEAM_MEMBER, roles)

class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.role = Role.objects.create(name=Role.TEAM_MEMBER)
        self.profile = UserProfile.objects.create(
            user=self.user,
            role=self.role,
            phone='1234567890',
            bio='Test bio'
        )

    def test_profile_creation(self):
        """Test profile creation"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.role.name, Role.TEAM_MEMBER)
        self.assertEqual(str(self.profile), "testuser's profile")

class AuthenticationTest(APITestCase):
    """Test cases for authentication endpoints"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
        Role.objects.create(name=Role.TEAM_MEMBER)

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data"""
        invalid_data = {
            'username': '',
            'password': 'test'
        }
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ProfileViewTest(APITestCase):
    """Test cases for profile view"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.role = Role.objects.create(name=Role.TEAM_MEMBER)
        self.profile = UserProfile.objects.create(
            user=self.user,
            role=self.role
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('profile')

    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['role_name'], Role.TEAM_MEMBER)

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PermissionTest(APITestCase):
    """Test cases for custom permissions"""

    def setUp(self):
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.pm_role = Role.objects.create(name=Role.PROJECT_MANAGER)
        self.team_role = Role.objects.create(name=Role.TEAM_MEMBER)

        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.pm_user = User.objects.create_user(
            username='pm',
            password='pm123'
        )
        self.team_user = User.objects.create_user(
            username='team',
            password='team123'
        )

        UserProfile.objects.create(user=self.admin_user, role=self.admin_role)
        UserProfile.objects.create(user=self.pm_user, role=self.pm_role)
        UserProfile.objects.create(user=self.team_user, role=self.team_role)

    def test_admin_permission(self):
        """Test admin permissions"""
        self.client.force_authenticate(user=self.admin_user)
        # Add your admin-specific endpoint test here
        self.assertTrue(self.admin_user.profile.role.name == Role.ADMIN)

    def test_project_manager_permission(self):
        """Test project manager permissions"""
        self.client.force_authenticate(user=self.pm_user)
        # Add your project manager-specific endpoint test here
        self.assertTrue(self.pm_user.profile.role.name == Role.PROJECT_MANAGER)
