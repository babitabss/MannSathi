import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group  = f'chat_{self.booking_id}'
        self.user        = self.scope.get('user', None)

        await self.accept()

        if not self.user or not self.user.is_authenticated:
            await self.send(text_data=json.dumps({'error': 'Not authenticated'}))
            await self.close()
            return

        allowed = await self.is_allowed()
        if not allowed:
            await self.send(text_data=json.dumps({'error': 'Not allowed'}))
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)

        messages = await self.get_messages()
        for msg in messages:
            await self.send(text_data=json.dumps(msg))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group'):
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data    = json.loads(text_data)
        message = data.get('message', '').strip()

        if not message:
            return

        saved = await self.save_message(message)

        # Notify the other person
        await self.notify_other_user(message)

        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':      'chat_message',
                'message':   saved['message'],
                'sender':    saved['sender'],
                'timestamp': saved['timestamp'],
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message':   event['message'],
            'sender':    event['sender'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def is_allowed(self):
        from mental.models import Booking
        try:
            booking = Booking.objects.get(pk=self.booking_id)
            user    = self.user
            return (
                user.is_authenticated and
                (user == booking.user or user == booking.counselor.user)
            )
        except Booking.DoesNotExist:
            return False

    @database_sync_to_async
    def get_messages(self):
        from .models import ChatMessage
        messages = ChatMessage.objects.filter(
            booking_id=self.booking_id
        ).select_related('sender').order_by('-timestamp')[:50]
        return [
            {
                'message':   m.message,
                'sender':    m.sender.username,
                'timestamp': m.timestamp.strftime('%I:%M %p'),
            }
            for m in reversed(list(messages))
        ]

    @database_sync_to_async
    def save_message(self, message):
        from .models import ChatMessage
        msg = ChatMessage.objects.create(
            booking_id=self.booking_id,
            sender=self.user,
            message=message,
        )
        return {
            'message':   msg.message,
            'sender':    msg.sender.username,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
        }

    @database_sync_to_async
    def notify_other_user(self, message):
        from mental.models import Booking
        from notifications.utils import notify
        try:
            booking = Booking.objects.select_related(
                'user', 'counselor__user'
            ).get(pk=self.booking_id)

            sender = self.user

            if sender == booking.user:
                other       = booking.counselor.user
                sender_name = sender.get_full_name() or sender.username
                notify(
                    user=other,
                    title='New Message from Client',
                    message=f'{sender_name}: {message[:80]}',
                    type='booking',
                    link=f'/chat/{booking.pk}/',
                )
            else:
                other       = booking.user
                sender_name = sender.get_full_name() or sender.username
                notify(
                    user=other,
                    title='New Message from Counselor',
                    message=f'{sender_name}: {message[:80]}',
                    type='booking',
                    link=f'/chat/{booking.pk}/',
                )
        except Exception:
            pass