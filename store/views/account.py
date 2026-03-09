from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from store.services.account import register_user, login_user, logout_user


def register(request):
    """
    Handles the registration page.

    GET  → renders the empty registration form
    POST → collects form data, delegates to service, redirects on success
    """

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        result = register_user(request, username, email, password, confirm_password)

        if result["success"]:
            return redirect("login")

        return render(request, "store/account/register.html", {"error": result["error"]})

    return render(request, "store/account/register.html")


def login_view(request):
    """
    Handles the login page.

    GET  → renders the empty login form
    POST → validates credentials via service, redirects on success

    Supports the ?next= parameter set by @login_required.
    After a successful login, the user is redirected back to where
    they were trying to go — not always to the product list.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        result = login_user(request, username, password)

        if result["success"]:
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("product_list")

        return render(request, "store/account/login.html", {
            "error": result["error"],
            "next": request.GET.get("next", ""),
        })

    return render(request, "store/account/login.html", {
        "next": request.GET.get("next", ""),
    })


@login_required
def logout_view(request):
    """
    Logs the user out and redirects to the product list.
    Protected by @login_required — only authenticated users can log out.
    """

    logout_user(request)

    return redirect("product_list")