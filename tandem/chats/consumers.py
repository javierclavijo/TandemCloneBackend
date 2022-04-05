import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from communities.models import Membership


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.chat_ids = self.get_chat_ids()

        # Join groups of all the user's chats
        for chat_id in self.chat_ids:
            async_to_sync(self.channel_layer.group_add)(
                chat_id,
                self.channel_name
            )

        self.accept()

    def get_chat_ids(self):
        # Get user, then fetch list of the user's chat's IDs
        user = self.scope['user']
        memberships = Membership.objects.filter(user=user).values_list('channel__id', flat=True)
        user_chats = user.chats.all().values_list('pk', flat=True)
        return [str(x) for x in list(memberships) + list(user_chats)]

    def disconnect(self, close_code):
        # Leave room group
        for chat_id in self.chat_ids:
            async_to_sync(self.channel_layer.group_discard)(
                chat_id,
                self.channel_name
            )

    # Receive message from WebSocket client, fetch the chat's ID and send it to the respective group
    def receive_json(self, content):
        chat_id = content['chat_id']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            chat_id,
            {
                'type': 'chat_message',
                'message': content
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
