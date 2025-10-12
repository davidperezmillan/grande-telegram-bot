import os
import asyncio
from src.utils.logger import get_logger

logger = get_logger()

class NotificationManager:
    """
    Gestor de notificaciones para el bot
    Maneja el envío de notificaciones al chat privado del dueño del bot
    """
    
    def __init__(self, client):
        self.client = client
        self.logger = logger
        
        # ID del dueño del bot
        self.bot_owner_id = int(os.getenv('USER_ID', '14824267'))
        
        # Diccionario para almacenar referencias de mensajes de progreso
        self.progress_messages = {}
        
        self.logger.info(f"NotificationManager inicializado - Owner ID: {self.bot_owner_id}")
    
    async def send_notification(self, chat_id, message, parse_mode=None, reply_to=None, silent=True):
        """Enviar notificación al chat privado del dueño"""
        try:
            sent_message = await self.client.send_message(
                self.bot_owner_id,
                message,
                parse_mode=parse_mode,
                reply_to=reply_to,
                silent=silent
            )
            return sent_message
        except Exception as e:
            self.logger.error(f"Error enviando notificación: {e}")
            return None
    
    async def send_download_start_notification(self, chat_id, message_id, file_info, reply_to_message_id=None):
        """Enviar notificación de inicio de descarga"""
        try:
            file_size_mb = file_info.get('size', 0) / (1024 * 1024)
            file_name = file_info.get('name', 'archivo_desconocido')
            file_type = file_info.get('type', 'archivo')
            
            message = f"📥 **Descarga iniciada**\n\n"
            message += f"📁 **Archivo**: {file_name}\n"
            message += f"📋 **Tipo**: {file_type}\n"
            message += f"📏 **Tamaño**: {file_size_mb:.1f} MB\n"
            message += f"🆔 **Mensaje ID**: {message_id}\n"
            message += f"💬 **Chat ID**: {chat_id}"
            
            await self.send_notification(
                chat_id=self.bot_owner_id,
                message=message,
                parse_mode='markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error enviando notificación de inicio de descarga: {e}")
    
    async def send_download_complete_notification(self, chat_id, message_id, download_result, reply_to_message_id=None):
        """Enviar notificación de descarga completada"""
        try:
            success = download_result.get('success', False)
            duration = download_result.get('duration', 0)
            file_size = download_result.get('file_size', 0)
            
            status_emoji = "✅" if success else "❌"
            status_text = "Completada" if success else "Fallida"
            
            message = f"{status_emoji} **Descarga {status_text}**\n\n"
            message += f"🆔 **Mensaje ID**: {message_id}\n"
            message += f"⏱️ **Duración**: {duration:.1f} segundos\n"
            message += f"📏 **Tamaño**: {file_size / (1024*1024):.1f} MB\n"
            
            if not success:
                error_msg = download_result.get('error', 'Error desconocido')
                message += f"❌ **Error**: {error_msg}"
            
            await self.send_notification(
                chat_id=self.bot_owner_id,
                message=message,
                parse_mode='markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error enviando notificación de descarga completada: {e}")
    
    async def create_progress_callback(self, chat_id, message_id, file_name):
        """Crear callback de progreso para descarga de archivos"""
        # Enviar mensaje inicial de progreso
        progress_message = await self.send_notification(
            chat_id=self.bot_owner_id,
            message=f"📊 **Descargando**: {file_name}\n🔄 **Progreso**: 0%",
            parse_mode='markdown'
        )
        
        if progress_message:
            # Almacenar referencia del mensaje de progreso
            progress_key = f"{chat_id}_{message_id}"
            self.progress_messages[progress_key] = progress_message.id
        
        async def progress_callback(current, total, percentage):
            """Callback interno para actualizar el progreso"""
            try:
                if progress_message:
                    # Calcular información de progreso
                    current_mb = current / (1024 * 1024)
                    total_mb = total / (1024 * 1024)
                    
                    # Actualizar solo cada 5% para evitar spam
                    if int(percentage) % 5 == 0:
                        new_text = f"📊 **Descargando**: {file_name}\n"
                        new_text += f"🔄 **Progreso**: {percentage:.1f}%\n"
                        new_text += f"📥 **Descargado**: {current_mb:.1f} MB / {total_mb:.1f} MB"
                        
                        try:
                            await self.client.edit_message(
                                self.bot_owner_id,
                                progress_message.id,
                                new_text,
                                parse_mode='markdown'
                            )
                        except Exception as e:
                            self.logger.warning(f"No se encontró mensaje de progreso para editar: {progress_message.id}")
                            
            except Exception as e:
                self.logger.warning(f"Error actualizando progreso: {e}")
        
        return progress_callback
    
    async def clear_progress_message(self, chat_id, message_id):
        """Limpiar mensaje de progreso"""
        try:
            progress_key = f"{chat_id}_{message_id}"
            if progress_key in self.progress_messages:
                progress_msg_id = self.progress_messages[progress_key]
                
                try:
                    # Intentar actualizar el mensaje final
                    await self.client.edit_message(
                        self.bot_owner_id,
                        progress_msg_id,
                        "✅ **Descarga completada**",
                        parse_mode='markdown'
                    )
                except Exception as e:
                    self.logger.warning(f"No se pudo actualizar mensaje de progreso final: {e}")
                
                # Eliminar de la referencia
                del self.progress_messages[progress_key]
                
        except Exception as e:
            self.logger.warning(f"Error limpiando mensaje de progreso: {e}")
