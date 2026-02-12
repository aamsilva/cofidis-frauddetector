"""
Cofidis Fraud Detector - Agents Package
"""
from .base_agent import BaseFraudAgent, RiskAssessment, AgentMessage
from .transaction_monitor import TransactionMonitorAgent
from .behavioral_analysis import BehavioralAnalysisAgent
from .risk_orchestrator import RiskOrchestrator

__all__ = [
    'BaseFraudAgent',
    'RiskAssessment',
    'AgentMessage',
    'TransactionMonitorAgent',
    'BehavioralAnalysisAgent',
    'RiskOrchestrator'
]
