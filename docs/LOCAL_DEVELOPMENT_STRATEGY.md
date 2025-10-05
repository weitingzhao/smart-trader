# Smart Trader Local Development & CI/CD Strategy

## 🏠 **Local Environment Overview**

### **Hardware Specifications**
```
10.0.0.60 - POWERHOUSE (Primary Development)
├── AMD 9750 CPU (High-performance)
├── RTX 4090 GPU (AI/ML workloads)
├── Role: ML Service, Strategy Optimization, GPU-intensive tasks
└── Primary: AI model training, backtesting, strategy optimization

10.0.0.80 - BALANCED (Secondary Development)
├── Better CPU than 10.0.0.75
├── Built-in GPU (Moderate performance)
├── Role: Portfolio Service, Risk Service, Analytics
└── Secondary: Data processing, risk calculations, analytics

10.0.0.75 - BASIC (Support Services)
├── Basic CPU
├── Basic GPU
├── Role: Data Service, Web Portal, API Gateway
└── Support: Data ingestion, web interface, API routing
```

## 🏗️ **Local Infrastructure Architecture**

### **Service Distribution Strategy**
```yaml
# 10.0.0.60 (Powerhouse) - GPU-Intensive Services
services:
  ml-service:
    host: 10.0.0.60
    gpu: true
    resources:
      cpu: "8 cores"
      memory: "32GB"
      gpu: "RTX 4090"
    
  strategy-service:
    host: 10.0.0.60
    gpu: true
    resources:
      cpu: "6 cores"
      memory: "16GB"
      gpu: "RTX 4090"
    
  analytics-service:
    host: 10.0.0.60
    gpu: false
    resources:
      cpu: "4 cores"
      memory: "8GB"

# 10.0.0.80 (Balanced) - CPU-Intensive Services
services:
  portfolio-service:
    host: 10.0.0.80
    resources:
      cpu: "6 cores"
      memory: "16GB"
    
  risk-service:
    host: 10.0.0.80
    resources:
      cpu: "4 cores"
      memory: "8GB"
    
  compliance-service:
    host: 10.0.0.80
    resources:
      cpu: "2 cores"
      memory: "4GB"

# 10.0.0.75 (Basic) - Lightweight Services
services:
  data-service:
    host: 10.0.0.75
    resources:
      cpu: "4 cores"
      memory: "8GB"
    
  web-portal:
    host: 10.0.0.75
    resources:
      cpu: "2 cores"
      memory: "4GB"
    
  api-gateway:
    host: 10.0.0.75
    resources:
      cpu: "2 cores"
      memory: "2GB"
```

## 🐳 **Docker Compose Configuration**

### **Multi-Host Docker Compose**
```yaml
# docker-compose.local.yml
version: '3.8'

services:
  # Shared Infrastructure (10.0.0.75)
  postgres:
    image: timescale/timescaledb:latest-pg17
    container_name: smart-trader.postgres
    hostname: postgres
    environment:
      POSTGRES_DB: smart_trader_local
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: local_password
      TIMESCALEDB_TELEMETRY: off
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  redis:
    image: redis:7.0.12
    container_name: smart-trader.redis
    hostname: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - smart-trader-network
    command: ["redis-server", "--appendonly", "yes"]

  # Data Service (10.0.0.75)
  data-service:
    build: 
      context: ./services/data-service
      dockerfile: Dockerfile.local
    container_name: smart-trader.data-service
    hostname: data-service
    ports:
      - "8001:8000"
    environment:
      - SERVICE_NAME=data-service
      - DATABASE_URL=postgresql://postgres:local_password@postgres:5432/smart_trader_local
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=local
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  # Portfolio Service (10.0.0.80)
  portfolio-service:
    build: 
      context: ./services/portfolio-service
      dockerfile: Dockerfile.local
    container_name: smart-trader.portfolio-service
    hostname: portfolio-service
    ports:
      - "8002:8000"
    environment:
      - SERVICE_NAME=portfolio-service
      - DATABASE_URL=postgresql://postgres:local_password@postgres:5432/smart_trader_local
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=local
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  # Risk Service (10.0.0.80)
  risk-service:
    build: 
      context: ./services/risk-service
      dockerfile: Dockerfile.local
    container_name: smart-trader.risk-service
    hostname: risk-service
    ports:
      - "8004:8000"
    environment:
      - SERVICE_NAME=risk-service
      - DATABASE_URL=postgresql://postgres:local_password@postgres:5432/smart_trader_local
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=local
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  # ML Service (10.0.0.60) - GPU Enabled
  ml-service:
    build: 
      context: ./services/ml-service
      dockerfile: Dockerfile.gpu
    container_name: smart-trader.ml-service
    hostname: ml-service
    ports:
      - "8005:8000"
    environment:
      - SERVICE_NAME=ml-service
      - DATABASE_URL=postgresql://postgres:local_password@postgres:5432/smart_trader_local
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=local
      - CUDA_VISIBLE_DEVICES=0
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
    runtime: nvidia
    volumes:
      - /usr/local/cuda:/usr/local/cuda:ro

  # Strategy Service (10.0.0.60) - GPU Enabled
  strategy-service:
    build: 
      context: ./services/strategy-service
      dockerfile: Dockerfile.gpu
    container_name: smart-trader.strategy-service
    hostname: strategy-service
    ports:
      - "8003:8000"
    environment:
      - SERVICE_NAME=strategy-service
      - DATABASE_URL=postgresql://postgres:local_password@postgres:5432/smart_trader_local
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=local
      - CUDA_VISIBLE_DEVICES=0
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
    runtime: nvidia

  # Web Portal (10.0.0.75)
  web-portal:
    build: 
      context: ./services/web-portal
      dockerfile: Dockerfile.local
    container_name: smart-trader.web-portal
    hostname: web-portal
    ports:
      - "8000:8000"
    environment:
      - SERVICE_NAME=web-portal
      - DATABASE_URL=postgresql://postgres:local_password@postgres:5432/smart_trader_local
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=local
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  # API Gateway (10.0.0.75)
  api-gateway:
    build: 
      context: ./services/api-gateway
      dockerfile: Dockerfile.local
    container_name: smart-trader.api-gateway
    hostname: api-gateway
    ports:
      - "8080:8080"
    environment:
      - SERVICE_NAME=api-gateway
      - ENVIRONMENT=local
    depends_on:
      - data-service
      - portfolio-service
      - strategy-service
      - risk-service
      - ml-service
    networks:
      - smart-trader-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

networks:
  smart-trader-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres_data:
  redis_data:
```

