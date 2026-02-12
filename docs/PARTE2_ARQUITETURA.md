# Parte 2: Arquitetura do Sistema

## 2.1 Visão Arquitetural

O Cofidis Fraud Detector segue uma arquitetura de orquestração distribuída onde cada agente é especialista numa dimensão específica do risco, trabalhando em conjunto através de um coordenador central.

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT REQUEST                        │
│              (Transaction Data + Context)                │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              RISK ORCHESTRATOR (API Gateway)            │
│         FastAPI - Coordenação e Agregação               │
│                                                         │
│  Responsabilidades:                                     │
│  • Recebe transação                                     │
│  • Distribui para agentes em paralelo                   │
│  • Agrega scores com pesos configuráveis                │
│  • Toma decisão final (APPROVE/REVIEW/BLOCK)            │
│  • Retorna explicação detalhada                         │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ TRANSACTION  │ │  BEHAVIORAL  │ │   IDENTITY   │
│   MONITOR    │ │   ANALYSIS   │ │ VERIFICATION │
│              │ │              │ │              │
│ • Velocity   │ │ • Z-score    │ │ • Documents  │
│ • Geography  │ │ • Profile    │ │ • Biometrics │
│ • Amount     │ │ • Deviation  │ │ • Deepfake   │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐        │
│   ANOMALY    │ │    DEVICE    │        │
│  DETECTION   │ │ FINGERPRINT  │        │
│   (ML)       │ │              │        │
│              │ │ • Device ID  │        │
│ • Isolation  │ │ • Emulator   │        │
│ • Z-score    │ │ • Browser    │        │
└──────────────┘ └──────────────┘        │
                                         │
                         ┌───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  RISK AGGREGATION                        │
│                                                         │
│  Score = Σ(AgentScore × Weight)                         │
│                                                         │
│  Weights:                                               │
│  • Transaction Monitor:    30%                          │
│  • Behavioral Analysis:    25%                          │
│  • Identity Verification:  20%                          │
│  • Anomaly Detection:      15%                          │
│  • Device Fingerprint:     10%                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 DECISION ENGINE                          │
│                                                         │
│  Score 0-39:   APPROVE ✅                               │
│  Score 40-69:  REVIEW  ⚠️  (Análise manual)             │
│  Score 70-100: BLOCK   ❌  (Rejeitar)                   │
│                                                         │
│  + Explicação detalhada                                 │
│  + Flags específicas                                    │
│  + Confiança (0-1)                                      │
└─────────────────────────────────────────────────────────┘
```

## 2.2 Fluxo de Dados

### Passo 1: Recepção da Transação
```python
POST /api/v1/fraud/evaluate
{
  "transaction_id": "TXN-2024-001",
  "customer_id": "CUST-12345",
  "amount": 1500.00,
  "currency": "EUR",
  "merchant": "Electronics Store",
  "location": {"lat": 38.7223, "lon": -9.1393},
  "timestamp": "2024-02-12T10:30:00",
  "device_info": {...},
  "identity_data": {...}
}
```

### Passo 2: Processamento Paralelo
O Risk Orchestrator envia a transação para todos os 5 agentes simultaneamente usando asyncio.gather():

```python
async def evaluate_transaction(transaction, context):
    tasks = [
        transaction_monitor.evaluate(transaction, context),
        behavioral_analysis.evaluate(transaction, context),
        identity_verification.evaluate(transaction, context),
        anomaly_detection.evaluate(transaction, context),
        device_fingerprint.evaluate(transaction, context)
    ]
    
    results = await asyncio.gather(*tasks)
    return aggregate_scores(results)
```

### Passo 3: Agregação de Scores
Cada agente retorna um RiskAssessment:
```python
@dataclass
class RiskAssessment:
    score: float           # 0-100
    confidence: float      # 0-1
    flags: List[str]       # ["VELOCITY_HIGH", "NEW_MERCHANT"]
    explanation: str       # "3 transações em 5 minutos"
    recommended_action: str # "REVIEW"
    agent_name: str        # "transaction_monitor"
```

O Orchestrator calcula o score final:
```python
def calculate_final_score(assessments):
    weights = {
        "transaction_monitor": 0.30,
        "behavioral_analysis": 0.25,
        "identity_verification": 0.20,
        "anomaly_detection": 0.15,
        "device_fingerprint": 0.10
    }
    
    final_score = sum(
        assessment.score * weights[assessment.agent_name]
        for assessment in assessments
    )
    
    return min(final_score, 100)  # Cap at 100
```

### Passo 4: Decisão e Resposta
```python
def make_decision(final_score):
    if final_score >= 70:
        return "BLOCK", "Fraude provável - múltiplos indicadores críticos"
    elif final_score >= 40:
        return "REVIEW", "Suspeita - requer análise manual"
    else:
        return "APPROVE", "Transação dentro dos padrões normais"
```

## 2.3 Comunicação Inter-Agente

### Padrão: Message Bus Interno

Os agentes não comunicam diretamente entre si. Toda a coordenação passa pelo Risk Orchestrator, que atua como message broker centralizado.

**Vantagens desta abordagem:**
- **Desacoplamento:** Agentes são independentes
- **Escalabilidade:** Cada agente pode escalar separadamente
- **Observabilidade:** Logs centralizados no Orchestrator
- **Resiliência:** Falha num agente não afeta os outros

### Exemplo de Comunicação

```
1. Orchestrator → Transaction Monitor: "Avalia esta transação"
2. Orchestrator → Behavioral Analysis: "Avalia esta transação"
3. [Paralelamente, todos os 5 agentes processam]
4. Transaction Monitor → Orchestrator: "Score: 45, Flags: [VELOCITY]"
5. Behavioral Analysis → Orchestrator: "Score: 20, Flags: []"
6. [... outros agentes ...]
7. Orchestrator: [Agrega e decide]
```

## 2.4 Modelo de Dados

### Entidades Principais

**Transaction (Transação)**
```python
{
  "transaction_id": UUID,
  "customer_id": String,
  "amount": Decimal,
  "currency": String (ISO 4217),
  "merchant": String,
  "merchant_category": String (MCC),
  "location": {
    "lat": Float,
    "lon": Float,
    "country": String,
    "city": String
  },
  "timestamp": DateTime (ISO 8601),
  "card_type": Enum [credit, debit, prepaid],
  "channel": Enum [online, pos, mobile, atm],
  "device_info": DeviceInfo,
  "identity_data": IdentityData
}
```

**RiskAssessment (Avaliação de Risco)**
```python
{
  "score": Float (0-100),
