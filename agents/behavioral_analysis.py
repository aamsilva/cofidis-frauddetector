"""
Behavioral Analysis Agent - Analyzes customer behavior patterns
Detects deviations from established behavioral baselines
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from .base_agent import BaseFraudAgent, RiskAssessment

class BehavioralAnalysisAgent(BaseFraudAgent):
    """
    Agent for analyzing customer behavior patterns
    Detects when behavior deviates from established baselines
    """
    
    def __init__(self):
        super().__init__(
            name="behavioral_analysis",
            description="Análise comportamental - deteta desvios do perfil normal do cliente",
            version="1.0"
        )
        # Customer behavior profiles cache
        self.customer_profiles = {}
        
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """
        Evaluate transaction against customer's behavioral baseline
        """
        start_time = datetime.now()
        flags = []
        score = 0.0
        
        customer_id = transaction.get("customer_id")
        if not customer_id:
            return self._create_default_assessment("No customer ID provided")
        
        # Get or create customer profile
        profile = self._get_customer_profile(customer_id)
        
        # Check various behavioral aspects
        checks = [
            ("amount", self._check_amount_deviation(transaction, profile)),
            ("time", self._check_time_deviation(transaction, profile)),
            ("location", self._check_location_deviation(transaction, profile)),
            ("merchant", self._check_merchant_deviation(transaction, profile)),
            ("frequency", self._check_frequency_deviation(transaction, profile)),
            ("device", self._check_device_deviation(transaction, profile))
        ]
        
        for check_name, (check_score, check_flags) in checks:
            if check_score > 0:
                score += check_score
                flags.extend(check_flags)
        
        # Update profile with new transaction
        self._update_profile(customer_id, transaction)
        
        # Determine action
        if score >= 60:
            action = "BLOCK"
        elif score >= 30:
            action = "REVIEW"
        else:
            action = "APPROVE"
        
        # Cap score
        score = min(score, 100)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=score,
            confidence=0.80 if flags else 0.5,
            flags=flags,
            explanation=self._generate_explanation(flags, score, profile),
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
    
    def can_handle(self, transaction_type: str, context: Dict = None) -> float:
        """High confidence when customer profile exists"""
        if context and context.get("customer_profile"):
            return 0.9
        return 0.6
    
    def _get_customer_profile(self, customer_id: str) -> Dict:
        """Get or create customer behavioral profile"""
        if customer_id not in self.customer_profiles:
            # Create default profile
            self.customer_profiles[customer_id] = {
                "avg_amount": 100.0,
                "std_amount": 30.0,
                "usual_hours": list(range(8, 23)),
                "usual_locations": [],
                "usual_merchants": [],
                "transaction_count": 0,
                "devices": [],
                "created_at": datetime.now()
            }
        return self.customer_profiles[customer_id]
    
    def _update_profile(self, customer_id: str, transaction: Dict):
        """Update customer profile with new transaction data"""
        profile = self.customer_profiles[customer_id]
        
        # Update amount statistics (simple moving average)
        amount = transaction.get("amount", 0)
        n = profile["transaction_count"]
        profile["avg_amount"] = (profile["avg_amount"] * n + amount) / (n + 1)
        profile["transaction_count"] += 1
        
        # Update usual hours
        hour = transaction.get("timestamp", datetime.now()).hour
        if hour not in profile["usual_hours"]:
            profile["usual_hours"].append(hour)
        
        # Update locations (keep last 10)
        location = transaction.get("location")
        if location:
            profile["usual_locations"].append(location)
            profile["usual_locations"] = profile["usual_locations"][-10:]
        
        # Update merchants (keep unique, max 50)
        merchant = transaction.get("merchant", "")
        if merchant and merchant not in profile["usual_merchants"]:
            profile["usual_merchants"].append(merchant)
            profile["usual_merchants"] = profile["usual_merchants"][-50:]
    
    def _check_amount_deviation(self, transaction: Dict, profile: Dict) -> tuple:
        """Check if transaction amount deviates from customer's norm"""
        amount = transaction.get("amount", 0)
        avg = profile["avg_amount"]
        std = profile["std_amount"]
        
        if avg == 0:
            return 0, []
        
        # Calculate z-score
        z_score = abs(amount - avg) / std if std > 0 else 0
        
        if z_score > 5:  # > 5 standard deviations
            return 25, [f"AMOUNT_DEVIATION: €{amount} (5σ above average €{avg:.0f})"]
        elif z_score > 3:  # > 3 standard deviations
            return 15, [f"AMOUNT_DEVIATION: €{amount} (3σ above average)"]
        elif z_score > 2:
            return 5, [f"AMOUNT_DEVIATION: €{amount} (2σ above average)"]
        
        return 0, []
    
    def _check_time_deviation(self, transaction: Dict, profile: Dict) -> tuple:
        """Check if transaction time is unusual for customer"""
        timestamp = transaction.get("timestamp", datetime.now())
        hour = timestamp.hour
        
        usual_hours = profile.get("usual_hours", [])
        
        # Very unusual hours (3am - 6am)
        if 3 <= hour <= 6:
            return 20, [f"TIME_DEVIATION: Transaction at {hour:02d}:00 (unusual hour)"]
        
        # If we have history and this hour is not in usual hours
        if len(usual_hours) > 5 and hour not in usual_hours:
            return 10, [f"TIME_DEVIATION: {hour:02d}:00h not in customer's usual hours"]
        
        return 0, []
    
    def _check_location_deviation(self, transaction: Dict, profile: Dict) -> tuple:
        """Check if location is unusual"""
        location = transaction.get("location")
        usual_locations = profile.get("usual_locations", [])
        
        if not location or len(usual_locations) < 3:
            return 0, []
        
        # Calculate distance to nearest usual location
        min_distance = float('inf')
        for usual_loc in usual_locations:
            dist = self._calculate_distance(location, usual_loc)
            min_distance = min(min_distance, dist)
        
        if min_distance > 500:  # > 500km from usual locations
            return 20, [f"LOCATION_DEVIATION: {min_distance:.0f}km from usual locations"]
        elif min_distance > 100:  # > 100km
            return 8, [f"LOCATION_DEVIATION: {min_distance:.0f}km from usual locations"]
        
        return 0, []
    
    def _check_merchant_deviation(self, transaction: Dict, profile: Dict) -> tuple:
        """Check if merchant is new/unusual"""
        merchant = transaction.get("merchant", "")
        usual_merchants = profile.get("usual_merchants", [])
        
        if not merchant or len(usual_merchants) < 5:
            return 0, []
        
        if merchant not in usual_merchants:
            return 5, [f"NEW_MERCHANT: {merchant} (first time)"]
        
        return 0, []
    
    def _check_frequency_deviation(self, transaction: Dict, profile: Dict) -> tuple:
        """Check if transaction frequency is unusual"""
        # This would check for sudden spikes in transaction frequency
        # Simplified implementation
        return 0, []
    
    def _check_device_deviation(self, transaction: Dict, profile: Dict) -> tuple:
        """Check if device is new/unusual"""
        device_id = transaction.get("device_id", "")
        known_devices = profile.get("devices", [])
        
        if device_id and device_id not in known_devices:
            if len(known_devices) > 0:  # If customer has known devices
                return 10, ["NEW_DEVICE: Transaction from unrecognized device"]
        
        return 0, []
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two coordinates (simplified)"""
        lat1 = loc1.get("lat", 0)
        lon1 = loc1.get("lon", 0)
        lat2 = loc2.get("lat", 0)
        lon2 = loc2.get("lon", 0)
        
        # Simplified distance (not haversine, but sufficient for relative comparison)
        return abs(lat1 - lat2) * 111 + abs(lon1 - lon2) * 111
    
    def _generate_explanation(self, flags: List[str], score: float, profile: Dict) -> str:
        """Generate human-readable explanation"""
        if not flags:
            return f"Comportamento dentro do padrão normal do cliente (score: {score:.1f})"
        
        return f"Desvios comportamentais: {', '.join(flags[:3])} (score: {score:.1f})"
    
    def _create_default_assessment(self, reason: str) -> RiskAssessment:
        """Create default assessment when evaluation fails"""
        return RiskAssessment(
            score=0.0,
            confidence=0.0,
            flags=[],
            explanation=reason,
            recommended_action="APPROVE",
            timestamp=datetime.now(),
            agent_name=self.name
        )
