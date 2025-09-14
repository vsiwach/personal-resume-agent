# Sample Data Directory

This directory contains sample files to demonstrate how to structure your personal resume data.

## Files to Add

1. **Resume PDF**: Add your resume PDF file (e.g., `john_doe_resume.pdf`)
2. **Persona Text**: Create a `persona.txt` file with additional context about your professional background
3. **Other Documents**: Add any other relevant documents in supported formats (.pdf, .docx, .txt, .md)

## Privacy Note

- The actual `data/` directory is excluded from version control via `.gitignore`
- Never commit personal resume files or sensitive information to the repository
- Use the sample files as templates for your own data structure

## Supported File Formats

- **PDF**: Resume files, portfolios
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files
- **MD**: Markdown documents

The RAG system will automatically process all supported files in the `data/` directory and make them searchable through the MCP server.