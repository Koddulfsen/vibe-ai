#!/usr/bin/env python3
"""
Test script to demonstrate comprehensive quality assessment
"""

import sys
from pathlib import Path

# Add agents directory to path
AGENT_DIR = Path(__file__).parent / "agents"
sys.path.insert(0, str(AGENT_DIR))

from quality_assessment import QualityAssessmentEngine, QualityDimension

def test_quality_assessment():
    """Test the quality assessment engine with sample outputs"""
    
    engine = QualityAssessmentEngine()
    
    # Test 1: High quality output
    print("🧪 Test 1: High Quality Output")
    print("=" * 50)
    
    good_output = """
    ✅ Task completed successfully!
    
    Created the following files:
    - main.py (implementation)
    - test_main.py (unit tests)
    - README.md (documentation)
    
    Tests passed: 15/15
    Linting: clean
    Type checking: passed
    
    All requirements have been implemented:
    - User authentication system
    - Database integration
    - API endpoints for CRUD operations
    - Comprehensive error handling
    - Input validation
    
    The system is ready for production deployment.
    """
    
    request_context = "implement user authentication system with database integration"
    result_context = {
        'success': True,
        'duration': 45.2,
        'request_type': 'implementation'
    }
    
    report = engine.assess_agent_output('execution', good_output, request_context, result_context)
    
    print(f"📊 Overall Quality Score: {report.overall_score:.1%}")
    print(f"🔮 Confidence: {report.confidence:.1%}")
    print()
    
    print("🎯 Quality Dimensions:")
    for dimension, metric in report.metrics.items():
        dimension_name = dimension.value.replace('_', ' ').title()
        print(f"   {dimension_name}: {metric.score:.1%}")
        if metric.evidence:
            print(f"      Evidence: {'; '.join(metric.evidence[:2])}")
        if metric.issues:
            print(f"      Issues: {'; '.join(metric.issues[:2])}")
    print()
    
    # Test 2: Poor quality output
    print("🧪 Test 2: Poor Quality Output")
    print("=" * 50)
    
    poor_output = """
    Error occurred
    Failed to complete task
    """
    
    report2 = engine.assess_agent_output('execution', poor_output, request_context, result_context)
    
    print(f"📊 Overall Quality Score: {report2.overall_score:.1%}")
    print(f"🔮 Confidence: {report2.confidence:.1%}")
    print()
    
    if report2.critical_issues:
        print("🚨 Critical Issues:")
        for issue in report2.critical_issues:
            print(f"   - {issue}")
    print()
    
    # Test 3: Medium quality output
    print("🧪 Test 3: Medium Quality Output")
    print("=" * 50)
    
    medium_output = """
    Task partially completed.
    
    Some functionality implemented:
    - Basic authentication
    - Database connection
    
    TODO:
    - Add error handling
    - Implement remaining endpoints
    - Write tests
    """
    
    report3 = engine.assess_agent_output('execution', medium_output, request_context, result_context)
    
    print(f"📊 Overall Quality Score: {report3.overall_score:.1%}")
    print(f"🔮 Confidence: {report3.confidence:.1%}")
    
    if report3.recommendations:
        print("💡 Key Recommendations:")
        for rec in report3.recommendations[:3]:
            print(f"   - {rec}")
    print()
    
    print("✅ Quality Assessment Testing Complete!")

if __name__ == "__main__":
    test_quality_assessment()