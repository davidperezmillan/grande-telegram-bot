from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
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