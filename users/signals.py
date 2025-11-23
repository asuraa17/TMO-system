from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

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