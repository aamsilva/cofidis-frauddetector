# Parte 3B: Agentes - Continuação (Identity, Anomaly, Device)

## 3.3 IDENTITY VERIFICATION (Continuação)

### Camada 2: Synthetic Identity Detection

**Objetivo:** Detetar identidades criadas sinteticamente usando dados reais combinados de forma fraudulenta.

**Verificações:**
- NIF/SSN: Formato válido e checksum
- Email: Domínio válido, não temporário
- Telefone: Formato nacional/internacional válido

```python
def check_synthetic_identity(identity_data):
    score = 0
    flags = []
    
    # Validar NIF
    if not validate_nif(identity_data.nif):
        score += 25
        flags.append("NIF_INVALID")
    
    # Verificar email temporário
    if is_temp_email(identity_data.email):
        score += 20
        flags.append("EMAIL_TEMPORARY")
    
    # Validar telefone
    if not validate_phone(identity_data.phone):
        score += 15
        flags.append("PHONE_INVALID")
    
    return Score(score, flags)
```

**Score:** +25 (NIF inválido) / +20 (email temporário) / +15 (telefone inválido)

---

### Camada 3: Biometric Verification

**Objetivo:** Verificação facial e deteção de deepfakes.

**Componentes:**
1. **Face Match:** Comparação face apresentada vs foto documento
2. **Liveness Detection:** Verifica se é pessoa real (não foto)
3. **Deepfake Detection:** Deteta manipulação por IA

```python
def verify_biometrics(biometric_data):
    score = 0
    flags = []
    
    # Face match score
    if biometric_data.face_match_score < 0.7:
        score += 30
        flags.append("FACE_MATCH_LOW")
    
    # Liveness check
    if not biometric_data.liveness_passed:
        score += 35
        flags.append("LIVENESS_FAILED")
    
    # Deepfake detection (CRÍTICO)
    if biometric_data.deepfake_detected:
        score += 50  # BLOCK imediato
        flags.append("DEEPFAKE_DETECTED")
    
    return Score(score, flags)
```

**Thresholds:**
- Face match <0.7: **+30 pontos**
- Liveness failed: **+35 pontos**
- **Deepfake detected: +50 pontos (BLOCK imediato)**

---

### Camada 4: Data Consistency

**Objetivo:** Verificar consistência entre diferentes fontes de dados.

**Verificações:**
- Nome consistente entre documentos
- Idade corresponde à data de nascimento
- Morada consistente

```python
def check_data_consistency(documents):
    score = 0
    flags = []
    
    # Nome consistente
    names = [doc.name for doc in documents]
    if len(set(names)) > 1:
        score += 25
        flags.append("NAME_INCONSISTENCY")
    
    # Idade consistente com DOB
    calculated_age = calculate_age(documents[0].dob)
    if abs(calculated_age - documents[0].claimed_age) > 2:
        score += 20
        flags.append("AGE_INCONSISTENCY")
    
    return Score(score, flags)
```

---

### Camada 5: Identity Reuse

**Objetivo:** Detetar quando a mesma identidade é usada em múltiplas contas.

**Mecanismo:**
- Criar fingerprint único: hash(nome + DOB + documento)
- Verificar se fingerprint já existe noutra conta

```python
def check_identity_reuse(identity_data):
    fingerprint = generate_fingerprint(
        identity_data.name,
        identity_data.dob,
        identity_data.document_number
    )
    
    existing_accounts = find_accounts_by_fingerprint(fingerprint)
    
    if len(existing_accounts) > 1:
        return Score(40, "IDENTITY_REUSE", "BLOCK")
    
    return Score(0, [], "APPROVE")
```

**Score:** **+40 pontos** (BLOCK imediato por reutilização de identidade)

---

## 3.4 AGENTE: Anomaly Detection (ML-Based)

### Propósito
Machine learning não-supervisionado para deteção de padrões desconhecidos e zero-day frauds.

### Algoritmo: Isolation Forest + Z-Score Adaptativo

**Vantagens do ML Não-Supervisionado:**
- ✓ Não requer dados de treino etiquetados
- ✓ Aprende padrões normais automaticamente
- ✓ Deteta anomalias nunca vistas antes
- ✓ Adapta-se a mudanças legítimas

