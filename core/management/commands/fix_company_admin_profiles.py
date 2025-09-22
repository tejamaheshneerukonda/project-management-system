from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Company, CompanyAdmin

class Command(BaseCommand):
    help = 'Fix CompanyAdmin profiles for users who have companies but no admin profile'

    def handle(self, *args, **options):
        # Find users who have companies but no CompanyAdmin profile
        companies_without_admin_profiles = Company.objects.filter(
            admin_user__isnull=False
        ).exclude(
            admin_user__company_admin_profile__isnull=False
        )
        
        self.stdout.write(f'Found {companies_without_admin_profiles.count()} companies without admin profiles')
        
        for company in companies_without_admin_profiles:
            admin_user = company.admin_user
            
            # Create CompanyAdmin profile
            company_admin, created = CompanyAdmin.objects.get_or_create(
                user=admin_user,
                defaults={
                    'company': company,
                    'phone': ''
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created CompanyAdmin profile for {admin_user.username} - {company.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'CompanyAdmin profile already exists for {admin_user.username} - {company.name}')
                )
        
        # Also check for orphaned CompanyAdmin profiles
        orphaned_admins = CompanyAdmin.objects.filter(company__isnull=True)
        if orphaned_admins.exists():
            self.stdout.write(f'Found {orphaned_admins.count()} orphaned CompanyAdmin profiles')
            for admin in orphaned_admins:
                self.stdout.write(
                    self.style.ERROR(f'Orphaned admin: {admin.user.username} (ID: {admin.id})')
                )
        
        self.stdout.write(self.style.SUCCESS('CompanyAdmin profile check completed'))
