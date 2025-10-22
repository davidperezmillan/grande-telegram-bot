from src.config.logger import Logger

class TelegramMessenger:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = Logger.setup_logger('TelegramMessenger')

    async def send_notification_to_me(self, text, parse_mode=None):
        self.logger.info(f"Sending notification to user {self.config.user_id}: {text}")
        message = await self.send_message(self.config.user_id, text, parse_mode)
        return message

    async def send_message(self, chat_id, text, parse_mode=None):
        self.logger.info(f"Sending message to chat {chat_id}: {text}")
        message = await self.client.send_message(chat_id, text, parse_mode=parse_mode)
        return message

    async def delete_message(self, message_or_id, chat_id=None):
        if hasattr(message_or_id, 'id'):
            await self.client.delete_messages(message_or_id.chat_id, message_or_id.id)
        else:
            if chat_id is None:
                raise ValueError("chat_id required when passing message id")
            await self.client.delete_messages(chat_id, message_or_id)