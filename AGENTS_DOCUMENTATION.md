ação normal |
| 40-69 | **REVIEW** ⚠️ | Análise manual necessária |
| 70-100 | **BLOCK** ❌ | Fraude provável - rejeitar |

---

## 🔧 Integração

### API Endpoint
```http
POST /api/v1/fraud/evaluate
```

### Request
```json
{
  "transaction_id": "TXN-123",
  "customer_id": "CUST-456",
  "amount": 1500.00,
  "currency": "EUR",
  "merchant": "Store",
  "location": {"lat": 38.72, "lon": -9.14},
  "device_info": {...},
  "identity_data": {...}
}
```

### Response
```json
{
  "risk_score": 65.5,
  "recommended_action": "REVIEW",
  "flags": ["VELOCITY_HIGH", "NEW_MERCHANT"],
  "agent_breakdown": {
    "transaction_monitor": 45,
    "behavioral_analysis": 20,
    "identity_verification": 0,
    "anomaly_detection": 15,
    "device_fingerprint": 5
  }
}
```

---

## 🚀 Deployment

```bash
# Local
docker-compose up -d

# Cloud
kubectl apply -f k8s-deployment.yaml
```

---

**Documentação completa dos 5 agentes de deteção de fraude.**
*Última atualização: 2026-02-12*
