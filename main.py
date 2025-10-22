import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from src.config.config import Config
from src.handlers.handler_registry import HandlerRegistry
from src.config.logger import setup_logger

# Cargar variables de entorno
load_dotenv()

async def main():
    logger = setup_logger('Main')
    logger.info("Iniciando bot...")
    
    config = Config()
    
    client = TelegramClient('bot', config.api_id, config.api_hash)
    await client.start(bot_token=config.bot_token)
    
    # Registrar manejadores
    handler_registry = HandlerRegistry(client, config)
    handler_registry.register_all_handlers()
    
    logger.info("Bot iniciado correctamente")
    print("Bot iniciado correctamente")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())