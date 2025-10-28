import os
import re
from telethon import events, Button
from src.config.logger import setup_logger
from src.telegram.telegram_messenger import TelegramMessenger
from src.utils.file_manager import FileManager
from src.database.manager import DatabaseManager
from src.utils.message_info import MessageInfo
import yt_dlp

class LinkHandler:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.logger = setup_logger('LinkHandler')
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

        @self.client.on(events.CallbackQuery)
        async def handle_callback(event):
            """Handle callback queries from inline buttons."""
            try:
                data = event.data.decode('utf-8')
                if data.startswith('persist:'):
                    filename = data.split(':', 1)[1]
                    filepath = os.path.join('downloads', filename)
                    if self.file_manager.persist_file(filepath):
                        await event.answer("✅ Archivo persistido correctamente")
                        await event.edit("", buttons=None)
                    else:
                        await event.answer("❌ Error al persistir archivo")
                elif data.startswith('delete:'):
                    filename = data.split(':', 1)[1]
                    filepath = os.path.join('downloads', filename)
                    if self.file_manager.delete_file(filepath):
                        await event.answer("🗑️ Archivo eliminado correctamente")
                        await event.edit("", buttons=None)
                    else:
                        await event.answer("❌ Error al eliminar archivo")
                else:
                    await event.answer("Acción desconocida")
            except Exception as e:
                self.logger.error(f"Error handling callback: {e}")
                await event.answer("❌ Error procesando acción")


    def _extract_all_links(self, text):
        """Extract all URLs from text."""
        pattern = r'https?://[^\s]+'
        return re.findall(pattern, text)

    async def _process_link(self, message, link):
        """Download video from link using yt-dlp."""
        # Initialize variables to avoid UnboundLocalError
        media_id = None
        access_hash = None
        
        try:
            self.logger.info(f"Processing link: {link}")
            proccess_msg = await self.messenger.send_message(message.chat_id,
                f"Descargando video de: {link}", parse_mode='md')

            try:
                if (self.config.user_id != message.chat_id):
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

            try:
                # recuperar info del mensaje, media_id	access_hash
                msg_info = MessageInfo(message)
                media_id = msg_info.get_media_id()
                access_hash = msg_info.get_access_hash()
            except Exception as e:
                self.logger.error(f"Error retrieving media info: {e}")



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
            
            # Verificar tamaño del archivo (límite de Telegram: 50MB para bots)
            file_size = os.path.getsize(filename)
            max_size = 50 * 1024 * 1024  # 50MB en bytes
            
            if file_size > max_size:
                error_msg = f"❌ Archivo demasiado grande ({file_size / (1024*1024):.1f}MB). Límite de Telegram: 50MB"
                self.logger.warning(f"File too large: {filename} ({file_size} bytes)")
                
                # Eliminar archivo y notificar
                os.remove(filename)
                await self.messenger.edit_message(proccess_msg, error_msg)
                await self.messenger.send_notification_to_me(f"Archivo rechazado por tamaño: {link}", parse_mode='md')
                return
            
            # Actualizar mensaje de progreso
            await self.messenger.edit_message(proccess_msg, "✅ Video descargado, enviando...")
            
    

        except Exception as e:
            error_msg = f"Error descargando video de: {str(e)}"
            self.logger.error(f"Error downloading video: {e}")
            
            # Intentar actualizar mensaje de progreso si existe
            try:
                if 'proccess_msg' in locals():
                    await self.messenger.edit_message(proccess_msg, f"❌ {error_msg}")
            except:
                pass  
            await self.messenger.send_notification_to_me(error_msg, parse_mode='md')

        try:
            # Crear botones inline
            buttons = [
                [Button.inline("💾 Persistir", f"persist:{os.path.basename(filename)}"),
                Button.inline("🗑️ Borrar", f"delete:{os.path.basename(filename)}")]
            ]

            # Enviar video al chat de origen con botones
            await self.client.send_file(
                message.chat_id,
                filename,
                caption=f"Video descargado de:\n{link}\n\nElige qué hacer con el archivo:",
                parse_mode='markdown',
                supports_streaming=True,
                spoiler=True,
                buttons=buttons
            )

            # Eliminar mensaje de progreso
            await self.messenger.delete_message(proccess_msg)

        except Exception as e:

            ## creamos el link
            video_link = f"https://portal.davidperezmillan.com/grande/download/{os.path.basename(filename)}"

            # copiar el archivo a app/www
            self.file_manager.copy_file_to_www(filename)


            self.logger.error(f"Error sending video: {e}")
            error_details = (
                f"ALTER-EGO\n\n"
                f"❌ **Error enviando video**\n\n"
                f"**Error:** {str(e)}\n\n"
                f"🔍 **Buscando solución alternativa...**\n\n"
                f"📋 **Detalles técnicos:**\n"
                f"• **Link:** {video_link}\n"
                f"• Media ID: `{media_id or 'N/A'}`\n"
                f"• Access Hash: `{access_hash or 'N/A'}`"
            )
            await self.messenger.send_notification_to_me(error_details, parse_mode='md')

    def _extract_xvideos_links(self, text):

        """Extract xvideos.com links from text."""
        pattern = r'https?://(?:www\.)?xvideos\.com/video[^/\s]+/[^/\s]*'
        return re.findall(pattern, text)