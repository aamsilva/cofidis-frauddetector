"""
Cofidis Fraud Detector - API Gateway
FastAPI application exposing fraud detection endpoints
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uvicorn

# Import agents
from agents.transaction_monitor import TransactionMonitorAgent
from agents.behavioral_analysis import BehavioralAnalysisAgent
from agents.identity_verification import IdentityVerificationAgent
from agents.risk_orchestrator import RiskOrchestrator

app = FastAPI(
    title="Cofidis Fraud Detector",
    description="Multi-Agent System for Real-time Fraud Detection",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system
orchestrator = RiskOrchestrator()

# Create agents
transaction_monitor = TransactionMonitorAgent()
behavioral_analysis = BehavioralAnalysisAgent()
identity_verification = IdentityVerificationAgent()

# Register all agents
orchestrator.register_agent(transaction_monitor)
orchestrator.register_agent(behavioral_analysis)
orchestrator.register_agent(identity_verification)

print(f"📊 Registered agents: {list(orchestrator.agents.keys())}")

print("🚀 Cofidis Fraud Detector initialized!")
print(f"📊 Registered agents: {list(orchestrator.agents.keys())}")

# Request/Response Models
class TransactionRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID")
    customer_id: str = Field(..., description="Customer identifier")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="EUR", description="Currency code")
    merchant: str = Field(..., description="Merchant name")
    merchant_category: str = Field(default="", description="Merchant category")
    location: Dict[str, float] = Field(default={}, description="Location {lat, lon}")
    timestamp: datetime = Field(default_factory=datetime.now)
    card_type: str = Field(default="credit", description="Card type")
    channel: str = Field(default="online", description="Transaction channel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-2024-001",
                "customer_id": "CUST-12345",
                "amount": 150.00,
                "currency": "EUR",
                "merchant": "Amazon",
                "merchant_category": "e-commerce",
                "location": {"lat": 38.7223, "lon": -9.1393},
                "timestamp": "2024-02-12T10:30:00",
                "card_type": "credit",
                "channel": "online"
            }
        }

class FraudAssessmentResponse(BaseModel):
    transaction_id: str
    customer_id: str
    risk_score: float = Field(..., description="Risk score 0-100")
    confidence: float = Field(..., description="Confidence 0-1")
    recommended_action: str = Field(..., description="APPROVE/REVIEW/BLOCK")
    flags: List[str] = Field(default=[], description="Risk flags detected")
    explanation: str = Field(..., description="Human-readable explanation")
    processing_time_ms: float
    timestamp: datetime
    agent_breakdown: Optional[Dict[str, Any]] = None

class CustomerProfile(BaseModel):
    customer_id: str
    avg_transaction_amount: float = 100.0
    max_transaction_amount: float = 500.0
    usual_transaction_hours: List[int] = list(range(8, 23))
    typical_locations: List[Dict[str, float]] = []
    risk_level: str = "low"  # low, medium, high

# API Endpoints

@app.get("/")
def root():
    """Root endpoint - system info"""
    return {
        "service": "Cofidis Fraud Detector",
        "version": "1.0.0",
        "status": "operational",
        "agents": orchestrator.get_system_status(),
        "endpoints": {
            "evaluate": "/api/v1/fraud/evaluate",
            "health": "/health",
            "status": "/status"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_online": len(orchestrator.agents),
        "version": "1.0.0"
    }

@app.get("/status")
def system_status():
    """Detailed system status"""
    return orchestrator.get_system_status()

@app.post("/api/v1/fraud/evaluate", response_model=FraudAssessmentResponse)
def evaluate_transaction(
    transaction: TransactionRequest,
    background_tasks: BackgroundTasks
):
    """
    Evaluate a transaction for fraud risk
    
    Returns risk assessment with score, flags, and recommended action
    """
    try:
        start_time = datetime.now()
        
        # Build customer profile (in production, fetch from database)
        customer_profile = {
            "avg_transaction_amount": 100.0,
            "max_transaction_amount": 500.0,
            "usual_transaction_hours": list(range(8, 23))
        }
        
        # Convert request to dict for evaluation
        transaction_dict = transaction.model_dump()
        context = {"customer_profile": customer_profile}
        
        # Evaluate
        assessment = orchestrator.evaluate(transaction_dict, context)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return FraudAssessmentResponse(
            transaction_id=transaction.transaction_id,
            customer_id=transaction.customer_id,
            risk_score=assessment.score,
            confidence=assessment.confidence,
            recommended_action=assessment.recommended_action,
            flags=assessment.flags,
            explanation=assessment.explanation,
            processing_time_ms=processing_time,
            timestamp=assessment.timestamp,
            agent_breakdown={
                "agents_evaluated": len(orchestrator.agents),
                "primary_agent": "risk_orchestrator"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fraud/evaluate-batch")
def evaluate_batch(transactions: List[TransactionRequest]):
    """
    Evaluate multiple transactions in batch
    """
    results = []
    for txn in transactions:
        try:
            assessment = orchestrator.evaluate(txn.model_dump(), {})
            results.append({
                "transaction_id": txn.transaction_id,
                "risk_score": assessment.score,
                "action": assessment.recommended_action
            })
        except Exception as e:
            results.append({
                "transaction_id": txn.transaction_id,
                "error": str(e)
            })
    
    return {"results": results, "total": len(results)}

@app.get("/api/v1/customer/{customer_id}/profile")
def get_customer_profile(customer_id: str):
    """
    Get customer risk profile
    """
    # In production, fetch from database
    return {
        "customer_id": customer_id,
        "risk_level": "low",
        "avg_transaction_amount": 100.0,
        "total_transactions": 150,
        "fraud_history": False,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/fraud/cases")
def get_fraud_cases(
    status: Optional[str] = "open",
    limit: int = 50,
    offset: int = 0
):
    """
    Get fraud cases for investigation
    """
    # In production, fetch from database
    return {
        "cases": [],
        "total": 0,
        "status": status,
        "limit": limit,
        "offset": offset
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
