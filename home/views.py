from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import ValidationError
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
        record_type = data.get("type")
        category = data.get("category")
        description = data.get("description")

        if not amount or not record_type or not category:
            messages.error(request, "Amount, type and category are required.")
            return render(request, "home/upload_record.html")

        try:
            parsed_amount = int(amount)
            if parsed_amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Amount must be a positive number.")
            return render(request, "home/upload_record.html")

        valid_types = {choice for choice, _ in Record._meta.get_field("type").choices}
        valid_categories = {choice for choice, _ in Record._meta.get_field("category").choices}

        if record_type not in valid_types:
            messages.error(request, "Invalid record type.")
            return render(request, "home/upload_record.html")

        if category not in valid_categories:
            messages.error(request, "Invalid record category.")
            return render(request, "home/upload_record.html")

        Record.objects.create(
            user=request.user,
            amount=parsed_amount,
            type=record_type,
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

    totals = Record.objects.aggregate(
        total_income=Coalesce(Sum('amount', filter=Q(type='Income')), 0),
        total_expense=Coalesce(Sum('amount', filter=Q(type='Expense')), 0),
    )
    total_income = totals['total_income']
    total_expense = totals['total_expense']

    category_breakdown = {
        item['category']: item
        for item in Record.objects.values('category').annotate(
            income=Coalesce(Sum('amount', filter=Q(type='Income')), 0),
            expense=Coalesce(Sum('amount', filter=Q(type='Expense')), 0),
        )
    }

    category_wise_totals = []
    for category_value, category_label in Record._meta.get_field('category').choices:
        category_data = category_breakdown.get(category_value, {})
        income_total = category_data.get('income', 0)
        expense_total = category_data.get('expense', 0)
        category_wise_totals.append({
            'category': category_label,
            'income': income_total,
            'expense': expense_total,
            'net': income_total - expense_total,
        })

    monthly_summary = (
        Record.objects.annotate(month=TruncMonth('time')).values('month').annotate(
            income=Coalesce(Sum('amount', filter=Q(type='Income')), 0),
            expense=Coalesce(Sum('amount', filter=Q(type='Expense')), 0),
        ).order_by('-month')[:12]
    )

    monthly_summary = list(monthly_summary)
    for entry in monthly_summary:
        entry['net'] = entry['income'] - entry['expense']

    filter_type_choices = Record._meta.get_field('type').choices
    filter_category_choices = Record._meta.get_field('category').choices
    search_query = request.GET.get("search", "").strip()

    filter_type = request.GET.get("filter_type", "").strip()
    filter_category = request.GET.get("filter_category", "").strip()
    filter_date = request.GET.get("filter_date", "").strip()

    has_filter_request = any([search_query, filter_type, filter_category, filter_date])
    if request.user.user_type == 'Viewer' and has_filter_request:
        messages.error(request, "Only Admin and Analyst can search/filter records!")
        return redirect("home")

    valid_filter_types = {value for value, _ in filter_type_choices}
    valid_filter_categories = {value for value, _ in filter_category_choices}

    if filter_type not in valid_filter_types:
        filter_type = ""

    if filter_category not in valid_filter_categories:
        filter_category = ""

    if search_query:
        queryset = queryset.filter(description__icontains=search_query)

    if filter_type:
        queryset = queryset.filter(type=filter_type)

    if filter_category:
        queryset = queryset.filter(category=filter_category)

    if filter_date:
        try:
            parsed_filter_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
            queryset = queryset.filter(time__date=parsed_filter_date)
        except ValueError:
            filter_date = ""

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
        "category_wise_totals": category_wise_totals,
        "filter_type_choices": filter_type_choices,
        "filter_category_choices": filter_category_choices,
        "search_query": search_query,
        "filter_type": filter_type,
        "filter_category": filter_category,
        "filter_date": filter_date,
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
            messages.error(request, "You can not delete your own account.")
            return redirect("home")
        if target_user.is_superuser:
            messages.error(request, "Can not delete a superuser account.")
            return redirect("home")
        else :
            messages.success(request, "User deleted successfully!")
            target_user.delete()
        return redirect("home")

    if action == "to_analyst":
        if target_user.is_superuser:
            messages.error(request, "Can not change role of a superuser account.")
            return redirect("home")
        target_user.user_type = "Analyst"
        target_user.save(update_fields=['user_type'])
        messages.success(request, "User role updated to Analyst successfully!")
        return redirect("home")

    if action == "to_viewer":
        if target_user.is_superuser:
            messages.error(request, "Can not change role of a superuser account.")
            return redirect("home")
        target_user.user_type = "Viewer"
        target_user.save(update_fields=['user_type'])
        messages.success(request, "User role updated to Viewer successfully!")
        return redirect("home")

    if action == "to_admin":
        if target_user.is_superuser:
            messages.error(request, "Can not change role of a superuser account.")
            return redirect("home")
        target_user.user_type = "Admin"
        target_user.save(update_fields=['user_type'])
        messages.success(request, "User role updated to Admin successfully!")
        return redirect("home")

    if action == "deactivate":
        if target_user == request.user:
            messages.error(request, "You can not deactivate your own account.")
            return redirect("home")
        if target_user.is_superuser:
            messages.error(request, "Can not deactivate a superuser account.")
            return redirect("home")
        if not target_user.is_active:
            messages.warning(request, "User is already inactive.")
            return redirect("home")
        target_user.is_active = False
        target_user.save(update_fields=['is_active'])
        messages.success(request, "User deactivated successfully!")
        return redirect("home")

    if action == "activate":
        if target_user.is_active:
            messages.warning(request, "User is already active.")
            return redirect("home")
        target_user.is_active = True
        target_user.save(update_fields=['is_active'])
        messages.success(request, "User activated successfully!")
        return redirect("home")

    return redirect("home")


@login_required(login_url='login')
def view_record(request, id):
    if request.user.user_type == 'Viewer':
        messages.error(request, "Only Admin and Analyst can view records.")
        return redirect("home")
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

        valid_types = {choice for choice, _ in Record._meta.get_field("type").choices}
        valid_categories = {choice for choice, _ in Record._meta.get_field("category").choices}

        if record_type not in valid_types:
            messages.error(request, "Invalid record type.")
            return render(request, "home/edit_record.html", {"record": record})

        if category not in valid_categories:
            messages.error(request, "Invalid record category.")
            return render(request, "home/edit_record.html", {"record": record})

        record.amount = parsed_amount
        record.type = record_type
        record.category = category
        record.description = description

        record.save(update_fields=['amount', 'type', 'category', 'description'])

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
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("home")

    return render(request, "home/login.html", {"next": next_url})


def register_page(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not username or not password or not confirm_password:
            messages.error(request, "All fields are required!")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        try:
            validate_password(password)
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
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