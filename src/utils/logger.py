import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name='grande_bot', log_level=None):
    """Configurar el sistema de logging"""
    
    # Obtener nivel de log desde variables de entorno
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (con rotación)
    log_dir = '/app/logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'bot.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name='grande_bot'):
    """Obtener el logger configurado"""
    return logging.getLogger(name)