from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsAdminRole(BasePermission):
    """
    Allows access only to users with admin role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin'
    


class IsUserRole(BasePermission):
    """
    Allows access only to users with user role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'user'
    


class IsAdminOrUser(BasePermission):
    """
    Allows access to users with admin or user role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) in ['admin', 'user']



class IsSelfOrAdminDeletingUser(BasePermission):
    """
    - Allows normal users to delete their own account.
    - Allows admin to delete other users' accounts.
    - Admin cannot delete their own account.
    """

    def has_object_permission(self, request, view, obj):
        # Must be authenticated and role must be admin or user
        if not request.user.is_authenticated or request.user.role not in ['admin', 'user']:
            return False

        # If user is deleting themselves
        if request.user == obj:
            return request.user.role == 'user'  # Only normal users can self-delete

        # If admin deleting someone else
        if request.user.role == 'admin':
            return True  # But admin cannot delete self (already excluded above)

        return False




