import random
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker

from common.models import AvailableLanguage, ProficiencyLevel, Interest
from users.models import UserLanguage, UserInterest


class Command(BaseCommand):
    help = 'Seeds the database with initial data for development and testing purposes'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--users',
            nargs='+',
            type=int,
            default=20,
            help=f'Specify the number of users to create (superuser not included).',
        )

    def handle(self, *args, **options):
        # Set user count to specified quantity, or to the default if it wasn't specified
        user_count = options['users'][0]

        # Initialize Faker object, then get the user model
        fake = Faker(OrderedDict([
            ('en-US', 1),
            ('es-ES', 2),
            ('de_DE', 3),
            ('fr_FR', 4),
            ('it_IT', 5)
        ]))
        Faker.seed(random.random())
        user_model = get_user_model()

        # Create and save admin user. If it already exists, skip it.
        try:
            admin = user_model.objects.create_user(
                username="admin",
                email="admin@example.com",
                password="password",
                is_staff=True
            )
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created user "{admin}"'))
        except IntegrityError:
            self.stdout.write(self.style.WARNING('Skipped creation of "admin" user: user already exists.'))

        # Create and save a list of users
        users = []
        for i in range(user_count):
            user_profile = fake.simple_profile()
            user = user_model.objects.create_user(
                username=user_profile['username'],
                email=user_profile['mail'],
                password="password",
                description=fake.paragraph(nb_sentences=5)
            )
            users.append(user)
            user.save()

        # Fetch the enums for languages, proficiency levels and interests as lists
        languages = list(AvailableLanguage)
        proficiency_levels = [
            ProficiencyLevel.A1,
            ProficiencyLevel.A2,
            ProficiencyLevel.B1,
            ProficiencyLevel.B2,
            ProficiencyLevel.C1,
            ProficiencyLevel.C2,
        ]
        interests = list(Interest)

        # Then, perform additional operations to each user object
        for user in users:
            # Add three users as friends to each user
            potential_friends = users.copy()
            # Exclude the user from the list of potential friends to avoid saving themselves as their own friend
            potential_friends.remove(user)
            friends = random.sample(potential_friends, k=3)
            for friend in friends:
                user.friends.add(friend)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created user "{user}"'))

            # Add a native language to each user
            available_languages = languages.copy()
            native_language_value = random.choice(languages)
            native_language_object = UserLanguage(
                user=user,
                language=native_language_value,
                level=ProficiencyLevel.NATIVE
            )
            native_language_object.save()

            # Add a foreign language to each user. First, remove native language from list of available languages to
            # avoid setting it again as the user's foreign language
            available_languages.remove(native_language_value)
            foreign_language_object = UserLanguage(
                user=user,
                language=random.choice(available_languages),
                level=random.choice(proficiency_levels)
            )
            foreign_language_object.save()

            # Add two interests to each user
            user_interests = random.sample(interests, k=2)
            for interest in user_interests:
                interest_object = UserInterest(
                    user=user,
                    interest=interest
                )
                interest_object.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully added languages and interests to user "{user}"'))
