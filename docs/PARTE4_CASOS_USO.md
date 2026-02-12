# Parte 4: Casos de Uso com Personas

## 4.1 JOÃO - Ataque Velocity (Cartão Clonado)

### Perfil do Cliente
- **Nome:** João Silva
- **Idade:** 45 anos
- **Perfil:** Cliente habitual há 3 anos
- **Padrão:** 1-2 compras/semana, valores €50-200
- **Localização:** Lisboa, Portugal
- **Dispositivo:** iPhone habitual

### O Incidente
**Data:** Sábado, 14:30
**Sequência:**
1. 14:30:05 - Compra online €500 (Loja A)
2. 14:30:45 - Compra online €500 (Loja B)
3. 14:31:20 - Compra online €500 (Loja C)
4. 14:32:10 - Compra online €500 (Loja D)
5. 14:32:45 - Compra online €500 (Loja E)
6. 14:33:30 - Compra online €500 (Loja F)

**Total:** 6 transações em 3 minutos = €3,000

### Deteção pelo Sistema

#### Transaction Monitor
```
VELOCITY_CRITICAL: 6 transações em 3 minutos
Score: +30 pontos
Recomendação: BLOCK
```

#### Behavioral Analysis
```
ZSCORE_EXTREME: Valor €500 vs média €125 (Z=25σ)
Score: +25 pontos
Recomendação: REVIEW
```

#### Device Fingerprint
```
Dispositivo reconhecido (iPhone habitual)
Score: 0 pontos
Recomendação: APPROVE
```

#### Risk Orchestrator - Decisão Final
```
Score Final: 30×0.30 + 25×0.25 + 0×0.10 = 15.25
                    ↓
Transações 3-6: BLOCK imediato
Transações 1-2: APPROVE (já processadas)
```

### Resultado
- ✅ **4 transações bloqueadas** (€2,000 salvos)
- ✅ **Análise manual confirma:** Cartão clonado
- ✅ **Cliente notificado** em 30 segundos
- ✅ **Novo cartão emitido** em 24h

### Porque Funcionou
O sistema detetou o padrão de velocidade impossível (6 compras em 3 min) combinado com valores atípicos para o perfil do cliente. A deteção em tempo real permitiu bloqueio imediato, minimizando perdas.

---

## 4.2 MARIA - Viagem Impossível (Conta Comprometida)

### Perfil do Cliente
- **Nome:** Maria Santos
- **Idade:** 38 anos
- **Perfil:** Cliente há 5 anos, nunca viajou fora de Portugal
- **Padrão:** Compras diárias em Lisboa, valores €20-100
- **Dispositivo:** Samsung Galaxy habitual

### O Incidente
**Sequência:**
1. **14:00** - Compra supermercado €85, Lisboa (38.72, -9.14)
2. **14:35** - Tentativa de compra €3,200, Nova Iorque (40.71, -74.01)

**Intervalo:** 35 minutos
**Distância:** 5,427 km

### Deteção pelo Sistema

#### Transaction Monitor
```
GEO_IMPOSSIBLE: 5,427 km em 35 min = 9,303 km/h
Score: +35 pontos (BLOCK)
Recomendação: BLOCK

VELOCITY: 2 transações em 35 min (normal)
Score: +5 pontos
```

#### Behavioral Analysis
```
LOCATION_FAR: 5,427 km do padrão habitual
Score: +20 pontos

TIME_DEVIATION: Transação 14:35 (dentro do normal)
Score: 0 pontos
```

#### Risk Orchestrator - Decisão Final
```
Score Final: 35×0.30 + 20×0.25 + 5×0.30 = 17.0
                    ↓
Decisão: BLOCK automático
Motivo: "Viagem fisicamente impossível"
```

### Resultado
- ✅ **Transação NY bloqueada** (€3,200 salvos)
- ✅ **Conta temporariamente suspensa**
- ✅ **Contacto telefónico com Maria**
- ✅ **Maria confirma:** Não fez a transação
- ✅ **Conta recuperada, password alterada**

### Porque Funcionou
A análise geográfica detetou velocidade impossível (9,303 km/h). Mesmo sem padrão de velocity, a geo-impossibilidade foi suficiente para BLOCK imediato. A combinação com desvio de localização elevou o score para nível crítico.

---

## 4.3 PEDRO - Valor Atípico (Compra Inusitada)

### Perfil do Cliente
- **Nome:** Pedro Costa
- **Idade:** 22 anos
- **Perfil:** Estudante universitário
- **Padrão:** Compras €15-30, máximo histórico €150 (livros)
- **Horário habitual:** 10:00-20:00

### O Incidente
**Data:** Terça-feira, 03:15 da madrugada
**Transação:** Joalharia online €8,000

### Deteção pelo Sistema

#### Behavioral Analysis
```
ZSCORE_EXTREME: €8,000 vs média €25 (desvio €15)
Z-score = (8000-25)/15 = 531σ
Score: +25 pontos (EXTREME)
```

#### Transaction Monitor
```
TIME_NIGHT_RISK: Transação às 03:15
Score: +20 pontos

AMOUNT_HIGH: >5x valor médio
Score: +15 pontos

MERCHANT_HIGH_RISK: Joalharia (categoria luxo)
Score: +5 pontos
```

#### Risk Orchestrator - Decisão Final
```
Score Final: 25×0.25 + 20×0.30 + 15×0.30 + 5×0.05 = 17.0
                    ↓
Decisão: BLOCK
Motivo: "Valor extremamente atípico + hora suspeita"
```

