# Study Groups MVP - Django Platform

A collaborative study groups management platform built with Django. Students can create study groups, share materials, schedule sessions, and discuss with other members.

## Features

- 👥 Create and join study groups by subject
- 📚 Upload and share study materials
- 📅 Schedule study sessions (online or in-person)
- 💬 Group discussions with comments and replies
- 🔔 Email notifications for upcoming sessions
- 👤 User profiles with interests and major
- 🔍 Search and filter groups by subject
- 👨‍💼 Role-based permissions (admin, moderator, member)

## Tech Stack

- **Backend**: Django 5.2
- **Database**: SQLite (development), SQL Server (production exports available)
- **Frontend**: Bootstrap 5, Font Awesome icons
- **Authentication**: Django built-in auth system

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

## Setup Instructions for Teammates

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd project1
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django
```

*(Consider creating `requirements.txt` with `pip freeze > requirements.txt` for easier dependency management)*

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Load Initial Data (Optional)

Load sample subjects:
```bash
python manage.py loaddata core/fixtures/initial_subjects.json
```

Or create comprehensive sample data:
```bash
python create_samples.py
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to set username, email, and password for admin access.

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

### 8. Access Admin Panel

Go to **http://127.0.0.1:8000/admin/** and log in with your superuser credentials to manage data.

## Default Demo Users (if using create_samples.py)

1. **Admin User:**
   - Username: `admin`
   - Password: `AdminPass123`
   - Full admin access

2. **Demo Student:**
   - Username: `demo_student`
   - Password: `student123`
   - Regular user account

## Database Schema

### Core Models

1. **Subject** - Academic subjects for organizing groups
2. **StudyGroup** - Study group with name, description, subject, members
3. **GroupMembership** - Links users to groups with roles (member/moderator/admin)
4. **StudySession** - Scheduled study sessions with date/time/location
5. **StudyMaterial** - Files and links shared within groups
6. **Comment** - Discussion threads with reply support
7. **Profile** - Extended user profiles with bio, major, interests
8. **Notification** - Email and in-app notifications

## Project Structure

```
project1/
├── core/                    # Main Django app
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   │   ├── core/
│   │   │   ├── comments/    # Comment section templates
│   │   │   ├── materials/   # Materials section
│   │   │   ├── email/       # Email templates
│   │   │   └── ...          # Other templates
│   │   ├── registration/    # Auth templates
│   │   └── admin/           # Custom admin templates
│   ├── fixtures/            # Initial data (subjects)
│   ├── admin.py             # Admin interface config
│   ├── models.py            # Database models
│   ├── views.py             # Views/controllers
│   ├── urls.py              # App URL routing
│   └── forms.py             # Django forms
├── project1/                # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI config
├── exports/                 # SQL Server export scripts (optional)
│   ├── *.csv                # Exported data
│   ├── *.tsv                # Tab-separated (for SQL Server)
│   ├── convert_csvs_to_tsv.ps1  # PowerShell converter
│   └── import_to_sqlserver.sql  # SQL Server import
├── tools/                   # Utility scripts
├── manage.py                # Django management script
├── create_samples.py        # Sample data generator
├── db.sqlite3               # SQLite database (created after migrations)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Usage Guide

### For Students:

1. **Register** - Create account at `/register/`
2. **Browse Groups** - View available study groups by subject
3. **Join Groups** - Request to join groups (auto-approved if space available)
4. **Participate** - Comment, download materials, attend sessions
5. **Update Profile** - Add bio, major, and interests

### For Group Creators/Admins:

1. **Create Group** - Set name, description, subject, max members
2. **Upload Materials** - Share PDFs, links, and resources
3. **Schedule Sessions** - Create online or in-person study sessions
4. **Moderate** - Manage comments, materials, and member roles
5. **Communicate** - Notifications sent for new sessions

## Development Commands

```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Run on different port
python manage.py runserver 8001

# Create sample data
python create_samples.py

# Django shell
python manage.py shell
```

## SQL Server Export (Optional)

For analytics or production database, export to SQL Server:

1. **Generate data**: `python create_samples.py`
2. **Export to CSV**: Django admin or custom management command
3. **Convert to TSV**: Run `.\exports\convert_csvs_to_tsv.ps1` in PowerShell
4. **Import to SQL Server**: Execute `exports\import_to_sqlserver.sql` in SSMS

## Troubleshooting

**Migration errors:**
```bash
python manage.py migrate --run-syncdb
```

**Static files not loading in development:**
- Django automatically serves static files with `DEBUG=True`
- Check `STATIC_URL` in `settings.py`

**Port already in use:**
```bash
python manage.py runserver 8001
```

**Permission denied on PowerShell script:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\exports\convert_csvs_to_tsv.ps1
```

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Make changes and test locally
3. Commit: `git commit -m "Add: description of changes"`
4. Push: `git push origin feature/your-feature-name`
5. Open Pull Request on GitHub

## Team & Credits

Created by [Your Team Names] for [Course/Project Name]

## License

Educational project - free to use and modify for learning purposes.