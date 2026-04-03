# Financial Records Management System

Internship Assignment project built with Django for managing financial records with role-based access control.

## 1. Assignment Overview

This system provides:
- User authentication (register, login, logout)
- Role-based authorization (Admin, Analyst, Viewer)
- Financial record management (create, read, update, delete)
- Dashboard insights (totals, category-wise net, monthly summary, recent activity)
- Search and filter support for records
- User administration controls (role change, activate/deactivate, delete)

## 2. Functional Scope Completed

### User and Role Management
- Custom user model with roles: Viewer, Analyst, Admin
- Registration with Django password validation
- Login/logout flow with session-based authentication
- Admin can manage users and update user roles
- Admin can activate/deactivate users and delete users (with safety checks)

### Financial Record Management
- Record fields: amount, type, category, timestamp, description, owner
- Admin can upload records
- Admin can edit and delete records
- Admin and Analyst can view record details

### Dashboard and Analytics
- Total income, total expense, and net balance
- Category-wise table with income, expense, and net balance
- Net values color-coded by positive/negative value
- Monthly income vs expense summary with monthly net
- Recent activity list (latest records)
- Uploaded records table with pagination

### Search and Filtering
- Filters in top navbar: type, category, date, and text search
- Filters apply to uploaded records table
- Pagination retains filter/search query values
- Viewer is blocked from using search/filter through direct URL query parameters

## 3. Role Permissions Matrix

View Dasboard = Admin, Analyst & Viewer

View Record Details = Admin & Analyst ONLY
Search/Filter records = Admin & Analyst ONLY

Upload, Edit or Delete Record = Admin ONLY
View All Users = Admin ONLY
Edit User role, status or Delete = Admin ONLY

## 4. Tech Stack

- Python
- Django
- SQLite (db.sqlite3)
- Bootstrap 5 (UI styling)

## 5. Project Structure

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

## 6. Local Setup and Run

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone or download this repository.
2. Open terminal in project root.
3. Create virtual environment:

```powershell
python -m venv .venv
```

4. Activate virtual environment (Windows PowerShell):

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

7. (Optional) Create admin user:

```powershell
python manage.py createsuperuser
```

8. Run server:

```powershell
python manage.py runserver
```

9. Open browser:

```
http://127.0.0.1:8000/
```

## 7. Main Route URLs

- `/` : Dashboard (home)
- `/login/` : Login page
- `/register/` : Register page
- `/logout/` : Logout action
- `/upload-record/` : Upload new record (Admin only)
- `/view-record/<id>/` : View record details
- `/edit-record/<id>/` : Edit/Delete record (Admin only)
- `/manage-user/<id>/` : User management actions (Admin only, POST)
- `/admin/` : Django admin panel

## 8. Validation and Security Highlights

- Password checks use Django built-in validators
- Upload/edit validates amount, type, and category
- User management actions restricted to POST requests
- Safe redirect handling for next URL on login
- Role checks enforced in backend views

## 9. Current Testing Status

- Automated tests are not yet implemented (placeholder tests file present)
- Functional behavior validated through manual execution flows

## 10. Internship Assignment Note

This repository is prepared as an internship assignment submission focused on functional requirements and role-based behavior as per the criteria set by the company.
