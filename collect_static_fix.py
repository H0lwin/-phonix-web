#!/usr/bin/env python
"""
Static Files Collection Fix Script
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def collect_static_files():
    """Collect static files for production"""
    
    print("=== Static Files Collection Fix ===")
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
    
    try:
        import django
        django.setup()
        
        from django.conf import settings
        from django.core.management import call_command
        
        print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        print(f"STATIC_URL: {settings.STATIC_URL}")
        
        # Collect static files
        print("\nCollecting static files...")
        call_command('collectstatic', '--noinput', '--verbosity=2')
        
        print("\n✓ Static files collected successfully!")
        print(f"Static files are now available at: {settings.STATIC_ROOT}")
        
        # List collected files
        if settings.STATIC_ROOT.exists():
            print(f"\nCollected static files:")
            for root, dirs, files in os.walk(settings.STATIC_ROOT):
                level = root.replace(str(settings.STATIC_ROOT), '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error collecting static files: {e}")
        return False

def verify_static_files():
    """Verify that static files are correctly configured"""
    
    print("\n=== Static Files Verification ===")
    
    try:
        from django.conf import settings
        
        # Check if static root exists
        if settings.STATIC_ROOT.exists():
            print("✓ STATIC_ROOT directory exists")
        else:
            print("✗ STATIC_ROOT directory does not exist")
            
        # Check if static dirs exist
        for static_dir in settings.STATICFILES_DIRS:
            if static_dir.exists():
                print(f"✓ STATICFILES_DIR exists: {static_dir}")
            else:
                print(f"✗ STATICFILES_DIR does not exist: {static_dir}")
                
        # Check if css/style.css exists in static dirs
        style_css_path = settings.STATICFILES_DIRS[0] / "css" / "style.css"
        if style_css_path.exists():
            print("✓ css/style.css found in static directory")
        else:
            print("✗ css/style.css not found in static directory")
            
        return True
        
    except Exception as e:
        print(f"✗ Error verifying static files: {e}")
        return False

def main():
    """Main function"""
    print("Phonix Static Files Fix")
    print("=" * 30)
    
    # Verify static files configuration
    verify_static_files()
    
    # Collect static files
    success = collect_static_files()
    
    if success:
        print("\n🎉 SUCCESS: Static files issue has been resolved!")
        print("The 500 error related to missing static files should now be fixed.")
    else:
        print("\n❌ FAILURE: Could not resolve static files issue.")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)