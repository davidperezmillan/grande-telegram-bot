# Grande Bot - Bot de Telegram con Telethon

Bot de Telegram desarrollado con Telethon para monitorear y procesar mensajes de grupos específicos.

## Características

- **Monitoreo de grupos**: Lee todos los mensajes de un grupo específico
- **Procesamiento por tipo**: Maneja texto, videos, animaciones, imágenes y stickers
- **Detección de archivos grandes**: Identifica y descarga videos >20MB automáticamente
- **Base de datos persistente**: Almacena IDs de mensajes y respuestas del bot
- **Arquitectura modular**: Código bien estructurado y reutilizable
- **Logs completos**: Sistema de logging con rotación de archivos
- **Comandos integrados**: `/id`, `/start`, `/help` para gestión
- **Dockerizado**: Fácil despliegue con Docker Compose

## Estructura del Proyecto

```
grande_bot/
├── main.py                     # Punto de entrada del bot
├── Dockerfile                  # Configuración de Docker
├── docker-compose.yml          # Orquestación de contenedores
├── requirements.txt            # Dependencias Python
├── .env.example               # Variables de entorno ejemplo
├── src/
│   ├── handlers/
│   │   └── message_handler.py # Manejador principal de mensajes
│   ├── database/
│   │   ├── models.py          # Modelos de base de datos
│   │   └── manager.py         # Gestor de base de datos
│   └── utils/
│       ├── file_handler.py    # Manejo de archivos
│       ├── text_processor.py  # Procesamiento de texto
│       └── logger.py          # Sistema de logging
├── data/                      # Base de datos SQLite
├── logs/                      # Archivos de log
└── downloads/                 # Archivos descargados
```

## Instalación y Configuración

### 1. Clonar y configurar

```bash
cd grande_bot
cp .env.example .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env`:

```env
# Credenciales de API de Telegram (desde https://my.telegram.org)
API_ID=your_api_id
API_HASH=your_api_hash

# Token del bot (desde @BotFather)
BOT_TOKEN=your_bot_token

# Grupo objetivo (ID numérico o username)
TARGET_GROUP_ID=-1001234567890
TARGET_GROUP_USERNAME=your_group_username

# Configuración
MAX_FILE_SIZE_MB=20
LOG_LEVEL=INFO
```

### **4. Obtener IDs para configuración**

Usa el comando `/id` del bot para obtener los IDs necesarios:

```bash
# En Telegram, envía a tu bot:
/id

# El bot te responderá con algo como:
# PARA COPIAR EN .ENV
# TARGET_GROUP_ID=-1001234567890
# TARGET_GROUP_USERNAME=mi_grupo
```

### **5. Construir y ejecutar**

```bash
docker-compose up -d
```

### **6. Ver logs**
```

### 4. Ver logs

```bash
docker-compose logs -f grande-bot
```

## 🤖 Comandos Disponibles

Grande Bot incluye comandos útiles para obtener información:

- **`/id`**: Obtiene información completa de IDs (chat, usuario, mensaje)
- **`/start`**: Mensaje de bienvenida y funcionalidades
- **`/help`**: Ayuda detallada del bot

> 📖 Ver documentación completa en [COMANDOS.md](COMANDOS.md)

## Funcionalidades por Tipo de Mensaje

### 📝 Texto
- **Actual**: Detecta enlaces, emails, teléfonos, texto largo
- **Por definir**: Acciones específicas según el contenido

### 🎥 Video
- **Actual**: Descarga automáticamente si >20MB
- **Por definir**: Procesamiento adicional de videos grandes

### 🎬 Animaciones/GIF
- **Actual**: Detecta y registra tamaño
- **Por definir**: Lógica de procesamiento específica

### 🖼️ Imágenes
- **Actual**: Detecta y registra información básica
- **Por definir**: Análisis de contenido, OCR, etc.

### 🎭 Stickers
- **Actual**: Detecta stickers
- **Por definir**: Categorización, estadísticas de uso

## Base de Datos

El bot utiliza SQLite con las siguientes tablas:

- **processed_messages**: Todos los mensajes procesados
- **bot_responses**: Respuestas enviadas por el bot
- **message_queue**: Cola de mensajes pendientes

## Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar el bot
docker-compose restart

# Entrar al contenedor
docker-compose exec grande-bot bash

# Ver estadísticas de la base de datos
sqlite3 data/bot_data.db "SELECT message_type, COUNT(*) FROM processed_messages GROUP BY message_type;"
```

## Desarrollo

### Añadir nueva funcionalidad

1. **Para nuevo tipo de mensaje**: Modificar `MessageHandler._process_by_type()`
2. **Para nuevo procesador**: Crear clase en `src/utils/`
3. **Para nueva tabla**: Añadir modelo en `src/database/models.py`

### Estructura de clases principales

- **GrandeBot**: Clase principal, maneja conexión y eventos
- **MessageHandler**: Procesa todos los tipos de mensajes
- **DatabaseManager**: Gestiona operaciones de BD
- **FileHandler**: Maneja descarga y análisis de archivos
- **TextProcessor**: Procesa y analiza texto

## Próximas Mejoras

- [ ] Definir acciones específicas para cada tipo de contenido
- [ ] Sistema de respuestas automáticas
- [ ] Dashboard web para estadísticas
- [ ] Integración con APIs externas
- [ ] Sistema de notificaciones
- [ ] Backup automático de base de datos

## Troubleshooting

### Error de conexión
- Verificar API_ID, API_HASH y BOT_TOKEN
- Asegurar que el bot esté en el grupo objetivo

### Error de permisos
- El bot necesita permisos de lectura en el grupo
- Verificar que TARGET_GROUP_ID sea correcto

### Error de espacio
- Limpiar directorio `downloads/` periódicamente
- Ajustar `MAX_FILE_SIZE_MB` según necesidades