import os
from telethon import TelegramClient
from src.utils.logger import get_logger
from datetime import datetime
import asyncio

logger = get_logger()

class NotificationManager:
    """Gestor centralizado de notificaciones para el bot"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.bot_owner_id = int(os.getenv('USER_ID', '14824267'))
        # Diccionario para almacenar referencias a mensajes de progreso
        self.progress_messages = {}  # {message_id: sent_message_id}
        # Control de throttling para evitar rate limiting
        self.last_progress_update = {}  # {message_id: timestamp}
        self.progress_update_interval = 10  # segundos entre updates
        
    async def send_notification(self, chat_id: int, message: str, parse_mode: str = 'markdown', 
                              reply_to_message_id: int = None, silent: bool = False):
        """
        Enviar una notificación a un chat específico
        
        Args:
            chat_id: ID del chat donde enviar el mensaje
            message: Texto del mensaje
            parse_mode: Modo de parseo ('markdown', 'html', None)
            reply_to_message_id: ID del mensaje al que responder
            silent: Si enviar silenciosamente
        """
        try:
            await self.client.send_message(
                chat_id,
                message,
                parse_mode=parse_mode,
                reply_to=reply_to_message_id,
                silent=silent
            )
            logger.debug(f"Notificación enviada a chat {chat_id}: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación a chat {chat_id}: {e}")
            return False
    
    async def send_download_start_notification(self, chat_id: int, message_id: int, 
                                             file_info: dict, reply_to_message_id: int = None):
        """
        Enviar notificación de inicio de descarga al chat privado del dueño
        
        Args:
            chat_id: ID del chat original (donde se originó el archivo)
            message_id: ID del mensaje original
            file_info: Información del archivo (type, size, name, etc.)
            reply_to_message_id: ID del mensaje al que responder (no usado en chat privado)
        """
        try:
            file_type = file_info.get('type', 'archivo').title()
            file_size = file_info.get('size', 0)
            file_name = file_info.get('name', 'archivo')
            
            # Formatear tamaño
            if file_size > 0:
                size_mb = file_size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB"
            else:
                size_str = "tamaño desconocido"

            # Obtener nombre del chat/grupo original
            try:
                chat = await self.client.get_entity(chat_id)
                chat_name = getattr(chat, 'title', getattr(chat, 'first_name', f'Chat {chat_id}'))
            except:
                chat_name = f'Chat {chat_id}'

            message = f"📥 **DESCARGA INICIADA**\n\n"
            message += f"🎬 **Tipo**: {file_type}\n"
            message += f"📏 **Tamaño**: {size_str}\n"
            message += f"📁 **Archivo**: `{file_name}`\n"
            message += f"🆔 **Mensaje ID**: `{message_id}`\n"
            message += f"💬 **Origen**: {chat_name}\n\n"
            message += f"⏳ Descargando... por favor espera."
            
            # Enviar al chat privado del dueño
            sent_message = await self.client.send_message(
                self.bot_owner_id,
                message,
                parse_mode='markdown',
                silent=True
            )
            
            # Guardar referencia al mensaje para editarlo durante el progreso
            # Usar una clave única que incluya el chat original y mensaje
            progress_key = f"{chat_id}_{message_id}"
            self.progress_messages[progress_key] = sent_message.id
            
            logger.info(f"Notificación de descarga iniciada enviada al chat privado para mensaje {message_id} de {chat_name}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de inicio de descarga: {e}")
    
    async def send_download_complete_notification(self, chat_id: int, message_id: int, 
                                                download_result: dict, reply_to_message_id: int = None):
        """
        Enviar notificación de descarga completada al chat privado del dueño
        
        Args:
            chat_id: ID del chat original (donde se originó el archivo)
            message_id: ID del mensaje original
            download_result: Resultado de la descarga (success, file_path, error, duration, etc.)
            reply_to_message_id: ID del mensaje al que responder (no usado en chat privado)
        """
        try:
            success = download_result.get('success', False)
            file_path = download_result.get('file_path', '')
            error = download_result.get('error', '')
            duration = download_result.get('duration', 0)
            file_size = download_result.get('file_size', 0)
            
            # Verificar si existe un mensaje de progreso para editar
            progress_key = f"{chat_id}_{message_id}"
            
            # Obtener nombre del chat/grupo original
            try:
                chat = await self.client.get_entity(chat_id)
                chat_name = getattr(chat, 'title', getattr(chat, 'first_name', f'Chat {chat_id}'))
            except:
                chat_name = f'Chat {chat_id}'
            
            if success:
                # Descarga exitosa
                message = f"✅ **DESCARGA COMPLETADA**\n\n"
                message += f"🆔 **Mensaje ID**: `{message_id}`\n"
                message += f"💬 **Origen**: {chat_name}\n"
                
                if file_path:
                    file_name = file_path.split('/')[-1]
                    message += f"📁 **Archivo**: `{file_name}`\n"
                
                if file_size > 0:
                    size_mb = file_size / (1024 * 1024)
                    message += f"📏 **Tamaño**: {size_mb:.1f} MB\n"
                
                if duration > 0:
                    if duration < 60:
                        time_str = f"{duration:.1f} segundos"
                    else:
                        minutes = duration / 60
                        time_str = f"{minutes:.1f} minutos"
                    message += f"⏱️ **Tiempo**: {time_str}\n"
                
                message += f"\n🎉 **Descarga guardada exitosamente**"
                
            else:
                # Error en descarga
                message = f"❌ **ERROR EN DESCARGA**\n\n"
                message += f"🆔 **Mensaje ID**: `{message_id}`\n"
                message += f"� **Origen**: {chat_name}\n"
                message += f"�🚫 **Error**: `{error}`\n\n"
                message += f"💡 **Nota**: El archivo podría ser demasiado grande o estar corrupto."
            
            # Intentar editar el mensaje existente en el chat privado primero
            if progress_key in self.progress_messages:
                try:
                    await self.client.edit_message(
                        self.bot_owner_id,
                        self.progress_messages[progress_key],
                        message,
                        parse_mode='markdown'
                    )
                    logger.info(f"Mensaje de descarga actualizado a completado en chat privado para mensaje {message_id}")
                except Exception as e:
                    logger.error(f"Error editando mensaje de descarga completada: {e}")
                    # Si no se puede editar, enviar nuevo mensaje al chat privado
                    await self.client.send_message(
                        self.bot_owner_id,
                        message,
                        parse_mode='markdown',
                        silent=True
                    )
            else:
                # Si no hay mensaje previo, enviar nuevo mensaje al chat privado
                await self.client.send_message(
                    self.bot_owner_id,
                    message,
                    parse_mode='markdown',
                    silent=True
                )
            
            status = "completada" if success else "fallida"
            logger.info(f"Notificación de descarga {status} enviada al chat privado para mensaje {message_id}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de descarga completada: {e}")
            
            status = "completada" if success else "fallida"
            logger.info(f"Notificación de descarga {status} enviada para mensaje {message_id}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de descarga completada: {e}")
    
    async def send_progress_notification(self, chat_id: int, message_id: int, 
                                       current_bytes: int, total_bytes: int, percentage: float,
                                       file_name: str = None, reply_to_message_id: int = None):
        """
        Actualizar notificación de progreso de descarga en el chat privado del dueño
        
        Args:
            chat_id: ID del chat original (donde se originó el archivo)
            message_id: ID del mensaje original
            current_bytes: Bytes descargados hasta ahora
            total_bytes: Total de bytes del archivo
            percentage: Porcentaje completado
            file_name: Nombre del archivo
            reply_to_message_id: ID del mensaje al que responder (no usado en chat privado)
        """
        try:
            import time
            
            # Control de throttling - solo actualizar cada X segundos
            current_time = time.time()
            progress_key = f"{chat_id}_{message_id}"
            
            if progress_key in self.last_progress_update:
                time_since_last = current_time - self.last_progress_update[progress_key]
                if time_since_last < self.progress_update_interval:
                    return  # Salir si no ha pasado suficiente tiempo
            
            # Solo actualizar en ciertos puntos (25%, 50%, 75%) para evitar spam
            milestone_percentages = [25, 50, 75]
            closest_milestone = min(milestone_percentages, key=lambda x: abs(x - percentage))
            
            # Solo actualizar si estamos muy cerca de un milestone (±3%)
            if abs(percentage - closest_milestone) > 3:
                return
            
            # Verificar si existe un mensaje de progreso para editar
            if progress_key not in self.progress_messages:
                logger.warning(f"No se encontró mensaje de progreso para editar: {message_id}")
                return
            
            # Formatear tamaños
            current_mb = current_bytes / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024)
            
            # Crear barra de progreso visual
            progress_bar_length = 10
            filled_length = int(progress_bar_length * percentage / 100)
            bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
            
            # Obtener nombre del chat/grupo original
            try:
                chat = await self.client.get_entity(chat_id)
                chat_name = getattr(chat, 'title', getattr(chat, 'first_name', f'Chat {chat_id}'))
            except:
                chat_name = f'Chat {chat_id}'
            
            message_text = f"📥 **DESCARGA EN PROGRESO**\n\n"
            message_text += f"📊 **Progreso**: {percentage:.0f}%\n"
            message_text += f"▓{bar}▓ {percentage:.0f}%\n\n"
            message_text += f"💾 **Descargado**: {current_mb:.1f} MB / {total_mb:.1f} MB\n"
            
            if file_name:
                message_text += f"📁 **Archivo**: `{file_name}`\n"
            
            message_text += f"🆔 **Mensaje ID**: `{message_id}`\n"
            message_text += f"💬 **Origen**: {chat_name}\n\n"
            message_text += f"⏳ Descargando... por favor espera."
            
            # Editar el mensaje existente en el chat privado del dueño
            try:
                await self.client.edit_message(
                    self.bot_owner_id,
                    self.progress_messages[progress_key],
                    message_text,
                    parse_mode='markdown'
                )
                # Actualizar timestamp del último update
                self.last_progress_update[progress_key] = current_time
                logger.info(f"Mensaje de progreso actualizado a {percentage:.0f}% en chat privado para mensaje {message_id}")
            except Exception as e:
                logger.error(f"Error editando mensaje de progreso: {e}")
                # Si no se puede editar, eliminar la referencia
                if progress_key in self.progress_messages:
                    del self.progress_messages[progress_key]
                if progress_key in self.last_progress_update:
                    del self.last_progress_update[progress_key]
            
        except Exception as e:
            logger.error(f"Error enviando notificación de progreso: {e}")
    
    async def _send_new_progress_message(self, chat_id: int, message_text: str, 
                                       reply_to_message_id: int, message_id: int, progress_key: str):
        """Método auxiliar para enviar un nuevo mensaje de progreso"""
        try:
            sent_message = await self.client.send_message(
                chat_id,
                message_text,
                parse_mode='markdown',
                reply_to=reply_to_message_id,
                silent=True
            )
            # Guardar referencia al mensaje enviado
            self.progress_messages[progress_key] = sent_message.id
            logger.info(f"Nuevo mensaje de progreso enviado para mensaje {message_id}")
        except Exception as e:
            logger.error(f"Error enviando nuevo mensaje de progreso: {e}")
    
    async def clear_progress_message(self, chat_id: int, message_id: int):
        """Limpiar referencia del mensaje de progreso cuando la descarga termine"""
        progress_key = f"{chat_id}_{message_id}"
        if progress_key in self.progress_messages:
            del self.progress_messages[progress_key]
        if progress_key in self.last_progress_update:
            del self.last_progress_update[progress_key]
        logger.debug(f"Referencia de progreso limpiada para mensaje {message_id}")
    
    async def create_progress_callback(self, chat_id: int, message_id: int, file_name: str = None):
        """
        Crear callback de progreso para usar con file_handler
        
        Returns:
            función callback para usar en download_file
        """
        async def progress_callback(current_bytes: int, total_bytes: int, percentage: float):
            await self.send_progress_notification(
                chat_id=chat_id,
                message_id=message_id,
                current_bytes=current_bytes,
                total_bytes=total_bytes,
                percentage=percentage,
                file_name=file_name,
                reply_to_message_id=message_id
            )
        
        return progress_callback

    async def send_processing_notification(self, chat_id: int, message_id: int, 
                                         process_type: str, status: str = "started", 
                                         details: dict = None, reply_to_message_id: int = None):
        """
        Enviar notificación de procesamiento general
        
        Args:
            chat_id: ID del chat
            message_id: ID del mensaje
            process_type: Tipo de procesamiento (video, image, animation, etc.)
            status: Estado (started, completed, error)
            details: Detalles adicionales
            reply_to_message_id: ID del mensaje al que responder
        """
        try:
            details = details or {}
            
            if status == "started":
                icon = "🔄"
                title = "PROCESAMIENTO INICIADO"
                action = "Procesando"
            elif status == "completed":
                icon = "✅"
                title = "PROCESAMIENTO COMPLETADO"
                action = "Completado"
            else:  # error
                icon = "❌"
                title = "ERROR EN PROCESAMIENTO"
                action = "Error"
            
            message = f"{icon} **{title}**\n\n"
            message += f"📝 **Tipo**: {process_type.title()}\n"
            message += f"🆔 **Mensaje ID**: `{message_id}`\n"
            
            if details:
                for key, value in details.items():
                    if key not in ['message_id', 'type']:
                        message += f"📋 **{key.title()}**: {value}\n"
            
            message += f"\n{action} procesamiento de {process_type}."
            
            await self.send_notification(
                chat_id=chat_id,
                message=message,
                reply_to_message_id=reply_to_message_id,
                silent=True
            )
            
            logger.info(f"Notificación de procesamiento {status} enviada para {process_type} {message_id}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de procesamiento: {e}")
    
    async def send_bot_status_notification(self, chat_id: int, status_type: str, 
                                         details: dict = None):
        """
        Enviar notificaciones de estado del bot
        
        Args:
            chat_id: ID del chat
            status_type: Tipo de estado (startup, shutdown, error, etc.)
            details: Detalles adicionales
        """
        try:
            details = details or {}
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            if status_type == "startup":
                message = f"🚀 **BOT INICIADO**\n\n"
                message += f"⏰ **Hora**: {timestamp}\n"
                message += f"🆔 **Bot ID**: {details.get('bot_id', 'N/A')}\n"
                message += f"📊 **Estado**: Funcionando correctamente"
                
            elif status_type == "shutdown":
                message = f"🛑 **BOT DETENIDO**\n\n"
                message += f"⏰ **Hora**: {timestamp}\n"
                message += f"📊 **Estado**: Bot desconectado"
                
            elif status_type == "error":
                message = f"⚠️ **ERROR DEL BOT**\n\n"
                message += f"⏰ **Hora**: {timestamp}\n"
                message += f"🚫 **Error**: {details.get('error', 'Error desconocido')}"
                
            else:
                message = f"ℹ️ **ESTADO DEL BOT**\n\n"
                message += f"⏰ **Hora**: {timestamp}\n"
                message += f"📊 **Tipo**: {status_type}"
            
            # Solo enviar a chats específicos de administración
            if chat_id:
                await self.send_notification(
                    chat_id=chat_id,
                    message=message,
                    silent=True
                )
                
                logger.info(f"Notificación de estado del bot enviada: {status_type}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de estado: {e}")
    
    async def send_database_notification(self, chat_id: int, operation: str, 
                                       result: dict = None, reply_to_message_id: int = None):
        """
        Enviar notificaciones relacionadas con operaciones de base de datos
        
        Args:
            chat_id: ID del chat
            operation: Tipo de operación (clean, backup, stats, etc.)
            result: Resultado de la operación
            reply_to_message_id: ID del mensaje al que responder
        """
        try:
            result = result or {}
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if operation == "clean":
                if result.get('success', False):
                    message = f"🧹 **BASE DE DATOS LIMPIADA**\n\n"
                    message += f"⏰ **Hora**: {timestamp}\n"
                    details = result.get('details', {})
                    total = sum(details.values()) if details else 0
                    message += f"🗑️ **Registros eliminados**: {total:,}\n"
                    
                    if details:
                        message += f"\n📊 **Detalle por tabla**:\n"
                        for table, count in details.items():
                            message += f"• {table}: {count:,}\n"
                else:
                    message = f"❌ **ERROR LIMPIANDO BD**\n\n"
                    message += f"⏰ **Hora**: {timestamp}\n"
                    message += f"🚫 **Error**: {result.get('error', 'Error desconocido')}"
            
            else:
                message = f"📊 **OPERACIÓN BD: {operation.upper()}**\n\n"
                message += f"⏰ **Hora**: {timestamp}\n"
                message += f"📋 **Resultado**: {result}"
            
            await self.send_notification(
                chat_id=chat_id,
                message=message,
                reply_to_message_id=reply_to_message_id,
                silent=True
            )
            
            logger.info(f"Notificación de BD enviada: {operation}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de BD: {e}")