import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.manager import DatabaseManager

async def show_stats():
    """Mostrar estadísticas de la base de datos"""
    db = DatabaseManager()
    
    try:
        stats = await db.get_message_statistics()
        
        print("📊 Estadísticas de Grande Bot")
        print("=" * 30)
        print(f"Total de mensajes procesados: {stats['total_messages']}")
        print("\nPor tipo de mensaje:")
        
        for msg_type, count in stats['by_type'].items():
            emoji = {
                'text': '📝',
                'video': '🎥',
                'animation': '🎬',
                'image': '🖼️',
                'sticker': '🎭'
            }.get(msg_type, '❓')
            
            print(f"  {emoji} {msg_type.capitalize()}: {count}")
        
        print("\n" + "=" * 30)
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")

if __name__ == '__main__':
    asyncio.run(show_stats())