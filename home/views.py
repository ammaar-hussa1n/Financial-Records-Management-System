from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Sum
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
    users = None
    latest_record = Record.objects.order_by('-time').first()
    
    total_income = 0
    for amount in Record.objects.filter(type='Income'):
        total_income += amount.amount

    total_expense = 0
    for amount in Record.objects.filter(type='Expense'):
        total_expense += amount.amount

    salary_total = 0
    for amount in Record.objects.filter(category='Salary'):
        salary_total += amount.amount

    friend_total = 0
    for amount in Record.objects.filter(category='Friend'):
        friend_total += amount.amount

    business_total = 0
    for amount in Record.objects.filter(category='Business'):
        business_total += amount.amount

    food_total = 0
    for amount in Record.objects.filter(category='Food'):
        food_total += amount.amount

    transportation_total = 0
    for amount in Record.objects.filter(category='Transportation'):
        transportation_total += amount.amount

    entertainment_total = 0
    for amount in Record.objects.filter(category='Entertainment'):
        entertainment_total += amount.amount

    groceries_total = 0
    for amount in Record.objects.filter(category='Groceries'):
        groceries_total += amount.amount

    healthcare_total = 0
    for amount in Record.objects.filter(category='Healthcare'):
        healthcare_total += amount.amount

    others_total = 0
    for amount in Record.objects.filter(category='Others'):
        others_total += amount.amount


    if request.GET.get("search"):
        queryset = queryset.filter(description__icontains=request.GET.get("search"))

    if request.user.user_type == 'Admin':
        users = User.objects.all().order_by('id')

    context = {
        "records": queryset,
        "users": users,
        "latest_record": latest_record,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "salary_total": salary_total,
        "friend_total": friend_total,
        "business_total": business_total,
        "food_total": food_total,
        "transportation_total": transportation_total,
        "entertainment_total": entertainment_total,
        "groceries_total": groceries_total,
        "healthcare_total": healthcare_total,
        "others_total": others_total
    }

    return render(request, "home/home.html", context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def manage_user(request, id):
    if request.user.user_type != 'Admin':
        messages.error(request, "Only Admin users can manage users.")
        return redirect('/login/?force=1')

    target_user = get_object_or_404(User, id=id)
    action = request.POST.get("action")

    if action == "delete":
        if target_user == request.user:
            return redirect("home")
        if target_user.is_superuser:
            return redirect("home")
        else :
            target_user.delete()
        return redirect("home")

    if action == "to_analyst":
        if target_user.is_superuser:
            return redirect("home")
        target_user.user_type = "Analyst"
        target_user.save(update_fields=['user_type'])
        return redirect("home")

    if action == "to_viewer":
        if target_user.is_superuser:
            return redirect("home")
        target_user.user_type = "Viewer"
        target_user.save(update_fields=['user_type'])
        return redirect("home")

    if action == "to_admin":
        target_user.user_type = "Admin"
        target_user.save(update_fields=['user_type'])
        return redirect("home")

    return redirect("home")


@login_required(login_url='login')
def view_record(request, id):

    record = get_object_or_404(Record, id=id)
    context = {
        "record": record
    }
    return render(request, "home/view_record.html", context)

@login_required(login_url='login')
def edit_record(request, id):
    if request.user.user_type != 'Admin':
        messages.error(request, "Only Admin users can edit records.")
        return redirect('/login/?force=1')

    record = get_object_or_404(Record, id=id)
    context = {
        "record": record
    }
    return render(request, "home/edit_record.html", context)

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