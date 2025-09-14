#!/usr/bin/env python3
"""
Basic tests for the Personal Resume Agent
"""

import sys
import os
import asyncio
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from resume_rag import ResumeRAGSystem
from personal_resume_agent import PersonalResumeAgent


def create_sample_resume(temp_dir):
    """Create a sample resume file for testing"""
    resume_content = """
    John Doe
    Software Engineer

    Experience:
    - Senior Python Developer at Tech Corp (2020-2023)
    - Full Stack Engineer at StartupXYZ (2018-2020)
    - Junior Developer at CodeCompany (2016-2018)

    Skills:
    - Programming Languages: Python, JavaScript, Java, Go
    - Web Frameworks: Django, Flask, React, Node.js
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud Platforms: AWS, Docker, Kubernetes
    - Tools: Git, Jenkins, Terraform

    Education:
    - BS Computer Science, State University (2012-2016)
    - Certified AWS Solutions Architect

    Projects:
    - Built scalable microservices architecture serving 1M+ users
    - Developed real-time analytics dashboard using React and Django
    - Implemented CI/CD pipeline reducing deployment time by 80%
    """

    resume_path = os.path.join(temp_dir, "sample_resume.txt")
    with open(resume_path, 'w') as f:
        f.write(resume_content.strip())

    return resume_path


async def test_resume_rag_system():
    """Test the Resume RAG System"""
    print("🧪 Testing Resume RAG System...")

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample resume
        resume_path = create_sample_resume(temp_dir)
        print(f"   Created sample resume: {resume_path}")

        # Initialize RAG system
        rag = ResumeRAGSystem(data_directory=temp_dir,
                            persist_directory=os.path.join(temp_dir, "vectordb"))

        # Load resume files
        success = rag.load_resume_files()
        assert success, "Failed to load resume files"
        print("   ✅ Resume files loaded successfully")

        # Test search functionality
        results = rag.search_resume("Python programming experience")
        assert len(results) > 0, "No search results found"
        print(f"   ✅ Search returned {len(results)} results")

        # Test summary
        summary = rag.get_resume_summary()
        assert "sample_resume.txt" in summary, "Resume file not in summary"
        print("   ✅ Resume summary generated")

        print("✅ Resume RAG System tests passed!")


async def test_personal_agent():
    """Test the Personal Resume Agent"""
    print("\n🧪 Testing Personal Resume Agent...")

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample resume
        resume_path = create_sample_resume(temp_dir)

        # Initialize agent
        agent = PersonalResumeAgent(data_directory=temp_dir)

        # Initialize agent
        success = await agent.initialize()
        assert success, "Failed to initialize agent"
        print("   ✅ Agent initialized successfully")

        # Test agent info
        info = agent.get_agent_info()
        assert info['initialized'], "Agent should be initialized"
        assert len(info['capabilities']) > 0, "Agent should have capabilities"
        print("   ✅ Agent info retrieved")

        # Test query processing
        result = await agent.process_query("What programming languages do you know?")
        assert result['response'], "No response received"
        confidence = result.get('confidence', 0)
        assert confidence >= 0, f"Confidence score should be >= 0, got {confidence}"
        print(f"   ✅ Query processed: {result['response'][:50]}...")
        print(f"   Confidence: {confidence:.2f}")

        # Test skill matching
        job_desc = "Python developer with Django experience"
        match = await agent.get_skill_match(job_desc)
        assert 'match_percentage' in match, "No match percentage"
        print(f"   ✅ Skill match: {match['match_percentage']}%")

        print("✅ Personal Resume Agent tests passed!")


async def run_all_tests():
    """Run all tests"""
    print("🚀 Running Personal Resume Agent Tests")
    print("=" * 50)

    try:
        await test_resume_rag_system()
        await test_personal_agent()

        print("\n🎉 All tests passed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)