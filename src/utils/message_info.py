class MessageInfo:
    def __init__(self, message):
        self.message = message

    def get_chat_id(self):
        """Devuelve el ID del chat."""
        return self.message.chat_id

    def get_chat_type(self):
        """Devuelve el tipo de chat: private, group, supergroup, channel."""
        if self.message.is_private:
            return 'private'
        elif self.message.is_group:
            return 'group'
        elif self.message.is_channel:
            return 'channel'
        else:
            return 'unknown'

    def is_forwarded(self):
        """Devuelve True si el mensaje está reenviado."""
        return self.message.forward is not None

    def get_forward_info(self):
        """Devuelve información del reenvío si aplica."""
        if not self.is_forwarded():
            return None
        
        forward = self.message.forward
        return {
            'original_sender_id': forward.sender_id,
            'original_chat_id': forward.chat_id,
            'original_message_id': forward.message_id,
            'original_date': forward.date,
            'from_chat_title': getattr(forward.chat, 'title', 'Unknown') if forward.chat else 'Unknown'
        }

    def get_sender_info(self):
        """Devuelve información del remitente."""
        sender = self.message.sender
        if sender:
            return {
                'id': sender.id,
                'username': sender.username,
                'first_name': sender.first_name,
                'last_name': sender.last_name
            }
        return None

    def get_summary_text(self):
        """Devuelve un resumen en texto para enviar como mensaje."""
        summary = self.get_summary()
        text = f"📍 **Información del Chat:**\n"
        text += f"ID: `{summary['chat_id']}`\n"
        text += f"Tipo: {summary['chat_type']}\n\n"
        
        if summary['sender_info']:
            sender = summary['sender_info']
            text += f"👤 **Remitente:**\n"
            text += f"ID: `{sender['id']}`\n"
            if sender['username']:
                text += f"Username: @{sender['username']}\n"
            if sender['first_name']:
                text += f"Nombre: {sender['first_name']}\n"
            if sender['last_name']:
                text += f"Apellido: {sender['last_name']}\n"
            text += "\n"
        
        if summary['is_forwarded']:
            forward = summary['forward_info']
            text += f"🔄 **Mensaje Reenviado:**\n"
            text += f"ID Remitente Original: `{forward['original_sender_id']}`\n"
            text += f"ID Chat Original: `{forward['original_chat_id']}`\n"
            text += f"ID Mensaje Original: `{forward['original_message_id']}`\n"
            text += f"De: {forward['from_chat_title']}\n"
            text += f"Fecha: {forward['original_date']}\n"
        else:
            text += "✅ **Mensaje Original** (no reenviado)\n"
        
        return text

    def get_summary(self):
        """Devuelve un resumen completo de la información del mensaje."""
        return {
            'chat_id': self.get_chat_id(),
            'chat_type': self.get_chat_type(),
            'is_forwarded': self.is_forwarded(),
            'forward_info': self.get_forward_info(),
            'sender_info': self.get_sender_info()
        }