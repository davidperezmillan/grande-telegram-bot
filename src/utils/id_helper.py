from telethon.tl.types import User, Chat, Channel
from src.utils.logger import get_logger

logger = get_logger()

class IdHelper:
    """Clase auxiliar para obtener información de IDs de Telegram"""
    
    @staticmethod
    def get_chat_info(chat):
        """Obtener información básica de un chat"""
        info = {
            'id': chat.id,
            'type': 'unknown',
            'title': None,
            'username': None,
            'participants_count': None,
            'access_hash': getattr(chat, 'access_hash', None),
            'is_bot': False,
            'is_premium': False,
            'is_verified': False
        }
        
        if isinstance(chat, User):
            info['type'] = 'private'
            name_parts = []
            if chat.first_name:
                name_parts.append(chat.first_name)
            if chat.last_name:
                name_parts.append(chat.last_name)
            info['title'] = " ".join(name_parts) if name_parts else "Sin nombre"
            info['username'] = chat.username
            info['is_bot'] = getattr(chat, 'bot', False)
            info['is_premium'] = getattr(chat, 'premium', False)
            info['is_verified'] = getattr(chat, 'verified', False)
            
        elif isinstance(chat, Chat):
            info['type'] = 'group'
            info['title'] = chat.title
            info['participants_count'] = getattr(chat, 'participants_count', None)
            
        elif isinstance(chat, Channel):
            if chat.megagroup:
                info['type'] = 'supergroup'
            elif chat.broadcast:
                info['type'] = 'channel'
            else:
                info['type'] = 'channel_group'
            
            info['title'] = chat.title
            info['username'] = chat.username
            info['participants_count'] = getattr(chat, 'participants_count', None)
        
        return info
    
    @staticmethod
    def format_chat_info(chat_info):
        """Formatear información de chat para mostrar"""
        lines = []
        
        # Emoji según el tipo
        emoji_map = {
            'private': '👤',
            'group': '👥',
            'supergroup': '👥',
            'channel': '📢',
            'channel_group': '📂'
        }
        
        emoji = emoji_map.get(chat_info['type'], '❓')
        type_name = {
            'private': 'Conversación privada',
            'group': 'Grupo básico',
            'supergroup': 'Supergrupo',
            'channel': 'Canal',
            'channel_group': 'Canal/Grupo'
        }.get(chat_info['type'], 'Desconocido')
        
        lines.append(f"{emoji} **Tipo**: {type_name}")
        lines.append(f"🆔 **ID**: `{chat_info['id']}`")
        
        # Para supergrupos, mostrar también el ID público
        if chat_info['type'] == 'supergroup' and str(chat_info['id']).startswith('-100'):
            public_id = str(chat_info['id'])[4:]  # Remover -100
            lines.append(f"🆔 **ID público**: `{public_id}`")
        
        if chat_info['title']:
            lines.append(f"📝 **Título**: `{chat_info['title']}`")
        
        if chat_info['username']:
            lines.append(f"🔗 **Username**: @{chat_info['username']}")
        else:
            lines.append(f"🔗 **Username**: No disponible")
        
        if chat_info['participants_count']:
            lines.append(f"👥 **Miembros**: {chat_info['participants_count']}")
        
        # Información adicional para usuarios
        if chat_info['type'] == 'private':
            if chat_info['is_bot']:
                lines.append("🤖 **Es bot**: Sí")
            if chat_info['is_premium']:
                lines.append("⭐ **Premium**: Sí")
            if chat_info['is_verified']:
                lines.append("✅ **Verificado**: Sí")
        
        return "\n".join(lines)
    
    @staticmethod
    async def get_full_chat_info(client, chat_id):
        """Obtener información completa de un chat usando el cliente"""
        try:
            entity = await client.get_entity(chat_id)
            return IdHelper.get_chat_info(entity)
        except Exception as e:
            logger.error(f"Error obteniendo información del chat {chat_id}: {e}")
            return None
    
    @staticmethod
    def format_id_for_config(chat_info):
        """Formatear ID para usar en configuración"""
        config_lines = []
        config_lines.append(f"TARGET_GROUP_ID={chat_info['id']}")
        
        if chat_info['username']:
            config_lines.append(f"TARGET_GROUP_USERNAME={chat_info['username']}")
        else:
            config_lines.append(f"# TARGET_GROUP_USERNAME= (no disponible)")
        
        config_lines.append(f"# TIPO={chat_info['type'].upper()}")
        
        return "\n".join(config_lines)
    
    @staticmethod
    def is_group_or_channel(chat_info):
        """Verificar si es un grupo o canal (no conversación privada)"""
        return chat_info['type'] in ['group', 'supergroup', 'channel', 'channel_group']