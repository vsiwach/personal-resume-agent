"""
Personal Resume Agent
AI agent with knowledge of personal resume and professional background
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from resume_rag import ResumeRAGSystem

logger = logging.getLogger(__name__)


class PersonalResumeAgent:
    """AI agent with personal resume knowledge"""

    def __init__(self, data_directory: str = "./data"):
        """Initialize the personal resume agent"""
        # Convert to absolute path to handle MCP server context
        import os
        if not os.path.isabs(data_directory):
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_directory = os.path.join(script_dir, data_directory.lstrip('./'))

        self.data_directory = data_directory
        self.rag_system = ResumeRAGSystem(data_directory=data_directory)
        self.initialized = False

        # Agent personality and context
        self.agent_context = """
        I am your personal resume agent. I have comprehensive knowledge of your professional background,
        skills, experience, and qualifications. I can help you with:

        - Answering questions about your work experience
        - Highlighting relevant skills for specific roles
        - Providing details about your education and certifications
        - Crafting tailored responses for job applications
        - Explaining your career progression and achievements

        I always provide accurate, professional responses based on your actual resume content.
        """

    async def initialize(self) -> bool:
        """Initialize the agent by loading resume data"""
        try:
            logger.info("Initializing Personal Resume Agent...")

            # Load resume files into RAG system
            success = self.rag_system.load_resume_files()

            if success:
                self.initialized = True
                logger.info("✅ Personal Resume Agent initialized successfully")
                return True
            else:
                logger.warning("⚠️ No resume files found, agent will have limited functionality")
                self.initialized = True  # Still allow agent to run
                return True

        except Exception as e:
            logger.error(f"Failed to initialize Personal Resume Agent: {e}")
            return False

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent and its capabilities"""
        resume_summary = self.rag_system.get_resume_summary()

        return {
            "agent_name": "Personal Resume Agent",
            "description": "AI agent with comprehensive knowledge of personal resume and professional background",
            "initialized": self.initialized,
            "capabilities": [
                "Answer questions about work experience",
                "Highlight relevant skills for job applications",
                "Provide education and certification details",
                "Explain career progression and achievements",
                "Generate tailored professional responses"
            ],
            "resume_summary": resume_summary,
            "last_updated": datetime.now().isoformat()
        }

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query and return a response"""
        try:
            if not self.initialized:
                return {
                    "response": "Agent not initialized. Please initialize first.",
                    "source": "system_error",
                    "confidence": 0.0
                }

            # Classify the query type
            query_type = self._classify_query(query.lower())

            # Search for relevant resume content
            search_results = self.rag_system.search_resume(query, n_results=5)

            # Generate response based on query type and search results
            response = await self._generate_response(query, query_type, search_results)

            return {
                "response": response,
                "query_type": query_type,
                "source_chunks": len(search_results),
                "confidence": self._calculate_confidence(search_results),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {
                "response": "I encountered an error while processing your question. Please try again.",
                "source": "system_error",
                "confidence": 0.0
            }

    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_keywords = {
            "experience": ["experience", "work", "job", "employment", "career", "role", "position"],
            "skills": ["skills", "technology", "programming", "languages", "tools", "expertise"],
            "education": ["education", "degree", "university", "college", "school", "certification"],
            "achievements": ["achievements", "accomplishments", "awards", "recognition", "success"],
            "projects": ["projects", "portfolio", "built", "developed", "created"],
            "contact": ["contact", "email", "phone", "location", "address", "reach"],
            "general": []
        }

        for category, keywords in query_keywords.items():
            if any(keyword in query for keyword in keywords):
                return category

        return "general"

    async def _generate_response(self, query: str, query_type: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate a response based on query and search results"""
        if not search_results:
            return self._get_no_info_response(query_type)

        # Combine relevant content
        relevant_content = []
        for result in search_results[:3]:  # Use top 3 most relevant results
            if result['relevance'] >= 0.0:  # Use all results (distance-based filtering)
                relevant_content.append(result['content'])

        if not relevant_content:
            return self._get_no_info_response(query_type)

        # Create contextual response
        context = "\n".join(relevant_content)

        response_template = self._get_response_template(query_type)
        response = f"{response_template}\n\n{context[:800]}"

        # Add source attribution
        if len(search_results) > 0:
            response += f"\n\n(Based on {len(search_results)} relevant sections from resume)"

        return response

    def _get_response_template(self, query_type: str) -> str:
        """Get response template based on query type"""
        templates = {
            "experience": "Here's information about professional experience:",
            "skills": "Here are the relevant skills and technologies:",
            "education": "Here's the educational background:",
            "achievements": "Here are notable achievements and accomplishments:",
            "projects": "Here are relevant projects and developments:",
            "contact": "Here's the contact information:",
            "general": "Based on the resume information:"
        }
        return templates.get(query_type, templates["general"])

    def _get_no_info_response(self, query_type: str) -> str:
        """Get response when no relevant information is found"""
        responses = {
            "experience": "I don't have specific information about that work experience in the resume.",
            "skills": "I don't have information about those particular skills in the resume.",
            "education": "I don't have information about that educational background in the resume.",
            "achievements": "I don't have information about those specific achievements in the resume.",
            "projects": "I don't have information about those particular projects in the resume.",
            "contact": "I don't have contact information available in the resume.",
            "general": "I don't have information about that topic in the resume."
        }
        return responses.get(query_type, responses["general"])

    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0

        # Average relevance of top results
        top_results = search_results[:3]
        if top_results:
            avg_relevance = sum(result['relevance'] for result in top_results) / len(top_results)
            return min(avg_relevance, 1.0)

        return 0.0

    async def get_skill_match(self, job_requirements: str) -> Dict[str, Any]:
        """Analyze skill match for a job description"""
        try:
            # Search for skills-related content
            skills_results = self.rag_system.search_resume("skills technologies programming", n_results=5)

            if not skills_results:
                return {
                    "match_percentage": 0,
                    "matching_skills": [],
                    "missing_skills": [],
                    "recommendations": "No skills information available in resume"
                }

            # Extract skills content
            skills_content = " ".join([result['content'] for result in skills_results])

            # Simple keyword matching (could be enhanced with NLP)
            job_keywords = job_requirements.lower().split()
            skills_keywords = skills_content.lower().split()

            matching_skills = []
            for keyword in job_keywords:
                if len(keyword) > 3 and keyword in skills_keywords:
                    matching_skills.append(keyword)

            match_percentage = min((len(matching_skills) / max(len(job_keywords), 1)) * 100, 100)

            return {
                "match_percentage": round(match_percentage, 1),
                "matching_skills": matching_skills[:10],  # Top 10 matches
                "skills_summary": skills_content[:500],
                "confidence": self._calculate_confidence(skills_results)
            }

        except Exception as e:
            logger.error(f"Failed to analyze skill match: {e}")
            return {
                "match_percentage": 0,
                "error": str(e)
            }


# Example usage and testing
async def test_personal_agent():
    """Test the personal resume agent"""
    agent = PersonalResumeAgent()

    print("🤖 Initializing Personal Resume Agent...")
    initialized = await agent.initialize()

    if not initialized:
        print("❌ Failed to initialize agent")
        return

    print("✅ Agent initialized successfully")

    # Get agent info
    info = agent.get_agent_info()
    print(f"\n📋 Agent Info:")
    print(f"  - Name: {info['agent_name']}")
    print(f"  - Initialized: {info['initialized']}")
    print(f"  - Capabilities: {len(info['capabilities'])} features")

    # Test queries
    test_queries = [
        "What work experience do you have?",
        "What programming languages do you know?",
        "Tell me about your education background",
        "What projects have you worked on?"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = await agent.process_query(query)
        print(f"  Response: {result['response'][:200]}...")
        print(f"  Confidence: {result['confidence']:.2f}")

    print("\n🎉 Personal Resume Agent test completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_personal_agent())