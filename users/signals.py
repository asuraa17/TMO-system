from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, BuyerProfile, ShowroomProfile, Vehicle

ROLE_GROUPS = {
    #choice = database
    User.Role.Showroom: 'showroom_user',
    User.Role.Buyer: 'buyer',
    User.Role.Tmo_officer: 'tmo_officer',
    User.Role.Inspector: 'inspector',
    User.Role.System_admin: 'system_admin',
}

@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Auto assigns user to appropriate group based on their role upon creation.
    """
    if created:
        group_name = ROLE_GROUPS.get(instance.role)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)
    
    else:
        # remove user from all groups if role is invalid
        instance.groups.clear()

        # assign to a new group if role is updated later
        group_name = ROLE_GROUPS.get(instance.role)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)

@receiver(pre_save, sender=BuyerProfile)
def reset_rejected_status_on_update(sender, instance, **kwargs):
    """
    Automatically reset verification status to pending when rejected buyer updates profile
    Only reset if the profile already exists (not on creation) and is currently rejected
    """
    if instance.pk:  
        # Check if this is an update (not creation)
        try:
            old_instance = BuyerProfile.objects.get(pk=instance.pk)
            
            # If status is rejected and profile data has changed
            if old_instance.verification_status == 'rejected':
                # Check if any key fields have changed
                fields_changed = (
                    old_instance.full_name != instance.full_name or
                    old_instance.address != instance.address or
                    old_instance.phone != instance.phone or
                    old_instance.dob != instance.dob or
                    old_instance.citizenship_file != instance.citizenship_file or
                    old_instance.nid_file != instance.nid_file or
                    old_instance.passport_photo != instance.passport_photo or
                    old_instance.signature_image != instance.signature_image
                )
                
                # If fields changed, reset verification status
                if fields_changed:
                    instance.verification_status = 'pending'
                    instance.verified_by = None
                    instance.verification_remarks = ''
                    instance.verified_at = None
        
        except BuyerProfile.DoesNotExist:
            pass


@receiver(pre_save, sender=ShowroomProfile)
def reset_rejected_showroom_status_on_update(sender, instance, **kwargs):
    """
    Automatically reset verification status to pending when rejected showroom updates profile
    Only reset if the profile already exists (not on creation) and is currently rejected
    """
    if instance.pk:
        # Check if this is an update (not creation)
        try:
            old_instance = ShowroomProfile.objects.get(pk=instance.pk)
            
            # If status is rejected and profile data has changed
            if old_instance.verification_status == 'rejected':
                # Check if any key fields have changed
                fields_changed = (
                    old_instance.showroom_name != instance.showroom_name or
                    old_instance.registration_number != instance.registration_number or
                    old_instance.pan_number != instance.pan_number or
                    old_instance.address != instance.address or
                    old_instance.phone != instance.phone or
                    old_instance.alternative_phone != instance.alternative_phone or
                    old_instance.owner_name != instance.owner_name or
                    old_instance.owner_citizenship != instance.owner_citizenship or
                    old_instance.registration_certificate != instance.registration_certificate or
                    old_instance.pan_certificate != instance.pan_certificate or
                    old_instance.owner_citizenship_file != instance.owner_citizenship_file or
                    old_instance.showroom_photo != instance.showroom_photo
                )
                
                # If fields changed, reset verification status
                if fields_changed:
                    instance.verification_status = 'pending'
                    instance.verified_by = None
                    instance.verification_remarks = ''
                    instance.verified_at = None
        
        except ShowroomProfile.DoesNotExist:
            pass

@receiver(pre_save, sender=Vehicle)
def reset_rejected_vehicle_status_on_update(sender, instance, **kwargs):
    """
    Automatically reset verification status to pending when rejected vehicle is updated
    Only reset if the vehicle already exists (not on creation) and is currently rejected
    """
    if instance.pk:
        try:
            old_instance = Vehicle.objects.get(pk=instance.pk)
            
            # If status is rejected and vehicle data has changed
            if old_instance.verification_status == 'rejected':
                # Check if any key vehicle fields have changed
                fields_changed = (
                    old_instance.chassis_number != instance.chassis_number or
                    old_instance.engine_number != instance.engine_number or
                    old_instance.make != instance.make or
                    old_instance.model != instance.model or
                    old_instance.year != instance.year or
                    old_instance.color != instance.color or
                    old_instance.vehicle_type != instance.vehicle_type or
                    old_instance.fuel_type != instance.fuel_type or
                    old_instance.engine_cc != instance.engine_cc or
                    old_instance.seating_capacity != instance.seating_capacity or
                    old_instance.price != instance.price or
                    old_instance.photo_front != instance.photo_front or
                    old_instance.photo_back != instance.photo_back or
                    old_instance.photo_left != instance.photo_left or
                    old_instance.photo_right != instance.photo_right or
                    old_instance.payment_receipt != instance.payment_receipt
                )
                
                # If fields changed, reset verification status
                if fields_changed:
                    instance.verification_status = 'pending'
                    instance.verified_by = None
                    instance.verification_remarks = ''
                    instance.verified_at = None
        
        except Vehicle.DoesNotExist:
            pass