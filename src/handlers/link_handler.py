import os
import re
from telethon import events
from src.config.logger import Logger
from src.telegram.telegram_messenger import TelegramMessenger
from src.utils.file_manager import FileManager
from src.database.manager import DatabaseManager
from src.utils.message_info import MessageInfo
import yt_dlp

class LinkHandler:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = Logger.setup_logger('LinkHandler')
        self.messenger = TelegramMessenger(client, config)
        self.file_manager = FileManager()
        self.db_manager = DatabaseManager()

    def register_handlers(self):
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_incoming_message(event):
            """Handle incoming messages with links."""
            try:
                message = event.message
                if message.text:
                    all_links = self._extract_all_links(message.text)
                    if all_links:
                        for link in all_links:
                            await self._process_link(message, link)
                    else:
                        self.logger.info(f"No links found in the message. {message.text} ")
            except Exception as e:
                self.logger.error(f"Error handling link message: {e}")


    def _extract_all_links(self, text):
        """Extract all URLs from text."""
        pattern = r'https?://[^\s]+'
        return re.findall(pattern, text)

    async def _process_link(self, message, link):
        """Download video from link using yt-dlp."""
        try:
            self.logger.info(f"Processing link: {link}")
            proccess_msg = await self.messenger.send_message(message.chat_id,
                f"Descargando video de: {link}", parse_mode='md')

            try:
                # Obtener información del usuario que solicita
                msg_info = MessageInfo(message)
                sender = msg_info.get_sender_info()
                user_info = f"👤 Usuario: {sender['first_name'] or 'Unknown'}"
                if sender['username']:
                    user_info += f" (@{sender['username']})"
                user_info += f" - ID: `{sender['id']}`"
                user_info += f"\n📍 Chat: `{msg_info.get_chat_id()}` ({msg_info.get_chat_type()})"
                
                # Notificar al usuario
                notification = f"🎥 **Nueva descarga solicitada**\n\n{user_info}\n\n🔗 Link: {link}"
                await self.messenger.send_notification_to_me(notification, parse_mode='md')
            except Exception as e:
                self.logger.error(f"Error notifying user: {e}")

            # Configure yt-dlp
            ydl_opts = {
                'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
                'format': 'best',  # Best available format
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                'update_self': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)

            self.logger.info(f"Downloaded: {filename}")
            
            ## editar proccess_msg
            await self.messenger.delete_message(message.id, chat_id=message.chat_id)
            await self.messenger.delete_message(proccess_msg.id, chat_id=proccess_msg.chat_id)
            proccess_msg = await self.messenger.send_message(message.chat_id,
                f"Video descargado: {filename}", parse_mode='md')

            ## enviar video al chat de origen
            await self.client.send_file(
                message.chat_id,
                filename,
                parse_mode='markdown',
                supports_streaming=True,
                spoiler=True
            )
            # borrar proccess_msg
            await self.messenger.delete_message(proccess_msg)

            ## borrar archivo descargado
            os.remove(filename)
            self.logger.info(f"Archivo {filename} eliminado después de enviar.")

            # Optionally, process like a video
            # But for now, just download

        except Exception as e:
            error_msg = f"Error descargando video de: {str(e)}"
            self.logger.error(f"Error downloading video: {e}")
            await self.messenger.send_notification_to_me(error_msg, parse_mode='md')


    def _extract_xvideos_links(self, text):

        """Extract xvideos.com links from text."""
        pattern = r'https?://(?:www\.)?xvideos\.com/video[^/\s]+/[^/\s]*'
        return re.findall(pattern, text)