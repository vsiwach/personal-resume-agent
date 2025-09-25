#!/usr/bin/env python3
"""
Resume NANDA Agent - Integration of Personal Resume Agent with NANDA Network
Makes your resume globally discoverable and queryable by other agents
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Add the nanda adapter to path
sys.path.insert(0, '/Users/vikramsiwach/nanda/adapter')
from nanda_adapter import NANDA

# Import our resume agent
from personal_resume_agent import PersonalResumeAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResumeNANDAWrapper:
    """Wrapper class to integrate Personal Resume Agent with NANDA network"""

    def __init__(self):
        """Initialize the Resume NANDA wrapper"""
        self.resume_agent = None
        self.initialized = False
        self.agent_context = {
            "name": "Vikram's Resume Agent",
            "description": "AI agent with comprehensive knowledge of Vikram Siwach's professional background",
            "capabilities": [
                "Professional experience queries",
                "Skill matching and analysis",
                "Career progression details",
                "Education and certifications",
                "Project and achievement highlights"
            ]
        }

    async def initialize_resume_agent(self):
        """Initialize the underlying resume agent"""
        try:
            logger.info("🤖 Initializing Personal Resume Agent...")
            self.resume_agent = PersonalResumeAgent()
            success = await self.resume_agent.initialize()

            if success:
                self.initialized = True
                logger.info("✅ Resume Agent initialized successfully")
                return True
            else:
                logger.error("❌ Failed to initialize Resume Agent")
                return False

        except Exception as e:
            logger.error(f"❌ Error initializing Resume Agent: {e}")
            return False

    def classify_message_type(self, message: str) -> str:
        """Classify the type of message for better response handling"""
        message_lower = message.lower()

        # Professional queries
        if any(word in message_lower for word in ['experience', 'work', 'job', 'role', 'position', 'career']):
            return 'experience'
        elif any(word in message_lower for word in ['skill', 'technology', 'programming', 'tech', 'tool']):
            return 'skills'
        elif any(word in message_lower for word in ['education', 'degree', 'university', 'school', 'certification']):
            return 'education'
        elif any(word in message_lower for word in ['project', 'achievement', 'accomplishment', 'portfolio']):
            return 'projects'
        elif any(word in message_lower for word in ['resume', 'cv', 'background', 'profile']):
            return 'general'
        else:
            return 'general'

    async def process_resume_query(self, message_text: str) -> str:
        """Process message through resume agent and return enhanced response"""
        try:
            if not self.initialized:
                logger.warning("⚠️ Resume agent not initialized, attempting to initialize...")
                success = await self.initialize_resume_agent()
                if not success:
                    return "Sorry, I'm having trouble accessing my resume knowledge right now."

            # Classify message type for context
            message_type = self.classify_message_type(message_text)
            logger.info(f"📝 Processing {message_type} query: {message_text[:50]}...")

            # Query the resume agent
            result = await self.resume_agent.process_query(message_text)

            if result and 'response' in result:
                response = result['response']
                confidence = result.get('confidence', 0)

                # Add context based on message type
                if message_type == 'skills':
                    response += "\n\nI can also help with skill matching for specific job requirements!"
                elif message_type == 'experience':
                    response += "\n\nWould you like more details about any specific role or project?"

                logger.info(f"✅ Generated response (confidence: {confidence:.2f})")
                return response

            else:
                logger.warning("⚠️ No response from resume agent")
                return self.get_fallback_response(message_text, message_type)

        except Exception as e:
            logger.error(f"❌ Error processing resume query: {e}")
            return self.get_fallback_response(message_text, "error")

    def get_fallback_response(self, message: str, context: str = "general") -> str:
        """Provide fallback responses when resume agent is unavailable"""
        fallback_responses = {
            'skills': "I have expertise in Python, JavaScript, cloud technologies (AWS), and full-stack development. What specific skills are you interested in?",
            'experience': "I'm a Senior Software Engineer with experience at MIT Sloan and various tech companies. What aspects of my experience would you like to know about?",
            'education': "I have a strong technical education background. What specific educational details are you looking for?",
            'projects': "I've worked on various projects involving web development, AI/ML, and system architecture. What kind of projects interest you?",
            'general': "I'm Vikram's personal resume agent. I can help you learn about his professional background, skills, and experience. What would you like to know?",
            'error': f"I'm having some technical difficulties right now, but I'd be happy to help answer questions about Vikram's professional background. Could you rephrase your question: '{message}'?"
        }

        return fallback_responses.get(context, fallback_responses['general'])


def create_resume_improvement():
    """Create the main improvement function for NANDA integration"""

    # Create the wrapper instance
    wrapper = ResumeNANDAWrapper()

    def resume_improvement(message_text: str) -> str:
        """
        Main improvement function that NANDA will call
        Transforms generic messages into resume-enhanced responses
        """
        try:
            logger.info(f"🔄 Processing NANDA message: {message_text[:100]}...")

            # Check if this is a resume-related query
            if any(keyword in message_text.lower() for keyword in [
                'vikram', 'resume', 'experience', 'skills', 'background',
                'work', 'job', 'career', 'education', 'project'
            ]):
                # This is a resume query - process it asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(wrapper.process_resume_query(message_text))
                    return response
                finally:
                    loop.close()
            else:
                # Generic message - add professional context
                context_response = f"As Vikram's professional representative, I can help with career-related questions. "
                context_response += f"Regarding your message: {message_text} - "
                context_response += "Would you like to know how this relates to Vikram's professional background?"

                return context_response

        except Exception as e:
            logger.error(f"❌ Error in resume improvement: {e}")
            # Fallback to simple enhancement
            return f"Hello! I'm Vikram's resume agent. Regarding your message '{message_text}' - I can help you learn about his professional background, skills, and experience. What specifically would you like to know?"

    # Initialize the wrapper asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(wrapper.initialize_resume_agent())
    finally:
        loop.close()

    return resume_improvement


def main():
    """Main function to start the Resume NANDA Agent"""

    print("=" * 60)
    print("🤖 RESUME NANDA AGENT")
    print("=" * 60)
    print("🔗 Integrating Personal Resume Agent with NANDA Network")
    print("📋 Agent: Vikram's Resume Agent")
    print("🌐 Network: Global NANDA Agent Discovery")
    print("=" * 60)

    # Check for required environment variables
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ Please set your ANTHROPIC_API_KEY environment variable")
        return

    domain = os.getenv("DOMAIN_NAME", "localhost")
    print(f"🏠 Domain: {domain}")

    try:
        # Create resume improvement function
        print("🔧 Creating resume improvement logic...")
        resume_logic = create_resume_improvement()

        # Initialize NANDA with resume logic
        print("🚀 Initializing NANDA with resume agent...")
        nanda = NANDA(resume_logic)

        print("✅ Resume NANDA Agent ready!")
        print("💬 All messages will be enhanced with resume knowledge")
        print("🌍 Agent will be discoverable on the global NANDA network")

        if domain != "localhost":
            print(f"🔐 Starting production server with SSL for {domain}...")
            nanda.start_server_api(anthropic_key, domain)
        else:
            print("🛠️  Starting development server...")
            nanda.start_server()

    except KeyboardInterrupt:
        print("\n👋 Shutting down Resume NANDA Agent...")
    except Exception as e:
        print(f"❌ Error starting Resume NANDA Agent: {e}")
        logger.error(f"Startup error: {e}")


if __name__ == "__main__":
    main()