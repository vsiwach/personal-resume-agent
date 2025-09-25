#!/usr/bin/env python3
"""
Startup Script for Resume NANDA Agent
Handles path setup and environment configuration
"""

import os
import sys

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Add NANDA adapter to path
nanda_adapter_path = os.path.join(os.path.dirname(current_dir), 'adapter')
sys.path.insert(0, nanda_adapter_path)

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []

    try:
        from nanda_adapter import NANDA
        print("✅ NANDA Adapter: Available")
    except ImportError as e:
        missing_deps.append(f"NANDA Adapter: {e}")

    try:
        from personal_resume_agent import PersonalResumeAgent
        print("✅ Personal Resume Agent: Available")
    except ImportError as e:
        missing_deps.append(f"Personal Resume Agent: {e}")

    try:
        from resume_nanda_agent import create_resume_improvement
        print("✅ Resume NANDA Integration: Available")
    except ImportError as e:
        missing_deps.append(f"Resume NANDA Integration: {e}")

    if missing_deps:
        print("\n❌ Missing Dependencies:")
        for dep in missing_deps:
            print(f"   {dep}")
        return False

    print("\n🎉 All dependencies available!")
    return True

def check_environment():
    """Check environment variables"""
    required_env = ["ANTHROPIC_API_KEY"]
    optional_env = ["DOMAIN_NAME", "AGENT_ID", "PORT"]

    print("\n🔧 Environment Check:")

    missing_required = []
    for env_var in required_env:
        if os.getenv(env_var):
            print(f"✅ {env_var}: Set")
        else:
            missing_required.append(env_var)
            print(f"❌ {env_var}: Not set")

    for env_var in optional_env:
        value = os.getenv(env_var, "default")
        print(f"ℹ️  {env_var}: {value}")

    if missing_required:
        print(f"\n❌ Missing required environment variables: {missing_required}")
        print("Please set them before running the agent:")
        for var in missing_required:
            print(f"   export {var}=your_value_here")
        return False

    return True

def check_data_directory():
    """Check if data directory exists and has content"""
    data_dir = os.path.join(current_dir, 'data')

    print(f"\n📁 Data Directory Check: {data_dir}")

    if not os.path.exists(data_dir):
        print("❌ Data directory does not exist")
        return False

    # Check for resume files
    resume_files = []
    for file in os.listdir(data_dir):
        if file.endswith(('.pdf', '.docx', '.txt', '.md')) and not file.startswith('.'):
            resume_files.append(file)

    if resume_files:
        print(f"✅ Found {len(resume_files)} resume file(s):")
        for file in resume_files[:3]:  # Show first 3 files
            print(f"   📄 {file}")
        if len(resume_files) > 3:
            print(f"   ... and {len(resume_files) - 3} more")
    else:
        print("⚠️  No resume files found in data directory")
        print("   Please add your resume files (.pdf, .docx, .txt, .md) to the data/ directory")

        # Check for sample files
        sample_dir = os.path.join(data_dir, 'sample')
        if os.path.exists(sample_dir):
            print(f"   📂 Sample files available in {sample_dir}")

    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 RESUME NANDA AGENT STARTUP")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please set required variables.")
        sys.exit(1)

    # Check data directory
    check_data_directory()

    print("\n" + "=" * 60)
    print("🎯 STARTING RESUME NANDA AGENT")
    print("=" * 60)

    # Import and run the agent
    try:
        from resume_nanda_agent import main as run_agent
        run_agent()
    except KeyboardInterrupt:
        print("\n\n👋 Resume NANDA Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()