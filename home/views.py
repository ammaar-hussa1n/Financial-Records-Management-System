from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Record, User


@login_required(login_url='login')
def upload_record(request):
    if request.user.user_type != 'Admin':
        messages.error(request, "Only Admin users can upload records.")
        return redirect('/login/?force=1')

    if request.method == "POST":
        data = request.POST
        amount = data.get("amount")
        type = data.get("type")
        category = data.get("category")
        description = data.get("description")

        Record.objects.create(
            user=request.user,
            amount=amount,
            type=type,
            category=category,
            description=description
        )

        return redirect("home")

    return render(request, "home/upload_record.html")


@login_required(login_url='login')
def home(request):
    queryset = Record.objects.all()

    if request.GET.get("search"):
        queryset = queryset.filter(description__icontains=request.GET.get("search"))

    context = {
        "records": queryset
    }

    return render(request, "home/home.html", context)


@login_required(login_url='login')
def view_record(request, id):
    if request.user.user_type != 'Admin':
        messages.error(request, "Only Admin users can view records.")
        return redirect('/login/?force=1')

    record = get_object_or_404(Record, id=id)
    context = {
        "record": record
    }
    return render(request, "home/view_record.html", context)

def login_page(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    force_login = request.GET.get("force") == "1"
    username = None
    password = None

    if request.user.is_authenticated and not force_login:
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("home")

    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            messages.error(request, "All fields are required!")
            return render(request, "home/login.html", {"next": next_url})

        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password!")
            return render(request, "home/login.html", {"next": next_url})
        else:
            login(request, user)
            if user.is_superuser and user.user_type != 'Admin':
                user.user_type = 'Admin'
                user.save(update_fields=['user_type'])
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("home")

    if next_url == "/submit-idea/":
        messages.error(request, "You need to be logged in to submit an idea.")

    return render(request, "home/login.html", {"next": next_url})


def register_page(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "home/register.html")


@login_required(login_url='login')
def logout_page(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("login")
    return redirect("login")