```python
class AnomalyDetectionAgent:
    def __init__(self):
        self.baselines = {}  # Por customer_id
    
    def evaluate(self, transaction, context):
        customer_id = transaction.customer_id
        
        # Obter ou criar baseline
        if customer_id not in self.baselines:
            self.baselines[customer_id] = CustomerBaseline()
        
        baseline = self.baselines[customer_id]
        
        # Calcular Z-score adaptativo
        zscore = baseline.calculate_zscore(transaction.amount)
        
        # Isolation Forest para multivariado
        features = [
            transaction.amount,
            transaction.hour_of_day,
            transaction.day_of_week,
            transaction.location_cluster
        ]
        anomaly_score = self.isolation_forest.score(features)
        
        # Combinar scores
        final_score = combine_scores(zscore, anomaly_score)
        
        # Atualizar baseline
        baseline.update(transaction)
        
        return RiskAssessment(score=final_score, ...)
```

### Baseline Adaptativo

Cada cliente tem o seu próprio perfil estatístico:

```python
class CustomerBaseline:
    def __init__(self):
        self.transactions = deque(maxlen=1000)  # Janela deslizante
        self.mean = 0
        self.std = 0
        self.last_updated = None
    
    def calculate_zscore(self, amount):
        if self.std == 0:
            return 0
        return abs(amount - self.mean) / self.std
    
    def update(self, transaction):
        self.transactions.append(transaction.amount)
        self.mean = statistics.mean(self.transactions)
        self.std = statistics.stdev(self.transactions) if len(self.transactions) > 1 else 0
```

### Resposta em Tempo Real

**Performance:**
- Cálculo: <100ms
- Sem chamadas a APIs externas
- Tudo em memória local

---

## 3.5 AGENTE: Device Fingerprint

### Propósito
Deteção de fraude baseada em dispositivo/browser.

### Capacidades de Deteção

#### 3.5.1 Device Fingerprint Hash

Cria identificador único do dispositivo:

```python
def generate_device_fingerprint(device_info):
    components = [
        device_info.user_agent,
        device_info.screen_resolution,
        device_info.color_depth,
        device_info.timezone,
        device_info.language,
        device_info.platform,
        device_info.touch_support,
        device_info.canvas_fingerprint
    ]
    
    fingerprint = hashlib.sha256(
        "|".join(components).encode()
    ).hexdigest()
    
    return fingerprint
```

#### 3.5.2 Device Sharing Detection

**Deteta:** Múltiplas contas usando o mesmo dispositivo

```python
def check_device_sharing(device_fingerprint, customer_id):
    accounts = get_accounts_by_device(device_fingerprint)
    
    if len(accounts) > 3:
        return Score(35, "DEVICE_SHARING_HIGH", "REVIEW")
    elif len(accounts) > 1:
        return Score(20, "DEVICE_SHARING", "MONITOR")
```

**Score:** +35 (partilha elevada) / +20 (partilha moderada)

#### 3.5.3 Rapid Device Changes

**Deteta:** Cliente a usar muitos dispositivos diferentes em curto espaço de tempo

```python
def check_rapid_device_changes(customer_id, device_fingerprint, timeframe=24):
    recent_devices = get_devices_last_n_hours(customer_id, timeframe)
    unique_devices = len(set(recent_devices))
    
    if unique_devices >= 5:
        return Score(30, "DEVICE_CHANGES_EXTREME", "REVIEW")
    elif unique_devices >= 3:
        return Score(15, "DEVICE_CHANGES_HIGH", "MONITOR")
```

**Score:** +30 (≥5 devices/24h) / +15 (≥3 devices/24h)

#### 3.5.4 Emulator Detection

**Deteta:** Uso de máquinas virtuais, emuladores, browsers headless

```python
def detect_emulator(device_info):
    score = 0
    flags = []
    
    # VMs comuns
    vm_indicators = ["vmware", "virtualbox", "qemu", "xen", "parallels"]
    if any(vm in device_info.user_agent.lower() for vm in vm_indicators):
        score += 40
        flags.append("EMULATOR_DETECTED")
    
    # Browser headless
    headless_indicators = ["headless", "phantomjs", "selenium"]
    if any(h in device_info.user_agent.lower() for h in headless_indicators):
        score += 35
        flags.append("HEADLESS_BROWSER")
    
    return Score(score, flags)
```

**Score:** **+40** (emulador/VM) / **+35** (headless browser)

---

## Resumo dos Agentes

| Agente | Foco Principal | Melhor em Detetar |
|--------|----------------|-------------------|
| Transaction Monitor | Regras de negócio em tempo real | Velocity, geo impossível |
| Behavioral Analysis | Desvios do perfil do cliente | Z-score, padrões incomuns |
| Identity Verification | Documentos e biometria | ID sintética, deepfakes |
| Anomaly Detection | ML não-supervisionado | Zero-day, padrões novos |
| Device Fingerprint | Contexto do dispositivo | Partilha, emuladores |

*Todas as decisões são agregadas pelo Risk Orchestrator com pesos configuráveis.*
