import random
from collections import OrderedDict
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.timezone import get_default_timezone
from faker import Faker

from chats.models import UserChatMessage, ChannelChatMessage, UserChat
from common.models import AvailableLanguage, ProficiencyLevel
from communities.models import Channel, Membership, ChannelRole
from users.models import UserLanguage


def save_random_image(instance):
    # Get and save a random placeholder image for the user or channel
    # Sources: https://stackoverflow.com/a/701430, https://stackoverflow.com/a/19037233
    path = Path(__file__).parent.parent.parent / 'resources' / 'images'
    random_file = random.choice(list(path.iterdir()))
    with open(random_file, 'rb') as file:
        image = File(file)
        instance.image = image
        instance.save()


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

        # Create and save a list of users. First, create a test user.
        users = []
        user = user_model.objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password="password",
            description=fake.paragraph(nb_sentences=5)
        )
        users.append(user)
        user.save()

        for i in range(self.USER_COUNT):
            user_profile = fake.simple_profile()

            user = user_model.objects.create_user(
                username=user_profile['username'],
                email=user_profile['mail'],
                password="password",
                description=fake.paragraph(nb_sentences=5),
            )
            users.append(user)
            user.save()

            # Get and save a random image
            save_random_image(user)

        # Fetch the enums for languages and proficiency levels as lists
        languages = list(AvailableLanguage)
        proficiency_levels = [
            ProficiencyLevel.BEGINNER,
            ProficiencyLevel.INTERMEDIATE,
            ProficiencyLevel.ADVANCED,
            ProficiencyLevel.NATIVE,
        ]

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

            self.stdout.write(self.style.SUCCESS(f'Successfully added languages to user "{user}"'))

        # Create user chats and messages
        # A number of messages is created randomly for each friend. This must be kept in a separate loop, as friends are
        # added on user creation --thus, no messages would be created from a user to a friend that is created later and
        # adds them.
        for user in users:
            for friend in user.friends.all():
                chat = None
                try:
                    # Check if a chat exists for the two users, and create it if it doesn't
                    chat = UserChat.objects.filter(users=user).get(users=friend)

                except UserChat.DoesNotExist:
                    chat = UserChat()
                    chat.save()
                    chat.users.add(friend)
                    chat.users.add(user)
                    chat.save()

                finally:
                    for i in range(10):
                        message = UserChatMessage(
                            author=user,
                            content=fake.sentence(nb_words=20),
                            timestamp=fake.date_time_this_month(tzinfo=get_default_timezone()),
                            chat=chat
                        )
                        message.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added messages to user "{user}"'))

        # Create channel
        # A channel is created for each available language, with an Intermediate language level
        channels = []
        for language in languages:
            channel = Channel(
                name=fake.slug(),
                description=fake.paragraph(nb_sentences=5),
                language=language,
                level=proficiency_levels[1]
            )
            channels.append(channel)
            channel.save()
            save_random_image(channel)

            self.stdout.write(self.style.SUCCESS(f'Successfully created channel "{channel.name}"'))

        # Create channel memberships and messages for all users
        # Each user is subscribed to the channels of the foreign languages that they speak and assigned a random role
        # Then, messages are created for each user in the channel
        for channel in channels:
            users = UserLanguage.objects \
                .filter(language=channel.language) \
                .exclude(level=ProficiencyLevel.NATIVE) \
                .values_list('user', flat=True)
            for user in users:
                membership = Membership(
                    user_id=user,
                    channel=channel,
                    role=random.choice(list(ChannelRole))
                )
                membership.save()

                for i in range(5):
                    message = ChannelChatMessage(
                        author_id=user,
                        content=fake.sentence(nb_words=20),
                        timestamp=fake.date_time_this_month(tzinfo=get_default_timezone()),
                        channel=channel
                    )
                    message.save()

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully subscribed user with id {user} to channel "{channel.name}" and created messages'
                ))
