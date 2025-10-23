# Template Deployment Fix for Phonix Project

## Problem Description

The error `TemplateDoesNotExist at /login/` occurs when Django tries to render the [login.html](file:///e:/phonix-dj/templates/admin/auth/user/change_password.html) template but cannot find it in the expected location on the production server.

Error details:
```
Template-loader postmortem
Django tried loading these templates, in this order:
django.template.loaders.filesystem.Loader: /home/shaherer/phonix/phonix-web/templates/login.html (Source does not exist)
```

## Root Cause

The issue is a deployment problem where the template directory structure on the production server differs from the development environment. Django is configured to look for templates in the [templates](file:///e:/phonix-dj/templates/) directory, but on the production server, this directory is not in the expected location.

## Solution Implemented

### 1. Verified Template Existence
- Confirmed that [login.html](file:///e:/phonix-dj/templates/admin/auth/user/change_password.html) exists in the correct location: `templates/login.html`
- Verified that the template contains valid HTML and Django template syntax

### 2. Verified Django Settings
- Confirmed that `settings.py` correctly configures the template directories:
  ```python
  TEMPLATES = [
      {
          "BACKEND": "django.template.backends.django.DjangoTemplates",
          "DIRS": [BASE_DIR / "templates"],  # Correct path
          "APP_DIRS": True,
          ...
      },
  ]
  ```

### 3. Created passenger_wsgi.py
- Added a proper WSGI configuration file for cPanel deployment:
  ```python
  import sys
  import os
  sys.path.insert(0, os.path.dirname(__file__))
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
  from django.core.wsgi import get_wsgi_application
  application = get_wsgi_application()
  ```

### 4. Deployment Verification Script
- Created [deploy_fix.py](file:///e:/phonix-dj/deploy_fix.py) to verify template loading and configuration

## Deployment Instructions

### For cPanel Deployment:

1. **Ensure correct directory structure**:
   ```
   phonix-dj/
   ├── templates/
   │   ├── login.html
   │   └── ... other templates
   ├── phonix/
   │   └── settings.py
   └── passenger_wsgi.py
   ```

2. **Run the verification script**:
   ```bash
   python deploy_fix.py
   ```

3. **In cPanel Python Setup**:
   - Point Application root to the project folder
   - Ensure the virtual environment has all required packages
   - Restart the application after any changes

### For Manual Deployment:

1. **Verify template directory**:
   ```bash
   ls -la /path/to/phonix-dj/templates/
   ```

2. **Check Django settings**:
   ```bash
   python manage.py shell -c "from django.conf import settings; print(settings.TEMPLATES[0]['DIRS'])"
   ```

3. **Test template loading**:
   ```bash
   python manage.py shell -c "from django.template.loader import get_template; template = get_template('login.html'); print('Success')"
   ```

## Troubleshooting

### If the error persists:

1. **Check file permissions**:
   ```bash
   chmod -R 755 templates/
   ```

2. **Verify BASE_DIR configuration** in `settings.py`:
   ```python
   BASE_DIR = Path(__file__).resolve().parent.parent
   ```

3. **Check for symbolic links or mount issues** that might affect file access

4. **Ensure the production server has the latest code**:
   ```bash
   git pull origin main
   ```

## Prevention

To prevent similar issues in the future:

1. Always verify template paths in both development and production environments
2. Use relative paths in Django settings based on BASE_DIR
3. Include template verification in deployment scripts
4. Test template loading as part of the CI/CD pipeline

## Contact

If issues persist after implementing this fix, please check the cPanel error logs for more detailed information about the template loading failure.