## 🚀 **Local CI/CD Pipeline**

### **GitHub Actions for Local Deployment**
```yaml
# .github/workflows/local-deploy.yml
name: Local Development Deployment

on:
  push:
    branches: [develop, feature/*]
  pull_request:
    branches: [develop]

jobs:
  test-services:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [data-service, portfolio-service, strategy-service, risk-service, ml-service]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          cd services/${{ matrix.service }}
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: services/${{ matrix.service }}/coverage.xml

  build-images:
    needs: test-services
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build Docker images
        run: |
          for service in data-service portfolio-service strategy-service risk-service ml-service; do
            docker build -t smart-trader-$service:latest ./services/$service/
            docker save smart-trader-$service:latest | gzip > $service.tar.gz
          done
      
      - name: Upload images
        uses: actions/upload-artifact@v3
        with:
          name: docker-images
          path: "*.tar.gz"

  deploy-to-local:
    needs: build-images
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download images
        uses: actions/download-artifact@v3
        with:
          name: docker-images
      
      - name: Deploy to 10.0.0.75 (Basic Services)
        run: |
          scp *.tar.gz user@10.0.0.75:/tmp/
          ssh user@10.0.0.75 "cd /tmp && docker load < data-service.tar.gz && docker load < web-portal.tar.gz && docker load < api-gateway.tar.gz"
          ssh user@10.0.0.75 "cd /home/user/smart-trader && docker-compose -f docker-compose.local.yml up -d data-service web-portal api-gateway"
      
      - name: Deploy to 10.0.0.80 (Balanced Services)
        run: |
          scp *.tar.gz user@10.0.0.80:/tmp/
          ssh user@10.0.0.80 "cd /tmp && docker load < portfolio-service.tar.gz && docker load < risk-service.tar.gz"
          ssh user@10.0.0.80 "cd /home/user/smart-trader && docker-compose -f docker-compose.local.yml up -d portfolio-service risk-service"
      
      - name: Deploy to 10.0.0.60 (GPU Services)
        run: |
          scp *.tar.gz user@10.0.0.60:/tmp/
          ssh user@10.0.0.60 "cd /tmp && docker load < strategy-service.tar.gz && docker load < ml-service.tar.gz"
          ssh user@10.0.0.60 "cd /home/user/smart-trader && docker-compose -f docker-compose.local.yml up -d strategy-service ml-service"
      
      - name: Health Check
        run: |
          sleep 30
          curl -f http://10.0.0.75:8000/health || exit 1
          curl -f http://10.0.0.75:8001/health || exit 1
          curl -f http://10.0.0.80:8002/health || exit 1
          curl -f http://10.0.0.60:8003/health || exit 1
```

## 🛠️ **Local Development Setup**

