#!/bin/bash
# Smart Trader Local Environment Setup Script

echo "🚀 Setting up Smart Trader Local Development Environment..."

# Configuration
GPU_SERVER="10.0.0.60"
BALANCED_SERVER="10.0.0.80"
BASIC_SERVER="10.0.0.75"
USER="user"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if servers are reachable
check_servers() {
    print_header "Checking Server Connectivity"
    
    for server in $GPU_SERVER $BALANCED_SERVER $BASIC_SERVER; do
        if ping -c 1 $server &> /dev/null; then
            print_status "✅ $server is reachable"
        else
            print_error "❌ $server is not reachable"
            exit 1
        fi
    done
}

# Setup SSH keys
setup_ssh() {
    print_header "Setting up SSH Keys"
    
    if [ ! -f ~/.ssh/id_rsa ]; then
        print_status "Generating SSH key pair..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    fi
    
    # Copy SSH key to all servers
    for server in $GPU_SERVER $BALANCED_SERVER $BASIC_SERVER; do
        print_status "Copying SSH key to $server..."
        ssh-copy-id $USER@$server
    done
}

# Install Docker on servers
install_docker() {
    print_header "Installing Docker on Servers"
    
    for server in $GPU_SERVER $BALANCED_SERVER $BASIC_SERVER; do
        print_status "Installing Docker on $server..."
        ssh $USER@$server << 'EOF'
            # Update system
            sudo apt-get update
            
            # Install Docker
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            
            echo "Docker installation complete on $(hostname)"
EOF
    done
}

# Install NVIDIA Docker on GPU server
install_nvidia_docker() {
    print_header "Installing NVIDIA Docker on GPU Server"
    
    print_status "Installing NVIDIA Docker on $GPU_SERVER..."
    ssh $USER@$GPU_SERVER << 'EOF'
        # Install NVIDIA Docker
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
        
        sudo apt-get update && sudo apt-get install -y nvidia-docker2
        sudo systemctl restart docker
        
        # Test NVIDIA Docker
        docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
        
        echo "NVIDIA Docker installation complete"
EOF
}

# Create project directories
create_directories() {
    print_header "Creating Project Directories"
    
    for server in $GPU_SERVER $BALANCED_SERVER $BASIC_SERVER; do
        print_status "Creating directories on $server..."
        ssh $USER@$server << 'EOF'
            mkdir -p /home/$USER/smart-trader/{services,monitoring,scripts,logs}
            mkdir -p /home/$USER/smart-trader/services/{data-service,portfolio-service,strategy-service,risk-service,ml-service,web-portal,api-gateway}
            echo "Directories created on $(hostname)"
EOF
    done
}

# Copy configuration files
copy_configs() {
    print_header "Copying Configuration Files"
    
    # Create local docker-compose file
    cat > docker-compose.local.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg17
    container_name: smart-trader.postgres
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

  redis:
    image: redis:7.0.12
    container_name: smart-trader.redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - smart-trader-network
    command: ["redis-server", "--appendonly", "yes"]

networks:
  smart-trader-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

    # Copy to basic server (10.0.0.75)
    print_status "Copying configuration to $BASIC_SERVER..."
    scp docker-compose.local.yml $USER@$BASIC_SERVER:/home/$USER/smart-trader/
    
    # Create deployment script
    cat > deploy-local.sh << 'EOF'
#!/bin/bash
echo "Deploying Smart Trader to Local Environment..."

# Deploy to 10.0.0.75 (Basic Services)
echo "Deploying to 10.0.0.75 (Basic Services)..."
ssh user@10.0.0.75 << 'EOF'
  cd /home/user/smart-trader
  docker-compose -f docker-compose.local.yml up -d postgres redis
EOF

echo "Basic infrastructure deployed!"
echo "Next steps:"
echo "1. Deploy services to respective servers"
echo "2. Configure monitoring"
echo "3. Set up CI/CD pipeline"
EOF

    chmod +x deploy-local.sh
    print_status "Configuration files created"
}

