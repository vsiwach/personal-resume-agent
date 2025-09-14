# Personal Resume Agent

A personalized AI agent that reads your resume and provides intelligent responses about your professional background through a standardized MCP (Model Context Protocol) server interface. Built with RAG (Retrieval-Augmented Generation) capabilities to make your professional information queryable through Claude Desktop.

## Features

- **Resume Processing**: Automatically reads and processes resume files (PDF, DOCX, TXT, MD)
- **RAG System**: Uses ChromaDB and sentence transformers for intelligent content retrieval
- **MCP Server**: Exposes functionality through standardized MCP protocol
- **Skill Matching**: Analyzes how well your skills match job requirements
- **Natural Language Interface**: Ask questions about your experience, skills, education, etc.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Your Resume**
   ```bash
   # Place your resume files in the data/ directory
   cp your-resume.pdf data/
   ```

3. **Test the Agent**
   ```bash
   cd src
   python personal_resume_agent.py
   ```

4. **Run as MCP Server**
   ```bash
   cd src
   python mcp_resume_server.py
   ```

## Project Structure

```
personal-resume-agent/
├── src/                    # Source code
│   ├── resume_rag.py      # RAG system for resume processing
│   ├── personal_resume_agent.py  # Main agent logic
│   └── mcp_resume_server.py      # MCP server implementation
├── data/                   # Resume files storage
├── tests/                  # Test files
├── docs/                   # Documentation
├── examples/               # Usage examples
└── requirements.txt        # Python dependencies
```

## Usage Examples

### Direct Agent Usage

```python
from personal_resume_agent import PersonalResumeAgent

agent = PersonalResumeAgent()
await agent.initialize()

# Ask questions about your resume
result = await agent.process_query("What programming languages do I know?")
print(result['response'])

# Analyze skill match for a job
match = await agent.get_skill_match("Python, React, AWS, Docker")
print(f"Match: {match['match_percentage']}%")
```

### MCP Server Tools

The MCP server exposes these tools:

- `query_resume`: Ask questions about resume content
- `get_agent_info`: Get agent capabilities and status
- `analyze_skill_match`: Compare skills with job requirements
- `get_resume_summary`: Get overview of resume knowledge base

## Configuration

### Claude Desktop Integration

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "personal-resume": {
      "command": "python",
      "args": ["/path/to/personal-resume-agent/src/mcp_resume_server.py"],
      "cwd": "/path/to/personal-resume-agent"
    }
  }
}
```

## Supported File Formats

- **PDF**: Extracted using PyPDF2
- **DOCX**: Processed with python-docx
- **TXT/MD**: Plain text files

## Requirements

- Python 3.8+
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- PyPDF2 for PDF processing
- python-docx for Word documents

## Privacy & Security

🔒 **Important Privacy Notes:**

- All resume data is processed **locally** on your machine
- No personal information is sent to external services
- Vector database is stored locally in `data/resume_vectordb/`
- The `data/` directory is excluded from version control
- Never commit personal resume files to public repositories

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Resume Files  │───▶│   RAG System    │───▶│   MCP Server    │
│   (PDF/DOCX)    │    │  (ChromaDB +    │    │  (Claude Tool)  │
│                 │    │  Transformers)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Personal Resume │
                       │     Agent       │
                       │ (Query Engine)  │
                       └─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details.