import sys
import os

# Debug information
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))

# Add the project directory to the Python path
project_dir = os.path.dirname(__file__)
sys.path.insert(0, project_dir)

# Print debug information
print("Project directory:", project_dir)
print("Project directory contents:", os.listdir(project_dir))

# Check if templates directory exists
templates_dir = os.path.join(project_dir, 'templates')
if os.path.exists(templates_dir):
    print("Templates directory found:", templates_dir)
    print("Templates directory contents:", os.listdir(templates_dir))
else:
    print("Templates directory NOT found:", templates_dir)
    
    # Try to find templates directory in parent directories
    parent_dir = os.path.dirname(project_dir)
    templates_dir_parent = os.path.join(parent_dir, 'templates')
    if os.path.exists(templates_dir_parent):
        print("Templates found in parent directory:", templates_dir_parent)
        print("Parent templates directory contents:", os.listdir(templates_dir_parent))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')

# Import and create the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()