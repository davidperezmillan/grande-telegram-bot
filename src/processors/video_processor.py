from src.processors.base_processor import BaseProcessor
from src.video_management import VideoDownloader, VideoForwarder, AdvancedVideoProcessor
import os

class VideoProcessor(BaseProcessor):
    """Procesador de mensajes de video con capacidades avanzadas"""
    
    def __init__(self, client, file_handler=None, text_processor=None):
        super().__init__(client, file_handler, text_processor)
        
        # Inicializar gestores especializados de video
        self.video_downloader = VideoDownloader(client, file_handler, self.notification_manager)
        self.video_forwarder = VideoForwarder(client, self.notification_manager)
        
        # Inicializar procesador avanzado para videos largos
        self.advanced_processor = AdvancedVideoProcessor(client, file_handler, self.notification_manager)
        
        # Configuración para procesamiento avanzado
        # Por defecto está deshabilitado, se puede habilitar con variable de entorno
        self.enable_advanced_processing = os.getenv('ENABLE_ADVANCED_VIDEO_PROCESSING', 'false').lower() == 'true'
        
        if self.enable_advanced_processing:
            self.log_info("Procesamiento avanzado de videos HABILITADO - se recortarán clips automáticamente")
        else:
            self.log_info("Procesamiento avanzado de videos DESHABILITADO - solo descarga/reenvío")
    
    async def process(self, message, message_data):
        self.log_info(f"Procesando video ID: {message.id}")

        file_info = self.file_handler.get_file_info(message)
        
        if file_info:
            message_data['file_size'] = file_info['file_size']
            
            should_download, reason = await self.file_handler.should_download_file(file_info)
            
            if should_download:
                # Determinar qué tipo de procesamiento usar
                if self.enable_advanced_processing:
                    # Usar procesamiento avanzado con recorte automático
                    self.log_info(f"Usando procesamiento avanzado para video ID: {message.id}")
                    result = await self.advanced_processor.process_long_video(
                        message, file_info, reason, message_data
                    )
                    
                    # Extraer información del resultado para compatibilidad
                    if result['success']:
                        return f"video largo procesado con clip - {reason}"
                    else:
                        return f"error procesando video largo - {reason}: {result.get('error', 'Unknown error')}"
                else:
                    # Usar procesamiento tradicional (solo descarga)
                    self.log_info(f"Usando procesamiento tradicional para video ID: {message.id}")
                    result = await self.video_downloader.download_video(message, file_info, reason, message_data)
                    return result
            else:
                # Videos pequeños siempre usan el forwarder tradicional
                result = await self.video_forwarder.forward_video_to_private_chat(message, file_info, reason)
                return result
        
        return "video sin información de archivo"