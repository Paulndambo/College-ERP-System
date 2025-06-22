from rest_framework.permissions import IsAuthenticated

class HasUserRole(IsAuthenticated):
    """
    Allows access only to authenticated users who have a role assigned.
    Optionally, specify allowed role names with `allowed_roles` attribute in the view.
    """

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        user = request.user

        """If the view defines allowed roles, check against them"""
        allowed_roles = getattr(view, 'allowed_roles', None)

        if not is_authenticated or not hasattr(user, 'role') or user.role is None:
            return False

        if allowed_roles is not None:
            return user.role.name in allowed_roles

        """If no allowed_roles specified, any assigned role is acceptable"""
        return True

"""sample useage in api view"""
    # permission_classes = [HasUserRole]
    # allowed_roles = ['Admin'] 
