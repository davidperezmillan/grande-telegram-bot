import os
import aiofiles
from datetime import datetime
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from src.utils.logger import get_logger

logger = get_logger()

class FileHandler:
    def __init__(self):
        self.download_dir = '/app/downloads'
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', 20))
        self.max_file_size_bytes = self.max_file_size_mb * 1024 * 1024
        
        # Crear directorio de descargas si no existe
        os.makedirs(self.download_dir, exist_ok=True)
    
    def get_file_info(self, message):
        """Obtener información del archivo en el mensaje"""
        if not message.media:
            return None
        
        file_info = {
            'has_file': False,
            'file_type': None,
            'file_size': 0,
            'file_name': None,
            'mime_type': None
        }
        
        if isinstance(message.media, MessageMediaDocument):
            document = message.media.document
            file_info['has_file'] = True
            file_info['file_size'] = document.size
            file_info['mime_type'] = document.mime_type
            
            # Obtener nombre del archivo
            for attr in document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    file_info['file_name'] = attr.file_name
                    break
            
            # Determinar tipo de archivo
            if document.mime_type:
                if document.mime_type.startswith('video/'):
                    file_info['file_type'] = 'video'
                elif document.mime_type.startswith('image/'):
                    file_info['file_type'] = 'animation' if 'gif' in document.mime_type else 'image'
                elif 'sticker' in document.mime_type or any(hasattr(attr, 'stickerset') for attr in document.attributes):
                    file_info['file_type'] = 'sticker'
        
        elif isinstance(message.media, MessageMediaPhoto):
            file_info['has_file'] = True
            file_info['file_type'] = 'image'
            file_info['mime_type'] = 'image/jpeg'
            # Las fotos no tienen tamaño directo, estimamos
            file_info['file_size'] = 0  # Se calculará si es necesario
        
        return file_info
    
    async def should_download_file(self, file_info):
        """Determinar si el archivo debe ser descargado"""
        if not file_info or not file_info['has_file']:
            return False, "No hay archivo"
        
        # Verificar tamaño para videos
        if file_info['file_type'] == 'video':
            if file_info['file_size'] > self.max_file_size_bytes:
                return True, f"Video grande detectado: {file_info['file_size'] / (1024*1024):.1f}MB"
            else:
                return False, f"Video pequeño: {file_info['file_size'] / (1024*1024):.1f}MB"
        
        # Por ahora, otros tipos no se descargan automáticamente
        return False, f"Tipo {file_info['file_type']} - pendiente de definir"
    
    async def download_file(self, client, message, file_info, progress_callback=None):
        """Descargar archivo del mensaje con callback de progreso"""
        try:
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = self._get_file_extension(file_info)
            
            if file_info['file_name']:
                base_name = os.path.splitext(file_info['file_name'])[0]
                file_name = f"{timestamp}_{base_name}{file_extension}"
            else:
                file_name = f"{timestamp}_message_{message.id}{file_extension}"
            
            file_path = os.path.join(self.download_dir, file_name)
            
            # Descargar archivo con callback de progreso
            logger.info(f"Descargando archivo: {file_name}")
            
            if progress_callback:
                # Función interna para manejar el progreso
                def progress_handler(current, total):
                    if total > 0:
                        percentage = (current / total) * 100
                        # Ejecutar callback de progreso de forma asíncrona
                        import asyncio
                        asyncio.create_task(progress_callback(current, total, percentage))
                
                await client.download_media(message, file_path, progress_callback=progress_handler)
            else:
                await client.download_media(message, file_path)
            
            # Verificar que el archivo se descargó correctamente
            if os.path.exists(file_path):
                actual_size = os.path.getsize(file_path)
                logger.info(f"Archivo descargado: {file_path} ({actual_size} bytes)")
                return file_path
            else:
                logger.error(f"Error: archivo no encontrado después de la descarga")
                return None
        
        except Exception as e:
            logger.error(f"Error descargando archivo: {e}")
            return None
    
    def _get_file_extension(self, file_info):
        """Obtener extensión del archivo basada en el tipo MIME"""
        mime_to_ext = {
            'video/mp4': '.mp4',
            'video/avi': '.avi',
            'video/mkv': '.mkv',
            'video/mov': '.mov',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
        }
        
        return mime_to_ext.get(file_info.get('mime_type', ''), '.bin')
    
    def format_file_size(self, size_bytes):
        """Formatear tamaño de archivo en formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"