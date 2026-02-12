# Parte 3: Agentes Especializados - Detalhamento Técnico

## 3.1 AGENTE: Transaction Monitor

### Propósito
Monitorização em tempo real de transações para deteção imediata de padrões de fraude através de regras de negócio e heurísticas.

### Capacidades de Deteção

#### 3.1.1 Velocity Fraud Detection
**Algoritmo:** Conta transações do mesmo cliente numa janela deslizante de 5 minutos.

```python
def check_velocity(customer_id, timestamp):
    recent_transactions = get_transactions_last_5min(customer_id)
    count = len(recent_transactions)
    
    if count >= 5:
        return Score(30, "VELOCITY_CRITICAL", "BLOCK")
    elif count >= 3:
        return Score(15, "VELOCITY_HIGH", "REVIEW")
    elif count >= 2:
        return Score(5, "VELOCITY_ELEVATED", "MONITOR")
    else:
        return Score(0, [], "APPROVE")
```

**Thresholds:**
- ≥5 transações/5min: **CRÍTICO** (+30 pontos, recomendação BLOCK)
- ≥3 transações/5min: **SUSPEITO** (+15 pontos, recomendação REVIEW)
- ≥2 transações/5min: **ELEVADO** (+5 pontos)

**Exemplo Real:**
Cliente habitual faz 1-2 compras por dia. Sábado às 14:30, sistema deteta 8 transações em 3 minutos, todas no valor de €500. VELOCITY_CRITICAL ativado → Transações 3-8 bloqueadas. Perda evitada: €2,500.

#### 3.1.2 Geographic Impossibility
**Algoritmo:** Calcula velocidade física necessária entre localização da transação anterior e atual.

```python
def check_geographic_impossibility(loc1, loc2, time_delta):
    distance_km = calculate_distance(loc1, loc2)
    hours = time_delta.total_seconds() / 3600
    speed_kmh = distance_km / hours
    
    if speed_kmh > 900:  # Mais rápido que avião comercial
        return Score(35, "GEO_IMPOSSIBLE", "BLOCK")
    elif speed_kmh > 300:  # Mais rápido que comboio alta velocidade
        return Score(20, "GEO_SUSPICIOUS", "REVIEW")
    elif speed_kmh > 120:  # Mais rápido que carro em autoestrada
        return Score(10, "GEO_ELEVATED", "MONITOR")
```

**Thresholds:**
- Velocidade >900 km/h: **IMPOSSÍVEL** (+35 pontos, BLOCK)
- Velocidade >300 km/h: **SUSPEITO** (+20 pontos)
- Velocidade >120 km/h: **ELEVADO** (+10 pontos)

**Exemplo Real:**
Transação em Lisboa (38.72, -9.14) às 14:00. Transação seguinte em Nova Iorque (40.71, -74.01) às 14:30. Distância: 5,400 km. Velocidade necessária: 10,800 km/h. Sistema deteta GEO_IMPOSSIBLE → BLOCK automático. Perda evitada: €3,200.

#### 3.1.3 Amount Anomaly
**Algoritmo:** Compara valor da transação com o máximo histórico do cliente.

```python
def check_amount_anomaly(amount, customer_profile):
    max_historical = customer_profile.max_transaction_amount
    avg_amount = customer_profile.avg_transaction_amount
    
    if amount > max_historical * 2:
        return Score(25, "AMOUNT_EXTREME", "REVIEW")
    elif amount > avg_amount * 5:
        return Score(15, "AMOUNT_HIGH", "REVIEW")
    elif amount > avg_amount * 2:
        return Score(8, "AMOUNT_ELEVATED", "MONITOR")
```

**Thresholds:**
- >2x valor máximo histórico: **EXTREMO** (+25 pontos)
- >5x valor médio: **ALTO** (+15 pontos)
- >2x valor médio: **ELEVADO** (+8 pontos)

#### 3.1.4 Time-Based Risk
**Algoritmo:** Verifica se hora da transação está fora do padrão normal.

```python
def check_time_risk(timestamp, customer_profile):
    hour = timestamp.hour
    usual_hours = customer_profile.usual_transaction_hours
    
    if 0 <= hour < 5:  # Madrugada
        return Score(20, "TIME_NIGHT_RISK", "REVIEW")
    elif hour not in usual_hours:
        return Score(10, "TIME_UNUSUAL", "MONITOR")
```

**Thresholds:**
- 00:00-05:00: **RISCO** (+20 pontos)
- Fora do perfil habitual: **ELEVADO** (+10 pontos)

