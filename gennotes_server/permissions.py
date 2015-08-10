from rest_framework import permissions
from oauth2_provider.ext.rest_framework.permissions import TokenHasScope
from allauth.account.models import EmailAddress


class EditAuthorizedOrReadOnly(TokenHasScope):
    """
    Verify permissions for viewing and editing GenNotes Variants and Relations.
        - Read only methods: always have permission. (GET, HEAD, OPTIONS)
        - Other methods require authorization.
            - OAuth2 auth requires: valid token, valid scope, and verified
              email address for the target user.
            - Other auth require: verified email address for the request.user
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.auth and hasattr(request.auth, 'scope'):
                required_scopes = self.get_scopes(request, view)
                token_valid = request.auth.is_valid(required_scopes)
                user_verified = EmailAddress.objects.get(
                    user=request.user).verified
                return token_valid and user_verified
            if request.user and request.user.is_authenticated():
                # Avoiding try/except; we think this will work for any user.
                return EmailAddress.objects.get(user=request.user).verified

        return False
