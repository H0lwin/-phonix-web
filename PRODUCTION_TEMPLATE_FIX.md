# Production Template Fix Solution

## Problem
The Django application throws a `TemplateDoesNotExist` error when trying to render the login page:
```
TemplateDoesNotExist at /login/
login.html
```

Django is looking for the template in `/home/shaherer/phonix/phonix-web/templates/login.html` but cannot find it there.

## Root Cause
This is a deployment issue where the template directory structure on the production server differs from the development environment.

## Solution Implemented

### 1. Enhanced Template Directory Configuration
Modified `phonix/settings.py` to handle multiple possible template directory locations:

```python
# Handle production environment template directory issue
TEMPLATE_DIRS = []

# Primary template directory (standard development setup)
primary_template_dir = BASE_DIR / "templates"
TEMPLATE_DIRS.append(primary_template_dir)

# Add production-specific paths that might be needed
production_template_dirs = [
    Path("/home/shaherer/phonix/phonix-web/templates"),  # Production path from error
    BASE_DIR.parent / "templates",  # Templates in parent directory
    Path(os.getcwd()) / "templates",  # Templates in current working directory
]

# Add existing directories to template dirs
for template_dir in production_template_dirs:
    if template_dir.exists():
        TEMPLATE_DIRS.append(template_dir)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATE_DIRS,  # Use multiple possible template directories
        "APP_DIRS": True,
        ...
    },
]
```

### 2. Fallback Template Rendering
Enhanced `core/auth_views.py` with a complete fallback template that renders directly without relying on file-based templates:

```python
# Fallback login template as string for production environments
LOGIN_TEMPLATE_FALLBACK = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ورود به سیستم - شهر راز</title>
    <!-- Complete HTML template -->
</head>
<body>
    <!-- Login form -->
</body>
</html>
"""

# In the view, if template is not found:
except TemplateDoesNotExist:
    # Render fallback template directly
    from django.template import Context, Template
    template = Template(LOGIN_TEMPLATE_FALLBACK)
    context = Context({...})
    html_content = template.render(context)
    return HttpResponse(html_content.encode('utf-8'), content_type="text/html; charset=utf-8")
```

### 3. Production Fix Script
Created `fix_production_templates.py` to automatically fix template paths:

```python
# Creates the exact directory structure Django expects
production_template_path = Path("/home/shaherer/phonix/phonix-web/templates")
source_templates_dir = Path(__file__).resolve().parent / "templates"

# Copies or creates symbolic links to ensure templates are found
```

## Files Created/Modified

1. `phonix/settings.py` - Enhanced template directory configuration
2. `core/auth_views.py` - Added fallback template rendering
3. `fix_production_templates.py` - Production template fix script
4. `passenger_wsgi.py` - Enhanced WSGI configuration

## Immediate Fix

To immediately fix the issue:

1. **Run the production fix script**:
   ```bash
   python fix_production_templates.py
   ```

2. **Or manually create the directory structure**:
   ```bash
   mkdir -p /home/shaherer/phonix/phonix-web/templates
   cp -r templates/* /home/shaherer/phonix/phonix-web/templates/
   ```

3. **Restart the application** in cPanel

## Verification

After implementing the fix:

1. The login page should load correctly
2. No more `TemplateDoesNotExist` errors
3. The fallback template ensures functionality even if file-based templates are not found

## Prevention

To prevent similar issues in the future:

1. Always test deployment in an environment that matches production
2. Use relative paths based on `BASE_DIR` in Django settings
3. Include template verification in deployment scripts
4. Implement fallback mechanisms for critical templates

## Contact

If issues persist, check the cPanel error logs for more detailed information.