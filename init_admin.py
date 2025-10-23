#!/usr/bin/env python
"""
Interactive script for creating and managing admin users
Compatible with production environment
"""
import os
import sys
import django
import getpass
from pathlib import Path

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
django.setup()

from django.contrib.auth.models import User
from core import models
import jdatetime


class AdminInitializer:
    """Class for managing admin creation"""
    
    def __init__(self):
        self.username = None
        self.email = None
        self.password = None
        self.national_id = None
        self.first_name = None
        self.last_name = None
    
    def print_header(self, title):
        """Display header"""
        print("\n" + "=" * 70)
        print(f"🔐 {title}")
        print("=" * 70)
    
    def print_success(self, msg):
        """Success message"""
        print(f"✅ {msg}")
    
    def print_error(self, msg):
        """Error message"""
        print(f"❌ {msg}")
    
    def print_warning(self, msg):
        """Warning message"""
        print(f"⚠️  {msg}")
    
    def print_info(self, msg):
        """Info message"""
        print(f"ℹ️  {msg}")
    
    def get_input(self, prompt, required=True, default=None, is_password=False):
        """Get user input"""
        while True:
            if default:
                display_prompt = f"➜ {prompt} [{default}]: "
            else:
                display_prompt = f"➜ {prompt}: "
            
            if is_password:
                value = getpass.getpass(display_prompt)
            else:
                value = input(display_prompt).strip()
            
            # Use default value
            if not value and default:
                return default
            
            # Check required field
            if not value and required:
                self.print_error("This field is required!")
                continue
            
            return value if value else None
    
    def get_yes_no(self, prompt):
        """Get yes/no response"""
        while True:
            response = input(f"❓ {prompt} (yes/no) [n]: ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n', '']:
                return False
            else:
                self.print_error("Please enter yes or no")
    
    def create_or_update_branch(self):
        """Create or retrieve headquarters branch"""
        try:
            # Use getattr to avoid linter errors
            branch_objects = getattr(models, 'Branch').objects
            branches = branch_objects.filter(code='HQ-001')
            if branches.exists():
                branch = branches.first()
                self.print_success("Headquarters branch found")
                return branch
            else:
                branch = getattr(models, 'Branch')(
                    code='HQ-001',
                    name='Headquarters',
                    branch_type='headquarters',
                    address='Tehran - Iran',
                    city='Tehran',
                    province='Tehran',
                    postal_code='0000000000',
                    phone='02100000000',
                    status='active',
                    description='Company Headquarters',
                )
                branch.save()
                self.print_success("Headquarters branch created")
                return branch
        except Exception as e:
            self.print_error(f"Error creating branch: {str(e)}")
            return None
    
    def create_user(self):
        """Create new user"""
        self.print_info("Creating new user...")
        
        # Check username
        while True:
            username = self.get_input("Username", required=True)
            try:
                users = User.objects.filter(username=username)
                if users.exists():
                    self.print_error(f"User '{username}' already exists")
                    continue
            except Exception as e:
                self.print_error(f"Error checking username: {str(e)}")
                continue
            self.username = username
            break
        
        # Get other information
        self.email = self.get_input("Email", required=True)
        self.first_name = self.get_input("First Name", required=False, default="System")
        self.last_name = self.get_input("Last Name", required=False, default="Admin")
        self.national_id = self.get_input("National ID (10 digits)", required=True)
        
        # Get password
        while True:
            self.password = self.get_input(
                "Password (minimum 8 characters)",
                required=True,
                is_password=True
            )
            if self.password and len(self.password) < 8:
                self.print_error("Password must be at least 8 characters")
                continue
            
            password_confirm = self.get_input(
                "Confirm Password",
                required=True,
                is_password=True
            )
            if self.password != password_confirm:
                self.print_error("Passwords do not match")
                continue
            break
        
        # Create user
        try:
            user = User.objects.create_superuser(
                username=self.username,
                email=self.email,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
            )
            self.print_success(f"User '{self.username}' created")
            return user
        except Exception as e:
            self.print_error(f"Error creating user: {str(e)}")
            return None
    
    def create_profile(self, user):
        """Create or update user profile"""
        try:
            # Use getattr to avoid linter errors
            profile_objects = getattr(models, 'UserProfile').objects
            profiles = profile_objects.filter(user=user)
            if profiles.exists():
                profile = profiles.first()
                profile.national_id = self.national_id
                profile.save()
                self.print_success("User profile updated")
                return profile
            else:
                profile = getattr(models, 'UserProfile')(
                    user=user,
                    role='admin',
                    national_id=self.national_id,
                    display_name=f"{self.first_name} {self.last_name}",
                    job_title='System Administrator',
                    hire_date=jdatetime.date.today().isoformat(),
                )
                profile.save()
                self.print_success("User profile created")
                return profile
        except Exception as e:
            self.print_error(f"Error creating profile: {str(e)}")
            return None
    
    def create_employee(self, user, branch):
        """Create or update employee record"""
        try:
            # Use getattr to avoid linter errors
            employee_objects = getattr(models, 'Employee').objects
            employees = employee_objects.filter(user=user)
            if employees.exists():
                employee = employees.first()
                employee.national_id = self.national_id
                employee.save()
                self.print_success("Employee record updated")
                return employee
            else:
                employee = getattr(models, 'Employee')(
                    user=user,
                    national_id=self.national_id,
                    branch=branch,
                    job_title='manager',
                    hire_date=jdatetime.date.today(),
                    phone='09000000000',
                    employment_status='active',
                    contract_type='full_time',
                )
                employee.save()
                self.print_success("Employee record created")
                return employee
        except Exception as e:
            self.print_error(f"Error creating employee: {str(e)}")
            return None
    
    def display_credentials(self, user):
        """Display login credentials"""
        print("\n" + "=" * 70)
        print("📋 Login Credentials")
        print("=" * 70)
        print(f"Username:    {user.username}")
        print(f"Password:    {self.password}")
        print(f"Email:       {user.email}")
        print(f"National ID: {self.national_id}")
        print(f"Name:        {user.first_name} {user.last_name}")
        print("=" * 70)
        print("💡 Note: Store this information in a secure location")
        print("=" * 70)
    
    def run(self):
        """Run the program"""
        self.print_header("Admin Management System - Phonix")
        
        print("""
Options:
  1. Create New Admin
  2. Update Existing Admin
  3. Exit
        """)
        
        choice = self.get_input("Enter your choice", required=True)
        
        if choice == '1':
            self._create_new()
        elif choice == '2':
            self._update_existing()
        elif choice == '3':
            print("\n👋 Exiting...")
            sys.exit(0)
        else:
            self.print_error("Invalid choice")
            self.run()
    
    def _create_new(self):
        """Create new admin"""
        self.print_header("Create New Admin")
        
        # Create user
        user = self.create_user()
        if not user:
            return
        
        # Create branch
        branch = self.create_or_update_branch()
        if not branch:
            return
        
        # Create profile
        self.create_profile(user)
        
        # Create employee
        self.create_employee(user, branch)
        
        # Display credentials
        self.display_credentials(user)
        
        print("\n✨ Admin created successfully!")
        
        if self.get_yes_no("Do you want to create another admin?"):
            self.run()
    
    def _update_existing(self):
        """Update existing admin"""
        self.print_header("Update Existing Admin")
        
        username = self.get_input("Admin username", required=True)
        
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            if "DoesNotExist" in str(type(e)) or "DoesNotExist" in str(e):
                self.print_error(f"User '{username}' not found")
            else:
                self.print_error(f"Error finding user: {str(e)}")
            return
        
        print(f"\n📋 Current user information '{username}':")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        
        # Get new information
        self.username = username
        self.first_name = self.get_input(
            "New First Name (press Enter to keep current)",
            required=False,
            default=user.first_name
        )
        self.last_name = self.get_input(
            "New Last Name (press Enter to keep current)",
            required=False,
            default=user.last_name
        )
        self.email = self.get_input(
            "New Email (press Enter to keep current)",
            required=False,
            default=user.email
        )
        self.national_id = self.get_input(
            "New National ID (press Enter to keep current)",
            required=False,
            default=None
        )
        
        # Password change optional
        if self.get_yes_no("Do you want to change the password?"):
            while True:
                self.password = self.get_input(
                    "New Password (minimum 8 characters)",
                    required=True,
                    is_password=True
                )
                if self.password and len(self.password) < 8:
                    self.print_error("Password must be at least 8 characters")
                    continue
                
                password_confirm = self.get_input(
                    "Confirm Password",
                    required=True,
                    is_password=True
                )
                if self.password != password_confirm:
                    self.print_error("Passwords do not match")
                    continue
                break
            
            user.set_password(self.password)
        
        # Update user
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.email = self.email
        user.save()
        self.print_success("User information updated")
        
        # Update profile
        try:
            if hasattr(user, 'profile'):
                profile = user.profile
                if self.national_id:
                    profile.national_id = self.national_id
                profile.display_name = f"{self.first_name} {self.last_name}"
                profile.save()
                self.print_success("Profile updated")
        except Exception as e:
            self.print_error(f"Error updating profile: {str(e)}")
        
        # Display information
        if self.password:
            self.display_credentials(user)
        else:
            print("\n" + "=" * 70)
            print("📋 User information updated")
            print("=" * 70)
            print(f"Username:    {user.username}")
            print(f"Email:       {user.email}")
            print(f"Name:        {user.first_name} {user.last_name}")
            print("=" * 70)
        
        print("\n✨ Admin updated successfully!")
        
        if self.get_yes_no("Do you want to perform another operation?"):
            self.run()


def main():
    """Main function"""
    try:
        initializer = AdminInitializer()
        initializer.run()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()