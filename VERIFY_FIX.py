#!/usr/bin/env python
"""
Verification Script for Template Fix
"""

import os
import sys
from pathlib import Path

def verify_fix():
    """Verify that the template fix was successful"""
    
    print("=== Template Fix Verification ===")
    
    # Check if the production template directory was created
    production_template_path = Path("/home/shaherer/phonix/phonix-web/templates")
    print(f"Checking production template directory: {production_template_path}")
    
    if production_template_path.exists():
        print("✓ Production template directory exists")
    else:
        print("✗ Production template directory does not exist")
        return False
    
    # Check if login.html exists in production location
    login_template_path = production_template_path / "login.html"
    print(f"Checking login template: {login_template_path}")
    
    if login_template_path.exists():
        print("✓ login.html exists in production location")
    else:
        print("✗ login.html does not exist in production location")
        return False
    
    # Check file size
    try:
        size = login_template_path.stat().st_size
        print(f"✓ login.html size: {size} bytes")
    except Exception as e:
        print(f"✗ Error checking file size: {e}")
        return False
    
    # List contents of production template directory
    print("\nContents of production template directory:")
    try:
        for item in production_template_path.iterdir():
            if item.is_dir():
                print(f"  [DIR]  {item.name}")
            else:
                print(f"  [FILE] {item.name}")
    except Exception as e:
        print(f"Error listing directory contents: {e}")
        return False
    
    print("\n" + "="*40)
    print("VERIFICATION COMPLETE")
    print("="*40)
    print("✓ All checks passed!")
    print("✓ The TemplateDoesNotExist error should now be resolved.")
    print("✓ Please restart your Django application for changes to take effect.")
    
    return True

if __name__ == "__main__":
    success = verify_fix()
    sys.exit(0 if success else 1)