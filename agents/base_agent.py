"""
Base Agent Class for Cofidis Fraud Detection System
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class AgentMessage:
    """Message format for inter-agent communication"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: str  # "request", "response", "alert", "notification"
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

@dataclass
class RiskAssessment:
    """Risk assessment result"""
    score: float  # 0-100
    confidence: float  # 0-1
    flags: List[str]
    explanation: str
    recommended_action: str  # "APPROVE", "REVIEW", "BLOCK"
    timestamp: datetime
    agent_name: str

class BaseFraudAgent(ABC):
    """
    Base class for all fraud detection agents
    """
    
    def __init__(self, name: str, description: str, version: str = "1.0"):
        self.name = name
        self.description = description
        self.version = version
        self.message_bus = None
        self.metrics = {
            "requests_processed": 0,
            "alerts_generated": 0,
            "avg_processing_time_ms": 0
        }
        
    @abstractmethod
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """
        Main evaluation method - must be implemented by subclasses
        
        Args:
            transaction: Transaction data
            context: Additional context (customer profile, history, etc.)
            
        Returns:
            RiskAssessment with score and recommendations
        """
        pass
    
    def can_handle(self, transaction_type: str, context: Dict = None) -> float:
        """
        Returns confidence score (0.0-1.0) for handling this transaction type
        Override in subclasses for specific logic
        """
        return 0.5  # Default medium confidence
    
    def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents"""
        if message.message_type == "request":
            return self._handle_request(message)
        elif message.message_type == "alert":
            self._handle_alert(message)
        return None
    
    def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Override to handle specific requests"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.name,
            to_agent=message.from_agent,
            message_type="response",
            payload={"status": "not_implemented"},
            timestamp=datetime.now(),
            priority=1
        )
    
    def _handle_alert(self, message: AgentMessage):
        """Override to handle alerts"""
        pass
    
    def send_message(self, to_agent: str, message_type: str, payload: Dict, priority: int = 1):
        """Send message to another agent"""
        if self.message_bus:
            message = AgentMessage(
                message_id=str(uuid.uuid4()),
                from_agent=self.name,
                to_agent=to_agent,
                message_type=message_type,
                payload=payload,
                timestamp=datetime.now(),
                priority=priority
            )
            self.message_bus.route_message(message)
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent metadata"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "metrics": self.metrics,
            "status": "active"
        }
    
    def update_metrics(self, processing_time_ms: float):
        """Update agent metrics"""
        self.metrics["requests_processed"] += 1
        # Update average processing time
        n = self.metrics["requests_processed"]
        old_avg = self.metrics["avg_processing_time_ms"]
        self.metrics["avg_processing_time_ms"] = (old_avg * (n-1) + processing_time_ms) / n
