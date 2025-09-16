# Smart Industrial Energy Monitoring System - Deployment Guide

## 🎯 Overview

This guide covers deployment options for the Smart Industrial Energy Monitoring & Optimization System, from development setup to production deployment.

## 🏗️ System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.4 GHz
- **RAM**: 4 GB
- **Storage**: 20 GB available space
- **Network**: 100 Mbps internet connection

### Recommended Production Requirements
- **CPU**: 4+ cores, 3.0 GHz
- **RAM**: 8+ GB
- **Storage**: 100+ GB SSD
- **Network**: 1 Gbps internet connection
- **Load Balancer**: For high availability setups

## 🐳 Docker Deployment (Recommended)

### Create Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    container_name: energy_monitor_db
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secure_password_123
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
    networks:
      - energy_monitor_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: energy_monitor_backend
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://admin:secure_password_123@mongodb:27017/energy_monitor?authSource=admin
      - DB_NAME=energy_monitor
      - JWT_SECRET_KEY=your-super-secure-jwt-secret-key-change-in-production
      - CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    networks:
      - energy_monitor_network
    volumes:
      - ./backend:/app
      - backend_logs:/app/logs

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: energy_monitor_frontend
    restart: unless-stopped
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - energy_monitor_network
    volumes:
      - ./frontend:/app
      - /app/node_modules

networks:
  energy_monitor_network:
    driver: bridge

volumes:
  mongodb_data:
  backend_logs:
```

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/ || exit 1

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Use nginx to serve the built app
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

### MongoDB Initialization

Create `mongo-init.js`:

```javascript
db = db.getSiblingDB('energy_monitor');

// Create collections with time-series optimization
db.createCollection("sensor_readings", {
  timeseries: {
    timeField: "timestamp",
    metaField: "device_id",
    granularity: "seconds"
  }
});

// Create indexes for better performance
db.users.createIndex({ "username": 1 }, { unique: true });
db.devices.createIndex({ "name": 1 }, { unique: true });
db.sensor_readings.createIndex({ "device_id": 1, "timestamp": -1 });
db.alerts.createIndex({ "device_id": 1, "acknowledged": 1, "timestamp": -1 });

print("Database initialized successfully");
```

### Deploy with Docker Compose

```bash
# Clone the repository
git clone <your-repo-url>
cd smart-energy-monitor

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (careful - deletes data!)
docker-compose down -v
```

## ☁️ Cloud Deployment Options

### AWS ECS Deployment

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name energy-monitor-cluster
```

2. **Push Images to ECR**
```bash
# Create repositories
aws ecr create-repository --repository-name energy-monitor-backend
aws ecr create-repository --repository-name energy-monitor-frontend

# Build and push images
docker build -t energy-monitor-backend ./backend
docker tag energy-monitor-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/energy-monitor-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/energy-monitor-backend:latest
```

3. **Create Task Definition** (`task-definition.json`)
```json
{
  "family": "energy-monitor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account>.dkr.ecr.<region>.amazonaws.com/energy-monitor-backend:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MONGO_URL",
          "value": "mongodb://your-mongo-connection-string"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/energy-monitor",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run Deployment

1. **Build and Deploy Backend**
```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/energy-monitor-backend ./backend

# Deploy to Cloud Run
gcloud run deploy energy-monitor-backend \
  --image gcr.io/PROJECT_ID/energy-monitor-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGO_URL="your-mongo-connection-string"
```

2. **Build and Deploy Frontend**
```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/energy-monitor-frontend ./frontend

# Deploy to Cloud Run
gcloud run deploy energy-monitor-frontend \
  --image gcr.io/PROJECT_ID/energy-monitor-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars REACT_APP_BACKEND_URL="https://your-backend-url"
```

### Azure Container Instances

```bash
# Create resource group
az group create --name energy-monitor-rg --location eastus

# Deploy backend
az container create \
  --resource-group energy-monitor-rg \
  --name energy-monitor-backend \
  --image your-registry/energy-monitor-backend:latest \
  --dns-name-label energy-monitor-backend \
  --ports 8001 \
  --environment-variables MONGO_URL="your-mongo-connection-string"

