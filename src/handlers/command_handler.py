from telethon import events
from src.config.logger import Logger
from src.utils.message_info import MessageInfo

class CommandHandler:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = Logger.setup_logger('CommandHandler')

    def register_commands(self):
        """Registra los comandos del bot."""
        
        @self.client.on(events.NewMessage(pattern=r'/info'))
        async def handle_info_command(event):
            """Maneja el comando /info."""
            try:
                message = event.message
                msg_info = MessageInfo(message)
                
                # Responder con la información
                info_text = msg_info.get_summary_text()
                await self.client.send_message(
                    message.chat_id,
                    info_text,
                    parse_mode='markdown',
                    reply_to=message.id
                )
                
                self.logger.info(f"Comando /info ejecutado en chat {message.chat_id}")
                
            except Exception as e:
                self.logger.error(f"Error procesando comando /info: {e}")
                await self.client.send_message(
                    message.chat_id,
                    "❌ Error al obtener información del chat.",
                    reply_to=message.id
                )