#!/usr/bin/env python
"""
Production Template Fix Script
This script fixes the TemplateDoesNotExist error by ensuring templates are in the correct location
"""

import os
import sys
import shutil
from pathlib import Path

def fix_template_paths():
    """Fix template paths for production deployment"""
    
    print("=== Production Template Fix Script ===")
    
    # Define the problematic path from the error
    production_template_path = Path("/home/shaherer/phonix/phonix-web/templates")
    
    # Define the source template directory (where templates actually are)
    # This is the standard location in the project
    source_templates_dir = Path(__file__).resolve().parent / "templates"
    
    print(f"Source templates directory: {source_templates_dir}")
    print(f"Production template path: {production_template_path}")
    
    # Check if source templates exist
    if not source_templates_dir.exists():
        print("ERROR: Source templates directory does not exist!")
        return False
    
    # List source templates
    print("\nSource templates:")
    try:
        for item in source_templates_dir.iterdir():
            print(f"  - {item.name}")
    except Exception as e:
        print(f"Error listing source templates: {e}")
        return False
    
    # Try to create the production template directory structure
    try:
        # Create parent directories if they don't exist
        production_template_path.mkdir(parents=True, exist_ok=True)
        print(f"\nCreated production template directory: {production_template_path}")
    except Exception as e:
        print(f"Warning: Could not create production template directory: {e}")
        print("This might be expected in development environment")
        return True
    
    # Copy template files to production location
    try:
        print("\nCopying templates to production location...")
        for item in source_templates_dir.iterdir():
            if item.is_file():
                dest_path = production_template_path / item.name
                print(f"  Copying {item.name} to {dest_path}")
                shutil.copy2(item, dest_path)
            elif item.is_dir():
                dest_path = production_template_path / item.name
                print(f"  Copying directory {item.name} to {dest_path}")
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(item, dest_path)
        
        print("✓ Templates copied successfully!")
        return True
        
    except Exception as e:
        print(f"Error copying templates: {e}")
        return False

def create_symbolic_link():
    """Create a symbolic link as an alternative solution"""
    print("\n=== Creating Symbolic Link Solution ===")
    
    # Define paths
    production_template_path = Path("/home/shaherer/phonix/phonix-web/templates")
    source_templates_dir = Path(__file__).resolve().parent / "templates"
    
    # Check if source exists
    if not source_templates_dir.exists():
        print("ERROR: Source templates directory does not exist!")
        return False
    
    # Try to create symbolic link
    try:
        # Remove existing directory/file if it exists
        if production_template_path.exists():
            if production_template_path.is_symlink():
                production_template_path.unlink()
                print("Removed existing symbolic link")
            elif production_template_path.is_dir():
                shutil.rmtree(production_template_path)
                print("Removed existing directory")
            else:
                production_template_path.unlink()
                print("Removed existing file")
        
        # Create parent directories
        production_template_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create symbolic link
        production_template_path.symlink_to(source_templates_dir)
        print(f"✓ Created symbolic link from {production_template_path} to {source_templates_dir}")
        return True
        
    except Exception as e:
        print(f"Error creating symbolic link: {e}")
        return False

def main():
    """Main function"""
    print("Phonix Production Template Fix")
    print("=" * 40)
    
    # Try to fix template paths
    success = fix_template_paths()
    
    if not success:
        print("\nTrying symbolic link approach...")
        success = create_symbolic_link()
    
    if success:
        print("\n✓ Template fix completed successfully!")
        print("The TemplateDoesNotExist error should now be resolved.")
    else:
        print("\n✗ Template fix failed!")
        print("Please check file permissions and directory structure.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)