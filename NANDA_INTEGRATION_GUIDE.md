# NANDA Integration Guide for Personal Resume Agent

## 🎉 Integration Complete!

Your Personal Resume Agent has been successfully integrated with the NANDA network! This integration makes your resume globally discoverable and queryable by other agents while preserving all local functionality.

## 🏗️ Architecture Overview

```
Personal Resume Agent + NANDA Adapter
├── Resume Files (PDF/DOCX/TXT/MD) → ChromaDB Vector Database
├── Personal Resume Agent (Local RAG System)
├── NANDA Integration Layer (Message Routing)
└── A2A Network Server (Global Discovery)
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- ANTHROPIC_API_KEY environment variable set
- Resume files in `data/` directory

### 2. Installation Complete ✅
- ✅ NANDA Adapter installed
- ✅ Personal Resume Agent ready
- ✅ Integration layer created
- ✅ Dependencies resolved

### 3. Run Your Agent

```bash
# Simple startup
python3 run_nanda_agent.py

# Or with explicit environment
ANTHROPIC_API_KEY=your_key DOMAIN_NAME=localhost python3 run_nanda_agent.py
```

## 📁 Project Structure

```
personal-resume-agent/
├── src/
│   ├── personal_resume_agent.py      # Original resume agent
│   ├── resume_rag.py                 # RAG system
│   ├── mcp_resume_server.py          # MCP server
│   └── resume_nanda_agent.py         # 🆕 NANDA integration
├── data/
│   ├── sample/                       # Sample resume data
│   └── [your-resume-files]           # Add your resume files here
├── run_nanda_agent.py                # 🆕 Easy startup script
├── requirements-nanda.txt            # 🆕 All dependencies
└── NANDA_INTEGRATION_GUIDE.md        # This guide
```

## 🔧 Configuration

### Environment Variables

**Required:**
- `ANTHROPIC_API_KEY`: Your Anthropic API key

**Optional:**
- `DOMAIN_NAME`: Your domain (default: localhost)
- `AGENT_ID`: Custom agent ID (default: auto-generated)
- `PORT`: Server port (default: 6000)

### Resume Files
Place your resume files in the `data/` directory:
- Supported formats: PDF, DOCX, TXT, MD
- The agent will automatically process and index them
- Sample files are available in `data/sample/`

## 🌐 NANDA Network Features

### What Your Agent Can Do Now:

1. **Local Resume Queries** (existing functionality)
   - Answer questions about your experience
   - Skill matching for job requirements
   - Career progression details

2. **Global Network Integration** (new!)
   - Discoverable by other agents worldwide
   - Receive queries from external agents
   - Enhanced responses with professional context
   - Agent-to-Agent (A2A) communication

### Message Enhancement Examples:

**Input:** "Tell me about Python experience"
**Output:** "I have 5+ years of Python experience, specializing in web development with Flask/Django, data science with pandas/scikit-learn, and AI/ML applications. I've used Python extensively in my roles at MIT Sloan and various tech companies for building scalable applications and data processing pipelines."

**Input:** "What are your cloud skills?"
**Output:** "I have extensive cloud experience with AWS (EC2, S3, Lambda, RDS), Google Cloud Platform, and Azure. I've architected and deployed microservices, managed containerized applications with Docker/Kubernetes, and implemented CI/CD pipelines. This experience spans my work in distributed systems and cloud-native applications."

## 🔍 Testing Your Integration

### 1. Check Agent Status
```bash
# The startup script will show:
✅ NANDA Adapter: Available
✅ Personal Resume Agent: Available
✅ Resume NANDA Integration: Available
```

### 2. Verify Server Running
```
🚀 Starting Agent bridge on port 6000
A2A server running on http://0.0.0.0:6000/a2a
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:6000/api/health

