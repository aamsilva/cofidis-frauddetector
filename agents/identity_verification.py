"""
Identity Verification Agent - Advanced KYC and Identity Fraud Detection
"""
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseFraudAgent, RiskAssessment
import hashlib


class IdentityVerificationAgent(BaseFraudAgent):
    """Agent for advanced identity verification"""
    
    def __init__(self):
        super().__init__(
            name="identity_verification",
            description="Verificação avançada de identidade",
            version="1.0"
        )
        self.known_identities = {}
        
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """Evaluate identity risk"""
        start_time = datetime.now()
        flags = []
        score = 0.0
        
        identity_data = context.get("identity_data", {}) if context else {}
        
        if not identity_data:
            return RiskAssessment(
                score=0.0, confidence=0.0, flags=[],
                explanation="No identity data provided",
                recommended_action="APPROVE",
                timestamp=datetime.now(), agent_name=self.name
            )
        
        # Check document authenticity
        doc = identity_data.get("document", {})
        if doc.get("type") == "passport":
            if len(doc.get("number", "")) < 6:
                score += 20
                flags.append("INVALID_PASSPORT")
        
        # Check for expired document
        expiry = doc.get("expiry_date")
        if expiry:
            try:
                from datetime import datetime as dt
                if dt.fromisoformat(expiry) < dt.now():
                    score += 30
                    flags.append("EXPIRED_DOCUMENT")
            except:
                score += 15
                flags.append("INVALID_DATE")
        
        # Check biometrics
        bio = identity_data.get("biometric", {})
        if bio.get("face_match_score", 1.0) < 0.7:
            score += 30
            flags.append("FACE_MISMATCH")
        
        if bio.get("deepfake_detected", False):
            score += 50
            flags.append("DEEPFAKE_DETECTED")
        
        # Check data consistency
        doc_name = doc.get("name", "").lower()
        personal_name = identity_data.get("personal", {}).get("name", "").lower()
        if doc_name and personal_name and doc_name != personal_name:
            score += 25
            flags.append("NAME_MISMATCH")
        
        score = min(score, 100)
        
        if score >= 75:
            action = "BLOCK"
        elif score >= 40:
            action = "REVIEW"
        else:
            action = "APPROVE"
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=score,
            confidence=0.90 if flags else 0.6,
            flags=flags,
            explanation=f"Identity score: {score:.1f}" + (f" - Flags: {', '.join(flags[:3])}" if flags else ""),
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
