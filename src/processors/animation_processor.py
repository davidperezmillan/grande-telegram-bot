from src.processors.base_processor import BaseProcessor
import time

class AnimationProcessor(BaseProcessor):
    """Procesador de mensajes de animación/GIF"""
    
    async def process(self, message, message_data):
        """Procesar mensaje de animación/GIF"""
        self.log_info(f"Procesando animación ID: {message.id}")
        
        file_info = self.file_handler.get_file_info(message)
        
        if file_info:
            message_data['file_size'] = file_info['file_size']
            
            should_download, reason = await self.file_handler.should_download_file(file_info)
            
            if should_download:
                self.log_info(f"Descargando animación: {reason}")
                
                # Enviar notificación de inicio de descarga
                await self.notification_manager.send_download_start_notification(
                    chat_id=message.chat_id,
                    message_id=message.id,
                    file_info={
                        'type': 'animación',
                        'size': file_info['file_size'],
                        'name': file_info.get('file_name', f'animacion_{message.id}')
                    },
                    reply_to_message_id=message.id
                )
                
                # Crear callback de progreso
                progress_callback = await self.notification_manager.create_progress_callback(
                    chat_id=message.chat_id,
                    message_id=message.id,
                    file_name=file_info.get('file_name', f'animacion_{message.id}')
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
                    return f"animación descargada - {reason}"
                else:
                    return f"error descargando animación - {reason}"
            else:
                size_str = self.file_handler.format_file_size(file_info['file_size'])
                self.log_info(f"Animación detectada: {size_str}")
                return f"animación detectada - {size_str} - {reason}"
        
        return "animación sin información de archivo"