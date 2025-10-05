from django.core.management.base import BaseCommand
from apps.core.models import UserRole, Module, RolePermission

class Command(BaseCommand):
    help = "Create admin role and assign all permissions to all modules"

    def handle(self, *args, **kwargs):
        # Create or get admin role
        admin_role, created = UserRole.objects.get_or_create(
            name="Admin",
            defaults={"description": "Administrator with full access to all modules"}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Admin role created"))
        else:
            self.stdout.write(self.style.WARNING("Admin role already exists"))

        modules = Module.objects.all()
        created_count = 0
        updated_count = 0

        for module in modules:
            perm, created_perm = RolePermission.objects.get_or_create(
                role=admin_role,
                module=module,
                defaults={
                    "can_view": True,
                    "can_create": True,
                    "can_edit": True,
                    "can_delete": True,
                    "can_approve": True,
                    "can_export": True,
                    "can_print": True,
                    "can_view_all": True,
                }
            )
            if created_perm:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Permissions assigned for module: {module.name}"))
            else:
                # Update existing permissions to full access
                perm.can_view = True
                perm.can_create = True
                perm.can_edit = True
                perm.can_delete = True
                perm.can_approve = True
                perm.can_export = True
                perm.can_print = True
                perm.can_view_all = True
                perm.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated permissions for module: {module.name}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {created_count}, Updated: {updated_count} permissions for Admin role."
        ))
