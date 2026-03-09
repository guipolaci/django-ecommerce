from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from store.selectors.account import get_user_by_username


def register_user(request, username: str, email: str, password: str, confirm_password: str) -> dict:
    """
    Business rule for registering a new user.

    Validates that:
    - Passwords match
    - Username is not already taken

    Returns a dict with:
    - success: bool
    - error: str (only when success is False)
    """

    if password != confirm_password:
        return {"success": False, "error": "As senhas não coincidem."}

    if get_user_by_username(username):
        return {"success": False, "error": "Este nome de usuário já está em uso."}

    User.objects.create_user(username=username, email=email, password=password)

    return {"success": True}


def login_user(request, username: str, password: str) -> dict:
    """
    Business rule for authenticating a user.

    Uses Django's built-in authenticate() to validate credentials.
    If valid, logs the user in via login().

    Returns a dict with:
    - success: bool
    - error: str (only when success is False)
    """

    user = authenticate(request, username=username, password=password)

    if user is None:
        return {"success": False, "error": "Usuário ou senha inválidos."}

    login(request, user)

    return {"success": True}


def logout_user(request) -> None:
    """
    Logs the current user out.
    Delegates directly to Django's logout().
    No business rules needed here.
    """

    logout(request)