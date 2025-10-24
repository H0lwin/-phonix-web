@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    خودکار ایجاد UserProfile هنگام ایجاد User و تعیین دسترسی‌ها بر اساس نقش
    Automatically create UserProfile when User is created and set permissions based on role
    """
    try:
        if created or not hasattr(instance, 'userprofile'):
            # Set admin role for superusers
            role = 'admin' if instance.is_superuser else 'employee'
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=instance,
                role=role,
                display_name=f"{instance.first_name} {instance.last_name}",
                job_title='System Administrator' if instance.is_superuser else 'Employee'
            )
            
            # Additional setup for superusers
            if instance.is_superuser:
                # Ensure user is in Admin group
                admin_group, _ = Group.objects.get_or_create(name='Admin')
                instance.groups.add(admin_group)
                
                # Create headquarters branch if needed
                hq_branch, _ = Branch.objects.get_or_create(
                    code='HQ-001',
                    defaults={
                        'name': 'Headquarters',
                        'branch_type': 'headquarters',
                        'status': 'active',
                        'address': 'Main Office',
                        'city': 'Tehran',
                        'province': 'Tehran'
                    }
                )
                
                # Create employee record for admin
                if not hasattr(instance, 'employee'):
                    Employee.objects.create(
                        user=instance,
                        national_id=profile.national_id if hasattr(profile, 'national_id') else None,
                        branch=hq_branch,
                        job_title='admin',
                        employment_status='active',
                        contract_type='full_time',
                        hire_date=jdatetime.date.today()
                    )

            # Log the action
            create_activity_log(
                user=None,
                action='create' if created else 'update',
                model_name='UserProfile',
                object_id=instance.id,
                description=f"{'Created' if created else 'Updated'} {role} profile for {instance.username}"
            )
            
    except Exception as e:
        logger.error(f"Error in user profile signal: {e}", exc_info=True)