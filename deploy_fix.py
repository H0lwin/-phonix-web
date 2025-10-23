#!/usr/bin/env python
"""
Deployment fix script for Phonix project
This script helps ensure that templates and static files are correctly deployed
"""

import os
import sys
import shutil
from pathlib import Path

def check_template_directory():
    """Check if the template directory exists and contains the required files"""
    # Get the project base directory
    base_dir = Path(__file__).resolve().parent
    
    # Check templates directory
    templates_dir = base_dir / "templates"
    if not templates_dir.exists():
        print(f"ERROR: Templates directory not found at {templates_dir}")
        return False
    
    # Check if login.html exists
    login_template = templates_dir / "login.html"
    if not login_template.exists():
        print(f"ERROR: login.html not found at {login_template}")
        return False
    
    print(f"✓ Templates directory found at {templates_dir}")
    print(f"✓ login.html found at {login_template}")
    return True

def check_settings():
    """Check Django settings for template configuration"""
    # Add the project to Python path
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
    
    try:
        import django
        django.setup()
        
        from django.conf import settings
        
        # Check template directories
        template_dirs = settings.TEMPLATES[0]['DIRS']
        print(f"✓ Template directories configured as: {template_dirs}")
        
        # Check if the first template directory exists
        if template_dirs:
            first_template_dir = Path(template_dirs[0])
            if first_template_dir.exists():
                print(f"✓ Configured template directory exists: {first_template_dir}")
            else:
                print(f"⚠ Configured template directory does not exist: {first_template_dir}")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to check Django settings: {e}")
        return False

def check_template_loading():
    """Check if Django can load the login template"""
    try:
        # Add the project to Python path
        project_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_dir))
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
        
        import django
        django.setup()
        
        from django.template.loader import get_template
        from django.template import TemplateDoesNotExist
        
        try:
            template = get_template('login.html')
            print("✓ Django can successfully load login.html template")
            return True
        except TemplateDoesNotExist as e:
            print(f"✗ Django cannot load login.html template: {e}")
            return False
        except Exception as e:
            print(f"✗ Error while loading template: {e}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to check template loading: {e}")
        return False

def main():
    """Main function to run all checks"""
    print("Phonix Deployment Fix Script")
    print("=" * 40)
    
    # Run all checks
    checks = [
        ("Template Directory Check", check_template_directory),
        ("Django Settings Check", check_settings),
        ("Template Loading Check", check_template_loading),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 20)
        result = check_func()
        results.append((check_name, result))
    
    # Print summary
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print("=" * 40)
    
    all_passed = True
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✓ All checks passed! The deployment should work correctly.")
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)