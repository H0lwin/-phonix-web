---
description: Repository Information Overview
alwaysApply: true
---

# Phonix Information

## Summary
Phonix is a Django-based project for law firm management with features for case management, employee management, financial tracking, and attendance reporting. The application uses a Persian (Farsi) interface and includes specialized modules for lawyers, employees, and administrators.

## Structure
- **phonix/**: Main Django project settings and configuration
- **core/**: Primary application with models, views, and business logic
- **templates/**: HTML templates including admin customizations and dashboards
- **static/**: CSS, JavaScript, and image files
- **staticfiles/**: Collected static files for production
- **venv/**: Python virtual environment

## Language & Runtime
**Language**: Python
**Version**: 3.11+
**Framework**: Django 4.2.7
**Build System**: Django's built-in tools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- Django 4.2.7 - Web framework
- mysqlclient 2.2.7 - MySQL database connector
- mysql-connector-python 9.4.0 - Alternative MySQL connector
- python-dotenv 1.0.0 - Environment variable management
- django-jalali 7.1.0+ - Persian date handling
- jdatetime 4.6.1+ - Persian datetime utilities
- unfold - Admin interface customization

## Database
**Engine**: MySQL
**Configuration**:
- Database: Phonix_suite
- Host: 127.0.0.1
- Port: 3306
- Charset: utf8mb4
- Alternative: SQLite (mentioned in README)

## Build & Installation
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Main Components
**Models**:
- UserProfile - Extended user information
- CaseFile - Legal case management
- Branch - Office branch management
- Employee - Staff information and HR
- Attendance - Time tracking
- ActivityReport - Work reporting
- FinancialReport - Financial summaries
- Income/Expense - Financial transactions
- Loan/LoanBuyer/LoanCreditor - Loan management
- Service - Service offerings

**Views**:
- Authentication views
- Dashboard views for different user roles
- Admin customizations

## Authentication
**Custom Backend**: NationalIDBackend
**User Roles**: Admin, Lawyer, Employee
**Login**: Username/password and National ID authentication

## Internationalization
**Language**: Persian (Farsi)
**Time Zone**: Asia/Tehran
**Date Format**: Persian calendar (Jalali) using django-jalali

## Testing
**Framework**: Django's built-in TestCase
**Test Location**: core/tests.py
**Run Command**:
```bash
python manage.py test
```

## Static Files
**CSS Framework**: Custom CSS
**JavaScript**: Custom JS for dashboard and landing pages
**Collection Command**:
```bash
python manage.py collectstatic
```

## Admin Interface
**Customization**: Uses unfold for enhanced admin UI
**Custom Forms**: Employee creation and management forms
**Specialized Panels**: Role-based dashboards for lawyers and employees