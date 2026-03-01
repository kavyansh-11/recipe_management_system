from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'
    
class IsCreator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['superadmin', 'creator']

class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['superadmin', 'creator', 'viewer']