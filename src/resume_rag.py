"""
Resume RAG System
Simple RAG system for personal resume knowledge
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx

logger = logging.getLogger(__name__)


class ResumeRAGSystem:
    """Simple RAG system for resume knowledge"""

    def __init__(self, data_directory: str = "./data", persist_directory: str = "./data/resume_vectordb"):
        """Initialize Resume RAG system"""
        # Convert to absolute paths
        if not os.path.isabs(data_directory):
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_directory = os.path.join(script_dir, data_directory.lstrip('./'))

        if not os.path.isabs(persist_directory):
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_directory = os.path.join(script_dir, persist_directory.lstrip('./'))

        self.data_directory = data_directory
        self.persist_directory = persist_directory

        # Ensure directories exist
        os.makedirs(data_directory, exist_ok=True)
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="resume_knowledge",
            metadata={
                "description": "Personal resume and professional information",
                "created_at": datetime.now().isoformat()
            }
        )

        logger.info("Initialized Resume RAG system")

    def load_resume_files(self) -> bool:
        """Load all resume files from data directory"""
        try:
            resume_files = self._find_resume_files()

            if not resume_files:
                logger.warning("No resume files found in data directory")
                return False

            for file_path in resume_files:
                logger.info(f"Processing resume file: {file_path}")
                self._process_resume_file(file_path)

            logger.info(f"Successfully loaded {len(resume_files)} resume files")
            return True

        except Exception as e:
            logger.error(f"Failed to load resume files: {e}")
            return False

    def _find_resume_files(self) -> List[str]:
        """Find resume files in data directory"""
        resume_files = []
        supported_extensions = ['.pdf', '.docx', '.txt', '.md']

        for file in os.listdir(self.data_directory):
            if any(file.lower().endswith(ext) for ext in supported_extensions):
                if 'resume' in file.lower() or 'cv' in file.lower():
                    resume_files.append(os.path.join(self.data_directory, file))

        # If no files with resume/cv in name, take all supported files
        if not resume_files:
            for file in os.listdir(self.data_directory):
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    resume_files.append(os.path.join(self.data_directory, file))

        return resume_files

    def _process_resume_file(self, file_path: str) -> bool:
        """Process a single resume file"""
        try:
            content = self._extract_content(file_path)
            if not content:
                logger.warning(f"Could not extract content from {file_path}")
                return False

            # Split content into chunks
            chunks = self._split_into_chunks(content)

            # Add chunks to vector database
            for i, chunk in enumerate(chunks):
                doc_id = f"resume_{os.path.basename(file_path)}_{i}"

                metadata = {
                    "source_file": os.path.basename(file_path),
                    "file_path": file_path,
                    "chunk_index": i,
                    "document_type": "resume",
                    "processed_at": datetime.now().isoformat()
                }

                self.collection.add(
                    documents=[chunk],
                    ids=[doc_id],
                    metadatas=[metadata]
                )

            logger.info(f"Added {len(chunks)} chunks from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return False

    def _extract_content(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                return self._extract_pdf_content(file_path)
            elif file_ext == '.docx':
                return self._extract_docx_content(file_path)
            elif file_ext in ['.txt', '.md']:
                return self._extract_text_content(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""

        except Exception as e:
            logger.error(f"Failed to extract content from {file_path}: {e}")
            return ""

    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract PDF content: {e}")
            return ""

    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract DOCX content: {e}")
            return ""

    def _extract_text_content(self, file_path: str) -> str:
        """Extract text from TXT/MD file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Failed to extract text content: {e}")
            return ""

    def _split_into_chunks(self, content: str, chunk_size: int = 500) -> List[str]:
        """Split content into manageable chunks"""
        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())

        return chunks

    def search_resume(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search through resume content"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0

                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "distance": distance,
                        "relevance": max(0.0, 1 - distance)
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search resume: {e}")
            return []

    def get_resume_summary(self) -> str:
        """Get a summary of available resume information"""
        try:
            # Get all documents
            all_docs = self.collection.get()

            if not all_docs['documents']:
                return "No resume information available"

            # Basic statistics
            total_chunks = len(all_docs['documents'])
            source_files = set()

            for metadata in all_docs['metadatas']:
                if metadata and 'source_file' in metadata:
                    source_files.add(metadata['source_file'])

            summary = f"""
Resume Knowledge Base Summary:
- Total content chunks: {total_chunks}
- Source files: {', '.join(source_files) if source_files else 'None'}
- Knowledge areas available for queries about professional experience, skills, education, etc.
            """.strip()

            return summary

        except Exception as e:
            logger.error(f"Failed to get resume summary: {e}")
            return "Error retrieving resume summary"

    def answer_question(self, question: str) -> str:
        """Answer questions about the resume"""
        try:
            # Search for relevant content
            results = self.search_resume(question, n_results=3)

            if not results:
                return "I don't have information about that in the resume."

            # Combine relevant chunks
            context = "\n".join([result['content'] for result in results])

            # Simple response based on context
            response = f"Based on the resume information:\n\n{context[:800]}..."

            return response

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return "Sorry, I encountered an error while processing your question."


# Example usage and testing
if __name__ == "__main__":
    # Test the Resume RAG system
    rag = ResumeRAGSystem()

    # Load resume files
    print("🔄 Loading resume files...")
    loaded = rag.load_resume_files()

    if loaded:
        print("✅ Resume files loaded successfully")

        # Get summary
        summary = rag.get_resume_summary()
        print(f"\n📋 {summary}")

        # Test search
        test_queries = [
            "work experience",
            "skills and technologies",
            "education background"
        ]

        for query in test_queries:
            print(f"\n🔍 Searching for: {query}")
            results = rag.search_resume(query)
            print(f"Found {len(results)} relevant results")

            if results:
                print(f"Most relevant: {results[0]['content'][:200]}...")
    else:
        print("❌ Failed to load resume files")
        print("💡 Please add resume files (PDF, DOCX, TXT, MD) to the ./data directory")