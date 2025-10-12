from src.processors.base_processor import BaseProcessor
from src.video_management import VideoDownloader, VideoForwarder


class VideoProcessor(BaseProcessor):
    """Procesador de mensajes de video"""
    
    def __init__(self, client, file_handler=None, text_processor=None):
        super().__init__(client, file_handler, text_processor)
        # Inicializar gestores especializados de video
        self.video_downloader = VideoDownloader(client, file_handler, self.notification_manager)
        self.video_forwarder = VideoForwarder(client, self.notification_manager)
    
    async def process(self, message, message_data):
        self.log_info(f"Procesando video ID: {message.id}")

        """Procesar mensaje de video"""
        file_info = self.file_handler.get_file_info(message)
        
        if file_info:
            message_data['file_size'] = file_info['file_size']
            
            should_download, reason = await self.file_handler.should_download_file(file_info)
            
            if should_download:
                # Delegar la descarga al gestor especializado de videos largos
                result = await self.video_downloader.download_video(message, file_info, reason, message_data)
                return result
            else:
                # Delegar el reenvío al gestor especializado de videos cortos
                result = await self.video_forwarder.forward_video_to_private_chat(message, file_info, reason)
                return result
        
        return "video sin información de archivo"