from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class ProcessedMessage(Base):
    __tablename__ = 'processed_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger, unique=True, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=True)
    username = Column(String(255), nullable=True)
    message_type = Column(String(50), nullable=False)  # text, video, animation, image, sticker
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    action_taken = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<ProcessedMessage(id={self.id}, message_id={self.message_id}, type={self.message_type})>"

class BotResponse(Base):
    __tablename__ = 'bot_responses'
    
    id = Column(Integer, primary_key=True)
    original_message_id = Column(BigInteger, nullable=False)
    bot_message_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    response_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BotResponse(id={self.id}, original_id={self.original_message_id}, bot_id={self.bot_message_id})>"

class MessageQueue(Base):
    __tablename__ = 'message_queue'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    message_type = Column(String(50), nullable=False)
    priority = Column(Integer, default=0)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<MessageQueue(id={self.id}, message_id={self.message_id}, processed={self.processed})>"

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///data/bot_data.db')
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_database():
    """Inicializar la base de datos creando las tablas"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session():
    """Obtener una sesión de base de datos"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()