from src.processors.text_processor import MessageTextProcessor
from src.processors.video_processor import VideoProcessor
from src.processors.animation_processor import AnimationProcessor
from src.processors.image_processor import ImageProcessor
from src.processors.sticker_processor import StickerProcessor

class ProcessorFactory:
    """Factory para crear procesadores según el tipo de mensaje"""
    
    @staticmethod
    def create_processor(message_type, client, file_handler=None, text_processor=None):
        """Crear el procesador apropiado según el tipo de mensaje"""
        processors = {
            'text': MessageTextProcessor,
            'video': VideoProcessor,
            'animation': AnimationProcessor,
            'image': ImageProcessor,
            'sticker': StickerProcessor
        }
        
        processor_class = processors.get(message_type)
        if processor_class:
            return processor_class(client, file_handler, text_processor)
        else:
            return None