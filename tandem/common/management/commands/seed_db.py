import random
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.timezone import make_aware
from faker import Faker

from channels.models import Channel, Membership, ChannelInterest, ChannelRole
from common.models import AvailableLanguage, ProficiencyLevel, Interest
from users.models import UserLanguage, UserInterest
from chats.models import UserChatMessage, ChannelChatMessage


class Command(BaseCommand):
    help = 'Seeds the database with initial data for development and testing purposes'
    USER_COUNT = 50

    def handle(self, *args, **options):
        """
        Insert initial data into the DB.

        The inserted data consists of a superuser, users and channels, and their respective message objects. By
        default, it creates 50 users and 5 channels.
        """

        # Initialize Faker object, then get the user model
        fake = Faker(OrderedDict([
            ('en-US', 1),
            ('es-ES', 2),
            ('de_DE', 3),
            ('fr_FR', 4),
            ('it_IT', 5)
        ]))
        Faker.seed(random.randint(0, 1000))
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
            self.stdout.write(self.style.WARNING('Skipping creation of "admin" user, as it already exists.'))

        # Create and save a list of users
        users = []
        for i in range(self.USER_COUNT):
            user_profile = fake.simple_profile()
            user_id = user_model.objects.create_user(
                username=user_profile['username'],
                email=user_profile['mail'],
                password="password",
                description=fake.paragraph(nb_sentences=5)
            )
            users.append(user_id)
            user_id.save()

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
        for user_id in users:
            # Add three users as friends to each user
            potential_friends = users.copy()
            # Exclude the user from the list of potential friends to avoid saving themselves as their own friend
            potential_friends.remove(user_id)
            friends = random.sample(potential_friends, k=3)
            for friend in friends:
                user_id.friends.add(friend)
            user_id.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created user "{user_id}"'))

            # Add a native language to each user
            available_languages = languages.copy()
            native_language_value = random.choice(languages)
            native_language_object = UserLanguage(
                user=user_id,
                language=native_language_value,
                level=ProficiencyLevel.NATIVE
            )
            native_language_object.save()

            # Add a foreign language to each user. First, remove native language from list of available languages to
            # avoid setting it again as the user's foreign language
            available_languages.remove(native_language_value)
            foreign_language_object = UserLanguage(
                user=user_id,
                language=random.choice(available_languages),
                level=random.choice(proficiency_levels)
            )
            foreign_language_object.save()

            # Add two interests to each user
            user_interests = random.sample(interests, k=2)
            for interest in user_interests:
                interest_object = UserInterest(
                    user=user_id,
                    interest=interest
                )
                interest_object.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added languages and interests to user "{user_id}"'))

            # Create user messages
            # A number of messages is created randomly for each friend
            for friend_id in user_id.friends.values_list('id', flat=True):
                for i in range(10):
                    message = UserChatMessage(
                        author=user_id,
                        content=fake.sentence(nb_words=20),
                        timestamp=make_aware(fake.date_time_this_month()),
                        recipient_id=friend_id
                    )
                    message.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added messages to user "{user_id}"'))

        # Create channel
        # A channel is created for each available language. All languages span levels A1 through C2
        channels = []
        for language in languages:
            channel = Channel(
                name=fake.slug(),
                description=fake.paragraph(nb_sentences=5),
                language=language,
                start_proficiency_level=proficiency_levels[0],
                end_proficiency_level=proficiency_levels[-1]
            )
            channels.append(channel)
            channel.save()

            # Add a random interest to the channel
            channel_interest = ChannelInterest(
                channel=channel,
                interest=random.choice(interests)
            )
            channel_interest.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully created channel "{channel.name}"'))

        # Create channel memberships and messages for all users
        # Each user is subscribed to the channels of the foreign languages that they speak and assigned a random role
        # Then, messages are created for each user in the channel
        for channel in channels:
            users = UserLanguage.objects \
                .filter(language=channel.language) \
                .exclude(level=ProficiencyLevel.NATIVE) \
                .values_list('user', flat=True)
            for user_id in users:
                membership = Membership(
                    user_id=user_id,
                    channel=channel,
                    role=random.choice(list(ChannelRole))
                )
                membership.save()

                for i in range(5):
                    message = ChannelChatMessage(
                        author_id=user_id,
                        content=fake.sentence(nb_words=20),
                        timestamp=make_aware(fake.date_time_this_month()),
                        channel=channel
                    )
                    message.save()

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully subscribed user with id {user_id} to channel "{channel.name}" and created messages'
                ))
