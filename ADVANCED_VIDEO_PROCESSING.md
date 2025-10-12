# Procesamiento Avanzado de Videos Largos

## Descripción

El sistema de procesamiento avanzado de videos largos permite descargar videos grandes, crear clips cortos automáticamente y reenviarlos al chat privado, todo de forma automatizada con métricas detalladas.

## Funcionalidades

### Proceso Completo (5 Pasos)

1. **Descarga de video largo**: Descarga el video completo con notificaciones de progreso
2. **Recorte de video corto**: Crea un clip de 30 segundos usando FFmpeg
3. **Reenvío de video corto**: Envía el clip al chat privado del dueño
4. **Limpieza de archivos**: Elimina archivos temporales para liberar espacio
5. **Borrado de mensajes**: Elimina el mensaje original del grupo

### Características Avanzadas

- ✅ **Métricas detalladas** para cada paso del proceso
- ✅ **Logs completos** con timestamps y duración de cada operación
- ✅ **Manejo robusto de errores** con fallback y recovery
- ✅ **Notificaciones en tiempo real** del progreso
- ✅ **Limpieza automática** de archivos temporales
- ✅ **Configuración flexible** vía variables de entorno

## Configuración

### Habilitar Procesamiento Avanzado

```bash
# En tu archivo .env
ENABLE_ADVANCED_VIDEO_PROCESSING=true
```

### Configurar Parámetros del Clip

```bash
# Duración del clip en segundos (default: 30)
VIDEO_CLIP_DURATION=30

# Segundos de offset desde el inicio (default: 10)
VIDEO_CLIP_START_OFFSET=10
```

## Ejemplo de Uso

### Modo Tradicional (Default)
```
Video > 200MB → Solo descarga → Guarda en /downloads
Video ≤ 200MB → Reenvío directo → Elimina del grupo
```

### Modo Avanzado (Habilitado)
```
Video > 200MB → Descarga → Recorta clip → Envía clip → Limpia archivos → Elimina mensaje
Video ≤ 200MB → Reenvío directo → Elimina del grupo
```

## Logs y Métricas

Cada procesamiento genera un ID único y métricas detalladas:

```
[video_123_1634567890] Iniciando procesamiento de video largo
[video_123_1634567890] Paso 1: Descargando video largo
[video_123_1634567890] Paso 1 completado en 45.32s
[video_123_1634567890] Paso 2: Creando clip corto
[video_123_1634567890] Paso 2 completado en 12.45s
[video_123_1634567890] Paso 3: Reenviando clip
[video_123_1634567890] Paso 3 completado en 2.15s
[video_123_1634567890] Paso 4: Limpiando archivos temporales
[video_123_1634567890] Paso 4 completado en 0.23s
[video_123_1634567890] Paso 5: Borrando mensajes relacionados
[video_123_1634567890] Paso 5 completado en 0.45s
[video_123_1634567890] Proceso finalizado. Success: True, Duration: 60.60s
```

## Notificaciones

El sistema envía notificaciones detalladas al chat privado:

1. **Inicio del proceso** con información del video
2. **Progreso de cada paso** (1/5, 2/5, etc.)
3. **Reporte final** con métricas y estado

## Estructura de Archivos

```
src/video_management/
├── video_processor_advanced.py  # Procesador principal
├── video_downloader.py         # Descarga tradicional
├── video_forwarder.py          # Reenvío de videos pequeños
└── __init__.py                 # Exports del módulo
```

## Dependencias Adicionales

- **FFmpeg**: Para recorte de videos
- **ffmpeg-python**: Wrapper de Python para FFmpeg

## Troubleshooting

### Error: FFmpeg no encontrado
```bash
# Instalar FFmpeg en el contenedor
apt-get update && apt-get install -y ffmpeg
```

### Error: Sin espacio en disco
- El sistema limpia automáticamente archivos temporales
- Verificar espacio disponible en `/app/downloads`

### Error: No se puede eliminar mensaje
- Normal si el bot no tiene permisos de administrador
- El clip se envía correctamente de todas formas

## Performance

### Tiempos Típicos (video 500MB)
- Descarga: ~60-120s (dependiente del ancho de banda)
- Recorte: ~10-30s (dependiente del CPU)
- Envío: ~5-15s (dependiente del ancho de banda)
- Limpieza: <1s
- **Total**: ~75-165s

### Uso de Recursos
- **Almacenamiento**: 2x tamaño del video original (temporal)
- **CPU**: Alto durante recorte, bajo en otros momentos
- **RAM**: ~100-500MB durante procesamiento

## Seguridad

- Archivos temporales se eliminan automáticamente
- Solo el dueño del bot recibe los clips
- Logs no contienen información sensible
- Process IDs únicos para trazabilidad