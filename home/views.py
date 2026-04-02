from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce, TruncMonth
from .models import Record, User


@login_required(login_url='login')
def upload_record(request):
    if request.user.user_type != 'Admin':
        messages.error(request, "Only Admin users can upload records.")
        return redirect("home")

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
    latest_records = list(Record.objects.order_by('-time')[:5])
    latest_record1 = latest_records[0] if len(latest_records) > 0 else None
    latest_record2 = latest_records[1] if len(latest_records) > 1 else None
    latest_record3 = latest_records[2] if len(latest_records) > 2 else None
    latest_record4 = latest_records[3] if len(latest_records) > 3 else None
    latest_record5 = latest_records[4] if len(latest_records) > 4 else None

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

    monthly_summary = (
        Record.objects
        .annotate(month=TruncMonth('time'))
        .values('month')
        .annotate(
            income=Coalesce(Sum('amount', filter=Q(type='Income')), 0),
            expense=Coalesce(Sum('amount', filter=Q(type='Expense')), 0),
        )
        .order_by('-month')[:12]
    )

    monthly_summary = list(monthly_summary)
    for entry in monthly_summary:
        entry['net'] = entry['income'] - entry['expense']


    if request.GET.get("search"):
        queryset = queryset.filter(description__icontains=request.GET.get("search"))

    records_paginator = Paginator(queryset, 5)
    records_page_number = request.GET.get("records_page")
    records_page = records_paginator.get_page(records_page_number)

    if request.user.user_type == 'Admin':
        users = User.objects.all().order_by('id')

    context = {
        "records": records_page,
        "page_number": records_page.number,
        "users": users,
        "latest_record1": latest_record1,
        "latest_record2": latest_record2,
        "latest_record3": latest_record3,
        "latest_record4": latest_record4,
        "latest_record5": latest_record5,
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
        "others_total": others_total,
        "monthly_summary": monthly_summary,
    }

    return render(request, "home/home.html", context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def manage_user(request, id):
    if request.user.user_type != 'Admin':
        messages.error(request, "Only Admin users can manage users.")
        return redirect("home")

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
        return redirect("home")

    record = get_object_or_404(Record, id=id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            record.delete()
            messages.success(request, "Record deleted successfully.")
            return redirect("home")

        amount = request.POST.get("amount")
        record_type = request.POST.get("type")
        category = request.POST.get("category")
        description = request.POST.get("description")

        if not amount or not record_type or not category:
            messages.error(request, "Amount, type and category are required.")
            return render(request, "home/edit_record.html", {"record": record})

        try:
            parsed_amount = int(amount)
            if parsed_amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Amount must be a positive number.")
            return render(request, "home/edit_record.html", {"record": record})

        if record_type not in ["Income", "Expense"]:
            messages.error(request, "Invalid record type.")
            return render(request, "home/edit_record.html", {"record": record})

        record.amount = parsed_amount
        record.type = record_type
        record.category = category
        record.description = description
        record.time = timezone.now()
        record.save(update_fields=['amount', 'type', 'category', 'description', 'time'])

        messages.success(request, "Record updated successfully.")
        return redirect("view_record", id=record.id)

    return render(request, "home/edit_record.html", {"record": record})


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