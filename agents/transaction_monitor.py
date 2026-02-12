"""
Transaction Monitor Agent - Real-time transaction analysis
Detects velocity fraud, geographic impossibility, and amount anomalies
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseFraudAgent, RiskAssessment

class TransactionMonitorAgent(BaseFraudAgent):
    """
    Agent for real-time transaction monitoring
    Uses rule-based scoring + statistical anomaly detection
    """
    
    def __init__(self):
        super().__init__(
            name="transaction_monitor",
            description="Monitorização em tempo real de transações - velocity, geografia, valores",
            version="1.0"
        )
        # Transaction history cache (in production, use Redis)
        self.recent_transactions = {}  # customer_id -> list of transactions
        
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """
        Evaluate transaction risk
        """
        start_time = datetime.now()
        flags = []
        score = 0.0
        
        # Extract transaction data
        customer_id = transaction.get("customer_id")
        amount = transaction.get("amount", 0)
        timestamp = transaction.get("timestamp", datetime.now())
        location = transaction.get("location", {})
        merchant = transaction.get("merchant", "")
        card_type = transaction.get("card_type", "")
        
        # Get customer profile from context
        customer_profile = context.get("customer_profile", {}) if context else {}
        avg_transaction = customer_profile.get("avg_transaction_amount", 100)
        max_transaction = customer_profile.get("max_transaction_amount", 500)
        
        # Rule 1: Amount anomaly (high value transaction)
        if amount > max_transaction * 2:
            score += 25
            flags.append(f"HIGH_AMOUNT: €{amount} (2x above max)")
        elif amount > avg_transaction * 5:
            score += 15
            flags.append(f"HIGH_AMOUNT: €{amount} (5x above average)")
        
        # Rule 2: Velocity check (multiple transactions in short time)
        velocity_score = self._check_velocity(customer_id, timestamp)
        if velocity_score > 0:
            score += velocity_score
            flags.append("VELOCITY: Multiple transactions in short window")
        
        # Rule 3: Geographic impossibility
        geo_score = self._check_geographic_impossibility(customer_id, location, timestamp)
        if geo_score > 0:
            score += geo_score
            flags.append("GEO_IMPOSSIBLE: Location change too fast")
        
        # Rule 4: Time-based risk (unusual hours)
        time_score = self._check_time_risk(timestamp, customer_profile)
        if time_score > 0:
            score += time_score
            flags.append("TIME_RISK: Unusual transaction time")
        
        # Rule 5: Merchant risk
        merchant_score = self._check_merchant_risk(merchant, customer_profile)
        if merchant_score > 0:
            score += merchant_score
            flags.append("MERCHANT_RISK: High-risk merchant category")
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine action
        if score >= 70:
            action = "BLOCK"
        elif score >= 40:
            action = "REVIEW"
        else:
            action = "APPROVE"
        
        # Store transaction for future velocity checks
        self._store_transaction(customer_id, transaction)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=score,
            confidence=0.85 if flags else 0.6,
            flags=flags,
            explanation=self._generate_explanation(flags, score),
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
    
    def can_handle(self, transaction_type: str, context: Dict = None) -> float:
        """Can handle all transaction types"""
        return 0.95  # High confidence for all transactions
    
    def _check_velocity(self, customer_id: str, timestamp: datetime) -> float:
        """Check for velocity fraud (multiple transactions in short time)"""
        if not customer_id or customer_id not in self.recent_transactions:
            return 0.0
        
        recent = self.recent_transactions[customer_id]
        window_start = timestamp - timedelta(minutes=5)
        
        # Count transactions in last 5 minutes
        count = sum(1 for t in recent if t["timestamp"] > window_start)
        
        if count >= 5:
            return 30.0  # Very suspicious
        elif count >= 3:
            return 15.0  # Suspicious
        elif count >= 2:
            return 5.0   # Mild concern
        return 0.0
    
    def _check_geographic_impossibility(self, customer_id: str, location: Dict, timestamp: datetime) -> float:
        """Check if location change is physically impossible"""
        if not customer_id or customer_id not in self.recent_transactions:
            return 0.0
        
        recent = self.recent_transactions[customer_id]
        if not recent:
            return 0.0
        
        last_transaction = recent[-1]
        last_location = last_transaction.get("location", {})
        last_time = last_transaction.get("timestamp")
        
        if not last_location or not last_time:
            return 0.0
        
        # Calculate distance and time difference
        distance_km = self._calculate_distance(last_location, location)
        time_diff_hours = (timestamp - last_time).total_seconds() / 3600
        
        if time_diff_hours == 0:
            return 0.0
        
        # Speed = distance / time
        speed_kmh = distance_km / time_diff_hours
        
        # If speed > 900 km/h (faster than commercial flights), impossible
        if speed_kmh > 900:
            return 35.0
        # If speed > 300 km/h (faster than high-speed train), very suspicious
        elif speed_kmh > 300:
            return 20.0
        # If speed > 120 km/h (faster than car on highway), mildly suspicious
        elif speed_kmh > 120 and distance_km > 200:
            return 10.0
        
        return 0.0
    
    def _check_time_risk(self, timestamp: datetime, customer_profile: Dict) -> float:
        """Check if transaction time is unusual for customer"""
        hour = timestamp.hour
        
        # Risk hours: 00:00 - 05:00
        if 0 <= hour < 5:
            return 10.0
        
        # Check against customer's usual hours
        usual_hours = customer_profile.get("usual_transaction_hours", list(range(8, 23)))
        if hour not in usual_hours:
            return 8.0
        
        return 0.0
    
    def _check_merchant_risk(self, merchant: str, customer_profile: Dict) -> float:
        """Check merchant risk category"""
        high_risk_merchants = ["crypto", "gambling", "adult", "money_transfer"]
        
        merchant_lower = merchant.lower()
        for risk in high_risk_merchants:
            if risk in merchant_lower:
                return 15.0
        
        return 0.0
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two coordinates (simplified)"""
        # In production, use haversine formula
        lat1 = loc1.get("lat", 0)
        lon1 = loc1.get("lon", 0)
        lat2 = loc2.get("lat", 0)
        lon2 = loc2.get("lon", 0)
        
        # Simplified distance calculation
        return abs(lat1 - lat2) * 111 + abs(lon1 - lon2) * 111
    
    def _store_transaction(self, customer_id: str, transaction: Dict):
        """Store transaction for velocity checks"""
        if not customer_id:
            return
        
        if customer_id not in self.recent_transactions:
            self.recent_transactions[customer_id] = []
        
        self.recent_transactions[customer_id].append({
            "timestamp": transaction.get("timestamp", datetime.now()),
            "location": transaction.get("location", {}),
            "amount": transaction.get("amount", 0)
        })
        
        # Keep only last 24 hours of transactions
        cutoff = datetime.now() - timedelta(hours=24)
        self.recent_transactions[customer_id] = [
            t for t in self.recent_transactions[customer_id]
            if t["timestamp"] > cutoff
        ]
    
    def _generate_explanation(self, flags: List[str], score: float) -> str:
        """Generate human-readable explanation"""
        if not flags:
            return f"Transação dentro dos padrões normais (score: {score:.1f})"
        
        return f"Detetados {len(flags)} sinais de alerta: {', '.join(flags[:3])} (score: {score:.1f})"