# Setup monitoring
setup_monitoring() {
    print_header "Setting up Monitoring"
    
    # Create Prometheus configuration
    cat > prometheus-local.yml << 'EOF'
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
EOF

    # Copy to basic server
    scp prometheus-local.yml $USER@$BASIC_SERVER:/home/$USER/smart-trader/monitoring/
    
    print_status "Monitoring configuration created"
}

# Create service templates
create_service_templates() {
    print_header "Creating Service Templates"
    
    # Create basic service template
    mkdir -p services/template-service/{src,tests,docs}
    
    cat > services/template-service/Dockerfile.local << 'EOF'
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
EOF

    cat > services/template-service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
psycopg2-binary==2.9.9
redis==5.0.1
pandas==2.1.4
numpy==1.24.3
python-dotenv==1.0.0
EOF

    cat > services/template-service/main.py << 'EOF'
from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Smart Trader Service", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": os.getenv("SERVICE_NAME", "template-service")}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": os.getenv("SERVICE_NAME", "template-service")}

@app.get("/metrics")
async def metrics():
    return {"metrics": "placeholder"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    print_status "Service templates created"
}

# Create development scripts
create_dev_scripts() {
    print_header "Creating Development Scripts"
    
    # Create development setup script
    cat > dev-setup.sh << 'EOF'
#!/bin/bash
echo "Setting up Smart Trader development environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start local services
docker-compose -f docker-compose.local.yml up -d

echo "Development environment ready!"
echo "Services available at:"
echo "- Web Portal: http://10.0.0.75:8000"
echo "- Data Service: http://10.0.0.75:8001"
echo "- Portfolio Service: http://10.0.0.80:8002"
echo "- Strategy Service: http://10.0.0.60:8003"
echo "- Risk Service: http://10.0.0.80:8004"
echo "- ML Service: http://10.0.0.60:8005"
echo "- API Gateway: http://10.0.0.75:8080"
EOF

    chmod +x dev-setup.sh
    
    # Create test script
    cat > test-all.sh << 'EOF'
#!/bin/bash
echo "Running tests for all services..."

for service in services/*; do
    if [ -d "$service" ]; then
        echo "Testing $service..."
        cd $service
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        if [ -f "requirements-dev.txt" ]; then
            pip install -r requirements-dev.txt
        fi
        if [ -d "tests" ]; then
            pytest tests/
        fi
        cd ../..
    fi
done

echo "All tests completed!"
EOF

    chmod +x test-all.sh
    
    print_status "Development scripts created"
}

# Main execution
main() {
    print_header "Smart Trader Local Environment Setup"
    
    check_servers
    setup_ssh
    install_docker
    install_nvidia_docker
    create_directories
    copy_configs
    setup_monitoring
    create_service_templates
    create_dev_scripts
    
    print_header "Setup Complete!"
    print_status "✅ All servers configured"
    print_status "✅ Docker installed on all servers"
    print_status "✅ NVIDIA Docker installed on GPU server"
    print_status "✅ Project directories created"
    print_status "✅ Configuration files copied"
    print_status "✅ Monitoring setup"
    print_status "✅ Service templates created"
    print_status "✅ Development scripts created"
    
    echo ""
    print_status "Next steps:"
    echo "1. Run ./deploy-local.sh to deploy basic infrastructure"
    echo "2. Develop services using the templates in services/"
    echo "3. Use ./test-all.sh to run tests"
    echo "4. Monitor services at http://10.0.0.75:9090 (Prometheus)"
    echo "5. Access web portal at http://10.0.0.75:8000"
    
    echo ""
    print_warning "Remember to:"
    echo "- Configure firewall rules for ports 8000-8080"
    echo "- Set up SSL certificates for production"
    echo "- Configure backup strategies"
    echo "- Set up log rotation"
}

# Run main function
main "$@"
