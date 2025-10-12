from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl, MessageEntityMention
from src.utils.logger import get_logger

logger = get_logger()

class TextProcessor:
    def __init__(self):
        pass
    
    def process_text_message(self, message):
        """Procesar mensaje de texto"""
        text_info = {
            'content': message.text or '',
            'has_entities': bool(message.entities),
            'entities': [],
            'urls': [],
            'mentions': [],
            'hashtags': [],
            'analysis': {}
        }
        
        if message.entities:
            text_info['entities'] = self._extract_entities(message)
        
        # Análisis básico del texto
        text_info['analysis'] = self._analyze_text(text_info['content'])
        
        return text_info
    
    def _extract_entities(self, message):
        """Extraer entidades del mensaje"""
        entities = []
        
        for entity in message.entities:
            entity_info = {
                'type': type(entity).__name__,
                'offset': entity.offset,
                'length': entity.length,
                'text': message.text[entity.offset:entity.offset + entity.length]
            }
            
            # Información específica según el tipo de entidad
            if isinstance(entity, MessageEntityTextUrl):
                entity_info['url'] = entity.url
            elif isinstance(entity, MessageEntityUrl):
                entity_info['is_url'] = True
            elif isinstance(entity, MessageEntityMention):
                entity_info['is_mention'] = True
            
            entities.append(entity_info)
        
        return entities
    
    def _analyze_text(self, text):
        """Análisis básico del texto"""
        if not text:
            return {}
        
        analysis = {
            'length': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'has_links': any(url in text.lower() for url in ['http://', 'https://', 'www.']),
            'has_phone': self._contains_phone_number(text),
            'has_email': '@' in text and '.' in text,
            'language_hint': self._detect_language_hint(text)
        }
        
        return analysis
    
    def _contains_phone_number(self, text):
        """Detectar si el texto contiene números de teléfono"""
        import re
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        return bool(re.search(phone_pattern, text))
    
    def _detect_language_hint(self, text):
        """Detectar pistas del idioma (básico)"""
        spanish_words = ['que', 'para', 'con', 'una', 'por', 'como', 'sus', 'del', 'las']
        english_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can']
        
        text_lower = text.lower()
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if spanish_count > english_count:
            return 'spanish'
        elif english_count > spanish_count:
            return 'english'
        else:
            return 'unknown'
    
    def should_process_text(self, text_info):
        """Determinar si el texto debe ser procesado especialmente"""
        analysis = text_info['analysis']
        
        # Criterios para procesamiento especial
        reasons = []
        
        if analysis.get('has_links'):
            reasons.append("contiene enlaces")
        
        if analysis.get('has_phone'):
            reasons.append("contiene números de teléfono")
        
        if analysis.get('word_count', 0) > 100:
            reasons.append("texto largo")
        
        if analysis.get('has_email'):
            reasons.append("contiene email")
        
        return len(reasons) > 0, reasons