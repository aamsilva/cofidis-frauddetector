# Use Cases Detalhados - Cofidis Fraud Detector
## Cenários Proativos com Workflows Silenciosos

---

## 🎯 AGENTE 1: SOCIAL ENGINEERING DETECTION

### **Caso Real: Ana Rodrigues (APP Fraud Prevention)**

**Perfil:**
- Nome: Ana Rodrigues
- Idade: 67 anos
- Cliente: 4 anos, nunca teve problemas
- Padrão: Transferências mensais fixas (renda, serviços)
- Valor médio transferência: €200-500

**O Incidente (Detetado Proativamente):**
```
10:15 - Ana recebe chamada de "Funcionário Cofidis" (vishing)
10:18 - Ana inicia login na app (comportamento normal)
10:19 - Ana acede a área de transferências
10:20 - Ana preenche transferência €15,000 para IBAN desconhecido
10:20:15 - AGENTE ATIVADO
```

**Deteção Proativa:**
| Indicador | Valor | Threshold |
|-----------|-------|-----------|
| Urgência artificial | 95% | >80% |
| Valor atípico | 30x acima da média | >10x |
| IBAN novo | Nunca usado | - |
| Comportamento stress | Typing speed 3x mais rápido | >2x |
| Padrão de hesitação | 4 pausas >5s no preenchimento | >3 |

**Workflow Silencioso:**
```
Score: 88/100 (Alto risco)
    ↓
[Tempo real - 500ms]
    ↓
┌─────────────────────────────────────────────┐
│ 1. TRANSFERÊNCIA BLOQUEADA (silent hold)    │
│    - Status: "Em processamento" (não       │
│      "Bloqueada" para não alarmar)          │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. NOTIFICAÇÃO PUSH (app) - Ana             │
│    "Confirme esta transferência grande      │
│     ligando para 808 91 91 91 (0€)"         │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. ALERTA EQUIPA RISCO (dashboard)          │
│    Prioridade: ALTA                           │
│    Cliente: Ana Rodrigues (67)              │
│    Score: 88 | Flags: VISHING_LIKELY        │
│    Ação recomendada: Contactar em 2 min     │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. CALL CENTER RECEBE POP-UP                │
│    "Ana Rodrigues - possível vishing        │
│     Verifique se foi contactada por alguém  │
│     a dizer ser da Cofidis"                 │
└─────────────────────────────────────────────┘
```

**Resolução:**
- Call center liga para Ana em 90 segundos
- Ana confirma: "Sim, ligaram-me a dizer que tinha problemas na conta"
- Call center: "Não fomos nós. É fraude. Não transfira."
- Transferência cancelada silenciosamente
- Nova password gerada e enviada por SMS
- **€15,000 salvos sem alarme desnecessário**

**Porque Funciona (Sem Falsos Positivos):**
- Score 88 exige MÚLTIPLOS indicadores (urgência + valor + IBAN novo + stress)
- Threshold ajustado: Só alerta se score >85
- Clientes normais com transferências grandes habituais não atingem score (falta "urgência" e "stress")

---

## 🎯 AGENTE 2: INSTANT PAYMENT FLOOD

### **Caso Real: Ricardo Mendes (MB Way Protection)**

**Perfil:**
- Nome: Ricardo Mendes
- Idade: 34 anos
- Cliente: 2 anos
- Padrão: Usa MB Way 3-5x/mês, valores €20-100

**O Incidente (Ataque em tempo real):**
```
14:32:00 - Ataque inicia (botnet)
14:32:01 - Pedido MB Way €500 (fonte: IP russo spoofed)
14:32:02 - Pedido MB Way €500 (fonte: IP ucraniano spoofed)
14:32:03 - Pedido MB Way €500 (fonte: IP chinês spoofed)
...
14:32:10 - 50 pedidos em 10 segundos
```

**Deteção Proativa:**
| Indicador | Valor | Threshold |
|-----------|-------|-----------|
| Velocity | 50 pedidos/10s | >10/10s |
| Origens geográficas | 12 países diferentes | >3 |
| Device fingerprints | 50 dispositivos diferentes | >3 |
| Padrão de timing | Milissegundos precisos (bots) | <100ms std dev |

**Workflow Silencioso:**
```
Score: 95/100 (Ataque confirmado)
    ↓
[Tempo real - 100ms]
    ↓
┌─────────────────────────────────────────────┐
│ 1. TODOS OS PEDIDOS REJEITADOS              │
│    - Sem notificação ao utilizador          │
│    - Attacker não sabe que foi detetado     │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. NOTIFICAÇÃO SILENCIOSA - Ricardo         │
│    SMS: "Detetamos tentativas suspeitas     │
│    de utilização do seu MB Way. Se não      │
│    foi você, ignore esta mensagem."         │
│    (Só envia se Ricardo não autorizou)      │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. COUNTER-MEASURES AUTOMÁTICOS             │
│    - IP addresses blacklisted               │
│    - Device fingerprints flagged            │
│    - Padrão adicionado a threat intel       │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. RELATÓRIO SEGURANÇA (dashboard)          │
│    Ataque MB Way mitigado                   │
│    Alvo: Ricardo Mendes                     │
│    Pedidos bloqueados: 50                   │
│    Valor protegido: €25,000                 │
│    Tempo de resposta: 100ms                 │
└─────────────────────────────────────────────┘
```

