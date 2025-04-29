from abc import ABC, abstractmethod
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
import logging

class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, bot: Client):
        self.bot = bot
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
        
    @abstractmethod
    async def handle_callback(self, callback_query: CallbackQuery) -> None:
        """Handle callback queries for this plugin"""
        pass
        
    @abstractmethod
    async def handle_command(self, message: Message) -> None:
        """Handle command messages for this plugin"""
        pass
        
    @abstractmethod
    def get_commands(self) -> list:
        """Return list of commands this plugin handles"""
        pass
        
    @abstractmethod 
    def get_callbacks(self) -> list:
        """Return list of callback patterns this plugin handles"""
        pass
        
    async def cleanup(self) -> None:
        """Cleanup any resources. Called when plugin is disabled."""
        pass 