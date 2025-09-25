#!/bin/bash
# EC2 User Data Script - Runs on instance boot
# Installs Docker, Python, and basic dependencies

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    jq \
    htop \
    tree \
    nginx \
    certbot \
    python3-certbot-nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Python 3.10 and pip
apt-get install -y python3.10 python3.10-venv python3-pip

# Create application directory
mkdir -p /opt/nanda-resume-agent
chown ubuntu:ubuntu /opt/nanda-resume-agent

# Create systemd service file for the agent
cat > /etc/systemd/system/nanda-resume-agent.service << 'EOF'
[Unit]
Description=NANDA Resume Agent
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/nanda-resume-agent
Environment="PYTHONPATH=/opt/nanda-resume-agent/src"
ExecStart=/usr/bin/python3 /opt/nanda-resume-agent/run_nanda_agent.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable the service (but don't start it yet)
systemctl daemon-reload
systemctl enable nanda-resume-agent

# Configure nginx for reverse proxy (placeholder)
cat > /etc/nginx/sites-available/nanda-resume-agent << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:6000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://localhost:6000/api/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/nanda-resume-agent /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl enable nginx
systemctl restart nginx

# Create log directory
mkdir -p /var/log/nanda-resume-agent
chown ubuntu:ubuntu /var/log/nanda-resume-agent

# Signal completion
echo "✅ EC2 User Data Script Completed at $(date)" > /var/log/user-data-completion.log