**Resolução:**
- Ricardo não recebe notificação push (não precisa de agir)
- Recebe SMS informativo 5 minutos depois
- Se Ricardo tinha autorizado: Nenhum impacto (workflow não dispara)
- **€25,000 protegidos sem interrupção do cliente**

**Porque Funciona (Sem Falsos Positivos):**
- Score 95 = combinação IMPOSSÍVEL em comportamento legítimo
- 50 pedidos em 10s é fisicamente impossível para humano
- Milissegundos precisos só ocorrem em bots
- Cliente normal nunca atinge estes thresholds

---

## 🎯 AGENTE 3: IDENTITY VERIFICATION (Onboarding)

### **Caso Real: Diogo Santos (Synthetic Identity)**

**Perfil (Fraudulento):**
- Nome: Diogo Santos
- Documento: BI apresentado via upload
- Morada: Rua Genérica, Lisboa
- Rendimento: €3,500/mês (comprovativo)

**O Incidente (Onboarding digital):**
```
11:00 - Diogo inicia aplicação crédito pessoal €10,000
11:05 - Upload documentos
11:06 - Selfie para verificação
11:06:30 - AGENTE ATIVADO
```

**Deteção Proativa:**
| Indicador | Valor | Threshold |
|-----------|-------|-----------|
| BI expiração | 15/05/2022 (JÁ EXPIROU) | < hoje |
| NIF checksum | Inválido | deve ser válido |
| Nome BI vs Comprovativo | "Diogo Santos" vs "Diogo S." | 100% match |
| Morada | Não existe em base de dados CTT | deve existir |
| Face match | 0.65 (baixo) | >0.80 |
| Digital footprint | Zero (no social media, no google) | >0 |

**Workflow Silencioso:**
```
Score: 82/100 (Identidade sintética)
    ↓
[Tempo real - 2 segundos]
    ↓
┌─────────────────────────────────────────────┐
│ 1. APLICAÇÃO EM ESPERA (silent)             │
│    Status: "Em análise documental"          │
│    (não "Rejeitada" para não alertar)       │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. ALERTA EQUIPA ONBOARDING                 │
│    Prioridade: MÉDIA                          │
│    Cliente: Diogo Santos                    │
│    Flags: BI_EXPIRADO + NIF_INVALIDO        │
│    Ação: Verificação manual obrigatória     │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. EMAIL CLIENTE (educativo)                │
│    "Prezado Diogo,                         │
│     Detetamos inconsistências nos           │
│     documentos apresentados. Por favor      │
│     envie novo BI válido."                  │
└─────────────────────────────────────────────┘
```

**Resolução:**
- Diogo não recebe "rejeição", recebe "pedido de esclarecimento"
- Fraudador geralmente desiste (não tem documentos válidos)
- Se for erro legítimo: Cliente envia documentos corretos
- **€10,000 de crédito fraudulento prevenido**

**Porque Funciona (Sem Falsos Positivos):**
- Score 82 exige múltiplas falhas (BI + NIF + nome + morada)
- Cliente legítimo raramente tem >1 inconsistência
- BI expirado é erro claro (não falso positivo)
- Processo é educativo, não punitivo

---

## 🎯 AGENTE 4: BEHAVIORAL ANALYSIS (Account Takeover)

### **Caso Real: Sofia Martins (Conta Comprometida)**

**Perfil:**
- Nome: Sofia Martins
- Idade: 42 anos
- Cliente: 6 anos
- Padrão: Login diário às 19h-21h, de Lisboa

**O Incidente (ATO - Account Takeover):**
```
Histórico normal:
- Login sempre de Lisboa
- Dispositivo: iPhone 12 (2 anos)
- Horário: 19h-21h
- Padrão: Ver saldo, pagar serviços

Incidente:
03:15 - Login de Budapeste (novo dispositivo Android)
03:16 - Alteração de email (para: sofia.martins.new@gmail.com)
03:17 - Pedido de transferência €5,000
03:17:30 - AGENTE ATIVADO
```

**Deteção Proativa:**
| Indicador | Valor | Threshold |
|-----------|-------|-----------|
| Localização | Budapeste (vs Lisboa) | >500km |
| Horário | 03:15 (vs habitual 19h-21h) | fora padrão |
| Dispositivo | Android novo (vs iPhone habitual) | novo |
| Ação pós-login | Alteração email (rara) | <1% dos users |
| Z-score comportamental | 8.5σ desvio | >5σ |

