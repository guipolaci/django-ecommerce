from django.contrib.auth.models import User

def get_user_by_username(username: str):
    """
        Retrieve a user by username.
        Returns None if not found.

        This layer is responsible only for read operations.
        No business rules should be placed here.
        """
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None