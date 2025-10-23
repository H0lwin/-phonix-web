#!/usr/bin/env python
"""
Final Verification Script for All Fixes
"""

import os
import sys
from pathlib import Path

def verify_all_fixes():
    """Verify that all fixes have been successfully implemented"""
    
    print("=== Final Verification of All Fixes ===")
    
    # 1. Check ALLOWED_HOSTS
    print("\n1. Checking ALLOWED_HOSTS...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
        import django
        django.setup()
        from django.conf import settings
        
        allowed_hosts = settings.ALLOWED_HOSTS
        print(f"   ALLOWED_HOSTS: {allowed_hosts}")
        
        # Check if required hosts are present
        required_hosts = ['shahereraz.ir', 'www.shahereraz.ir']
        missing_hosts = [host for host in required_hosts if host not in allowed_hosts]
        
        if not missing_hosts:
            print("   ✓ All required hosts are present in ALLOWED_HOSTS")
        else:
            print(f"   ✗ Missing hosts: {missing_hosts}")
            return False
            
    except Exception as e:
        print(f"   ✗ Error checking ALLOWED_HOSTS: {e}")
        return False
    
    # 2. Check template directory
    print("\n2. Checking template directory...")
    try:
        production_template_path = Path("/home/shaherer/phonix/phonix-web/templates")
        print(f"   Production template path: {production_template_path}")
        
        if production_template_path.exists():
            print("   ✓ Production template directory exists")
            
            # Check if login.html exists
            login_template = production_template_path / "login.html"
            if login_template.exists():
                print("   ✓ login.html exists in production location")
            else:
                print("   ✗ login.html not found in production location")
                return False
        else:
            print("   ✗ Production template directory does not exist")
            return False
            
    except Exception as e:
        print(f"   ✗ Error checking template directory: {e}")
        return False
    
    # 3. Check .env file
    print("\n3. Checking .env file...")
    try:
        env_file = Path(__file__).resolve().parent / ".env"
        if env_file.exists():
            print("   ✓ .env file exists")
            
            # Check contents
            with open(env_file, 'r') as f:
                content = f.read()
                if 'shahereraz.ir' in content:
                    print("   ✓ .env file contains shahereraz.ir")
                else:
                    print("   ✗ .env file does not contain shahereraz.ir")
                    return False
        else:
            print("   ✗ .env file does not exist")
            return False
            
    except Exception as e:
        print(f"   ✗ Error checking .env file: {e}")
        return False
    
    # 4. Check settings.py modifications
    print("\n4. Checking settings.py modifications...")
    try:
        settings_file = Path(__file__).resolve().parent / "phonix" / "settings.py"
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'shahereraz.ir' in content:
                print("   ✓ settings.py contains shahereraz.ir")
            else:
                print("   ✗ settings.py does not contain shahereraz.ir")
                return False
                
    except Exception as e:
        print(f"   ✗ Error checking settings.py: {e}")
        return False
    
    print("\n" + "="*50)
    print("FINAL VERIFICATION COMPLETE")
    print("="*50)
    print("✓ All fixes have been successfully implemented!")
    print("✓ The application should now work correctly on shahereraz.ir")
    print("✓ Please restart your Django application for changes to take effect.")
    
    return True

if __name__ == "__main__":
    success = verify_all_fixes()
    if success:
        print("\n🎉 SUCCESS: All issues have been resolved!")
    else:
        print("\n❌ FAILURE: Some issues remain. Please check the errors above.")
    
    sys.exit(0 if success else 1)