import os

class Config:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.user_id = int(os.getenv('USER_ID'))
        
        # Validar que todas las variables estén presentes
        if not all([self.bot_token, self.api_id, self.api_hash, self.user_id]):
            raise ValueError("Faltan variables de entorno requeridas: BOT_TOKEN, API_ID, API_HASH, USER_ID")