# A2A communication
curl -X POST http://localhost:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your Python skills"}'
```

## 🌍 Production Deployment

For production deployment with global discovery:

### 1. Domain Setup
```bash
export DOMAIN_NAME=yourdomain.com
export ANTHROPIC_API_KEY=your_key
```

### 2. SSL Certificates
```bash
# Generate SSL certificates
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to current directory
sudo cp -L /etc/letsencrypt/live/yourdomain.com/fullchain.pem .
sudo cp -L /etc/letsencrypt/live/yourdomain.com/privkey.pem .
sudo chown $USER:$USER fullchain.pem privkey.pem
chmod 600 fullchain.pem privkey.pem
```

### 3. Start Production Server
```bash
python3 run_nanda_agent.py
```

The agent will automatically:
- Register with the global NANDA network
- Enable SSL/HTTPS communication
- Provide global discoverability
- Generate enrollment links for registration

## 🎯 Key Features

### Resume-Enhanced Messaging
- **Smart Query Classification**: Automatically routes queries to appropriate resume sections
- **Context-Aware Responses**: Adds professional context to all interactions
- **Fallback Handling**: Graceful responses when resume data unavailable
- **Confidence Scoring**: Provides confidence levels for responses

### Professional Networking
- **Global Discovery**: Your professional profile queryable worldwide
- **Skill Matching**: Advanced matching against job requirements
- **Career Consultation**: Other agents can query your experience
- **Professional Representation**: AI-powered professional avatar

### Privacy & Security
- **Local Processing**: All resume data processed locally
- **Controlled Sharing**: You control what information is shared
- **Secure Communication**: SSL/TLS encrypted agent communication
- **No Data Transmission**: Resume files never leave your system

## 🔧 Troubleshooting

### Common Issues:

1. **Missing Resume Files**
   ```
   ⚠️ No resume files found in data directory
   ```
   **Solution:** Add your resume files to the `data/` directory

2. **API Key Issues**
   ```
   ❌ ANTHROPIC_API_KEY: Not set
   ```
   **Solution:** Set your API key: `export ANTHROPIC_API_KEY=your_key`

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'nanda_adapter'
   ```
   **Solution:** Run `pip install -e /path/to/adapter` from the adapter directory

4. **Port Conflicts**
   ```
   OSError: [Errno 48] Address already in use
   ```
   **Solution:** Set different port: `export PORT=6001`

## 📊 Monitoring

### Logs Location:
- **Conversation Logs**: `conversation_logs/`
- **Application Logs**: Console output
- **ChromaDB Data**: `data/resume_vectordb/`

### Health Monitoring:
- **Health Endpoint**: `GET /api/health`
- **A2A Status**: `GET /a2a`
- **Agent Info**: Available in startup logs

## 🚀 Next Steps

1. **Add Your Resume**: Place your resume files in `data/` directory
2. **Test Locally**: Use the startup script to test functionality
3. **Deploy to Production**: Set up domain and SSL for global access
4. **Monitor Usage**: Check logs and health endpoints
5. **Extend Functionality**: Add custom message improvement logic

## 💡 Advanced Usage

### Custom Message Logic
You can extend the `ResumeNANDAWrapper` class to add:
- Industry-specific responses
- Custom skill classifications
- Advanced query routing
- Integration with other AI services

### Integration with Other Agents
Your agent can now:
- Communicate with other professional agents
- Participate in multi-agent workflows
- Share expertise in agent networks
- Collaborate on complex tasks

## 📞 Support

For issues and questions:
- **Personal Resume Agent**: Check the original repository
- **NANDA Adapter**: https://github.com/projnanda/adapter
- **Integration Issues**: Review logs and troubleshooting section

---

## 🎉 Congratulations!

Your Personal Resume Agent is now part of the global NANDA agent network!

🌟 **Key Achievement**: Your professional expertise is now accessible to AI agents worldwide while maintaining complete privacy and local control over your data.

**Your agent is ready to:**
- Represent your professional profile globally ✅
- Answer career-related questions intelligently ✅
- Connect with other professional agents ✅
- Maintain privacy and data security ✅

Welcome to the future of AI-powered professional networking! 🤖🌍