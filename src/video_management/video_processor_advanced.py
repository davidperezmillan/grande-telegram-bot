import os
import time
import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger()

class AdvancedVideoProcessor:
    """
    Procesador avanzado de videos largos con recorte automático
    
    Funcionalidades:
    1. Descarga de video largo
    2. Recorte de video corto
    3. Reenvío de video corto
    4. Limpieza de archivos temporales
    5. Manejo de errores y reporte de estado
    6. Métricas de tiempo para cada paso
    7. Logs detallados
    8. Manejo robusto de excepciones
    9. Borrado de mensajes relacionados
    """
    
    def __init__(self, client, file_handler, notification_manager):
        self.client = client
        self.file_handler = file_handler
        self.notification_manager = notification_manager
        self.logger = logger
        
        # Configuración de recorte (configurable por variables de entorno)
        try:
            self.clip_duration = int(os.getenv('VIDEO_CLIP_DURATION', '30'))  # segundos
        except ValueError:
            self.logger.warning(f"Valor inválido para VIDEO_CLIP_DURATION. Usando valor por defecto: 30 segundos.")
            self.clip_duration = 30
        
        # Obtener offset de inicio (puede estar vacío para inicio aleatorio)
        start_offset_env = os.getenv('VIDEO_CLIP_START_OFFSET', '').strip()
        self.clip_start_offset = None
        
        # Validar que el offset sea un número válido
        if start_offset_env:
            try:
                # Ignorar líneas que empiecen con # (comentarios)
                if not start_offset_env.startswith('#'):
                    self.clip_start_offset = int(start_offset_env)
            except ValueError:
                self.logger.warning(f"Valor inválido para VIDEO_CLIP_START_OFFSET: '{start_offset_env}'. Usando inicio aleatorio.")
        
        self.use_random_start = self.clip_start_offset is None
        
        # Configuración de limpieza de archivos
        cleanup_files_env = os.getenv('VIDEO_CLEANUP_FILES', 'true').strip().lower()
        self.cleanup_files = cleanup_files_env in ['true', '1', 'yes', 'on']
        
        # Métricas de tiempo
        self.metrics = {}
        
        start_info = "aleatorio" if self.use_random_start else f"{self.clip_start_offset}s"
        cleanup_info = "habilitada" if self.cleanup_files else "deshabilitada"
        self.logger.info(f"AdvancedVideoProcessor inicializado - Clip: {self.clip_duration}s desde {start_info}, Limpieza: {cleanup_info}")
        
    async def process_long_video(self, message, file_info, reason, message_data):
        """
        Proceso completo de procesamiento de video largo
        
        Args:
            message: Mensaje de Telegram con el video
            file_info: Información del archivo de video
            reason: Razón del procesamiento
            message_data: Datos del mensaje
            
        Returns:
            dict: Resultado del procesamiento con métricas
        """
        process_id = f"video_{message.id}_{int(time.time())}"
        self.logger.info(f"[{process_id}] Iniciando procesamiento de video largo")
        
        # Inicializar métricas
        self.metrics[process_id] = {
            'start_time': time.time(),
            'steps': {},
            'errors': [],
            'files_created': [],
            'success': False
        }
        
        try:
            # Paso 1: Descargar video largo
            download_result = await self._step_1_download_video(
                process_id, message, file_info, reason, message_data
            )
            
            if not download_result['success']:
                return await self._finalize_process(process_id, download_result)
            
            # Paso 2: Recortar video corto
            clip_result = await self._step_2_create_clip(
                process_id, download_result['file_path'], file_info
            )
            
            if not clip_result['success']:
                return await self._finalize_process(process_id, clip_result)
            
            # Paso 3: Reenviar video corto
            forward_result = await self._step_3_forward_clip(
                process_id, message, clip_result['clip_path'], file_info
            )
            
            # Paso 4: Limpiar archivos temporales (condicional)
            cleanup_result = {'success': True, 'skipped': True}  # Default para cuando se omite
            if self.cleanup_files:
                cleanup_result = await self._step_4_cleanup_files(
                    process_id, [download_result['file_path'], clip_result['clip_path']]
                )
            else:
                self.logger.info(f"[{process_id}] Paso 4: Limpieza de archivos deshabilitada por configuración")
                # Registrar paso omitido en métricas
                self.metrics[process_id]['steps']['cleanup_files'] = {
                    'duration': 0,
                    'success': True,
                    'skipped': True,
                    'reason': 'Disabled by VIDEO_CLEANUP_FILES setting'
                }
            
            # Paso 5: Borrar mensajes relacionados
            delete_result = await self._step_5_delete_messages(
                process_id, message
            )
            
            # Marcar como exitoso
            self.metrics[process_id]['success'] = True
            
            # Resultado final
            final_result = {
                'success': True,
                'process_id': process_id,
                'steps_completed': 5,
                'forward_success': forward_result['success'],
                'cleanup_success': cleanup_result['success'],
                'cleanup_skipped': cleanup_result.get('skipped', False),
                'delete_success': delete_result['success'],
                'metrics': self.metrics[process_id]
            }
            
            return await self._finalize_process(process_id, final_result)
            
        except Exception as e:
            self.logger.error(f"[{process_id}] Error crítico en procesamiento: {e}")
            self.metrics[process_id]['errors'].append(f"Error crítico: {str(e)}")
            
            error_result = {
                'success': False,
                'error': str(e),
                'process_id': process_id,
                'metrics': self.metrics[process_id]
            }
            
            return await self._finalize_process(process_id, error_result)
    
    async def _step_1_download_video(self, process_id, message, file_info, reason, message_data):
        """
        Paso 1: Descargar video largo con métricas
        """
        step_name = "download_video"
        self.logger.info(f"[{process_id}] Paso 1: Descargando video largo")
        
        step_start = time.time()
        
        try:
            # Notificar inicio de descarga
            await self.notification_manager.send_notification(
                chat_id=self.notification_manager.bot_owner_id,
                message=f"🎬 **Procesando Video Largo**\n\n"
                       f"📥 **Paso 1/5**: Descargando video...\n"
                       f"📏 **Tamaño**: {file_info['file_size'] / (1024*1024):.1f} MB\n"
                       f"🆔 **ID**: {message.id}",
                parse_mode='markdown'
            )
            
            # Crear callback de progreso (enviar al chat privado)
            progress_callback = await self.notification_manager.create_progress_callback(
                chat_id=self.notification_manager.bot_owner_id,
                message_id=message.id,
                file_name=f"video_largo_{message.id}"
            )
            
            # Descargar archivo
            file_path = await self.file_handler.download_file(
                self.client,
                message,
                file_info,
                progress_callback=progress_callback
            )
            
            if not file_path:
                raise Exception("No se pudo descargar el archivo")
            
            # Registrar archivo creado
            self.metrics[process_id]['files_created'].append(file_path)
            
            # Métricas del paso
            step_duration = time.time() - step_start
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': True,
                'file_path': file_path,
                'file_size': file_info['file_size']
            }
            
            self.logger.info(f"[{process_id}] Paso 1 completado en {step_duration:.2f}s")
            
            return {
                'success': True,
                'file_path': file_path,
                'duration': step_duration
            }
            
        except Exception as e:
            step_duration = time.time() - step_start
            error_msg = f"Error en descarga: {str(e)}"
            
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': False,
                'error': error_msg
            }
            self.metrics[process_id]['errors'].append(error_msg)
            
            self.logger.error(f"[{process_id}] {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': step_duration
            }
    
    async def _step_2_create_clip(self, process_id, video_path, file_info):
        """
        Paso 2: Crear clip corto del video largo
        """
        step_name = "create_clip"
        self.logger.info(f"[{process_id}] Paso 2: Creando clip corto")
        
        step_start = time.time()
        
        try:
            # Determinar el tiempo de inicio del clip
            actual_start_offset = self.clip_start_offset
            start_info = f"{actual_start_offset}s"
            
            if self.use_random_start:
                # Obtener duración del video para calcular inicio aleatorio
                video_duration = await self._get_video_duration(video_path)
                
                if video_duration is not None:
                    actual_start_offset = self._calculate_random_start_time(video_duration)
                    start_info = f"{actual_start_offset}s (aleatorio de {video_duration:.1f}s total)"
                else:
                    # Fallback: usar un offset fijo si no se puede obtener la duración
                    actual_start_offset = 10
                    start_info = f"{actual_start_offset}s (fallback, no se pudo obtener duración)"
                    self.logger.warning(f"[{process_id}] No se pudo obtener duración del video, usando offset fijo")
            
            # Notificar inicio de recorte
            await self.notification_manager.send_notification(
                chat_id=self.notification_manager.bot_owner_id,
                message=f"✂️ **Paso 2/5**: Recortando video...\n"
                       f"⏱️ **Duración clip**: {self.clip_duration}s\n"
                       f"▶️ **Inicio**: {start_info}",
                parse_mode='markdown'
            )
            
            # Generar nombre para el clip
            video_file = Path(video_path)
            clip_path = video_file.parent / f"clips/clip_{video_file.stem}.mp4"
            
            # Crear clip usando ffmpeg con el offset calculado
            await self._create_video_clip(video_path, str(clip_path), actual_start_offset)
            
            # Verificar que el clip se creó correctamente
            if not clip_path.exists():
                raise Exception("El clip no se generó correctamente")
            
            clip_size = clip_path.stat().st_size
            
            # Registrar archivo creado
            self.metrics[process_id]['files_created'].append(str(clip_path))
            
            # Métricas del paso
            step_duration = time.time() - step_start
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': True,
                'clip_path': str(clip_path),
                'clip_size': clip_size,
                'clip_duration': self.clip_duration,
                'start_offset': actual_start_offset,
                'random_start': self.use_random_start
            }
            
            self.logger.info(f"[{process_id}] Paso 2 completado en {step_duration:.2f}s")
            
            return {
                'success': True,
                'clip_path': str(clip_path),
                'clip_size': clip_size,
                'duration': step_duration
            }
            
        except Exception as e:
            step_duration = time.time() - step_start
            error_msg = f"Error creando clip: {str(e)}"
            
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': False,
                'error': error_msg
            }
            self.metrics[process_id]['errors'].append(error_msg)
            
            self.logger.error(f"[{process_id}] {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': step_duration
            }
    
    async def _step_3_forward_clip(self, process_id, original_message, clip_path, file_info):
        """
        Paso 3: Reenviar clip al chat privado
        """
        step_name = "forward_clip"
        self.logger.info(f"[{process_id}] Paso 3: Reenviando clip")
        
        step_start = time.time()
        
        try:
            # Notificar inicio de reenvío
            await self.notification_manager.send_notification(
                chat_id=self.notification_manager.bot_owner_id,
                message=f"📤 **Paso 3/5**: Enviando clip al chat privado...",
                parse_mode='markdown'
            )
            
            # Obtener información del chat original
            try:
                chat = await self.client.get_entity(original_message.chat_id)
                chat_name = getattr(chat, 'title', getattr(chat, 'first_name', f'Chat {original_message.chat_id}'))
            except:
                chat_name = f'Chat {original_message.chat_id}'
            
            # Crear caption para el clip
            clip_size_mb = Path(clip_path).stat().st_size / (1024 * 1024)
            original_size_mb = file_info['file_size'] / (1024 * 1024)
            
            caption = f"🎬 **Clip de Video Largo Procesado**\n\n"
            caption += f"💬 **Origen**: {chat_name}\n"
            caption += f"🆔 **Mensaje original**: {original_message.id}\n"
            caption += f"📏 **Tamaño original**: {original_size_mb:.1f} MB\n"
            caption += f"📦 **Tamaño clip**: {clip_size_mb:.1f} MB\n"
            caption += f"⏱️ **Duración clip**: {self.clip_duration}s\n"
            caption += f"🕐 **Procesado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Enviar clip al chat privado
            sent_message = await self.client.send_file(
                entity=self.notification_manager.bot_owner_id,
                file=clip_path,
                caption=caption,
                parse_mode='markdown'
            )
            
            # Métricas del paso
            step_duration = time.time() - step_start
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': True,
                'sent_message_id': sent_message.id,
                'clip_size': clip_size_mb
            }
            
            self.logger.info(f"[{process_id}] Paso 3 completado en {step_duration:.2f}s")
            
            return {
                'success': True,
                'sent_message_id': sent_message.id,
                'duration': step_duration
            }
            
        except Exception as e:
            step_duration = time.time() - step_start
            error_msg = f"Error reenviando clip: {str(e)}"
            
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': False,
                'error': error_msg
            }
            self.metrics[process_id]['errors'].append(error_msg)
            
            self.logger.error(f"[{process_id}] {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': step_duration
            }
    
    async def _step_4_cleanup_files(self, process_id, file_paths):
        """
        Paso 4: Limpiar archivos temporales
        """
        step_name = "cleanup_files"
        self.logger.info(f"[{process_id}] Paso 4: Limpiando archivos temporales")
        
        step_start = time.time()
        
        try:
            # Notificar inicio de limpieza
            await self.notification_manager.send_notification(
                chat_id=self.notification_manager.bot_owner_id,
                message=f"🧹 **Paso 4/5**: Limpiando archivos temporales...",
                parse_mode='markdown'
            )
            
            deleted_files = []
            failed_deletions = []
            total_size_freed = 0
            
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        total_size_freed += file_size
                        self.logger.info(f"[{process_id}] Archivo eliminado: {file_path}")
                    else:
                        self.logger.warning(f"[{process_id}] Archivo no encontrado: {file_path}")
                except Exception as e:
                    failed_deletions.append(f"{file_path}: {str(e)}")
                    self.logger.error(f"[{process_id}] Error eliminando {file_path}: {e}")
            
            # Métricas del paso
            step_duration = time.time() - step_start
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': len(failed_deletions) == 0,
                'deleted_files': deleted_files,
                'failed_deletions': failed_deletions,
                'total_size_freed_mb': total_size_freed / (1024 * 1024)
            }
            
            self.logger.info(f"[{process_id}] Paso 4 completado en {step_duration:.2f}s")
            
            return {
                'success': len(failed_deletions) == 0,
                'deleted_files': deleted_files,
                'failed_deletions': failed_deletions,
                'duration': step_duration
            }
            
        except Exception as e:
            step_duration = time.time() - step_start
            error_msg = f"Error en limpieza: {str(e)}"
            
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': False,
                'error': error_msg
            }
            self.metrics[process_id]['errors'].append(error_msg)
            
            self.logger.error(f"[{process_id}] {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': step_duration
            }
    
    async def _step_5_delete_messages(self, process_id, original_message):
        """
        Paso 5: Borrar mensaje original del grupo
        """
        step_name = "delete_messages"
        self.logger.info(f"[{process_id}] Paso 5: Borrando mensajes relacionados")
        
        step_start = time.time()
        
        try:
            # Notificar inicio de borrado
            await self.notification_manager.send_notification(
                chat_id=self.notification_manager.bot_owner_id,
                message=f"🗑️ **Paso 5/5**: Eliminando mensaje original...",
                parse_mode='markdown'
            )
            
            # Intentar eliminar el mensaje original del grupo
            try:
                await self.client.delete_messages(
                    entity=original_message.chat_id,
                    message_ids=[original_message.id]
                )
                deletion_success = True
                self.logger.info(f"[{process_id}] Mensaje {original_message.id} eliminado del chat {original_message.chat_id}")
            except Exception as e:
                deletion_success = False
                self.logger.error(f"[{process_id}] Error eliminando mensaje: {e}")
            
            # Métricas del paso
            step_duration = time.time() - step_start
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': deletion_success,
                'message_id': original_message.id,
                'chat_id': original_message.chat_id
            }
            
            self.logger.info(f"[{process_id}] Paso 5 completado en {step_duration:.2f}s")
            
            return {
                'success': deletion_success,
                'message_id': original_message.id,
                'duration': step_duration
            }
            
        except Exception as e:
            step_duration = time.time() - step_start
            error_msg = f"Error borrando mensajes: {str(e)}"
            
            self.metrics[process_id]['steps'][step_name] = {
                'duration': step_duration,
                'success': False,
                'error': error_msg
            }
            self.metrics[process_id]['errors'].append(error_msg)
            
            self.logger.error(f"[{process_id}] {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration': step_duration
            }
    
    async def _create_video_clip(self, input_path, output_path, start_offset=None):
        """
        Crear clip de video usando ffmpeg
        
        Args:
            input_path (str): Ruta del video original
            output_path (str): Ruta donde guardar el clip
            start_offset (int, optional): Tiempo de inicio en segundos. Si es None, usa self.clip_start_offset
        """
        try:
            # Usar el offset proporcionado o el configurado por defecto
            actual_start_offset = start_offset if start_offset is not None else self.clip_start_offset
            
            self.logger.info(f"Creando clip: {input_path} -> {output_path} (inicio: {actual_start_offset}s, duración: {self.clip_duration}s)")
            
            # Ejecutar ffmpeg de forma asíncrona
            process = await asyncio.create_subprocess_exec(
                'ffmpeg',
                '-i', input_path,
                '-ss', str(actual_start_offset),     # Tiempo de inicio
                '-t', str(self.clip_duration),       # Duración del clip
                '-c:v', 'libx264',                   # Codec de video
                '-c:a', 'aac',                       # Codec de audio
                '-preset', 'fast',                   # Preset de encoding
                '-y',                                # Sobrescribir archivo existente
                output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg error: {stderr.decode()}")
                
            self.logger.info(f"Clip creado exitosamente: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creando clip con ffmpeg: {e}")
            raise
    
    async def _finalize_process(self, process_id, result):
        """
        Finalizar proceso y enviar reporte final
        """
        total_duration = time.time() - self.metrics[process_id]['start_time']
        self.metrics[process_id]['total_duration'] = total_duration
        
        # Crear reporte final
        success = result.get('success', False)
        status_emoji = "✅" if success else "❌"
        
        report = f"{status_emoji} **Procesamiento de Video Completado**\n\n"
        report += f"🆔 **Process ID**: `{process_id}`\n"
        report += f"⏱️ **Duración total**: {total_duration:.2f}s\n"
        report += f"📊 **Estado**: {'Exitoso' if success else 'Fallido'}\n\n"
        
        # Detalles de pasos
        report += "📋 **Detalles de pasos**:\n"
        for step_name, step_data in self.metrics[process_id]['steps'].items():
            if step_data.get('skipped', False):
                step_emoji = "⏭️"
                step_info = f"{step_name}: Omitido ({step_data.get('reason', 'N/A')})"
            else:
                step_emoji = "✅" if step_data['success'] else "❌"
                step_info = f"{step_name}: {step_data['duration']:.2f}s"
            report += f"{step_emoji} {step_info}\n"
        
        # Errores si los hay
        if self.metrics[process_id]['errors']:
            report += f"\n⚠️ **Errores ({len(self.metrics[process_id]['errors'])})**:\n"
            for error in self.metrics[process_id]['errors'][:3]:  # Máximo 3 errores
                report += f"• {error}\n"
        
        # Enviar reporte final
        await self.notification_manager.send_notification(
            chat_id=self.notification_manager.bot_owner_id,
            message=report,
            parse_mode='markdown'
        )
        
        self.logger.info(f"[{process_id}] Proceso finalizado. Success: {success}, Duration: {total_duration:.2f}s")
        
        return result
    
    async def _get_video_duration(self, video_path):
        """
        Obtener la duración del video en segundos usando ffprobe
        
        Args:
            video_path (str): Ruta al archivo de video
            
        Returns:
            float: Duración del video en segundos, o None si hay error
        """
        try:
            process = await asyncio.create_subprocess_exec(
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'json',
                video_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Error ejecutando ffprobe: {stderr.decode()}")
                return None
                
            # Parsear la salida JSON
            result = json.loads(stdout.decode())
            duration = float(result['format']['duration'])
            
            self.logger.info(f"Duración del video detectada: {duration:.2f}s")
            return duration
            
        except Exception as e:
            self.logger.error(f"Error obteniendo duración del video: {e}")
            return None
    
    def _calculate_random_start_time(self, video_duration):
        """
        Calcular un tiempo de inicio aleatorio para el clip
        
        Args:
            video_duration (float): Duración total del video en segundos
            
        Returns:
            int: Tiempo de inicio en segundos
        """
        if video_duration <= self.clip_duration:
            # Si el video es más corto que el clip deseado, empezar desde el inicio
            return 0
        
        # Calcular el rango válido para el inicio del clip
        # Dejar un margen al final para que el clip completo quepa
        max_start_time = int(video_duration - self.clip_duration)
        
        # Asegurar que tenemos al menos 5 segundos de margen al inicio
        min_start_time = min(5, max_start_time)
        
        if max_start_time <= min_start_time:
            return min_start_time
        
        # Generar tiempo aleatorio
        random_start = random.randint(min_start_time, max_start_time)
        
        self.logger.info(f"Tiempo de inicio aleatorio calculado: {random_start}s (rango: {min_start_time}-{max_start_time}s)")
        return random_start