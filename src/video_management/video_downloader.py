import time
from src.utils.logger import get_logger

logger = get_logger()

class VideoDownloader:
    """
    Clase especializada para la descarga de videos largos
    """
    
    def __init__(self, client, file_handler, notification_manager):
        self.client = client
        self.file_handler = file_handler
        self.notification_manager = notification_manager
        self.logger = logger
    
    async def download_video(self, message, file_info, reason, message_data):
        """
        Manejar el proceso completo de descarga de video largo
        
        Args:
            message: Mensaje de Telegram con el video
            file_info: Información del archivo de video
            reason: Razón por la cual se debe descargar
            message_data: Diccionario para almacenar datos del mensaje
            
        Returns:
            str: Resultado de la operación de descarga
        """
        return await self.__download_long_video(message, file_info, reason, message_data)

    # metodo para descargar videos largos con metrica
    async def __download_long_video(self, message, file_info, reason, message_data):
        """
        Manejar el proceso completo de descarga de video largo

        Args:
            message: Mensaje de Telegram con el video
            file_info: Información del archivo de video
            reason: Razón por la cual se debe descargar
            message_data: Diccionario para almacenar datos del mensaje

        Returns:
            str: Resultado de la operación de descarga
        """
        self.log_info(f"Descargando video largo: {reason}")

        # Enviar notificación de inicio de descarga
        await self.notification_manager.send_download_start_notification(
            chat_id=message.chat_id,
            message_id=message.id,
            file_info={
                'type': 'video',
                'size': file_info['file_size'],
                'name': file_info.get('file_name', f'video_{message.id}')
            },
            reply_to_message_id=message.id
        )

        # Crear callback de progreso
        progress_callback = await self.notification_manager.create_progress_callback(
            chat_id=message.chat_id,
            message_id=message.id,
            file_name=file_info.get('file_name', f'video_{message.id}')
        )

        # Registrar tiempo de inicio
        start_time = time.time()

        # Descargar archivo con callback de progreso
        file_path = await self.file_handler.download_file(
            self.client,
            message,
            file_info,
            progress_callback=progress_callback
        )

        # Actualizar message_data con el path del archivo
        message_data['file_path'] = file_path

        # Calcular duración de descarga
        download_duration = time.time() - start_time

        # Preparar resultado de descarga
        download_result = {
            'success': bool(file_path),
            'file_path': file_path,
            'duration': download_duration,
            'file_size': file_info['file_size']
        }

        if not file_path:
            download_result['error'] = 'No se pudo descargar el archivo'

        # Enviar notificación de descarga completada
        await self.notification_manager.send_download_complete_notification(
            chat_id=message.chat_id,
            message_id=message.id,
            download_result=download_result,
            reply_to_message_id=message.id
        )

        # Limpiar referencia del mensaje de progreso
        await self.notification_manager.clear_progress_message(
            chat_id=message.chat_id,
            message_id=message.id
        )

        if file_path:
            return f"video largo descargado - {reason}"
        else:
            return f"error descargando video largo - {reason}"
    
    def log_info(self, message):
        """Helper para logging"""
        self.logger.info(message)
    
    def log_error(self, message):
        """Helper para logging de errores"""
        self.logger.error(message)