from src.utils.logger import get_logger

logger = get_logger()

class VideoForwarder:
    """
    Clase especializada para el reenvío de videos cortos al chat privado
    """
    
    def __init__(self, client, notification_manager):
        self.client = client
        self.notification_manager = notification_manager
        self.logger = logger
    
    async def forward_video_to_private_chat(self, message, file_info, reason):
        """
        Reenviar video al chat privado del dueño y eliminarlo del grupo
        
        Args:
            message: Mensaje de Telegram con el video
            file_info: Información del archivo de video
            reason: Razón por la cual no se descargó
            
        Returns:
            str: Resultado de la operación
        """
        try:
            # Obtener información del chat original
            try:
                chat = await self.client.get_entity(message.chat_id)
                chat_name = getattr(chat, 'title', getattr(chat, 'first_name', f'Chat {message.chat_id}'))
            except:
                chat_name = f'Chat {message.chat_id}'
            
            # Formatear información del archivo
            size_mb = file_info['file_size'] / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB"
            
            # Crear mensaje informativo
            caption = f"📹 **Video reenviado desde grupo**\n\n"
            caption += f"💬 **Origen**: {chat_name}\n"
            caption += f"📏 **Tamaño**: {size_str}\n"
            caption += f"🆔 **Mensaje ID**: {message.id}\n"
            caption += f"ℹ️ **Razón**: {reason}\n\n"
            caption += f"*Video no descargado automáticamente*"
            
            # Reenviar el video al chat privado del dueño
            forwarded_message = await self.client.forward_messages(
                entity=self.notification_manager.bot_owner_id,
                messages=message,
                from_peer=message.chat_id
            )
            
            # Enviar mensaje explicativo al chat privado
            await self.client.send_message(
                self.notification_manager.bot_owner_id,
                caption,
                parse_mode='markdown',
                reply_to=forwarded_message.id if forwarded_message else None,
                silent=True
            )
            
            # Intentar eliminar el mensaje del grupo original
            try:
                await self.client.delete_messages(
                    entity=message.chat_id,
                    message_ids=[message.id]
                )
                self.log_info(f"Video {message.id} reenviado a chat privado y eliminado del grupo {chat_name}")
                return f"video reenviado y eliminado - {reason}"
            except Exception as e:
                self.log_error(f"Error eliminando mensaje del grupo {chat_name} (ID: {message.chat_id}): {type(e).__name__}: {e}")
                self.log_info(f"Video {message.id} reenviado a chat privado (no se pudo eliminar del grupo)")
                return f"video reenviado - {reason} (no eliminado del grupo)"
                
        except Exception as e:
            self.log_error(f"Error reenviando video a chat privado: {e}")
            return f"error reenviando video - {reason}"
    
    def log_info(self, message):
        """Helper para logging"""
        self.logger.info(message)
    
    def log_error(self, message):
        """Helper para logging de errores"""
        self.logger.error(message)