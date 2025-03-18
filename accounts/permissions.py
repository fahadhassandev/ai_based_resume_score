from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.role.name == 'admin'

class IsProjectManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.role.name == 'project_manager'
