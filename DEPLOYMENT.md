# Cofidis Fraud Detector - Deployment Guide

## 🚀 Quick Start (Local)

### Option 1: Docker Compose (Easiest)
```bash
# Clone repository
git clone https://github.com/aamsilva/cofidis-frauddetector.git
cd cofidis-frauddetector

# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f fraud-detector
```

### Option 2: Local Python
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python gateway.py

# Access API
curl http://localhost:8000/docs
```

---

## ☁️ Cloud Deployment

### AWS (EKS + ECR)

```bash
# 1. Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin [ACCOUNT].dkr.ecr.[REGION].amazonaws.com

docker build -t cofidis/fraud-detector:latest .
docker tag cofidis/fraud-detector:latest [ACCOUNT].dkr.ecr.[REGION].amazonaws.com/cofidis/fraud-detector:latest
docker push [ACCOUNT].dkr.ecr.[REGION].amazonaws.com/cofidis/fraud-detector:latest

# 2. Deploy to EKS
kubectl apply -f k8s-deployment.yaml

# 3. Check deployment
kubectl get pods -l app=fraud-detector
kubectl get svc fraud-detector-service
```

### Google Cloud (GKE + Cloud Build)

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/[PROJECT]/fraud-detector:latest

# Deploy to GKE
gcloud container clusters get-credentials [CLUSTER] --zone [ZONE]
kubectl apply -f k8s-deployment.yaml

# Get external IP
kubectl get svc fraud-detector-service
```

### Azure (AKS + ACR)

```bash
# Build and push to ACR
az acr login --name [ACR_NAME]
docker build -t [ACR_NAME].azurecr.io/fraud-detector:latest .
docker push [ACR_NAME].azurecr.io/fraud-detector:latest

# Deploy to AKS
az aks get-credentials --resource-group [RG] --name [CLUSTER]
kubectl apply -f k8s-deployment.yaml
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/staging/production) | `development` |
| `LOG_LEVEL` | Logging level (debug/info/warning/error) | `info` |
| `REDIS_URL` | Redis cache URL | `redis://localhost:6379` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `WORKERS` | Number of Uvicorn workers | `4` |

### Scaling

```bash
# Scale deployment
kubectl scale deployment fraud-detector --replicas=5

# Autoscaling (HPA)
kubectl autoscale deployment fraud-detector --min=3 --max=10 --cpu-percent=70
```

---

## 📊 Monitoring

### Health Checks
- **Liveness:** `GET /health` - Returns 200 if service is running
- **Readiness:** `GET /health` - Returns 200 if ready to accept traffic

### Metrics (Future)
- Prometheus metrics at `/metrics`
- Custom fraud detection metrics
- Agent performance metrics

### Logging
- JSON format for production
- Structured logging with correlation IDs
- Centralized logging (ELK/EFK stack)

---

## 🔒 Security

### Best Practices
- ✅ Non-root container user
- ✅ Read-only filesystem
- ✅ Security context constraints
- ✅ Resource limits
- ✅ Network policies (K8s)

### Secrets Management
```bash
# Create secrets
kubectl create secret generic fraud-detector-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=api-key=...
```

---

## 🔄 CI/CD Pipeline

See `.github/workflows/deploy.yml` for automated deployment pipeline.

### Manual Deployment Checklist
- [ ] Update version tag
- [ ] Run tests
- [ ] Build image
- [ ] Push to registry
- [ ] Update K8s deployment
- [ ] Verify rollout
- [ ] Monitor metrics

---

## 📞 Support

For deployment issues:
1. Check logs: `kubectl logs -l app=fraud-detector`
2. Verify health: `curl [URL]/health`
3. Review metrics in monitoring dashboard
