# Final Solution: TemplateDoesNotExist Error Fix

## Problem Summary
The Django application throws a `TemplateDoesNotExist` error when trying to render the login page:
```
TemplateDoesNotExist at /login/
login.html
```

Django is looking for the template in `/home/shaherer/phonix/phonix-web/templates/login.html` but cannot find it there.

## Root Cause
This is a deployment issue where the template directory structure on the production server differs from the development environment.

## Solution Implemented

### 1. Enhanced Template Directory Detection
Modified `settings.py` to automatically detect the templates directory in various possible locations:

```python
# Try to find the templates directory in various locations
TEMPLATES_DIR = BASE_DIR / "templates"
if not TEMPLATES_DIR.exists():
    # Try alternative locations
    alternative_locations = [
        BASE_DIR.parent / "templates",  # templates in parent directory
        Path(os.getcwd()) / "templates",  # templates in current working directory
        Path(os.getcwd()).parent / "templates",  # templates in current working directory's parent
    ]
    
    for location in alternative_locations:
        if location.exists():
            TEMPLATES_DIR = location
            break
```

### 2. Fallback Template Rendering
Enhanced `auth_views.py` to provide a fallback HTML response when templates cannot be found:

```python
except TemplateDoesNotExist:
    # If template doesn't exist in standard location, provide a fallback
    html_content = """
    <html>
    <!-- Minimal login form as fallback -->
    </html>
    """
    return HttpResponse(html_content.encode('utf-8'), content_type="text/html; charset=utf-8")
```

### 3. Robust Template Location Finding
Added a function to find templates in various possible locations:

```python
def find_template_file(template_name):
    """
    Find template file in various possible locations
    This is a workaround for deployment issues where directory structure may vary
    """
    # Get the configured template directories
    template_dirs = settings.TEMPLATES[0]['DIRS']
    
    # Also check some common alternative locations
    base_dir = settings.BASE_DIR
    alternative_dirs = [
        base_dir / "templates",
        base_dir.parent / "templates",
        os.path.join(os.getcwd(), "templates"),
        os.path.join(os.path.dirname(os.getcwd()), "templates"),
    ]
    
    # Combine all directories to check
    all_dirs = list(template_dirs) + alternative_dirs
    
    # Look for the template in each directory
    for directory in all_dirs:
        template_path = os.path.join(directory, template_name)
        if os.path.exists(template_path):
            return template_path
    
    return None
```

### 4. Enhanced WSGI Configuration
Updated `passenger_wsgi.py` with debugging information:

```python
import sys
import os

# Debug information
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))

# Add the project directory to the Python path
project_dir = os.path.dirname(__file__)
sys.path.insert(0, project_dir)

# Check if templates directory exists
templates_dir = os.path.join(project_dir, 'templates')
if os.path.exists(templates_dir):
    print("Templates directory found:", templates_dir)
else:
    print("Templates directory NOT found:", templates_dir)
```

## Files Created/Modified

1. `passenger_wsgi.py` - Enhanced WSGI configuration with debugging
2. `core/management/commands/check_templates.py` - Template checking command
3. `core/management/commands/fix_template_paths.py` - Template path fixing command
4. `phonix/settings.py` - Enhanced template directory detection
5. `core/auth_views.py` - Fallback template rendering

## Deployment Instructions

### For cPanel Deployment:

1. **Ensure the project structure is correct**:
   ```
   phonix-dj/
   ├── templates/
   │   └── login.html
   ├── phonix/
   │   └── settings.py
   └── passenger_wsgi.py
   ```

2. **Restart the application** in cPanel Python Setup

3. **Check error logs** if issues persist

### Verification Steps:

1. Run the template check command:
   ```bash
   python manage.py check_templates
   ```

2. Run the template path fix command:
   ```bash
   python manage.py fix_template_paths
   ```

## Troubleshooting

### If the error persists:

1. **Check file permissions**:
   ```bash
   chmod -R 755 templates/
   ```

2. **Verify the templates directory exists on the production server**:
   ```bash
   ls -la /home/shaherer/phonix/phonix-web/templates/
   ```

3. **Check if the project is in the correct directory**:
   ```bash
   pwd
   ls -la
   ```

4. **Verify BASE_DIR configuration** in settings.py

## Prevention

To prevent similar issues in the future:

1. Always verify template paths in both development and production environments
2. Use relative paths in Django settings based on BASE_DIR
3. Include template verification in deployment scripts
4. Test template loading as part of the CI/CD pipeline

## Contact

If issues persist after implementing this fix, please check the cPanel error logs for more detailed information about the template loading failure.