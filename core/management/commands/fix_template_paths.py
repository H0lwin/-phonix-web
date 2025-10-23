from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys

class Command(BaseCommand):
    help = 'Fix template directory paths for production deployment'

    def handle(self, *args, **options):
        self.stdout.write("=== Template Path Fix Utility ===")
        
        # Get current working directory
        cwd = os.getcwd()
        self.stdout.write(f"Current working directory: {cwd}")
        
        # Get project directory
        project_dir = str(settings.BASE_DIR)
        self.stdout.write(f"Project directory (BASE_DIR): {project_dir}")
        
        # Check if we're in the right directory
        if cwd != project_dir:
            self.stdout.write(f"WARNING: Current directory ({cwd}) != Project directory ({project_dir})")
        
        # Check template directories
        template_dirs = settings.TEMPLATES[0]['DIRS']
        self.stdout.write(f"Configured template directories: {template_dirs}")
        
        # Check each template directory
        for i, template_dir in enumerate(template_dirs):
            self.stdout.write(f"\n--- Checking template directory {i+1} ---")
            self.stdout.write(f"Configured path: {template_dir}")
            
            # Check if it exists as-is
            if os.path.exists(template_dir):
                self.stdout.write("SUCCESS: Directory exists as configured")
                continue
            
            # Try to find it relative to current working directory
            relative_path = os.path.join(cwd, 'templates')
            if os.path.exists(relative_path):
                self.stdout.write(f"SUCCESS: Found templates at relative path: {relative_path}")
                continue
                
            # Try to find it relative to project directory
            project_relative_path = os.path.join(project_dir, 'templates')
            if os.path.exists(project_relative_path):
                self.stdout.write(f"SUCCESS: Found templates at project relative path: {project_relative_path}")
                continue
            
            # Try to find it in parent directories
            parent_dir = os.path.dirname(cwd)
            parent_template_path = os.path.join(parent_dir, 'templates')
            if os.path.exists(parent_template_path):
                self.stdout.write(f"SUCCESS: Found templates in parent directory: {parent_template_path}")
                continue
                
            self.stdout.write("ERROR: Could not locate templates directory!")
            
        # List actual template directory contents
        templates_dir = os.path.join(project_dir, 'templates')
        if os.path.exists(templates_dir):
            self.stdout.write(f"\n=== Templates directory contents ===")
            try:
                files = os.listdir(templates_dir)
                for file in files:
                    self.stdout.write(f"  - {file}")
            except Exception as e:
                self.stdout.write(f"Error listing files: {e}")
        else:
            self.stdout.write(f"\n=== ERROR: Templates directory not found at {templates_dir} ===")
            
            # Try to find it elsewhere
            search_paths = [
                os.path.join(cwd, 'templates'),
                os.path.join(os.path.dirname(cwd), 'templates'),
                os.path.join(os.path.dirname(project_dir), 'templates'),
            ]
            
            found = False
            for path in search_paths:
                if os.path.exists(path):
                    self.stdout.write(f"FOUND: Templates directory at {path}")
                    try:
                        files = os.listdir(path)
                        for file in files:
                            self.stdout.write(f"  - {file}")
                    except Exception as e:
                        self.stdout.write(f"Error listing files: {e}")
                    found = True
                    break
                    
            if not found:
                self.stdout.write("ERROR: Could not find templates directory anywhere!")
        
        self.stdout.write("\n=== Python Path ===")
        for path in sys.path:
            self.stdout.write(f"  - {path}")