#### 3.1.5 Merchant Risk
**Algoritmo:** Verifica se comerciante pertence a categorias de alto risco.

```python
HIGH_RISK_CATEGORIES = [
    "crypto", "cryptocurrency", "bitcoin", "exchange",
    "gambling", "casino", "betting", "poker",
    "adult", "xxx", "pornography",
    "money_transfer", "wire_transfer", "remittance"
]

def check_merchant_risk(merchant_category):
    if any(risk in merchant_category.lower() for risk in HIGH_RISK_CATEGORIES):
        return Score(15, "MERCHANT_HIGH_RISK", "REVIEW")
```

**Score:** +15 pontos por match

---

## 3.2 AGENTE: Behavioral Analysis

### Propósito
Análise de padrões comportamentais do cliente para deteção de desvios estatísticos do perfil normal.

### Capacidades de Deteção

#### 3.2.1 Amount Deviation (Z-Score Analysis)
**Algoritmo:** Calcula Z-score estatístico: (valor - média) / desvio_padrão

```python
def calculate_zscore(amount, customer_profile):
    mean = customer_profile.avg_transaction_amount
    std = customer_profile.std_transaction_amount
    
    if std == 0:
        return 0
    
    z_score = abs(amount - mean) / std
    return z_score

def evaluate_zscore(z_score):
    if z_score > 5:    # 99.9999% dos casos normais
        return Score(25, "ZSCORE_EXTREME", "REVIEW")
    elif z_score > 3:  # 99.7% dos casos normais
        return Score(15, "ZSCORE_HIGH", "REVIEW")
    elif z_score > 2:  # 95% dos casos normais
        return Score(8, "ZSCORE_ELEVATED", "MONITOR")
```

**Thresholds:**
- Z >5σ: **EXTREME** (+25 pontos) - ocorre em <0.0001% dos casos normais
- Z >3σ: **HIGH** (+15 pontos) - ocorre em 0.3% dos casos normais
- Z >2σ: **ELEVATED** (+8 pontos) - ocorre em 5% dos casos normais

**Exemplo Real:**
Cliente com média de €100 por transação (desvio padrão €30) faz compra de €5,000.
Z = (5000 - 100) / 30 = 163σ
Sistema deteta EXTREME_ZSCORE → REVIEW/BLOCK. Perda evitada: €5,000.

#### 3.2.2 Time Deviation
**Algoritmo:** Aprende horários habituais do cliente e deteta outliers.

```python
def check_time_deviation(timestamp, customer_profile):
    hour = timestamp.hour
    usual_hours = customer_profile.usual_transaction_hours
    
    if 0 <= hour < 5:
        return Score(20, "TIME_DEVIATION_NIGHT", "REVIEW")
    elif hour not in usual_hours:
        return Score(10, "TIME_DEVIATION_UNUSUAL", "MONITOR")
```

#### 3.2.3 Location Deviation
**Algoritmo:** Compara localização atual com as últimas 10 localizações habituais.

```python
def check_location_deviation(current_location, customer_profile):
    usual_locations = customer_profile.usual_locations  # Últimas 10
    
    min_distance = min(
        calculate_distance(current_location, loc)
        for loc in usual_locations
    )
    
    if min_distance > 500:  # km
        return Score(20, "LOCATION_FAR", "REVIEW")
    elif min_distance > 100:
        return Score(8, "LOCATION_UNUSUAL", "MONITOR")
```

#### 3.2.4 Merchant Deviation
**Algoritmo:** Verifica se é primeira vez que cliente usa este comerciante.

```python
def check_merchant_deviation(merchant_id, customer_profile):
    if merchant_id not in customer_profile.known_merchants:
        return Score(5, "MERCHANT_NEW", "MONITOR")
```

#### 3.2.5 Device Deviation
**Algoritmo:** Verifica se é dispositivo nunca visto anteriormente.

```python
def check_device_deviation(device_id, customer_profile):
    if device_id not in customer_profile.known_devices:
        return Score(10, "DEVICE_NEW", "MONITOR")
```

---

## 3.3 AGENTE: Identity Verification

### Propósito
Verificação avançada de identidade com 5 camadas de segurança para deteção de identidade sintética e documentos fraudulentos.

### As 5 Camadas de Verificação

#### Camada 1: Document Authenticity
**Verifica:**
- Formato do número do documento (passaporte, CC)
- Data de validade (expirado?)
- Características de segurança

```python
def check_document_authenticity(document):
    score = 0
    flags = []
    
    # Validar formato
    if document.type == "passport":
        if not validate_passport_format(document.number):
            score