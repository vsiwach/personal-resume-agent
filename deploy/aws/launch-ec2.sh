#!/bin/bash
# AWS EC2 Launch Script for NANDA Resume Agent
# This script creates and configures an EC2 instance for production deployment

set -e

# Configuration
INSTANCE_NAME="nanda-resume-agent"
INSTANCE_TYPE="t3.small"
KEY_NAME="nanda-resume-key"
SECURITY_GROUP_NAME="nanda-resume-sg"
AMI_ID="ami-03c89b290c1f0cf4e" # Ubuntu 22.04 LTS (us-east-1)
REGION="us-east-1"
AVAILABILITY_ZONE="us-east-1a"

echo "🚀 AWS EC2 Deployment: NANDA Resume Agent"
echo "=========================================="
echo "Instance Type: $INSTANCE_TYPE"
echo "Region: $REGION"
echo "AMI: $AMI_ID"
echo ""

# Check AWS CLI configuration
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Create key pair if it doesn't exist
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "🔑 Creating key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --region "$REGION" \
        --query 'KeyMaterial' \
        --output text > "${KEY_NAME}.pem"
    chmod 600 "${KEY_NAME}.pem"
    echo "✅ Key pair created and saved as ${KEY_NAME}.pem"
else
    echo "✅ Key pair $KEY_NAME already exists"
fi

# Create security group if it doesn't exist
if ! aws ec2 describe-security-groups --group-names "$SECURITY_GROUP_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "🔒 Creating security group: $SECURITY_GROUP_NAME"
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for NANDA Resume Agent" \
        --region "$REGION" \
        --query 'GroupId' \
        --output text)

    # Add rules for HTTP, HTTPS, SSH, and A2A communication
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 6000 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"

    echo "✅ Security group created with ID: $SECURITY_GROUP_ID"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names "$SECURITY_GROUP_NAME" \
        --region "$REGION" \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
    echo "✅ Security group $SECURITY_GROUP_NAME already exists: $SECURITY_GROUP_ID"
fi

# Launch EC2 instance
echo "🖥️  Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --count 1 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SECURITY_GROUP_ID" \
    --placement AvailabilityZone="$AVAILABILITY_ZONE" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --user-data file://user-data.sh \
    --region "$REGION" \
    --query "Instances[0].InstanceId" \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance to be running
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

# Get instance details
INSTANCE_INFO=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION" \
    --query 'Reservations[0].Instances[0]')

PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress')
PRIVATE_IP=$(echo "$INSTANCE_INFO" | jq -r '.PrivateIpAddress')

echo "✅ Instance is running!"
echo "📋 Instance Details:"
echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   Private IP: $PRIVATE_IP"
echo "   Key File: ${KEY_NAME}.pem"
echo ""

# Create or allocate Elastic IP
echo "🌐 Allocating Elastic IP..."
ELASTIC_IP_ALLOCATION=$(aws ec2 allocate-address \
    --domain vpc \
    --region "$REGION" \
    --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value=$INSTANCE_NAME-eip}]" \
    --query 'AllocationId' \
    --output text)

ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids "$ELASTIC_IP_ALLOCATION" \
    --region "$REGION" \
    --query 'Addresses[0].PublicIp' \
    --output text)

# Associate Elastic IP with instance
aws ec2 associate-address \
    --instance-id "$INSTANCE_ID" \
    --allocation-id "$ELASTIC_IP_ALLOCATION" \
    --region "$REGION" >/dev/null

echo "✅ Elastic IP allocated and associated: $ELASTIC_IP"

# Wait for instance to be accessible
echo "⏳ Waiting for instance to be accessible via SSH..."
for i in {1..30}; do
    if ssh -i "${KEY_NAME}.pem" -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@"$ELASTIC_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
        echo "✅ SSH connection successful"
        break
    fi
    echo "   Attempt $i/30: SSH not ready, waiting..."
    sleep 10
done

echo ""
echo "🎉 EC2 Instance Setup Complete!"
echo "================================"
echo "📋 Connection Details:"
echo "   Public IP (Elastic): $ELASTIC_IP"
echo "   SSH Command: ssh -i ${KEY_NAME}.pem ubuntu@$ELASTIC_IP"
echo ""
echo "📝 Next Steps:"
echo "1. Configure your domain to point to: $ELASTIC_IP"
echo "2. Run the deployment script to install the NANDA agent"
echo "3. Set up SSL certificates for your domain"
echo ""
echo "💡 Save these details for deployment!"

# Save instance details to file
cat > instance-details.json << EOF
{
  "instance_id": "$INSTANCE_ID",
  "elastic_ip": "$ELASTIC_IP",
  "private_ip": "$PRIVATE_IP",
  "key_file": "${KEY_NAME}.pem",
  "security_group_id": "$SECURITY_GROUP_ID",
  "region": "$REGION"
}
EOF

echo "📄 Instance details saved to: instance-details.json"