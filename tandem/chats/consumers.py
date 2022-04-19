from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from chats.models import UserChat, ChannelChatMessage, UserChatMessage
from communities.models import Membership, Channel


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        if isinstance(user, AnonymousUser):
            # If the user is not authenticated, disconnect to prevent exceptions
            self.disconnect(1003)

        chat_ids = self.get_chat_ids(user)
        self.chat_ids = chat_ids

        # Join groups of all the user's chats
        for chat_id in self.chat_ids:
            async_to_sync(self.channel_layer.group_add)(
                chat_id,
                self.channel_name
            )

        self.accept()

    def get_chat_ids(self, user):
        # Get user, then fetch list of the user's chat's IDs
        memberships = Membership.objects.filter(user=user).values_list('channel__id', flat=True)
        user_chats = user.chats.all().values_list('pk', flat=True)
        return [str(x) for x in list(memberships) + list(user_chats)]

    def disconnect(self, close_code):
        # Leave room group
        try:
            for chat_id in self.chat_ids:
                async_to_sync(self.channel_layer.group_discard)(
                    chat_id,
                    self.channel_name
                )
        except AttributeError as e:
            # If the consumer object has no 'chat_ids' attribute (i.e. is not properly initialized), do nothing
            pass

    def save_message(self, message):
        """Saves a message to the DB before sending it."""
        try:
            chat_id = message['chat_id']
            chat_type = message['chat_type']
            message_content = message['content']
            user = self.scope['user']

            if chat_type == "channel":
                channel = Channel.objects.get(id=chat_id)

                # Check that the user has permission to post in the chat
                if not channel.memberships.get(user=user):
                    raise PermissionDenied("User is not allowed to post messages to this chat.")

                message_object = ChannelChatMessage(
                    content=message_content,
                    author=user,
                    channel=channel
                )
                message_object.save()

            elif chat_type == "user":
                chat = UserChat.objects.get(id=chat_id)

                # Check that the user has permission to post in the chat (same as above)
                if user not in chat.users.all():
                    raise PermissionDenied("User is not allowed to post messages to this chat.")

                message_object = UserChatMessage(
                    content=message_content,
                    author=user,
                    chat=chat
                )
                message_object.save()

            else:
                raise ValueError("Attribute chat_type must be one of the following: 'channel', 'user'.")

            return {
                'id': str(message_object.id),
                'chat_id': chat_id,
                'url': "mock_url",
                'author': {
                    'id': str(user.id),
                    'url': "mock_url",
                    'username': user.username
                },
                'content': message_content,
                'timestamp': message_object.timestamp.isoformat(),
            }
        except (KeyError, ValueError, Channel.DoesNotExist, UserChat.DoesNotExist, PermissionDenied) as e:
            # If the message does not have the required attributes or the provided ID is not found, close the
            # connection.
            # TODO: log error
            self.disconnect(1003)

    # Receive message from WebSocket client, fetch the chat's ID and send it to the respective group
    def receive_json(self, content):
        # Persist message to DB
        chat_id = content['chat_id']
        saved_message = self.save_message(content)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            chat_id,
            {
                'type': 'chat_message',
                'message': saved_message
            }
        )

    # Receive message from room group, forward it to the client
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send_json({
            'message': message
        })

# Code initially sourced from https://channels.readthedocs.io/en/stable/tutorial/part_2.html
