from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Recommended way to get the User model dynamically

class Role(models.Model):
    ADMIN = 'admin'
    PROJECT_MANAGER = 'project_manager'
    TEAM_MEMBER = 'team_member'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (PROJECT_MANAGER, 'Project Manager'),
        (TEAM_MEMBER, 'Team Member'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
