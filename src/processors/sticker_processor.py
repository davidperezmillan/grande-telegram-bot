from src.processors.base_processor import BaseProcessor

class StickerProcessor(BaseProcessor):
    """Procesador de mensajes de sticker"""
    
    async def process(self, message, message_data):
        """Procesar mensaje de sticker"""
        file_info = self.file_handler.get_file_info(message)
        
        if file_info:
            self.log_info("Sticker detectado")
            
            # Por definir: lógica específica para stickers
            return "sticker detectado - acción por definir"
        
        return "sticker sin información de archivo"