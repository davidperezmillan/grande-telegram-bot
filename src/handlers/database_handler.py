from telethon import events
from src.utils.logger import get_logger
from src.database.manager import DatabaseManager
from datetime import datetime

logger = get_logger()

class DatabaseHandler:
    def __init__(self, client):
        self.client = client
        self.db_manager = DatabaseManager()
    
    def register_commands(self):
        """Registrar comandos de gestión de base de datos"""
        
        @self.client.on(events.NewMessage(pattern=r'/dbinfo'))
        async def cmd_dbinfo(event):
            """Comando /dbinfo - Información de la base de datos"""
            try:
                await self._handle_dbinfo_command(event)
            except Exception as e:
                logger.error(f"Error en comando /dbinfo: {e}")
                await event.respond("❌ Error obteniendo información de la base de datos")
        
        @self.client.on(events.NewMessage(pattern=r'/dbclean'))
        async def cmd_dbclean(event):
            """Comando /dbclean - Limpiar base de datos"""
            try:
                await self._handle_dbclean_command(event)
            except Exception as e:
                logger.error(f"Error en comando /dbclean: {e}")
                await event.respond("❌ Error limpiando la base de datos")
        
        @self.client.on(events.NewMessage(pattern=r'/dbstats'))
        async def cmd_dbstats(event):
            """Comando /dbstats - Estadísticas detalladas de la BD"""
            try:
                await self._handle_dbstats_command(event)
            except Exception as e:
                logger.error(f"Error en comando /dbstats: {e}")
                await event.respond("❌ Error obteniendo estadísticas")
    
    async def _handle_dbinfo_command(self, event):
        """Manejar comando /dbinfo - Información general de la BD"""
        try:
            # Obtener estadísticas básicas
            stats = await self.db_manager.get_basic_stats()
            
            response = "🗄️ **INFORMACIÓN DE LA BASE DE DATOS**\n"
            response += "=" * 40 + "\n\n"
            
            # Estadísticas generales
            response += "📊 **ESTADÍSTICAS GENERALES**\n"
            response += f"📝 **Total mensajes**: {stats.get('total_messages', 0):,}\n"
            response += f"👥 **Usuarios únicos**: {stats.get('unique_users', 0):,}\n"
            response += f"💬 **Chats únicos**: {stats.get('unique_chats', 0):,}\n"
            response += f"📁 **Archivos procesados**: {stats.get('total_files', 0):,}\n\n"
            
            # Tipos de mensajes
            message_types = stats.get('message_types', {})
            if message_types:
                response += "📑 **TIPOS DE MENSAJES**\n"
                for msg_type, count in message_types.items():
                    response += f"• {msg_type.title()}: {count:,}\n"
                response += "\n"
            
            # Información de fechas
            date_info = stats.get('date_info', {})
            if date_info:
                response += "📅 **INFORMACIÓN TEMPORAL**\n"
                if date_info.get('first_message'):
                    response += f"🔺 **Primer mensaje**: {date_info['first_message']}\n"
                if date_info.get('last_message'):
                    response += f"🔻 **Último mensaje**: {date_info['last_message']}\n"
                response += "\n"
            
            # Tamaño de la BD
            db_size = stats.get('database_size', 0)
            if db_size > 0:
                size_mb = db_size / (1024 * 1024)
                response += f"💾 **Tamaño de BD**: {size_mb:.2f} MB\n\n"
            
            response += "💡 **Comandos disponibles**:\n"
            response += "• `/dbstats` - Estadísticas detalladas\n"
            response += "• `/dbclean` - Limpiar base de datos\n"
            response += "• `/dbinfo` - Esta información"
            
            await event.respond(response, parse_mode='markdown')
            
            # Log del comando
            sender = await event.get_sender()
            username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
            logger.info(f"Comando /dbinfo usado por {username} (ID: {sender.id if sender else 'N/A'})")
            
        except Exception as e:
            logger.error(f"Error en _handle_dbinfo_command: {e}")
            await event.respond("❌ Error obteniendo información de la base de datos")
    
    async def _handle_dbstats_command(self, event):
        """Manejar comando /dbstats - Estadísticas detalladas"""
        try:
            # Obtener estadísticas detalladas
            detailed_stats = await self.db_manager.get_detailed_stats()
            
            response = "📈 **ESTADÍSTICAS DETALLADAS**\n"
            response += "=" * 35 + "\n\n"
            
            # Top usuarios más activos
            top_users = detailed_stats.get('top_users', [])
            if top_users:
                response += "👥 **USUARIOS MÁS ACTIVOS** (Top 5)\n"
                for i, user in enumerate(top_users[:5], 1):
                    username = user.get('username', 'Sin username')
                    response += f"{i}. {username}: {user['count']:,} mensajes\n"
                response += "\n"
            
            # Top chats más activos
            top_chats = detailed_stats.get('top_chats', [])
            if top_chats:
                response += "💬 **CHATS MÁS ACTIVOS** (Top 5)\n"
                for i, chat in enumerate(top_chats[:5], 1):
                    chat_name = chat.get('chat_name', f"Chat {chat['chat_id']}")
                    response += f"{i}. {chat_name}: {chat['count']:,} mensajes\n"
                response += "\n"
            
            # Actividad por días
            daily_activity = detailed_stats.get('daily_activity', [])
            if daily_activity:
                response += "📅 **ACTIVIDAD ÚLTIMOS 7 DÍAS**\n"
                for day in daily_activity[-7:]:
                    response += f"• {day['date']}: {day['count']:,} mensajes\n"
                response += "\n"
            
            # Tipos de archivos
            file_types = detailed_stats.get('file_types', {})
            if file_types:
                response += "📁 **TIPOS DE ARCHIVOS**\n"
                for file_type, count in file_types.items():
                    response += f"• {file_type.title()}: {count:,}\n"
                response += "\n"
            
            response += f"⏰ **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await event.respond(response, parse_mode='markdown')
            
            # Log del comando
            sender = await event.get_sender()
            username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
            logger.info(f"Comando /dbstats usado por {username} (ID: {sender.id if sender else 'N/A'})")
            
        except Exception as e:
            logger.error(f"Error en _handle_dbstats_command: {e}")
            await event.respond("❌ Error obteniendo estadísticas detalladas")
    
    async def _handle_dbclean_command(self, event):
        """Manejar comando /dbclean - Limpiar base de datos"""
        try:
            # Obtener estadísticas antes de limpiar
            stats_before = await self.db_manager.get_basic_stats()
            
            # Confirmar la acción
            sender = await event.get_sender()
            user_id = sender.id if sender else 0
            
            # Solo permitir a usuarios específicos (opcional - puedes cambiar esta lógica)
            # if user_id not in [ADMIN_USER_ID]:  # Descomenta si quieres restringir
            #     await event.respond("❌ No tienes permisos para limpiar la base de datos")
            #     return
            
            response = "⚠️ **CONFIRMACIÓN DE LIMPIEZA**\n"
            response += "=" * 30 + "\n\n"
            response += "🗄️ **Datos actuales en la BD:**\n"
            response += f"📝 Mensajes: {stats_before.get('total_messages', 0):,}\n"
            response += f"👥 Usuarios: {stats_before.get('unique_users', 0):,}\n"
            response += f"💬 Chats: {stats_before.get('unique_chats', 0):,}\n"
            response += f"📁 Archivos: {stats_before.get('total_files', 0):,}\n\n"
            response += "⚠️ **ATENCIÓN**: Esta acción eliminará TODOS los datos.\n"
            response += "Esta acción NO se puede deshacer.\n\n"
            response += "Para confirmar, envía: `/dbclean_confirm`"
            
            await event.respond(response, parse_mode='markdown')
            
            # Log del intento de limpieza
            username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
            logger.warning(f"Intento de limpieza de BD por {username} (ID: {user_id}) - Esperando confirmación")
            
        except Exception as e:
            logger.error(f"Error en _handle_dbclean_command: {e}")
            await event.respond("❌ Error preparando limpieza de la base de datos")
    
    def register_confirmation_commands(self):
        """Registrar comandos de confirmación"""
        
        @self.client.on(events.NewMessage(pattern=r'/dbclean_confirm'))
        async def cmd_dbclean_confirm(event):
            """Comando /dbclean_confirm - Confirmar limpieza de BD"""
            try:
                await self._handle_dbclean_confirm_command(event)
            except Exception as e:
                logger.error(f"Error en comando /dbclean_confirm: {e}")
                await event.respond("❌ Error ejecutando limpieza de la base de datos")
    
    async def _handle_dbclean_confirm_command(self, event):
        """Manejar confirmación de limpieza"""
        try:
            sender = await event.get_sender()
            username = getattr(sender, 'username', 'sin_username') if sender else 'desconocido'
            user_id = sender.id if sender else 0
            
            # Obtener estadísticas antes
            stats_before = await self.db_manager.get_basic_stats()
            
            # Ejecutar limpieza
            cleanup_result = await self.db_manager.clean_database()
            
            response = "🧹 **LIMPIEZA COMPLETADA**\n"
            response += "=" * 25 + "\n\n"
            
            if cleanup_result.get('success', False):
                response += "✅ **Limpieza exitosa**\n\n"
                response += "📊 **Datos eliminados:**\n"
                response += f"📝 Mensajes: {stats_before.get('total_messages', 0):,}\n"
                response += f"👥 Usuarios: {stats_before.get('unique_users', 0):,}\n"
                response += f"💬 Chats: {stats_before.get('unique_chats', 0):,}\n"
                response += f"📁 Archivos: {stats_before.get('total_files', 0):,}\n\n"
                
                details = cleanup_result.get('details', {})
                if details:
                    response += "🔍 **Detalles de limpieza:**\n"
                    for table, count in details.items():
                        response += f"• {table}: {count:,} registros eliminados\n"
                
                response += f"\n🕐 **Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # Log de éxito
                logger.warning(f"BD limpiada exitosamente por {username} (ID: {user_id})")
                logger.info(f"Registros eliminados: {cleanup_result.get('details', {})}")
                
            else:
                response += "❌ **Error en la limpieza**\n"
                error_msg = cleanup_result.get('error', 'Error desconocido')
                response += f"**Error**: {error_msg}"
                
                # Log de error
                logger.error(f"Error en limpieza de BD por {username} (ID: {user_id}): {error_msg}")
            
            await event.respond(response, parse_mode='markdown')
            
        except Exception as e:
            logger.error(f"Error en _handle_dbclean_confirm_command: {e}")
            await event.respond("❌ Error crítico durante la limpieza")