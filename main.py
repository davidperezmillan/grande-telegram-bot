import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError

from src.database.models import init_database
from src.handlers.message_handler import MessageHandler
from src.handlers.command_handler import CommandHandler
from src.handlers.database_handler import DatabaseHandler
from src.utils.notification_manager import NotificationManager
from src.utils.logger import setup_logger

# Cargar variables de entorno
load_dotenv()

class GrandeBot:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.bot_token = os.getenv('BOT_TOKEN')
        
        # Manejo seguro del TARGET_GROUP_ID
        target_group_id_str = os.getenv('TARGET_GROUP_ID', '').strip()
        self.target_group_id = int(target_group_id_str) if target_group_id_str else None
        
        self.target_group_username = os.getenv('TARGET_GROUP_USERNAME', '').strip() or None
        
        # Crear cliente de Telethon
        self.client = TelegramClient('grande_bot_session', self.api_id, self.api_hash)
        
        # Inicializar handlers
        self.message_handler = MessageHandler(self.client)
        self.command_handler = CommandHandler(self.client)
        self.database_handler = DatabaseHandler(self.client)
        self.notification_manager = NotificationManager(self.client)
        
        # Configurar logger
        self.logger = setup_logger('grande_bot')
        
    async def start(self):
        """Iniciar el bot"""
        try:
            # Conectar cliente con manejo de FloodWaitError
            try:
                await self.client.start(bot_token=self.bot_token)
                self.logger.info("Bot iniciado correctamente")
            except FloodWaitError as e:
                self.logger.warning(f"FloodWaitError: Esperando {e.seconds} segundos antes de reconectar...")
                await asyncio.sleep(e.seconds)
                await self.client.start(bot_token=self.bot_token)
                self.logger.info("Bot iniciado correctamente después de esperar")
            
            # Inicializar base de datos
            await init_database()
            self.logger.info("Base de datos inicializada")
            
            # Obtener información del bot
            me = await self.client.get_me()
            self.logger.info(f"Bot conectado como: @{me.username}")
            self.logger.info(f"ID del bot: {me.id}")

            # Configuración de grupos objetivo
            if self.target_group_id or self.target_group_username:
                self.logger.info(f"Bot configurado para grupo específico: ID={self.target_group_id}, Username={self.target_group_username}")
            else:
                self.logger.info("🌍 Bot configurado para funcionar en TODOS los grupos donde esté agregado")
                self.target_group_id = None  # Asegurar que está en None
            
            # Registrar handlers de eventos
            self._register_handlers()
            
            # Registrar comandos del bot
            self.command_handler.register_commands()
            self.database_handler.register_commands()
            self.database_handler.register_confirmation_commands()
            self.logger.info("Comandos del bot registrados")
            
            # Mantener el bot corriendo
            self.logger.info("🚀 Grande Bot en funcionamiento...")
            await self.client.run_until_disconnected()
            
        except Exception as e:
            self.logger.error(f"Error al iniciar Grande Bot: {e}")
            raise
    
    def _register_handlers(self):
        """Registrar handlers de eventos"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            # Procesar TODOS los mensajes, sin restricciones de grupo
            try:
                # Log de información básica del mensaje
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', 'Chat privado')
                self.logger.info(f"📨 Mensaje recibido de: {chat_title} (ID: {event.chat_id})")
                
                # Procesar el mensaje
                await self.message_handler.handle_message(event)
                
            except Exception as e:
                self.logger.error(f"Error procesando mensaje: {e}")
        
        @self.client.on(events.MessageEdited)
        async def handle_edited_message(event):
            # Procesar TODOS los mensajes editados, sin restricciones
            try:
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', 'Chat privado')
                self.logger.info(f"✏️ Mensaje editado en: {chat_title} (ID: {event.chat_id})")
                
                await self.message_handler.handle_edited_message(event)
                
            except Exception as e:
                self.logger.error(f"Error procesando mensaje editado: {e}")

async def main():
    bot = GrandeBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())