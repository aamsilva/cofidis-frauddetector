"""
Risk Orchestrator - Coordinates all fraud detection agents
Aggregates risk scores and makes final decisions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseFraudAgent, RiskAssessment, AgentMessage

class RiskOrchestrator(BaseFraudAgent):
    """
    Central orchestrator that coordinates all fraud detection agents
    Aggregates scores and makes final risk decisions
    """
    
    def __init__(self):
        super().__init__(
            name="risk_orchestrator",
            description="Orquestrador central - agrega scores e decide ação final",
            version="1.0"
        )
        self.agents = {}
        self.weights = {
            "transaction_monitor": 0.30,
            "behavioral_analysis": 0.25,
            "identity_verification": 0.20,
            "anomaly_detection": 0.15,
            "external_intelligence": 0.10
        }
        
    def register_agent(self, agent: BaseFraudAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        agent.message_bus = self
        print(f"✅ Agent registered: {agent.name}")
    
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """
        Orchestrate evaluation across all agents and make final decision
        """
        start_time = datetime.now()
        context = context or {}
        
        # Collect assessments from all agents
        assessments = []
        agent_results = {}
        
        for name, agent in self.agents.items():
            try:
                assessment = agent.evaluate(transaction, context)
                assessments.append(assessment)
                agent_results[name] = assessment
                
                # If any agent returns critical score, short-circuit
                if assessment.score >= 90:
                    return self._create_final_assessment(
                        agent_results, 
                        "BLOCK",
                        f"Score crítico detetado por {name}",
                        start_time
                    )
                    
            except Exception as e:
                print(f"Error in agent {name}: {e}")
                continue
        
        # Calculate weighted aggregate score
        final_score = self._calculate_weighted_score(agent_results)
        
        # Collect all flags
        all_flags = []
        for assessment in assessments:
            all_flags.extend(assessment.flags)
        
        # Determine final action
        if final_score >= 75:
            action = "BLOCK"
        elif final_score >= 45:
            action = "REVIEW"
        else:
            action = "APPROVE"
        
        # Generate comprehensive explanation
        explanation = self._generate_final_explanation(agent_results, final_score)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=final_score,
            confidence=self._calculate_confidence(assessments),
            flags=list(set(all_flags)),  # Remove duplicates
            explanation=explanation,
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
    
    def _calculate_weighted_score(self, agent_results: Dict[str, RiskAssessment]) -> float:
        """Calculate weighted aggregate score"""
        total_score = 0.0
        total_weight = 0.0
        
        for agent_name, assessment in agent_results.items():
            weight = self.weights.get(agent_name, 0.1)
            total_score += assessment.score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(total_score / total_weight, 100.0)
    
    def _calculate_confidence(self, assessments: List[RiskAssessment]) -> float:
        """Calculate aggregate confidence"""
        if not assessments:
            return 0.0
        
        # Average confidence weighted by score (higher scores = more confident)
        total_confidence = sum(a.confidence * a.score for a in assessments)
        total_score = sum(a.score for a in assessments)
        
        if total_score == 0:
            return 0.5
        
        return min(total_confidence / total_score, 1.0)
    
    def _create_final_assessment(self, agent_results: Dict, action: str, reason: str, start_time: datetime) -> RiskAssessment:
        """Create final assessment (for short-circuit cases)"""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=95.0,
            confidence=0.95,
            flags=["CRITICAL_RISK", reason],
            explanation=f"Ação imediata necessária: {reason}",
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
    
    def _generate_final_explanation(self, agent_results: Dict[str, RiskAssessment], final_score: float) -> str:
        """Generate comprehensive explanation"""
        explanations = []
        
        for agent_name, assessment in agent_results.items():
            if assessment.score > 20:  # Only include significant scores
                explanations.append(f"{agent_name}: {assessment.score:.0f}/100 - {assessment.explanation[:100]}")
        
        if not explanations:
            return f"Transação aprovada - score agregado: {final_score:.1f}/100"
        
        return f"Score agregado: {final_score:.1f}/100. " + " | ".join(explanations[:3])
    
    def route_message(self, message: AgentMessage):
        """Route messages between agents"""
        if message.to_agent in self.agents:
            target_agent = self.agents[message.to_agent]
            response = target_agent.receive_message(message)
            
            if response and message.message_type == "request":
                # Send response back
                self._send_response(message.from_agent, response)
    
    def _send_response(self, to_agent: str, response: AgentMessage):
        """Send response back to requesting agent"""
        if to_agent in self.agents:
            self.agents[to_agent].receive_message(response)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "orchestrator": self.get_info(),
            "registered_agents": [agent.get_info() for agent in self.agents.values()],
            "total_agents": len(self.agents),
            "weights": self.weights
        }
