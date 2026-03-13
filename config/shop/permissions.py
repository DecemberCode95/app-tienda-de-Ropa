from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow owner to modify their content.
    Read-only access for others.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow admin to modify content.
    Read-only access for others.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAuthenticated(permissions.BasePermission):
    """
    Allow authenticated users only.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