### **Development Scripts**
```bash
# scripts/setup-local-env.sh
#!/bin/bash

echo "Setting up Smart Trader Local Environment..."

# Create shared network
docker network create smart-trader-network 2>/dev/null || true

# Setup on 10.0.0.75 (Basic Services)
echo "Setting up 10.0.0.75 (Basic Services)..."
ssh user@10.0.0.75 << 'EOF'
  mkdir -p /home/user/smart-trader
  cd /home/user/smart-trader
  
  # Install Docker and Docker Compose
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  
  # Install NVIDIA Docker (if needed)
  distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
  curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
  curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
  sudo apt-get update && sudo apt-get install -y nvidia-docker2
  sudo systemctl restart docker
EOF

# Setup on 10.0.0.80 (Balanced Services)
echo "Setting up 10.0.0.80 (Balanced Services)..."
ssh user@10.0.0.80 << 'EOF'
  mkdir -p /home/user/smart-trader
  cd /home/user/smart-trader
  
  # Install Docker and Docker Compose
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
EOF

# Setup on 10.0.0.60 (GPU Services)
echo "Setting up 10.0.0.60 (GPU Services)..."
ssh user@10.0.0.60 << 'EOF'
  mkdir -p /home/user/smart-trader
  cd /home/user/smart-trader
  
  # Install Docker and Docker Compose
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  
  # Install NVIDIA Docker for GPU support
  distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
  curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
  curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
  sudo apt-get update && sudo apt-get install -y nvidia-docker2
  sudo systemctl restart docker
EOF

echo "Local environment setup complete!"
```

### **Service-Specific Dockerfiles**

#### **GPU Services Dockerfile**
```dockerfile
# services/ml-service/Dockerfile.gpu
FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Install ML dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install GPU-specific packages
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip3 install tensorflow-gpu
RUN pip3 install cupy-cuda11x

# Copy application code
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 8000

# Run application
CMD ["python3", "main.py"]
```