# Deploy frontend
az container create \
  --resource-group energy-monitor-rg \
  --name energy-monitor-frontend \
  --image your-registry/energy-monitor-frontend:latest \
  --dns-name-label energy-monitor-frontend \
  --ports 3000 \
  --environment-variables REACT_APP_BACKEND_URL="https://energy-monitor-backend.eastus.azurecontainer.io:8001"
```

## 🔧 Production Configuration

### Environment Variables

**Backend (.env)**:
```env
# Database
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/energy_monitor
DB_NAME=energy_monitor

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-256bits-minimum
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Monitoring
LOG_LEVEL=INFO
```

**Frontend (.env)**:
```env
# API Configuration
REACT_APP_BACKEND_URL=https://api.yourdomain.com

# Build Configuration
GENERATE_SOURCEMAP=false
REACT_APP_NODE_ENV=production
```

### Reverse Proxy Configuration (Nginx)

Create `nginx.conf`:
```nginx
upstream backend {
    server backend:8001;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Database Setup

### MongoDB Atlas (Recommended for Production)

1. **Create Cluster**
   - Go to MongoDB Atlas
   - Create a new cluster
   - Choose your preferred cloud provider and region

2. **Configure Network Access**
   - Add your application's IP addresses
   - For development: `0.0.0.0/0` (not recommended for production)

3. **Create Database User**
   - Create a user with read/write permissions
   - Generate a strong password

4. **Get Connection String**
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/energy_monitor?retryWrites=true&w=majority
   ```

### Self-hosted MongoDB

```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database and user
mongo
> use energy_monitor
> db.createUser({
    user: "energy_monitor_user",
    pwd: "secure_password_123",
    roles: [{ role: "readWrite", db: "energy_monitor" }]
  })
```

## 🔒 Security Considerations

### SSL/TLS Configuration

1. **Obtain SSL Certificate**
   - Use Let's Encrypt for free certificates
   - Or purchase from a commercial CA

2. **Configure HTTPS**
   ```bash
   # Using certbot for Let's Encrypt
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

### Firewall Configuration

```bash
# UFW Configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Application Security

1. **JWT Secret**: Use a strong, randomly generated secret key
2. **CORS**: Configure specific origins, not wildcards
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Ensure all inputs are properly validated
5. **Database Security**: Use strong passwords and network restrictions

## 📈 Monitoring & Logging

### Application Monitoring

Create `docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  grafana_data:
```

### Log Aggregation

```yaml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Backup strategy planned

### Deployment
- [ ] Build and test all containers
- [ ] Deploy database first
- [ ] Deploy backend services
- [ ] Deploy frontend
- [ ] Configure reverse proxy
- [ ] Test all endpoints
- [ ] Verify WebSocket connections

### Post-deployment
- [ ] Monitor application logs
- [ ] Test user registration/login
- [ ] Verify data ingestion
- [ ] Test alert system
- [ ] Set up monitoring dashboards
- [ ] Schedule regular backups
- [ ] Document deployment process

## 🔄 Backup & Recovery

### Database Backup

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb://username:password@host:port/energy_monitor" --out=/backups/mongo_$DATE
tar -czf /backups/mongo_$DATE.tar.gz /backups/mongo_$DATE
rm -rf /backups/mongo_$DATE

# Cron job for daily backups
0 2 * * * /path/to/backup-script.sh
```

### Application Backup

```bash
# Backup application data
docker run --rm \
  -v energy_monitor_mongodb_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/mongodb_data_backup.tar.gz /data
```

## 📞 Support & Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if services are running: `docker-compose ps`
   - Verify port mappings
   - Check firewall rules

2. **Database Connection Failed**
   - Verify MongoDB connection string
   - Check network connectivity
   - Verify credentials

3. **CORS Errors**
   - Update CORS_ORIGINS environment variable
   - Ensure frontend URL is included

4. **WebSocket Connection Failed**
   - Check if WebSocket endpoint is accessible
   - Verify proxy configuration for WebSocket upgrades

### Getting Help

- Check application logs: `docker-compose logs`
- Monitor system resources: `docker stats`
- Review error messages in browser console
- Consult API documentation for endpoint details

---

**For additional deployment support, please refer to the main README.md or contact the development team.**