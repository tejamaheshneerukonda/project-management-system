from django.core.management.base import BaseCommand
from core.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create default subscription plans'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Starter',
                'plan_type': 'BASIC',
                'description': 'Perfect for small teams getting started with project management',
                'price': 29.00,
                'billing_cycle': 'MONTHLY',
                'max_users': 5,
                'max_projects': 10,
                'max_storage_gb': 10,
                'max_api_calls': 1000,
                'has_analytics': False,
                'has_advanced_reporting': False,
                'has_api_access': False,
                'has_priority_support': False,
                'has_custom_integrations': False,
                'has_white_label': False,
                'is_active': True,
                'is_popular': False,
                'sort_order': 1,
            },
            {
                'name': 'Professional',
                'plan_type': 'PROFESSIONAL',
                'description': 'Advanced features for growing teams and businesses',
                'price': 99.00,
                'billing_cycle': 'MONTHLY',
                'max_users': 25,
                'max_projects': 50,
                'max_storage_gb': 100,
                'max_api_calls': 10000,
                'has_analytics': True,
                'has_advanced_reporting': True,
                'has_api_access': True,
                'has_priority_support': True,
                'has_custom_integrations': False,
                'has_white_label': False,
                'is_active': True,
                'is_popular': True,
                'sort_order': 2,
            },
            {
                'name': 'Enterprise',
                'plan_type': 'ENTERPRISE',
                'description': 'Full-featured solution for large organizations',
                'price': 299.00,
                'billing_cycle': 'MONTHLY',
                'max_users': 100,
                'max_projects': 200,
                'max_storage_gb': 500,
                'max_api_calls': 50000,
                'has_analytics': True,
                'has_advanced_reporting': True,
                'has_api_access': True,
                'has_priority_support': True,
                'has_custom_integrations': True,
                'has_white_label': True,
                'is_active': True,
                'is_popular': False,
                'sort_order': 3,
            },
            {
                'name': 'Enterprise Yearly',
                'plan_type': 'ENTERPRISE',
                'description': 'Enterprise plan with yearly billing (2 months free)',
                'price': 2990.00,
                'billing_cycle': 'YEARLY',
                'max_users': 100,
                'max_projects': 200,
                'max_storage_gb': 500,
                'max_api_calls': 50000,
                'has_analytics': True,
                'has_advanced_reporting': True,
                'has_api_access': True,
                'has_priority_support': True,
                'has_custom_integrations': True,
                'has_white_label': True,
                'is_active': True,
                'is_popular': False,
                'sort_order': 4,
            },
        ]

        created_count = 0
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created subscription plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Subscription plan already exists: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} subscription plans')
        )
