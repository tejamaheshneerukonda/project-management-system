from django.core.management.base import BaseCommand
from core.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Add monthly, quarterly, and yearly plans for all plan types'

    def handle(self, *args, **options):
        plans = [
            # Starter Plans
            {
                'name': 'Starter Monthly',
                'plan_type': 'BASIC',
                'description': 'Perfect for small teams getting started - monthly billing',
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
                'name': 'Starter Quarterly',
                'plan_type': 'BASIC',
                'description': 'Perfect for small teams getting started - quarterly billing (save 5%)',
                'price': 82.65,  # $29 * 3 * 0.95 = $82.65 (5% discount)
                'billing_cycle': 'QUARTERLY',
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
                'sort_order': 2,
            },
            {
                'name': 'Starter Yearly',
                'plan_type': 'BASIC',
                'description': 'Perfect for small teams getting started - yearly billing (save 2 months)',
                'price': 290.00,  # $29 * 10 = $290 (2 months free)
                'billing_cycle': 'YEARLY',
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
                'sort_order': 3,
            },
            
            # Professional Plans
            {
                'name': 'Professional Monthly',
                'plan_type': 'PROFESSIONAL',
                'description': 'Advanced features for growing teams - monthly billing',
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
                'sort_order': 4,
            },
            {
                'name': 'Professional Quarterly',
                'plan_type': 'PROFESSIONAL',
                'description': 'Advanced features for growing teams - quarterly billing (save 5%)',
                'price': 282.15,  # $99 * 3 * 0.95 = $282.15 (5% discount)
                'billing_cycle': 'QUARTERLY',
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
                'is_popular': False,
                'sort_order': 5,
            },
            {
                'name': 'Professional Yearly',
                'plan_type': 'PROFESSIONAL',
                'description': 'Advanced features for growing teams - yearly billing (save 2 months)',
                'price': 990.00,  # $99 * 10 = $990 (2 months free)
                'billing_cycle': 'YEARLY',
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
                'is_popular': False,
                'sort_order': 6,
            },
            
            # Enterprise Plans
            {
                'name': 'Enterprise Monthly',
                'plan_type': 'ENTERPRISE',
                'description': 'Full-featured solution for large organizations - monthly billing',
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
                'sort_order': 7,
            },
            {
                'name': 'Enterprise Quarterly',
                'plan_type': 'ENTERPRISE',
                'description': 'Full-featured solution for large organizations - quarterly billing (save 5%)',
                'price': 852.15,  # $299 * 3 * 0.95 = $852.15 (5% discount)
                'billing_cycle': 'QUARTERLY',
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
                'sort_order': 8,
            },
            {
                'name': 'Enterprise Yearly',
                'plan_type': 'ENTERPRISE',
                'description': 'Full-featured solution for large organizations - yearly billing (save 2 months)',
                'price': 2990.00,  # $299 * 10 = $2,990 (2 months free)
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
                'sort_order': 9,
            },
        ]

        created_count = 0
        updated_count = 0
        
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
                # Update existing plan with new data
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated subscription plan: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {created_count + updated_count} subscription plans')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created: {created_count}, Updated: {updated_count}')
        )
