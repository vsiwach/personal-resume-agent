#!/bin/bash
# Deploy NANDA Resume Agent to EC2
# This script uploads and deploys the application to the EC2 instance

set -e

# Load instance details if available
if [ -f "instance-details.json" ]; then
    ELASTIC_IP=$(jq -r '.elastic_ip' instance-details.json)
    KEY_FILE=$(jq -r '.key_file' instance-details.json)
    INSTANCE_ID=$(jq -r '.instance_id' instance-details.json)
else
    echo "❌ instance-details.json not found. Please run launch-ec2.sh first."
    exit 1
fi

# Check required environment variables
required_vars=("ANTHROPIC_API_KEY" "DOMAIN_NAME" "PUBLIC_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Environment variable $var is not set"
        echo "Please set: export $var=your_value"
        exit 1
    fi
done

echo "🚀 Deploying NANDA Resume Agent to EC2"
echo "======================================"
echo "Target: ubuntu@$ELASTIC_IP"
echo "Domain: $DOMAIN_NAME"
echo "Public URL: $PUBLIC_URL"
echo ""

# Test SSH connectivity
echo "🔍 Testing SSH connection..."
if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@$ELASTIC_IP "echo 'SSH connection successful'"; then
    echo "❌ SSH connection failed"
    exit 1
fi

# Create deployment directory on EC2
echo "📁 Creating deployment directory..."
ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
    sudo rm -rf /opt/nanda-resume-agent
    sudo mkdir -p /opt/nanda-resume-agent
    sudo chown ubuntu:ubuntu /opt/nanda-resume-agent
"

# Upload application files
echo "📤 Uploading application files..."
rsync -avz -e "ssh -i $KEY_FILE" \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    --exclude='conversation_logs' \
    --exclude='data/resume_vectordb' \
    ../../ ubuntu@$ELASTIC_IP:/opt/nanda-resume-agent/

# Upload NANDA adapter
echo "📤 Uploading NANDA adapter..."
rsync -avz -e "ssh -i $KEY_FILE" \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    ../../../adapter ubuntu@$ELASTIC_IP:/opt/nanda-resume-agent/

# Install dependencies and setup
echo "⚙️ Installing dependencies on EC2..."
ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
    cd /opt/nanda-resume-agent

    # Install Python dependencies
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-nanda.txt

    # Install NANDA adapter in development mode
    cd adapter && pip install -e . && cd ..

    # Create necessary directories
    mkdir -p logs conversation_logs

    # Set proper permissions
    chmod +x run_nanda_agent.py
"

# Create environment file
echo "🔧 Creating environment configuration..."
ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
    cd /opt/nanda-resume-agent
    cat > .env << EOF
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
PUBLIC_URL=$PUBLIC_URL
DOMAIN_NAME=$DOMAIN_NAME
AGENT_ID=vikram_resume_agent_prod
PORT=6000
IMPROVE_MESSAGES=true
PYTHONPATH=/opt/nanda-resume-agent/src
EOF
"

# Update systemd service with environment file
echo "🔧 Updating systemd service..."
ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
    sudo tee /etc/systemd/system/nanda-resume-agent.service > /dev/null << 'EOF'
[Unit]
Description=NANDA Resume Agent
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/nanda-resume-agent
EnvironmentFile=/opt/nanda-resume-agent/.env
ExecStartPre=/bin/bash -c 'source /opt/nanda-resume-agent/venv/bin/activate'
ExecStart=/opt/nanda-resume-agent/venv/bin/python /opt/nanda-resume-agent/run_nanda_agent.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
"

# Setup SSL certificates if domain is not localhost
if [ "$DOMAIN_NAME" != "localhost" ] && [ "$DOMAIN_NAME" != "$ELASTIC_IP" ]; then
    echo "🔐 Setting up SSL certificates..."
    ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
        # Stop nginx temporarily for certbot
        sudo systemctl stop nginx

        # Generate SSL certificate
        sudo certbot certonly \
            --standalone \
            --agree-tos \
            --email admin@$DOMAIN_NAME \
            --non-interactive \
            -d $DOMAIN_NAME

        # Update nginx configuration with SSL
        sudo tee /etc/nginx/sites-available/nanda-resume-agent > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name $DOMAIN_NAME;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;
    add_header X-Content-Type-Options \"nosniff\" always;

    location / {
        proxy_pass http://localhost:6000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://localhost:6000/api/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        access_log off;
    }
}
NGINXEOF

        sudo systemctl start nginx
    "
    echo "✅ SSL certificates configured"
else
    echo "ℹ️  Skipping SSL setup for localhost/IP deployment"
fi

# Start services
echo "🚀 Starting services..."
ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
    # Start and enable the NANDA agent service
    sudo systemctl start nanda-resume-agent
    sudo systemctl enable nanda-resume-agent

    # Restart nginx to ensure configuration is loaded
    sudo systemctl restart nginx
"

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Test deployment
echo "🔍 Testing deployment..."
if [ "$DOMAIN_NAME" != "localhost" ] && [ "$DOMAIN_NAME" != "$ELASTIC_IP" ]; then
    HEALTH_URL="https://$DOMAIN_NAME/health"
else
    HEALTH_URL="http://$ELASTIC_IP/health"
fi

if curl -f -s "$HEALTH_URL" >/dev/null; then
    echo "✅ Health check passed: $HEALTH_URL"
else
    echo "⚠️  Health check failed, checking service status..."
    ssh -i "$KEY_FILE" ubuntu@$ELASTIC_IP "
        echo 'Service status:'
        sudo systemctl status nanda-resume-agent --no-pager -l
        echo ''
        echo 'Recent logs:'
        sudo journalctl -u nanda-resume-agent --no-pager -l -n 20
    "
fi

echo ""
echo "🎉 Deployment completed!"
echo "======================="
if [ "$DOMAIN_NAME" != "localhost" ] && [ "$DOMAIN_NAME" != "$ELASTIC_IP" ]; then
    echo "🌐 Your NANDA Resume Agent is available at: https://$DOMAIN_NAME"
    echo "🔒 SSL/HTTPS: Enabled"
else
    echo "🌐 Your NANDA Resume Agent is available at: http://$ELASTIC_IP"
    echo "🔒 SSL/HTTPS: Disabled (localhost deployment)"
fi
echo "📋 Health check: $HEALTH_URL"
echo "🔧 SSH access: ssh -i $KEY_FILE ubuntu@$ELASTIC_IP"
echo ""
echo "📊 Monitor your agent:"
echo "   Logs: ssh -i $KEY_FILE ubuntu@$ELASTIC_IP 'sudo journalctl -u nanda-resume-agent -f'"
echo "   Status: ssh -i $KEY_FILE ubuntu@$ELASTIC_IP 'sudo systemctl status nanda-resume-agent'"
echo ""
echo "🌍 Your resume agent should now be registered in the global NANDA network!"