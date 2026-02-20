"""
Message Class
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

class Message(ABC):
    """
    Message Base Class
    
    Args: message_id (int): The unique identifier for the message.
        message_id (int): The unique identifier for the message.
        content (Dict[str, Any], optional): The content of the message. Defaults to None.
    """
    def __init__(self, m_id: int, m_content: Dict[str, Any] = None):
        self.m_id = m_id #may not need this, if it is in m_content, but it is more convenient to have it as a separate attribute
        self.m_content = m_content
    @abstractmethod
    def execute(self) -> Optional[Dict[str, Any]]:
        """
        Execute the message and return the result.
        
        Returns:
            Dict for message requests and None for message responses. 
        """
        pass
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        
        Returns:
            A dictionary representation of the message.
        """
        return {
            "message_id": self.m_id,
            "content": self.m_content
        }
    
