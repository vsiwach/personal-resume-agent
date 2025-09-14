#!/usr/bin/env python3
"""
Example usage of the Personal Resume Agent
"""

import sys
import os
import asyncio

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from personal_resume_agent import PersonalResumeAgent


async def main():
    """Example usage of the Personal Resume Agent"""
    print("🤖 Personal Resume Agent Example")
    print("=" * 40)

    # Initialize agent
    agent = PersonalResumeAgent(data_directory="../data")

    print("\n🔄 Initializing agent...")
    success = await agent.initialize()

    if not success:
        print("❌ Failed to initialize agent")
        print("💡 Make sure to add resume files to the data/ directory")
        return

    print("✅ Agent initialized successfully!")

    # Get agent info
    info = agent.get_agent_info()
    print(f"\n📋 Agent Info:")
    print(f"  - Status: {'Ready' if info['initialized'] else 'Not Ready'}")
    print(f"  - Capabilities: {len(info['capabilities'])}")
    print(f"  - Resume Summary: {info['resume_summary'][:100]}...")

    # Example queries
    example_queries = [
        "What work experience do you have?",
        "What programming languages and technologies do you know?",
        "Tell me about your education background",
        "What are your key skills?",
        "What projects have you worked on?",
        "What achievements do you have?"
    ]

    print(f"\n💬 Testing Example Queries:")
    print("-" * 40)

    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Query: {query}")

        result = await agent.process_query(query)

        print(f"   Response: {result['response'][:150]}...")
        print(f"   Type: {result.get('query_type', 'unknown')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        print(f"   Sources: {result.get('source_chunks', 0)} chunks")

    # Example skill matching
    print(f"\n🎯 Testing Skill Matching:")
    print("-" * 40)

    job_description = """
    We are looking for a software engineer with experience in:
    - Python programming
    - Web development with frameworks like Django or Flask
    - Database design and SQL
    - Cloud platforms (AWS, Azure, GCP)
    - Version control with Git
    - Agile development methodologies
    """

    print(f"Job Requirements: {job_description[:100]}...")

    skill_match = await agent.get_skill_match(job_description)

    print(f"\nSkill Match Results:")
    print(f"  - Match Percentage: {skill_match.get('match_percentage', 0)}%")
    print(f"  - Matching Skills: {skill_match.get('matching_skills', [])[:5]}")
    print(f"  - Confidence: {skill_match.get('confidence', 0):.2f}")

    print(f"\n🎉 Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())