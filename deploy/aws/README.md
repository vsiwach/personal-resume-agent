# AWS Deployment Guide for NANDA Resume Agent

## 🚀 Quick Start

Deploy your NANDA Resume Agent to AWS with public IP and SSL for global NANDA network registration.

### Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Domain name** (optional, but recommended for SSL)
3. **Environment variables** set:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export DOMAIN_NAME="your-domain.com"  # or use IP
   export PUBLIC_URL="https://your-domain.com"
   ```

### One-Command Deployment

```bash
# 1. Launch EC2 instance
./launch-ec2.sh

# 2. Configure your domain DNS (if using custom domain)
# Point your domain to the Elastic IP shown in the output

# 3. Deploy the application
./deploy-to-ec2.sh
```

## 📋 Detailed Steps

### Step 1: Launch EC2 Instance

```bash
cd deploy/aws
./launch-ec2.sh
```

**What this does:**
- ✅ Creates EC2 t3.medium instance (optimized for ML workloads)
- ✅ Sets up security groups (ports 22, 80, 443, 6000)
- ✅ Allocates and associates Elastic IP
- ✅ Installs Docker, Python, nginx via user-data
- ✅ Configures systemd service for auto-restart
- ✅ Saves instance details to `instance-details.json`

**Output:**
```
🎉 EC2 Instance Setup Complete!
================================
📋 Connection Details:
   Public IP (Elastic): 54.123.45.67
   SSH Command: ssh -i nanda-resume-key.pem ubuntu@54.123.45.67

📝 Next Steps:
1. Configure your domain to point to: 54.123.45.67
2. Run the deployment script to install the NANDA agent
3. Set up SSL certificates for your domain
```

### Step 2: Configure Domain (Optional)

If using a custom domain:

1. **Update DNS Records:**
   - Add A record: `your-domain.com` → `54.123.45.67`
   - Wait for DNS propagation (5-10 minutes)

2. **Verify DNS:**
   ```bash
   dig your-domain.com +short
   # Should return your Elastic IP
   ```

### Step 3: Deploy Application

```bash
# Set required environment variables
export ANTHROPIC_API_KEY="your-key"
export DOMAIN_NAME="your-domain.com"
export PUBLIC_URL="https://your-domain.com"

