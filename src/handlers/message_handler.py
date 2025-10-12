from datetime import datetime
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage
from src.database.manager import DatabaseManager
from src.utils.file_handler import FileHandler
from src.utils.text_processor import TextProcessor
from src.utils.logger import get_logger
from src.processors.processor_factory import ProcessorFactory

logger = get_logger()

class MessageHandler:
    def __init__(self, client):
        self.client = client
        self.db = DatabaseManager()
        self.file_handler = FileHandler()
        self.text_processor = TextProcessor()
    
    async def handle_message(self, event):
        """Manejar nuevo mensaje"""
        message = event.message
        
        # Ignorar comandos del bot (que empiecen con /)
        if message.text and message.text.startswith('/'):
            return
        
        # Verificar si el mensaje ya fue procesado
        if await self.db.is_message_processed(message.id):
            logger.debug(f"Mensaje {message.id} ya procesado, omitiendo")
            return
        
        logger.info(f"Procesando nuevo mensaje ID: {message.id}")
        
        # Determinar tipo de mensaje
        message_type = self._determine_message_type(message)
        
        # Preparar datos básicos del mensaje
        message_data = {
            'message_id': message.id,
            'chat_id': message.chat_id,
            'user_id': message.from_id.user_id if message.from_id else None,
            'username': None,
            'message_type': message_type,
            'content': None,
            'file_path': None,
            'file_size': None,
            'action_taken': None
        }
        
        # Obtener información del usuario
        if message.from_id:
            try:
                user = await self.client.get_entity(message.from_id.user_id)
                message_data['username'] = user.username
            except Exception as e:
                logger.warning(f"No se pudo obtener información del usuario: {e}")
        
        # Procesar según el tipo de mensaje
        action_taken = await self._process_by_type(message, message_type, message_data)
        message_data['action_taken'] = action_taken
        
        # Guardar en base de datos
        try:
            await self.db.save_processed_message(message_data)
            logger.info(f"Mensaje {message.id} guardado en BD. Acción: {action_taken}")
        except Exception as e:
            logger.error(f"Error guardando mensaje en BD: {e}")
    
    async def handle_edited_message(self, event):
        """Manejar mensaje editado"""
        message = event.message
        logger.info(f"Mensaje editado ID: {message.id}")
        
        # Verificar si tenemos el mensaje original
        original = await self.db.get_processed_message(message.id)
        if original:
            logger.info(f"Mensaje {message.id} fue editado. Tipo original: {original.message_type}")
            # Aquí puedes decidir si reprocesar o solo registrar el cambio
        else:
            logger.info(f"Mensaje editado {message.id} no estaba en BD, procesando como nuevo")
            await self.handle_message(event)
    
    def _determine_message_type(self, message):
        """Determinar el tipo de mensaje"""
        if message.text and not message.media:
            return 'text'
        
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                return 'image'
            elif isinstance(message.media, MessageMediaDocument):
                document = message.media.document
                if document.mime_type:
                    if document.mime_type.startswith('video/'):
                        return 'video'
                    elif 'gif' in document.mime_type:
                        return 'animation'
                    elif document.mime_type.startswith('image/'):
                        return 'image'
                    elif any(hasattr(attr, 'stickerset') for attr in document.attributes):
                        return 'sticker'
            elif isinstance(message.media, MessageMediaWebPage):
                return 'text'  # Mensaje con vista previa de enlace
        
        return 'unknown'
    
    async def _process_by_type(self, message, message_type, message_data):
        """Procesar mensaje según su tipo usando procesadores especializados"""
        
        # Crear procesador específico
        processor = ProcessorFactory.create_processor(
            message_type, 
            self.client, 
            self.file_handler, 
            self.text_processor
        )
        
        if processor:
            return await processor.process(message, message_data)
        else:
            return "tipo desconocido - sin acción"
