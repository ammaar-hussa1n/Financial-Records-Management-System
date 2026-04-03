# Financial Records Management System

Internship assignment project for financial record management, with role-based access control, using Django.

## Overview

Implemented capabilities:
- Authentication : register, login, logout
- Roles : Admin, Analyst, Viewer
- Record operations : create, read, update, soft delete
- Dashboard analytics : totals, category wise totals, monthly summary, recent record activity
- Admin user management : role updates, activate/deactivate, delete
- Search or filters in records

## Final Backend Behavior

### User and role management
- Custom `User` model with `user_type` (Viewer, Analyst, Admin)
- Password validation uses Django built-in validators
- Login supports safe `next` redirects with allowed-host checks
- Admin safety checks :
  - Can not change/delete/deactivate/activate own account
  - Can not change/delete/deactivate/activate superuser accounts

### Records and soft delete
- Admin can upload and edit records
- Delete from edit sets `validity = False` (soft delete)
- Admin and Analyst can view record details
- Soft deleted records are blocked in view/edit page

### Dashboard and data scope
- All dashboard record data is scoped to active records
- Includes :
  - Total income, total expense, net balance
  - Category-wise income/expense/net table
  - Monthly income vs expense summary
  - Recent activity (latest 5 active records)
- Uploaded records table uses pagination (5 per page)

### Search and filtering
- Filters : type, category, date, and description search
- Invalid filter values are normalized to empty values
- Pagination retains active filter/query values
- Viewer can not search or filter

## Role Permissions Matrix
- Dashboard summary and analytics tables : Admin / Analyst / Viewer
- Uploaded records table and pagination : Admin / Analyst
- Record details : Admin / Analyst
- Search/filter actions : Admin / Analyst
- Record managment : Admin
- User management : Admin

## Main Routes

- `/` : Dashboard (login required)
- `/login/` : Login page
- `/register/` : Register page
- `/logout/` : Logout action (POST)
- `/upload-record/` : Upload record (Admin only)
- `/view-record/<id>/` : View record details (Admin/Analyst only)
- `/edit-record/<id>/` : Edit or soft delete record (Admin only)
- `/manage-user/<id>/` : User management action endpoint (Admin only, POST)
- `/admin/` : Django admin panel

## Tech Stack

- Python
- Django
- SQLite (`db.sqlite3`)
- Bootstrap 5

## Project Structure

```
Financial-Records-Management-System/
|-- manage.py
|-- db.sqlite3
|-- README.md
|-- InternAssignment/
|   |-- settings.py
|   |-- urls.py
|-- home/
|   |-- models.py
|   |-- views.py
|   |-- admin.py
|   |-- tests.py
|   |-- migrations/
|   |-- templates/home/
|       |-- base.html
|       |-- home.html
|       |-- login.html
|       |-- register.html
|       |-- upload_record.html
|       |-- view_record.html
|       |-- edit_record.html
```

## Local Setup

Prerequisites:
- Python 3.10+
- pip

Steps:
1. Clone or download this repository.
2. Open terminal in project root.
3. Create virtual environment:

```powershell
python -m venv .venv
```

4. Activate environment (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

5. Install Django:

```powershell
pip install django
```

6. Apply migrations:

```powershell
python manage.py migrate
```

7. Optional: create admin user

```powershell
python manage.py createsuperuser
```

8. Run server:

```powershell
python manage.py runserver
```

9. Open:

```
http://127.0.0.1:8000/
```

## Validation and Security Highlights

- Upload/edit validates amount, type, and category
- Role checks are enforced in backend views
- `manage_user` actions are POST-restricted
- Login redirect validates safe `next` URLs
- CSRF middleware and template CSRF tokens are in use
- Soft-deleted records are excluded by backend query filters