#### **Standard Services Dockerfile**
```dockerfile
# services/data-service/Dockerfile.local
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

## 📊 **Local Monitoring Setup**

### **Prometheus Configuration**
```yaml
# monitoring/prometheus-local.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'smart-trader-services'
    static_configs:
      - targets: 
        - '10.0.0.75:8001'  # data-service
        - '10.0.0.80:8002'  # portfolio-service
        - '10.0.0.60:8003'  # strategy-service
        - '10.0.0.80:8004'  # risk-service
        - '10.0.0.60:8005'  # ml-service
        - '10.0.0.75:8000'  # web-portal
        - '10.0.0.75:8080'  # api-gateway
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['10.0.0.75:5432']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['10.0.0.75:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: 
        - '10.0.0.60:9100'  # GPU server
        - '10.0.0.80:9100'  # Balanced server
        - '10.0.0.75:9100'  # Basic server
```

### **Grafana Dashboard for Local Environment**
```json
{
  "dashboard": {
    "title": "Smart Trader Local Environment",
    "panels": [
      {
        "title": "Service Health by Server",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"smart-trader-services\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "GPU Utilization (10.0.0.60)",
        "type": "graph",
        "targets": [
          {
            "expr": "nvidia_gpu_utilization_percent",
            "legendFormat": "GPU {{gpu}}"
          }
        ]
      },
      {
        "title": "CPU Usage by Server",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Memory Usage by Server",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

## 🔧 **Development Workflow**

### **Cursor IDE Multi-Host Configuration**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "remote.SSH.remotePlatform": {
    "10.0.0.60": "linux",
    "10.0.0.80": "linux", 
    "10.0.0.75": "linux"
  },
  "remote.SSH.configFile": "~/.ssh/config",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true
  }
}
```

### **SSH Configuration**
```bash
# ~/.ssh/config
Host gpu-server
    HostName 10.0.0.60
    User user
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host balanced-server
    HostName 10.0.0.80
    User user
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host basic-server
    HostName 10.0.0.75
    User user
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

## 🚀 **Deployment Commands**

### **Local Deployment Scripts**
```bash
# scripts/deploy-local.sh
#!/bin/bash

echo "Deploying Smart Trader to Local Environment..."

# Deploy to 10.0.0.75 (Basic Services)
echo "Deploying to 10.0.0.75 (Basic Services)..."
ssh user@10.0.0.75 << 'EOF'
  cd /home/user/smart-trader
  docker-compose -f docker-compose.local.yml up -d postgres redis data-service web-portal api-gateway
EOF

# Deploy to 10.0.0.80 (Balanced Services)
echo "Deploying to 10.0.0.80 (Balanced Services)..."
ssh user@10.0.0.80 << 'EOF'
  cd /home/user/smart-trader
  docker-compose -f docker-compose.local.yml up -d portfolio-service risk-service
EOF

# Deploy to 10.0.0.60 (GPU Services)
echo "Deploying to 10.0.0.60 (GPU Services)..."
ssh user@10.0.0.60 << 'EOF'
  cd /home/user/smart-trader
  docker-compose -f docker-compose.local.yml up -d strategy-service ml-service
EOF

echo "Deployment complete!"
echo "Services available at:"
echo "- Web Portal: http://10.0.0.75:8000"
echo "- Data Service: http://10.0.0.75:8001"
echo "- Portfolio Service: http://10.0.0.80:8002"
echo "- Strategy Service: http://10.0.0.60:8003"
echo "- Risk Service: http://10.0.0.80:8004"
echo "- ML Service: http://10.0.0.60:8005"
echo "- API Gateway: http://10.0.0.75:8080"
```

## 📈 **Performance Optimization**

### **Resource Allocation Strategy**
```yaml
# Resource optimization for local environment
resource_allocation:
  "10.0.0.60":  # GPU Server
    total_cpu: "16 cores"
    total_memory: "64GB"
    total_gpu: "RTX 4090"
    services:
      ml-service:
        cpu: "8 cores"
        memory: "32GB"
        gpu: "RTX 4090"
      strategy-service:
        cpu: "6 cores"
        memory: "16GB"
        gpu: "RTX 4090"
      analytics-service:
        cpu: "2 cores"
        memory: "8GB"
        gpu: false

  "10.0.0.80":  # Balanced Server
    total_cpu: "12 cores"
    total_memory: "32GB"
    services:
      portfolio-service:
        cpu: "6 cores"
        memory: "16GB"
      risk-service:
        cpu: "4 cores"
        memory: "8GB"
      compliance-service:
        cpu: "2 cores"
        memory: "4GB"

  "10.0.0.75":  # Basic Server
    total_cpu: "8 cores"
    total_memory: "16GB"
    services:
      data-service:
        cpu: "4 cores"
        memory: "8GB"
      web-portal:
        cpu: "2 cores"
        memory: "4GB"
      api-gateway:
        cpu: "2 cores"
        memory: "2GB"
```

## 🔄 **CI/CD Pipeline for Local Environment**

### **Automated Testing and Deployment**
```yaml
# .github/workflows/local-ci-cd.yml
name: Local CI/CD Pipeline

on:
  push:
    branches: [develop, feature/*]
  pull_request:
    branches: [develop]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Test all services
        run: |
          for service in services/*; do
            echo "Testing $service..."
            cd $service
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
            pytest tests/
            cd ../..
          done
      
      - name: Build Docker images
        run: |
          for service in services/*; do
            service_name=$(basename $service)
            docker build -t smart-trader-$service_name:latest $service/
          done
      
      - name: Deploy to local environment
        run: |
          # Copy images to local servers
          docker save smart-trader-data-service:latest | ssh user@10.0.0.75 "docker load"
          docker save smart-trader-portfolio-service:latest | ssh user@10.0.0.80 "docker load"
          docker save smart-trader-strategy-service:latest | ssh user@10.0.0.60 "docker load"
          docker save smart-trader-risk-service:latest | ssh user@10.0.0.80 "docker load"
          docker save smart-trader-ml-service:latest | ssh user@10.0.0.60 "docker load"
          
          # Restart services
          ssh user@10.0.0.75 "cd /home/user/smart-trader && docker-compose -f docker-compose.local.yml restart data-service web-portal api-gateway"
          ssh user@10.0.0.80 "cd /home/user/smart-trader && docker-compose -f docker-compose.local.yml restart portfolio-service risk-service"
          ssh user@10.0.0.60 "cd /home/user/smart-trader && docker-compose -f docker-compose.local.yml restart strategy-service ml-service"
```

## 🎯 **Benefits of Local Development Strategy**

### **Cost Benefits**
- **No cloud costs** during development
- **Full control** over hardware resources
- **No data transfer costs** for large datasets
- **Unlimited testing** without usage limits

### **Performance Benefits**
- **Direct GPU access** for ML training
- **Low latency** between services
- **High bandwidth** for data processing
- **Custom hardware optimization**

### **Development Benefits**
- **Faster iteration** cycles
- **Easy debugging** with direct access
- **Custom configurations** for each server
- **Offline development** capability

## 🚀 **Migration to Cloud Strategy**

### **When to Move to Cloud**
```yaml
triggers_for_cloud_migration:
  - "System running stable for 3+ months"
  - "Profitable trading strategies validated"
  - "Need for 24/7 uptime"
  - "Requirement for global access"
  - "Need for auto-scaling"
  - "Compliance requirements"

cloud_migration_plan:
  phase_1: "Replicate local setup in cloud"
  phase_2: "Implement auto-scaling"
  phase_3: "Add global distribution"
  phase_4: "Implement disaster recovery"
```

This local development strategy provides:
- **Cost-effective development** environment
- **Optimal resource utilization** across your hardware
- **GPU-accelerated** ML and strategy development
- **Scalable architecture** ready for cloud migration
- **Complete CI/CD pipeline** for local deployment

Would you like me to help you implement any specific part of this local development strategy?
