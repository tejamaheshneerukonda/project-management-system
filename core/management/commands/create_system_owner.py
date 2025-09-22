from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SystemOwner


class Command(BaseCommand):
    help = 'Create SystemOwner profile for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to create SystemOwner profile for')
        parser.add_argument('--phone', type=str, help='Phone number for the owner profile')

    def handle(self, *args, **options):
        username = options['username']
        phone = options.get('phone', '')

        try:
            user = User.objects.get(username=username)
            
            # Check if SystemOwner profile already exists
            if hasattr(user, 'system_owner_profile'):
                self.stdout.write(
                    self.style.WARNING(f'SystemOwner profile already exists for user: {username}')
                )
                return

            # Create SystemOwner profile
            owner_profile = SystemOwner.objects.create(
                user=user,
                phone=phone
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created SystemOwner profile for user: {username}')
            )
            self.stdout.write(f'Profile ID: {owner_profile.id}')
            if phone:
                self.stdout.write(f'Phone: {phone}')

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating SystemOwner profile: {str(e)}')
            )
