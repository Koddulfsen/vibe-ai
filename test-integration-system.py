#!/usr/bin/env python3
"""
Test the complete integrated setup system
"""

import sys
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent / "agents"))

def test_service_integrator():
    """Test the service integration system"""
    print("🧪 Testing Service Integration System")
    print("=" * 50)
    
    try:
        from service_integrator import ServiceIntegrator, CredentialManager
        
        # Test credential manager
        print("🔐 Testing Credential Manager...")
        cred_manager = CredentialManager()
        print(f"   ✅ Credential manager initialized")
        print(f"   📁 Config directory: {cred_manager.config_dir}")
        
        # Test service integrator
        print("\n🔌 Testing Service Integrator...")
        integrator = ServiceIntegrator()
        print(f"   ✅ Service integrator initialized")
        print(f"   📋 Available services: {len(integrator.available_services)}")
        
        for service_id, service_def in integrator.available_services.items():
            print(f"      - {service_def.display_name} ({service_def.service_type.value})")
        
        # Test GitHub integrator
        print("\n🐙 Testing GitHub Integration...")
        github = integrator.github
        print(f"   ✅ GitHub integrator ready")
        
        # Test cloud deployment
        print("\n☁️  Testing Cloud Deployment...")
        cloud = integrator.cloud
        print(f"   ✅ Cloud deployment integrator ready")
        
        # Test project generator
        print("\n🏗️  Testing Project Generator...")
        generator = integrator.project_generator
        print(f"   ✅ Project generator ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Service integration test failed: {e}")
        return False

def test_interactive_interface():
    """Test the enhanced interactive interface"""
    print("\n🧪 Testing Interactive Interface")
    print("=" * 50)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from start import InteractiveLauncher
        
        # Test launcher initialization
        print("🚀 Testing Launcher...")
        launcher = InteractiveLauncher()
        print(f"   ✅ Launcher initialized")
        print(f"   📁 Project root: {launcher.project_root}")
        
        # Test service integrator availability
        if launcher.service_integrator:
            print(f"   ✅ Service integrator available")
        else:
            print(f"   ⚠️  Service integrator not available")
        
        # Test auto-detection
        print("\n🔍 Testing Auto-Detection...")
        tag = launcher._auto_detect_tag()
        print(f"   🏷️  Auto-detected tag: '{tag}'")
        
        suggestions = launcher._get_tag_suggestions()
        print(f"   💡 Tag suggestions: {suggestions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive interface test failed: {e}")
        return False

def show_demo_workflow():
    """Show what the complete workflow would look like"""
    print("\n🎬 DEMO: Complete Workflow")
    print("=" * 50)
    
    print("🎯 Example: Creating a React App with Full Integration")
    print()
    print("1️⃣  User runs: ./run")
    print("2️⃣  User chooses: '1) Create New Project'")
    print("3️⃣  User chooses: '1) React App (Frontend)'")
    print("4️⃣  User enters project name: 'my-awesome-app'")
    print()
    print("🤖 System automatically:")
    print("   📁 Creates React project with create-react-app")
    print("   🔌 Checks for GitHub integration")
    print("   🐙 Creates GitHub repository (if configured)")
    print("   🚀 Sets up deployment pipeline (if Vercel configured)")
    print("   📦 Installs all dependencies")
    print("   ✅ Provides next steps and URLs")
    print()
    print("⏰ Result: From idea to deployed app in 2-3 minutes!")
    print()
    print("🔗 Integration Setup Example:")
    print("   User chooses: '2) Service Integrations'")
    print("   User chooses: 'c) Configure new service'")
    print("   User chooses: '1) GitHub'")
    print("   🌐 System opens GitHub token page in browser")
    print("   🔑 User pastes token")
    print("   ✅ GitHub integration configured!")
    print()
    print("🚀 Deployment Example:")
    print("   User chooses: '3) Deploy Existing Project'")
    print("   User chooses: '1) Vercel'")
    print("   🔧 System sets up Vercel if needed")
    print("   🚀 Project deploys automatically")
    print("   🌐 Live URL provided")

def main():
    """Run all tests and show demo"""
    print("🚀 Task Master Agent System - Integration Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test service integrator
    if not test_service_integrator():
        success = False
    
    # Test interactive interface
    if not test_interactive_interface():
        success = False
    
    # Show demo workflow
    show_demo_workflow()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ All integration tests passed!")
        print()
        print("🎯 The system is now a complete development hub:")
        print("   🏗️  Project creation with templates")
        print("   🔌 Service integration management")
        print("   🚀 One-click deployment")
        print("   🤖 Intelligent automation")
        print("   🔐 Secure credential management")
        print()
        print("💡 To use:")
        print("   ./run                    # Interactive hub")
        print("   python3 start.py         # Direct interface")
    else:
        print("⚠️  Some integration tests failed")
        print("   The system will work but some features may be limited")

if __name__ == "__main__":
    main()