from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func
from src.database.models import ProcessedMessage, BotResponse, MessageQueue, AsyncSessionLocal
from datetime import datetime
from typing import Optional, List

class DatabaseManager:
    def __init__(self):
        pass
    
    async def get_session(self) -> AsyncSession:
        """Obtener una nueva sesión de base de datos"""
        return AsyncSessionLocal()
    
    async def save_processed_message(self, message_data: dict) -> ProcessedMessage:
        """Guardar un mensaje procesado en la base de datos"""
        async with AsyncSessionLocal() as session:
            processed_msg = ProcessedMessage(
                message_id=message_data['message_id'],
                chat_id=message_data['chat_id'],
                user_id=message_data.get('user_id'),
                username=message_data.get('username'),
                message_type=message_data['message_type'],
                content=message_data.get('content'),
                file_path=message_data.get('file_path'),
                file_size=message_data.get('file_size'),
                action_taken=message_data.get('action_taken')
            )
            
            session.add(processed_msg)
            await session.commit()
            await session.refresh(processed_msg)
            return processed_msg
    
    async def save_bot_response(self, response_data: dict) -> BotResponse:
        """Guardar una respuesta del bot en la base de datos"""
        async with AsyncSessionLocal() as session:
            bot_response = BotResponse(
                original_message_id=response_data['original_message_id'],
                bot_message_id=response_data['bot_message_id'],
                chat_id=response_data['chat_id'],
                response_type=response_data['response_type'],
                content=response_data.get('content')
            )
            
            session.add(bot_response)
            await session.commit()
            await session.refresh(bot_response)
            return bot_response
    
    async def is_message_processed(self, message_id: int) -> bool:
        """Verificar si un mensaje ya fue procesado"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ProcessedMessage).where(ProcessedMessage.message_id == message_id)
            )
            return result.scalar_one_or_none() is not None
    
    async def get_processed_message(self, message_id: int) -> Optional[ProcessedMessage]:
        """Obtener un mensaje procesado por su ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ProcessedMessage).where(ProcessedMessage.message_id == message_id)
            )
            return result.scalar_one_or_none()
    
    async def get_bot_responses_for_message(self, original_message_id: int) -> List[BotResponse]:
        """Obtener todas las respuestas del bot para un mensaje original"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(BotResponse).where(BotResponse.original_message_id == original_message_id)
            )
            return result.scalars().all()
    
    async def add_to_queue(self, message_data: dict) -> MessageQueue:
        """Añadir un mensaje a la cola de procesamiento"""
        async with AsyncSessionLocal() as session:
            queue_item = MessageQueue(
                message_id=message_data['message_id'],
                chat_id=message_data['chat_id'],
                message_type=message_data['message_type'],
                priority=message_data.get('priority', 0)
            )
            
            session.add(queue_item)
            await session.commit()
            await session.refresh(queue_item)
            return queue_item
    
    async def mark_queue_item_processed(self, queue_id: int, error_message: str = None):
        """Marcar un elemento de la cola como procesado"""
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(MessageQueue)
                .where(MessageQueue.id == queue_id)
                .values(
                    processed=True,
                    processed_at=datetime.utcnow(),
                    error_message=error_message
                )
            )
            await session.commit()
    
    async def get_pending_queue_items(self, limit: int = 100) -> List[MessageQueue]:
        """Obtener elementos pendientes de la cola"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(MessageQueue)
                .where(MessageQueue.processed == False)
                .order_by(MessageQueue.priority.desc(), MessageQueue.created_at.asc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_message_statistics(self) -> dict:
        """Obtener estadísticas de mensajes procesados"""
        async with AsyncSessionLocal() as session:
            # Total de mensajes procesados
            total_result = await session.execute(select(ProcessedMessage))
            total_messages = len(total_result.scalars().all())
            
            # Mensajes por tipo
            type_stats = {}
            for msg_type in ['text', 'video', 'animation', 'image', 'sticker']:
                result = await session.execute(
                    select(ProcessedMessage).where(ProcessedMessage.message_type == msg_type)
                )
                type_stats[msg_type] = len(result.scalars().all())
            
            return {
                'total_messages': total_messages,
                'by_type': type_stats
            }
    
    async def get_basic_stats(self) -> dict:
        """Obtener estadísticas básicas de la base de datos"""
        async with AsyncSessionLocal() as session:
            try:
                from src.utils.logger import get_logger
                logger = get_logger()
                
                logger.info("Iniciando consulta de estadísticas básicas...")
                
                # Total de mensajes usando count más eficiente
                total_messages_result = await session.execute(
                    select(func.count(ProcessedMessage.id))
                )
                total_messages = total_messages_result.scalar() or 0
                logger.info(f"Total mensajes encontrados: {total_messages}")
                
                # Usuarios únicos
                unique_users_result = await session.execute(
                    select(func.count(func.distinct(ProcessedMessage.user_id)))
                )
                unique_users = unique_users_result.scalar() or 0
                
                # Chats únicos
                unique_chats_result = await session.execute(
                    select(func.count(func.distinct(ProcessedMessage.chat_id)))
                )
                unique_chats = unique_chats_result.scalar() or 0
                
                # Archivos procesados (mensajes con file_path)
                files_result = await session.execute(
                    select(func.count(ProcessedMessage.id)).where(ProcessedMessage.file_path.isnot(None))
                )
                total_files = files_result.scalar() or 0
                
                # Tipos de mensajes
                message_types = {}
                for msg_type in ['text', 'video', 'animation', 'image', 'sticker']:
                    result = await session.execute(
                        select(func.count(ProcessedMessage.id)).where(ProcessedMessage.message_type == msg_type)
                    )
                    count = result.scalar()
                    if count > 0:
                        message_types[msg_type] = count
                
                # Información de fechas - solo si hay mensajes
                date_info = {}
                if total_messages > 0:
                    # Primer mensaje
                    first_msg_result = await session.execute(
                        select(ProcessedMessage.processed_at).order_by(ProcessedMessage.processed_at.asc()).limit(1)
                    )
                    first_msg_date = first_msg_result.scalar()
                    
                    # Último mensaje
                    last_msg_result = await session.execute(
                        select(ProcessedMessage.processed_at).order_by(ProcessedMessage.processed_at.desc()).limit(1)
                    )
                    last_msg_date = last_msg_result.scalar()
                    
                    if first_msg_date:
                        date_info['first_message'] = first_msg_date.strftime('%Y-%m-%d %H:%M:%S')
                    if last_msg_date:
                        date_info['last_message'] = last_msg_date.strftime('%Y-%m-%d %H:%M:%S')

                return {
                    'total_messages': total_messages or 0,
                    'unique_users': unique_users or 0,
                    'unique_chats': unique_chats or 0,
                    'total_files': total_files or 0,
                    'message_types': message_types,
                    'date_info': date_info,
                    'database_size': 0  # Placeholder - se puede implementar más tarde
                }
                
            except Exception as e:
                from src.utils.logger import get_logger
                logger = get_logger()
                logger.error(f"Error en get_basic_stats: {str(e)}")
                logger.error(f"Tipo de error: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                return {
                    'total_messages': 0,
                    'unique_users': 0,
                    'unique_chats': 0,
                    'total_files': 0,
                    'message_types': {},
                    'date_info': {},
                    'database_size': 0,
                    'error': str(e)
                }
    
    async def get_detailed_stats(self) -> dict:
        """Obtener estadísticas detalladas de la base de datos"""
        async with AsyncSessionLocal() as session:
            try:
                from sqlalchemy import func, desc
                
                # Top usuarios más activos
                top_users_result = await session.execute(
                    select(ProcessedMessage.user_id, ProcessedMessage.username, func.count(ProcessedMessage.id).label('count'))
                    .group_by(ProcessedMessage.user_id, ProcessedMessage.username)
                    .order_by(desc('count'))
                    .limit(10)
                )
                top_users = [
                    {
                        'user_id': row[0],
                        'username': row[1] or f'User_{row[0]}',
                        'count': row[2]
                    }
                    for row in top_users_result.all()
                ]
                
                # Top chats más activos
                top_chats_result = await session.execute(
                    select(ProcessedMessage.chat_id, func.count(ProcessedMessage.id).label('count'))
                    .group_by(ProcessedMessage.chat_id)
                    .order_by(desc('count'))
                    .limit(10)
                )
                top_chats = [
                    {
                        'chat_id': row[0],
                        'chat_name': f'Chat_{row[0]}',  # Se puede mejorar con info real del chat
                        'count': row[1]
                    }
                    for row in top_chats_result.all()
                ]
                
                # Actividad por días (últimos 30 días)
                from datetime import date, timedelta
                daily_activity = []
                for i in range(30, 0, -1):
                    target_date = date.today() - timedelta(days=i)
                    result = await session.execute(
                        select(func.count(ProcessedMessage.id))
                        .where(func.date(ProcessedMessage.processed_at) == target_date)
                    )
                    count = result.scalar() or 0
                    daily_activity.append({
                        'date': target_date.strftime('%Y-%m-%d'),
                        'count': count
                    })
                
                # Tipos de archivos
                file_types = {}
                files_result = await session.execute(
                    select(ProcessedMessage.message_type, func.count(ProcessedMessage.id).label('count'))
                    .where(ProcessedMessage.file_path.isnot(None))
                    .group_by(ProcessedMessage.message_type)
                )
                for row in files_result.all():
                    file_types[row[0]] = row[1]
                
                return {
                    'top_users': top_users,
                    'top_chats': top_chats,
                    'daily_activity': daily_activity,
                    'file_types': file_types
                }
                
            except Exception as e:
                return {
                    'top_users': [],
                    'top_chats': [],
                    'daily_activity': [],
                    'file_types': {},
                    'error': str(e)
                }
    
    async def clean_database(self) -> dict:
        """Limpiar completamente la base de datos"""
        async with AsyncSessionLocal() as session:
            try:
                # Contar registros antes de eliminar
                processed_messages_result = await session.execute(select(ProcessedMessage))
                processed_count = len(processed_messages_result.scalars().all())
                
                bot_responses_result = await session.execute(select(BotResponse))
                responses_count = len(bot_responses_result.scalars().all())
                
                queue_result = await session.execute(select(MessageQueue))
                queue_count = len(queue_result.scalars().all())
                
                # Eliminar todos los registros
                await session.execute(ProcessedMessage.__table__.delete())
                await session.execute(BotResponse.__table__.delete())
                await session.execute(MessageQueue.__table__.delete())
                
                await session.commit()
                
                return {
                    'success': True,
                    'details': {
                        'processed_messages': processed_count,
                        'bot_responses': responses_count,
                        'message_queue': queue_count
                    }
                }
                
            except Exception as e:
                await session.rollback()
                return {
                    'success': False,
                    'error': str(e)
                }