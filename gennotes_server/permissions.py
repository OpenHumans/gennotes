from rest_framework import permissions
from allauth.account.models import EmailAddress


class IsVerifiedOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user with verified email
    address, or is a read-only request.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user and request.user.is_authenticated():
                # Avoiding try/except; we think this will work for any user.
                return EmailAddress.objects.get(user=request.user).verified

        return False