### Resultado
- ✅ **Transação bloqueada** (€8,000 salvos)
- ✅ **SMS enviado para Pedro:** "Transação suspeita detetada"
- ✅ **Pedro responde:** "Não fui eu"
- ✅ **Investigação:** Cartão clonado em ATM
- ✅ **Novo cartão emitido**

### Porque Funcionou
O Z-score estatístico (531σ) tornou óbvio que a transação era anômala. Para um estudante com média de €25, uma compra de €8,000 é estatisticamente impossível de ser legítima. A hora (03:15) e categoria (joalharia) reforçaram a decisão.

---

## 4.4 ANA - Identidade Sintética (Fraude de Aplicação)

### Perfil
- **Nome:** Ana Silva (nome comum, red flag)
- **Data de Nascimento:** 15/03/1990
- **Documento:** Bilhete de Identidade
- **Morada:** Rua genérica, Lisboa

### O Incidente
**Processo:** Nova candidatura a cartão de crédito
**Submissão:** Online, documentos digitalizados

### Inconsistências Detetadas

#### Identity Verification - Camada 4: Data Consistency
```
Documento BI: Nome "Ana Silva"
Comprovativo morada: Nome "Ana Santos"

NAME_INCONSISTENCY: +25 pontos
```

#### Identity Verification - Camada 1: Document Authenticity
```
Data expiração BI: 15/05/2022 (JÁ EXPIROU!)

DOCUMENT_EXPIRED: +30 pontos
```

#### Identity Verification - Camada 2: Synthetic Identity
```
NIF: 123456789 (checksum inválido)

NIF_INVALID: +25 pontos
```

#### Risk Orchestrator - Decisão Final
```
Score Final: 25 + 30 + 25 = 80 pontos
                    ↓
Decisão: BLOCK (Aplicação rejeitada)
Motivo: "Múltiplas inconsistências de identidade"
```

### Resultado
- ✅ **Aplicação rejeitada automaticamente**
- ✅ **Nenhum crédito aprovado** (€15,000 potencial perdido para fraudador)
- ✅ **Dados reportados** para autoridades
- ✅ **IP address flagged** para monitorização futura

### Porque Funcionou
A verificação em 5 camadas detetou inconsistências óbvias que seriam ignoradas num processo manual. O nome diferente entre documentos, BI expirado e NIF inválido são red flags clássicas de identidade sintética.

---

## 4.5 CARLOS - Deepfake (Verificação Biométrica)

### Perfil
- **Nome:** Carlos Mendes
- **Processo:** Onboarding digital (abertura de conta)
- **Etapa:** Verificação de identidade por selfie

### O Incidente
**Submissão:** Selfie + foto do documento
**Tentativa:** Usar deepfake para enganar sistema biométrico

### Deteção pelo Sistema

#### Identity Verification - Camada 3: Biometric Verification
```python
# Análise da selfie submetida
biometric_analysis = {
    "face_match_score": 0.95,  # Alta similaridade (deepfake bom)
    "liveness_score": 0.3,      # BAIXO - falha em testes de vivacidade
    "deepfake_probability": 0.94,  # ALTO - artefacts de IA detetados
    "unnatural_texture": True,     # Textura facial não natural
    "inconsistent_lighting": True  # Iluminação inconsistente
}
```

**Resultados:**
```
FACE_MATCH: 0.95 (bom)
LIVENESS_FAILED: +35 pontos
DEEPFAKE_DETECTED: +50 pontos (CRÍTICO)
```

#### Risk Orchestrator - Decisão Final
```
Score Final: 35 + 50 = 85 pontos
                    ↓
Decisão: BLOCK IMEDIATO
Motivo: "Deepfake detetado na verificação biométrica"
```

### Resultado
- ✅ **Onboarding bloqueado**
- ✅ **Tentativa de fraude documentada**
- ✅ **Sistema de deepfake atualizado** com novo padrão
- ✅ **Proteção contra ataques de IA generativa**

### Porque Funcionou
O sistema de deepfake detection analisa múltiplas características além do simples face match. Artefactos de IA, falha em testes de vivacidade e inconsistências de iluminação são detetados por modelos especializados. Mesmo deepfakes sofisticados são identificados.

---

## 4.6 Resumo dos Casos de Uso

| Persona | Tipo de Fraude | Agente Principal | Resultado | Valor Protegido |
|---------|---------------|------------------|-----------|-----------------|
| **João** | Cartão clonado (velocity) | Transaction Monitor | BLOCK | €2,000 |
| **Maria** | Conta comprometida (geo) | Transaction Monitor | BLOCK | €3,200 |
| **Pedro** | Cartão clonado (valor) | Behavioral Analysis | BLOCK | €8,000 |
| **Ana** | Identidade sintética | Identity Verification | REJEIÇÃO | €15,000 |
| **Carlos** | Deepfake | Identity Verification | BLOCK | N/A (preventivo) |

### Métricas de Sucesso

**Taxa de Deteção:** 100% (5/5 casos)
**Tempo Médio de Deteção:** <100ms
**Falsos Positivos:** 0 nesta amostra
**Valor Total Protegido:** €28,200

### Porque o Sistema é Eficaz

1. **Múltiplas Camadas:** Nenhum agente atua sozinho - decisão é ensemble
2. **Especialização:** Cada agente é especialista num tipo de fraude
3. **Velocidade:** Deteção em tempo real permite bloqueio imediato
4. **Adaptabilidade:** Sistema aprende com cada caso
5. **Explicabilidade:** Cada decisão tem justificação clara

---

*Continua na Parte 5: ROI e Implementação*
