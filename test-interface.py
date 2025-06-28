#!/usr/bin/env python3
"""
Quick test of the new interactive interface components
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "agents"))

def test_dependency_manager():
    """Test dependency detection"""
    print("🧪 Testing Dependency Manager...")
    
    try:
        from agents.dependency_manager import SmartDependencyManager
        
        manager = SmartDependencyManager()
        dependencies = manager.detector.detect_project_dependencies()
        
        print(f"✅ Detected {len(dependencies)} dependencies:")
        for dep in dependencies[:5]:  # Show first 5
            print(f"   - {dep.name} ({dep.type.value}): {dep.description}")
        
        # Quick check
        essential = manager.quick_check()
        print(f"✅ Essential dependencies check: {essential}")
        
    except Exception as e:
        print(f"❌ Dependency manager test failed: {e}")

def test_master_agent():
    """Test master agent integration"""
    print("\n🧪 Testing Master Agent...")
    
    try:
        from master_agent import MasterAgent
        
        agent = MasterAgent()
        status = agent.show_status()
        
        print(f"✅ Master agent initialized")
        print(f"   Available agents: {len(status['agents'])}")
        print(f"   All agents available: {all(info['available'] for info in status['agents'].values())}")
        
    except Exception as e:
        print(f"❌ Master agent test failed: {e}")

def test_quality_assessment():
    """Test quality assessment integration"""
    print("\n🧪 Testing Quality Assessment...")
    
    try:
        from agents.quality_assessment import QualityAssessmentEngine
        
        engine = QualityAssessmentEngine()
        
        # Quick test
        test_output = "Task completed successfully. Created test.py file. Tests passed."
        report = engine.assess_agent_output('execution', test_output, 'test task', {
            'success': True,
            'duration': 1.0,
            'request_type': 'test'
        })
        
        print(f"✅ Quality assessment working")
        print(f"   Overall score: {report.overall_score:.1%}")
        print(f"   Metrics: {len(report.metrics)} dimensions assessed")
        
    except Exception as e:
        print(f"❌ Quality assessment test failed: {e}")

def test_interactive_components():
    """Test interactive launcher components"""
    print("\n🧪 Testing Interactive Components...")
    
    try:
        from start import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        
        # Test auto-detection
        tag = launcher._auto_detect_tag()
        print(f"✅ Auto-detected project tag: '{tag}'")
        
        # Test tag suggestions
        suggestions = launcher._get_tag_suggestions()
        print(f"✅ Tag suggestions: {suggestions}")
        
    except Exception as e:
        print(f"❌ Interactive components test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Task Master Agent System - Component Tests")
    print("=" * 60)
    
    test_dependency_manager()
    test_master_agent() 
    test_quality_assessment()
    test_interactive_components()
    
    print("\n" + "=" * 60)
    print("✅ Component testing complete!")
    print()
    print("💡 To use the system:")
    print("   ./run                    # Interactive interface")
    print("   python3 start.py         # Direct interface launch")
    print("   ./master-agent.py status # CLI status check")

if __name__ == "__main__":
    main()