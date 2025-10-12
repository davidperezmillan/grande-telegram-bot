from src.processors.base_processor import BaseProcessor

class MessageTextProcessor(BaseProcessor):
    """Procesador de mensajes de texto"""
    
    async def process(self, message, message_data):
        """Procesar mensaje de texto"""
        text_info = self.text_processor.process_text_message(message)
        message_data['content'] = text_info['content']
        
        should_process, reasons = self.text_processor.should_process_text(text_info)
        
        if should_process:
            self.log_info(f"Texto requiere procesamiento especial: {', '.join(reasons)}")
            # Aquí implementarías la lógica específica para textos especiales
            return f"texto procesado - {', '.join(reasons)}"
        else:
            return "texto normal - sin acción especial"