# Deploy
./deploy-to-ec2.sh
```

**What this does:**
- ✅ Uploads application code via rsync
- ✅ Installs Python dependencies and NANDA adapter
- ✅ Configures environment variables
- ✅ Sets up SSL certificates (if domain provided)
- ✅ Starts services (NANDA agent + nginx)
- ✅ Configures systemd for auto-restart
- ✅ Tests deployment health

## 🔧 Architecture

```
Internet → Route 53/DNS → Elastic IP → EC2 Instance
                                         ├── nginx (80/443) → NANDA Agent (6000)
                                         ├── systemd service (auto-restart)
                                         └── SSL/TLS (Let's Encrypt)
```

### Service Architecture

```
EC2 Instance
├── nginx (reverse proxy)
│   ├── HTTP → HTTPS redirect
│   ├── SSL termination
│   └── Proxy to localhost:6000
├── NANDA Resume Agent
│   ├── Personal Resume Agent (RAG)
│   ├── NANDA Integration Layer
│   └── A2A Server (port 6000)
└── systemd service
    ├── Auto-restart on failure
    ├── Log management
    └── Environment configuration
```

## 🔍 Monitoring & Management

### Service Management

```bash
# SSH to your instance
ssh -i nanda-resume-key.pem ubuntu@ELASTIC_IP

# Check service status
sudo systemctl status nanda-resume-agent

# View logs
sudo journalctl -u nanda-resume-agent -f

# Restart service
sudo systemctl restart nanda-resume-agent

# Stop/start service
sudo systemctl stop nanda-resume-agent
sudo systemctl start nanda-resume-agent
```

### Health Monitoring

```bash
# Health check endpoint
curl https://your-domain.com/health

# A2A communication test
curl -X POST https://your-domain.com/a2a \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your Python skills"}'
```

### Log Locations

- **Application Logs:** `/opt/nanda-resume-agent/logs/`
- **System Logs:** `sudo journalctl -u nanda-resume-agent`
- **Nginx Logs:** `/var/log/nginx/`
- **Conversation Logs:** `/opt/nanda-resume-agent/conversation_logs/`

## 🔐 Security

### SSL/TLS Configuration

- **Automatic SSL:** Let's Encrypt certificates auto-generated
- **HTTPS Redirect:** HTTP automatically redirects to HTTPS
- **Security Headers:** X-Frame-Options, XSS Protection, etc.
- **Rate Limiting:** API endpoints rate-limited

### Security Groups

- **Port 22:** SSH (your IP only recommended)
- **Port 80:** HTTP (redirects to HTTPS)
- **Port 443:** HTTPS (public access)
- **Port 6000:** A2A communication (public access for agents)

### Firewall Recommendations

```bash
# Restrict SSH to your IP only
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_IP/32
```

## 💰 Cost Estimation

### Monthly AWS Costs

- **t3.medium EC2:** ~$30-35/month
- **Elastic IP:** $3.65/month (when attached)
- **EBS Storage:** ~$5/month (20GB)
- **Data Transfer:** Variable (minimal for most use cases)

**Total:** ~$40-45/month

### Cost Optimization

- **Spot Instances:** Use for development (50-90% savings)
- **Reserved Instances:** 1-year commitment (30-50% savings)
- **Auto Scaling:** Scale to zero during off-hours (development)

## 🔧 Troubleshooting

### Common Issues

1. **Agent won't start:**
   ```bash
   # Check logs
   sudo journalctl -u nanda-resume-agent --no-pager -l -n 50

   # Check environment variables
   cat /opt/nanda-resume-agent/.env

   # Test manually
   cd /opt/nanda-resume-agent
   source venv/bin/activate
   python run_nanda_agent.py
   ```

2. **SSL certificate issues:**
   ```bash
   # Check certificate status
   sudo certbot certificates

   # Renew certificate
   sudo certbot renew

   # Test nginx config
   sudo nginx -t
   ```

3. **NANDA registration fails:**
   ```bash
   # Check PUBLIC_URL is set correctly
   echo $PUBLIC_URL

   # Test external connectivity
   curl -f https://your-domain.com/health

   # Check A2A endpoint
   curl -f https://your-domain.com/a2a
   ```

### Log Analysis

```bash
# Recent application errors
sudo journalctl -u nanda-resume-agent --since "1 hour ago" | grep ERROR

# NANDA registration logs
sudo journalctl -u nanda-resume-agent | grep -E "(NANDA|registration|PUBLIC_URL)"

# Network connectivity issues
sudo journalctl -u nanda-resume-agent | grep -E "(connection|timeout|refused)"
```

## 🚀 Production Optimizations

### Performance Tuning

1. **Increase instance size** for better ML performance:
   ```bash
   # Stop instance
   aws ec2 stop-instances --instance-ids i-xxxxxxxxx

   # Change instance type
   aws ec2 modify-instance-attribute \
       --instance-id i-xxxxxxxxx \
       --instance-type Value=t3.large

   # Start instance
   aws ec2 start-instances --instance-ids i-xxxxxxxxx
   ```

2. **Enable CloudWatch monitoring:**
   ```bash
   # Install CloudWatch agent
   sudo apt-get install amazon-cloudwatch-agent
   ```

### Backup & Recovery

1. **EBS Snapshots:**
   ```bash
   # Create snapshot
   aws ec2 create-snapshot \
       --volume-id vol-xxxxxxxxx \
       --description "NANDA agent backup $(date)"
   ```

2. **Application Backup:**
   ```bash
   # Backup resume data and configuration
   rsync -avz ubuntu@ELASTIC_IP:/opt/nanda-resume-agent/data/ ./backup/
   rsync -avz ubuntu@ELASTIC_IP:/opt/nanda-resume-agent/.env ./backup/
   ```

## 🌍 Global NANDA Network

Once deployed with a public IP and proper configuration, your agent will:

- ✅ **Register automatically** with the NANDA network
- ✅ **Be discoverable** by other agents globally
- ✅ **Receive A2A messages** about your professional background
- ✅ **Provide enhanced responses** using your resume knowledge
- ✅ **Maintain privacy** (only responses shared, not raw resume data)

### Expected Logs

```
🚀 NANDA starting agent_bridge server with custom logic...
✅ PUBLIC_URL set: https://your-domain.com
🌐 Agent registered with NANDA network
✅ Global discovery enabled
🔄 A2A server listening on port 6000
```

## 📞 Support

### Instance Management

- **AWS Console:** Monitor via EC2 dashboard
- **CloudWatch:** Set up alarms for high CPU/memory
- **Auto-restart:** Systemd automatically restarts on failure

### Application Support

- **Health Endpoint:** `/health` for monitoring tools
- **Logs:** Structured logging for debugging
- **Graceful Shutdown:** SIGTERM handling

---

## ✅ Deployment Checklist

- [ ] AWS CLI configured with appropriate permissions
- [ ] Domain name configured (optional)
- [ ] Environment variables set (ANTHROPIC_API_KEY, DOMAIN_NAME, PUBLIC_URL)
- [ ] Run `./launch-ec2.sh` successfully
- [ ] DNS configured to point to Elastic IP
- [ ] Run `./deploy-to-ec2.sh` successfully
- [ ] Health check passing
- [ ] NANDA registration successful (no WARNING messages)
- [ ] A2A communication working
- [ ] SSL certificates valid (if using HTTPS)

**🎉 Your NANDA Resume Agent is now globally accessible!**