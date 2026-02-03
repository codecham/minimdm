from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission that only allows admin users (is_staff=True).
    """
    
    def has_permission(self, request, _view):
        return request.user and request.user.is_staff


class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission for user detail view:
    - Admin can see any user
    - Regular users can only see their own profile
    """
    
    def has_object_permission(self, request, _view, obj):
        # Admin can access any user
        if request.user.is_staff:
            return True
        
        # Regular users can only access their own profile
        return obj == request.user