"""
Message Class
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

class Message(ABC):
    """
    Message Base Class
    
    Args: message_id (str): The unique identifier for the message.
        message_id (str): The unique identifier for the message.
        content (Dict[str, Any], optional): The content of the message. Defaults to None.
        M_TYPE (str): m_type of message, class constant, to be defined in subclasses. Handle Error if not defined in constructor.
        _m_type (str): m_type of message, private instance variable, initialized to M_TYPE in constructor.
    """
    M_TYPE: str = None 
    def __init__(self, m_id: str, m_content: Dict[str, Any] = None):

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
    
class MessageResponse(Message):
    """
        Initialize response message.
        
        Args:
            m_id: Response message ID
            m_type: Response message type (e.g., 'get-nodes-response')
            responding_to: Original request message ID
            results: Dictionary containing query results
        
    Message Response does not have a fixed M_TYPE, (it can be either get-nodes-response or get-datum-response or others)
    """
    def __init__(self, m_id: str, responding_to: str, m_type: str, results: Dict[str, Any], m_content: Dict[str, Any] = None):
        self.responding_to = responding_to 
        self.results = results
        self.M_TYPE = m_type #override M_TYPE in constructor
        super().__init__(m_id, m_content)

    def execute(self):
        #Message Response does not execute
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for publishing"""
        return {
            "m_id": self.m_id,
            "m_type": self.m_type,
            "responding_to": self.responding_to,
            **self.results
        }
    

class MessageRequest(Message):
    def execute(self):
        #Note: Needs DB Manager instance
        pass