from abc import ABC, abstractmethod
from src.utils.logger import get_logger
from src.utils.notification_manager import NotificationManager

logger = get_logger()

class BaseProcessor(ABC):
    """Clase base para todos los procesadores de mensajes"""
    
    def __init__(self, client, file_handler=None, text_processor=None):
        self.client = client
        self.file_handler = file_handler
        self.text_processor = text_processor
        self.logger = logger
        self.notification_manager = NotificationManager(client)
    
    @abstractmethod
    async def process(self, message, message_data):
        """Método abstracto que debe implementar cada procesador"""
        pass
    
    def log_info(self, message):
        """Helper para logging"""
        self.logger.info(message)
    
    def log_error(self, message):
        """Helper para logging de errores"""
        self.logger.error(message)