from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass
class AgentMessage:
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str

class AgentCommunicationHub:
    def __init__(self):
        self.message_queue = []
        self.agent_registry = {}
    
    def register_agent(self, agent_id: str, agent_instance):
        """Register agent for communication"""
        self.agent_registry[agent_id] = agent_instance
    
    def send_message(self, message: AgentMessage):
        """Send message between agents"""
        self.message_queue.append(message)
        return self._route_message(message)
    
    def _route_message(self, message: AgentMessage):
        """Route message to target agent"""
        if message.receiver in self.agent_registry:
            return f"Message delivered to {message.receiver}"
        return f"Agent {message.receiver} not found"
    
    def broadcast(self, sender: str, content: Dict[str, Any]):
        """Broadcast message to all agents"""
        results = []
        for agent_id in self.agent_registry:
            if agent_id != sender:
                msg = AgentMessage(sender, agent_id, "broadcast", content, "")
                results.append(self.send_message(msg))
        return results