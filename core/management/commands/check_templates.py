from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import os
import sys

class Command(BaseCommand):
    help = 'Check template directory configuration and template availability'

    def handle(self, *args, **options):
        self.stdout.write("=== Template Directory Check ===")
        
        # Check BASE_DIR
        self.stdout.write(f"BASE_DIR: {settings.BASE_DIR}")
        
        # Check template directories
        template_dirs = settings.TEMPLATES[0]['DIRS']
        self.stdout.write(f"Configured template directories: {template_dirs}")
        
        # Check if template directories exist
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                self.stdout.write(f"SUCCESS: Template directory exists: {template_dir}")
            else:
                self.stdout.write(f"ERROR: Template directory does not exist: {template_dir}")
        
        # List files in template directory
        if template_dirs:
            first_template_dir = template_dirs[0]
            if os.path.exists(first_template_dir):
                self.stdout.write(f"\n=== Files in template directory ===")
                try:
                    files = os.listdir(first_template_dir)
                    for file in files:
                        self.stdout.write(f"  - {file}")
                except Exception as e:
                    self.stdout.write(f"Error listing files: {e}")
        
        # Check if login.html can be loaded
        self.stdout.write(f"\n=== Template Loading Test ===")
        try:
            template = get_template('login.html')
            self.stdout.write("SUCCESS: login.html template can be loaded successfully")
        except TemplateDoesNotExist as e:
            self.stdout.write(f"ERROR: login.html template cannot be loaded: {e}")
        except Exception as e:
            self.stdout.write(f"ERROR: Error loading template: {e}")
        
        # Check Python path
        self.stdout.write(f"\n=== Python Path ===")
        for path in sys.path:
            self.stdout.write(f"  - {path}")