from src.handlers.link_handler import LinkHandler
from src.handlers.command_handler import CommandHandler

class HandlerRegistry:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.handlers = []

    def register_all_handlers(self):

        command_handler = CommandHandler(self.client, self.config)
        command_handler.register_commands()
        self.handlers.append(command_handler)

        """Register all event handlers."""
        link_handler = LinkHandler(self.client, self.config)
        link_handler.register_handlers()
        self.handlers.append(link_handler)
        
