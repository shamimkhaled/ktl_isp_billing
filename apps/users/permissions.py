from rest_framework import permissions


class IsSuperAdminOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow super admin and admin users to perform write operations.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to perform the action.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow super admin and admin user types
        return request.user.user_type in ['super_admin', 'admin']
