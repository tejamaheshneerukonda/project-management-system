from django.core.management.base import BaseCommand
from core.models import Company, Employee, ChatRoom

class Command(BaseCommand):
    help = 'Create default chat rooms for all companies'

    def handle(self, *args, **options):
        companies = Company.objects.all()
        
        for company in companies:
            # Get the first employee as the creator, or skip if no employees
            first_employee = Employee.objects.filter(company=company).first()
            if not first_employee:
                self.stdout.write(
                    self.style.WARNING(f'No employees found for {company.name}, skipping...')
                )
                continue
            
            # Check if General room already exists
            general_room, created = ChatRoom.objects.get_or_create(
                name='General',
                company=company,
                defaults={
                    'room_type': 'GROUP',
                    'description': 'General discussion room for all employees',
                    'is_active': True,
                    'created_by': first_employee
                }
            )
            
            if created:
                # Add all employees to the General room
                employees = Employee.objects.filter(company=company)
                general_room.participants.set(employees)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created General room for {company.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'General room already exists for {company.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Default chat rooms setup completed!')
        )
