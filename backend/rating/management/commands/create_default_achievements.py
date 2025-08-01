from django.core.management.base import BaseCommand
from rating.models import Achievement


class Command(BaseCommand):
    help_text = 'Create default achievements for the rating system'

    def handle(self, *args, **options):
        default_achievements = [
            {
                'name': 'First Bite',
                'description': 'Write your very first review',
                'reviews_required': 1,
                'icon': '🔥'
            },
            {
                'name': 'Newbie Shaurmie',
                'description': 'Write 10 reviews to become a newbie shaurmie',
                'reviews_required': 10,
                'icon': '🌯'
            },
            {
                'name': 'Shawarma Enthusiast',
                'description': 'Write 25 reviews to show your enthusiasm',
                'reviews_required': 25,
                'icon': '⭐'
            },
            {
                'name': 'Shawarma Expert',
                'description': 'Write 50 reviews to become an expert',
                'reviews_required': 50,
                'icon': '🏆'
            },
            {
                'name': 'Shawarma Master',
                'description': 'Write 100 reviews to achieve mastery',
                'reviews_required': 100,
                'icon': '👑'
            },
            {
                'name': 'Shawarma Legend',
                'description': 'Write 250 reviews to become a legend',
                'reviews_required': 250,
                'icon': '⚡'
            }
        ]

        for achievement_data in default_achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created achievement: {achievement.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Achievement already exists: {achievement.name}'
                    )
                )
