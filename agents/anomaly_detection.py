"""
Anomaly Detection Agent - ML-based fraud detection
"""
from typing import Dict, Any, List
from datetime import datetime
from collections import deque
import math
from .base_agent import BaseFraudAgent, RiskAssessment


class AnomalyDetectionAgent(BaseFraudAgent):
    """Agent for ML-based anomaly detection"""
    
    def __init__(self):
        super().__init__(
            name="anomaly_detection",
            description="Deteção de anomalias com ML",
            version="1.0"
        )
        self.transaction_history = {}
        
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """Evaluate using statistical anomaly detection"""
        start_time = datetime.now()
        flags = []
        score = 0.0
        
        customer_id = transaction.get("customer_id")
        if not customer_id or customer_id not in self.transaction_history:
            # First transaction - no baseline yet
            self._store_transaction(customer_id, transaction)
            return RiskAssessment(
                score=0.0, confidence=0.3, flags=[],
                explanation="Primeira transação - baseline em construção",
                recommended_action="APPROVE",
                timestamp=datetime.now(), agent_name=self.name
            )
        
        history = list(self.transaction_history[customer_id])
        if len(history) < 5:
            self._store_transaction(customer_id, transaction)
            return RiskAssessment(
                score=0.0, confidence=0.4, flags=[],
                explanation="Histórico insuficiente para análise",
                recommended_action="APPROVE",
                timestamp=datetime.now(), agent_name=self.name
            )
        
        # Calculate statistics
        amounts = [t["amount"] for t in history]
        mean = sum(amounts) / len(amounts)
        variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
        std = math.sqrt(variance) if variance > 0 else 1
        
        # Z-score for current transaction
        current_amount = transaction.get("amount", 0)
        z_score = abs(current_amount - mean) / std if std > 0 else 0
        
        if z_score > 5:
            score += 35
            flags.append(f"EXTREME_ZSCORE: {z_score:.1f}σ desvio")
        elif z_score > 3:
            score += 20
            flags.append(f"HIGH_ZSCORE: {z_score:.1f}σ desvio")
        elif z_score > 2:
            score += 8
            flags.append(f"ELEVATED_ZSCORE: {z_score:.1f}σ desvio")
        
        # Store for future
        self._store_transaction(customer_id, transaction)
        
        score = min(score, 100)
        action = "BLOCK" if score >= 70 else "REVIEW" if score >= 40 else "APPROVE"
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=score,
            confidence=0.8 if flags else 0.5,
            flags=flags,
            explanation=f"Z-score: {z_score:.2f} (média: €{mean:.0f}, σ: {std:.0f})" if flags else f"Dentro do padrão (z: {z_score:.2f})",
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
    
    def _store_transaction(self, customer_id: str, transaction: Dict):
        """Store transaction"""
        if not customer_id:
            return
        if customer_id not in self.transaction_history:
            self.transaction_history[customer_id] = deque(maxlen=1000)
        self.transaction_history[customer_id].append({
            "amount": transaction.get("amount", 0),
            "timestamp": transaction.get("timestamp", datetime.now())
        })
