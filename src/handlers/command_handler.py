from telethon import events
from telethon.tl.types import User, Chat, Channel
from src.utils.logger import get_logger
from src.utils.id_helper import IdHelper

logger = get_logger()

class CommandHandler:
    def __init__(self, client):
        self.client = client
    
    def register_commands(self):
        """Registrar todos los comandos del bot"""
        
        @self.client.on(events.NewMessage(pattern=r'/id'))
        async def cmd_id(event):
            """Comando /id - Muestra información completa de IDs"""
            try:
                await self._handle_id_command(event)
            except Exception as e:
                logger.error(f"Error en comando /id: {e}")
                await event.respond("❌ Error obteniendo información de IDs")
        
        @self.client.on(events.NewMessage(pattern=r'/start'))
        async def cmd_start(event):
            """Comando /start - Mensaje de bienvenida"""
            try:
                await self._handle_start_command(event)
            except Exception as e:
                logger.error(f"Error en comando /start: {e}")
        
        @self.client.on(events.NewMessage(pattern=r'/help'))
        async def cmd_help(event):
            """Comando /help - Ayuda del bot"""
            try:
                await self._handle_help_command(event)
            except Exception as e:
                logger.error(f"Error en comando /help: {e}")
        
        @self.client.on(events.NewMessage(pattern=r'/status'))
        async def cmd_status(event):
            """Comando /status - Estado del bot y configuración"""
            try:
                await self._handle_status_command(event)
            except Exception as e:
                logger.error(f"Error en comando /status: {e}")
                await event.respond("❌ Error obteniendo información de estado")
    
    async def _handle_id_command(self, event):
        """Manejar comando /id"""
        message = event.message
        chat = await event.get_chat()
        sender = await event.get_sender()
        
        # Información básica usando IdHelper
        chat_info = IdHelper.get_chat_info(chat)
        sender_info = IdHelper.get_chat_info(sender) if sender else None
        
        # Construir respuesta
        response = "🆔 **INFORMACIÓN DE IDs**\n"
        response += "=" * 30 + "\n\n"
        
        # ID del mensaje
        response += f"� **Mensaje ID**: `{message.id}`\n"
        response += f"� **Fecha**: `{message.date}`\n\n"
        
        # Información del chat
        response += "� **INFORMACIÓN DEL CHAT**\n"
        response += IdHelper.format_chat_info(chat_info) + "\n\n"
        
        # Información del remitente
        if sender_info:
            response += "👤 **INFORMACIÓN DEL REMITENTE**\n"
            response += IdHelper.format_chat_info(sender_info) + "\n\n"
        
        # Si es un reenvío, mostrar información original
        if message.forward:
            response += "📤 **MENSAJE REENVIADO**\n"
            if message.forward.chat:
                forward_chat_info = IdHelper.get_chat_info(message.forward.chat)
                response += IdHelper.format_chat_info(forward_chat_info) + "\n"
            if message.forward.sender:
                forward_sender_info = IdHelper.get_chat_info(message.forward.sender)
                response += "**Remitente original:**\n"
                response += IdHelper.format_chat_info(forward_sender_info) + "\n"
            response += "\n"
        
        # Si es una respuesta, mostrar información del mensaje original
        if message.reply_to_msg_id:
            response += "↩️ **RESPUESTA A MENSAJE**\n"
            response += f"📨 **Mensaje original ID**: `{message.reply_to_msg_id}`\n"
            
            try:
                original_msg = await event.get_reply_message()
                if original_msg and original_msg.sender:
                    original_sender_info = IdHelper.get_chat_info(original_msg.sender)
                    response += "**Autor original:**\n"
                    response += IdHelper.format_chat_info(original_sender_info) + "\n"
            except Exception as e:
                logger.warning(f"No se pudo obtener mensaje original: {e}")
            response += "\n"
        
        # Formato para copiar fácilmente
        response += "📋 **PARA COPIAR EN .ENV**\n"
        response += "```\n"
        if IdHelper.is_group_or_channel(chat_info):
            response += f"TARGET_GROUP_ID={chat_info['id']}\n"
            if chat_info['username']:
                response += f"TARGET_GROUP_USERNAME={chat_info['username']}\n"
            else:
                response += f"# TARGET_GROUP_USERNAME= (no disponible)\n"
        else:
            response += f"# Este es un chat privado, no un grupo/canal\n"
            response += f"USER_ID={chat_info['id']}\n"
            if chat_info['username']:
                response += f"USERNAME={chat_info['username']}\n"
            else:
                response += f"# USERNAME= (no disponible)\n"
        
        response += "\n# Información adicional:\n"
        response += IdHelper.format_id_for_config(chat_info).replace('TARGET_GROUP_', '# ')
        response += "\n```"
        
        await event.respond(response, parse_mode='markdown')
        
        # Log del uso del comando
        username = sender_info['username'] if sender_info else 'sin_username'
        user_id = sender_info['id'] if sender_info else 'N/A'
        logger.info(f"Comando /id usado por {username} (ID: {user_id}) en chat {chat_info['id']}")
    
    async def _handle_start_command(self, event):
        """Manejar comando /start"""
        chat = await event.get_chat()
        sender = await event.get_sender()
        
        welcome_msg = "🤖 **¡Hola! Soy Grande Bot**\n\n"
        welcome_msg += "Soy un bot especializado en monitorear y procesar mensajes de grupos.\n\n"
        welcome_msg += "**Comandos disponibles:**\n"
        welcome_msg += "• `/id` - Obtener información completa de IDs\n"
        welcome_msg += "• `/start` - Mostrar este mensaje\n"
        welcome_msg += "• `/help` - Ayuda detallada\n"
        welcome_msg += "• `/status` - Estado del bot\n"
        welcome_msg += "• `/dbinfo` - Información de la base de datos\n\n"
        welcome_msg += "**Funcionalidades:**\n"
        welcome_msg += "• 📝 Procesamiento de texto\n"
        welcome_msg += "• 🎥 Detección de videos grandes (>20MB)\n"
        welcome_msg += "• 🖼️ Análisis de imágenes\n"
        welcome_msg += "• 🎬 Procesamiento de animaciones\n"
        welcome_msg += "• 🎭 Detección de stickers\n\n"
        welcome_msg += "ℹ️ Usa `/id` para obtener IDs de chats, usuarios y mensajes."
        
        await event.respond(welcome_msg, parse_mode='markdown')
        
        # Log del comando start
        username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
        logger.info(f"Comando /start usado por {username} (ID: {sender.id if sender else 'N/A'})")
    
    async def _handle_help_command(self, event):
        """Manejar comando /help"""
        help_msg = "❓ **AYUDA - Grande Bot**\n\n"
        help_msg += "**📋 COMANDOS DISPONIBLES:**\n\n"
        
        help_msg += "🆔 `/id`\n"
        help_msg += "Muestra información completa de IDs:\n"
        help_msg += "• ID del chat/grupo/canal\n"
        help_msg += "• ID del usuario que envía\n"
        help_msg += "• ID del mensaje\n"
        help_msg += "• Información de reenvíos\n"
        help_msg += "• Datos técnicos adicionales\n"
        help_msg += "• Username (si está disponible)\n\n"
        
        help_msg += "🏠 `/start`\n"
        help_msg += "Muestra mensaje de bienvenida\n\n"
        
        help_msg += "❓ `/help`\n"
        help_msg += "Muestra esta ayuda\n\n"
        
        help_msg += "📊 `/status`\n"
        help_msg += "Estado del bot y configuración actual\n\n"
        
        help_msg += "**�️ COMANDOS DE BASE DE DATOS:**\n\n"
        help_msg += "📊 `/dbinfo`\n"
        help_msg += "Información general de la base de datos\n\n"
        
        help_msg += "📈 `/dbstats`\n"
        help_msg += "Estadísticas detalladas de la BD\n\n"
        
        help_msg += "🧹 `/dbclean`\n"
        help_msg += "Limpiar completamente la base de datos\n\n"
        
        help_msg += "**�🔧 FUNCIONALIDADES AUTOMÁTICAS:**\n\n"
        help_msg += "📝 **Texto**: Detecta enlaces, emails, teléfonos\n"
        help_msg += "🎥 **Videos**: Descarga automáticamente si >20MB\n"
        help_msg += "🖼️ **Imágenes**: Análisis y registro\n"
        help_msg += "🎬 **Animaciones**: Detección de GIFs\n"
        help_msg += "🎭 **Stickers**: Catalogación automática\n\n"
        
        help_msg += "**💡 CONSEJOS:**\n\n"
        help_msg += "• Usa `/id` en cualquier chat para obtener su información\n"
        help_msg += "• Responde a un mensaje con `/id` para ver IDs relacionados\n"
        help_msg += "• Reenvía un mensaje y usa `/id` para ver el origen\n"
        help_msg += "• El bot registra automáticamente toda la actividad\n"
        help_msg += "• Usa `/dbinfo` para ver estadísticas de la base de datos\n\n"
        
        help_msg += "**📊 DATOS GUARDADOS:**\n"
        help_msg += "• Todos los mensajes procesados\n"
        help_msg += "• IDs de mensajes originales y respuestas\n"
        help_msg += "• Archivos descargados\n"
        help_msg += "• Estadísticas de uso"
        
        await event.respond(help_msg, parse_mode='markdown')
        
        # Log del comando help
        sender = await event.get_sender()
        username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
        logger.info(f"Comando /help usado por {username} (ID: {sender.id if sender else 'N/A'})")
    
    async def _handle_status_command(self, event):
        """Manejar comando /status para verificar configuración"""
        import os
        from datetime import datetime
        
        chat = await event.get_chat()
        chat_info = IdHelper.get_chat_info(chat)
        
        response = "📊 **ESTADO DEL BOT**\n"
        response += "=" * 30 + "\n\n"
        
        # Información del chat actual
        response += "📍 **CHAT ACTUAL**\n"
        response += f"🏷️ **Nombre**: {chat_info['title']}\n"
        response += f"🆔 **ID**: `{chat_info['id']}`\n"
        response += f"📝 **Tipo**: {chat_info['type']}\n\n"
        
        # Configuración del grupo objetivo
        target_group_id = os.getenv('TARGET_GROUP_ID')
        target_group_username = os.getenv('TARGET_GROUP_USERNAME')
        
        response += "🎯 **CONFIGURACIÓN**\n"
        response += f"🆔 **Grupo objetivo ID**: `{target_group_id or 'No configurado'}`\n"
        response += f"📛 **Grupo objetivo Username**: `{target_group_username or 'No configurado'}`\n\n"
        
        # Verificar si estamos en el grupo objetivo
        current_chat_id = chat_info['id']
        if target_group_id:
            try:
                target_id = int(target_group_id)
                if current_chat_id == target_id:
                    response += "✅ **ESTADO**: Este ES el grupo objetivo configurado\n"
                    response += "🟢 **El bot debería procesar mensajes aquí**\n\n"
                else:
                    response += "ℹ️ **ESTADO**: Este NO es el grupo objetivo\n"
                    response += f"📤 **Grupo objetivo**: `{target_id}`\n"
                    response += f"📥 **Chat actual**: `{current_chat_id}`\n\n"
            except ValueError:
                response += "⚠️ **ERROR**: ID del grupo objetivo no válido\n\n"
        else:
            response += "⚠️ **ESTADO**: No hay grupo objetivo configurado\n"
            response += "🟡 **El bot procesará mensajes de todos los grupos**\n\n"
        
        # Información adicional
        response += "🤖 **INFORMACIÓN DEL BOT**\n"
        me = await self.client.get_me()
        response += f"👤 **Nombre**: {me.first_name}\n"
        response += f"🆔 **ID**: `{me.id}`\n"
        response += f"📛 **Username**: @{me.username}\n\n"
        
        response += "⏰ **TIEMPO**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        await event.respond(response, parse_mode='markdown')
        
        # Log del comando status
        sender = await event.get_sender()
        username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
        logger.info(f"Comando /status usado por {username} (ID: {sender.id if sender else 'N/A'}) en chat {current_chat_id}")