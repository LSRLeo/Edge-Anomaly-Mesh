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
        M_TYPE (str): m_type of message, class constant, to be defined in subclasses. Handle Error if not defined in constructor.
        _m_type (str): m_type of message, private instance variable, initialized to M_TYPE in constructor.
    """
    M_TYPE: str = None 
    def __init__(self, m_id: int, m_content: Dict[str, Any] = None):

        if self.M_TYPE is None:
            raise NotImplementedError("M_TYPE must be defined in subclasses")
        
        self._m_type = self.M_TYPE #private
        self.m_id = m_id 
        self.m_content = m_content #
    @property
    def m_type(self) -> str:
        """Get the m_type of the message.""" 
        return self._m_type
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
        if self.m_content is None:
            return {
                "m_id": self.m_id,
                "m_type": self.m_type
            }
        return {
           **self.m_content 
        }
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(m_id='{self.m_id}', m_type='{self.m_type}')"
    