**Workflow Silencioso:**
```
Score: 91/100 (Account takeover confirmado)
    ↓
[Tempo real - 500ms]
    ↓
┌─────────────────────────────────────────────┐
│ 1. AÇÕES BLOQUEADAS (silent)                │
│    - Alteração de email: HOLD               │
│    - Transferência: HOLD                    │
│    - Mensagem: "Verificação de segurança    │
│      em curso"                              │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. NOTIFICAÇÃO IMEDIATA - Sofia             │
│    SMS: "Login detetado em Budapeste.       │
│    Se não foi você, ligue 808 91 91 91"     │
│    APP: Push notification com "Não fui eu"  │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. SE SOFIA CLICAR "Não fui eu":            │
│    - Sessão Budapeste terminada             │
│    - Password reset forçado                 │
│    - Email original restaurado              │
│    - Equipa fraude notificada               │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. SE SOFIA CLICAR "Fui eu":                │
│    - Aprovação manual por risco             │
│    - Baseline atualizado (nova viagem)      │
│    - Sem bloqueios futuros similares        │
└─────────────────────────────────────────────┘
```

**Resolução:**
- Sofia recebe SMS às 03:17:35 (5s após deteção)
- Sofia clica "Não fui eu" (está a dormir em Lisboa)
- Ataque bloqueado antes de qualquer dano
- **€5,000 + conta protegidos**

**Porque Funciona (Sem Falsos Positivos):**
- Score 91 = múltiplos desvios simultâneos (geo + horário + device + ação)
- Cliente em viagem legítima: Só tem 1-2 desvios (geo + talvez device)
- Se score 70-85: Fluxo de confirmação, não bloqueio automático
- Threshold ajustável por perfil de risco

---

## 🎯 AGENTE 5: MONEY MULE DETECTION

### **Caso Real: Tiago Ferreira (Jovem Mule)**

**Perfil:**
- Nome: Tiago Ferreira
- Idade: 19 anos, estudante universitário
- Conta: Nova (aberta há 2 meses)
- Atividade anterior: Pouca (salário part-time €400/mês)

**O Incidente (Mule Recrutado):**
```
Histórico normal:
- Depósitos: €400/mês (salário)
- Gastos: Supermercado, transporte
- Nunca transferiu >€200

Incidente:
Segunda: Recebe €5,000 (desconhecido)
Terça: Recebe €3,000 (desconhecido)
Quarta: Transfere €7,900 para offshore (Islas Caimão)
Quarta 14:30 - AGENTE ATIVADO
```

**Deteção Proativa:**
| Indicador | Valor | Threshold |
|-----------|-------|-----------|
| Velocity in/out | €8,000 in / €7,900 out em 72h | >5x normal |
| Origem fundos | Desconhecidos | conhecidos |
| Destino | Offshore (alerta AML) | offshore |
| Padrão | "Funnel" (muitos in, um out) | característico |
| Idade/Perfil | 19 anos, estudante | high risk |
| Network | Conexão com 3 outras contas similares | >2 links |

**Workflow Silencioso:**
```
Score: 87/100 (Money mule likely)
    ↓
[Tempo real - após transferência]
    ↓
┌─────────────────────────────────────────────┐
│ 1. TRANSFERÊNCIA HOLD (silent)              │
│    Status: "Em processamento (até 24h)"     │
│    (não "Bloqueada")                        │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. ALERTA EQUIPA AML                        │
│    Prioridade: ALTA                           │
│    Suspeita: Money mule / Layering          │
│    Valor: €7,900 para offshore              │
│    Ação: Investigar origem dos €8,000       │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. CONTACTO DISCRETO - Tiago                │
│    Call center: "Olá Tiago, estamos a       │
│    fazer uma verificação de rotina.         │
│    Pode dizer-nos de onde vieram os         │
│    €8,000 depositados esta semana?"         │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. SE CONFIRMAR MULE:                       │
│    - Transferência cancelada                │
│    - Conta suspensa (investigação)          │
│    - Report às autoridades                  │
│    - Tiago orientado (vítima vs cúmplice)   │
└─────────────────────────────────────────────┘
```

**Resolução:**
- Tiago explica: "Um amigo do Instagram pediu para receber dinheiro e transferir"
- Transferência cancelada antes de sair do sistema
- €7,900 recuperados
- Tiago é orientado como vítima (não cúmplice consciente)
- **€7,900 protegidos + jovem protegido de consequências legais**

**Porque Funciona (Sem Falsos Positivos):**
- Score 87 = combinação "funnel" + offshore + idade + velocidade
- Transferência legítima (herança, venda): Tem explicação clara, documentação
- Se Tiago tivesse justificação: Transferência aprovada após verificação
- Processo educativo, não punitivo

---

## 📊 COMPARAÇÃO: ABORDAGEM REATIVA vs PROATIVA

| Aspecto | Sistema Tradicional | Cofidis FD (Proativo) |
|---------|---------------------|----------------------|
| **Descoberta** | Cliente reclama | Deteção automática |
| **Tempo** | Dias | <1 segundo |
| **Notificação** | Cliente chama banco | Banco contacta cliente |
| **Falsos Positivos** | Altos (15-20%) | Baixos (<5%) |
| **Experiência** | Stressante | Silenciosa/corretiva |
| **Prejuízo** | Já aconteceu | Prevenido |
| **Workflow** | Manual | Automático |

---

*Documentação completa de workflows proativos*
