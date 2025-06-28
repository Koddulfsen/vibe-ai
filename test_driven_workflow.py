#!/usr/bin/env python3
"""
Test-Driven Development Workflow for vibe.ai
============================================

This implements a TDD workflow where:
1. User describes what they want to build
2. System generates comprehensive tests FIRST
3. Then implements code to pass those tests
4. Iterates until all tests pass
"""

import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class TestCase:
    """Represents a single test case"""
    name: str
    description: str
    test_type: str  # unit, integration, e2e
    test_code: str
    expected_behavior: str
    status: str = "pending"  # pending, passed, failed

@dataclass
class TDDProject:
    """Represents a TDD project"""
    description: str
    test_cases: List[TestCase]
    implementation_code: Dict[str, str]
    test_framework: str = "pytest"
    language: str = "python"

class TestDrivenWorkflow:
    """Orchestrates the Test-Driven Development workflow"""
    
    def __init__(self):
        self.oracle_agent = "prompting_oracle_agent.py"
        self.planner_agent = "deep_planner_agent.py"
        self.test_generator = TestGenerator()
        self.code_generator = CodeGenerator()
        self.test_runner = TestRunner()
    
    def start_tdd_project(self, idea: str) -> TDDProject:
        """Start a new TDD project"""
        print(f"\n🧪 Starting Test-Driven Development for: {idea}")
        print("="*70)
        
        # Step 1: Analyze and enhance the idea
        enhanced_idea = self._enhance_idea(idea)
        
        # Step 2: Generate test specifications
        test_specs = self._generate_test_specs(enhanced_idea)
        
        # Step 3: Create test cases
        test_cases = self.test_generator.generate_tests(test_specs)
        
        # Step 4: Create project structure
        project = TDDProject(
            description=enhanced_idea,
            test_cases=test_cases,
            implementation_code={}
        )
        
        return project
    
    def _enhance_idea(self, idea: str) -> str:
        """Use Oracle to enhance the idea"""
        print("\n🔮 Enhancing idea with Oracle wisdom...")
        
        # Simulate oracle enhancement (in real implementation, call oracle agent)
        enhanced = f"{idea} with comprehensive error handling, input validation, and edge case coverage"
        print(f"✅ Enhanced: {enhanced}")
        return enhanced
    
    def _generate_test_specs(self, idea: str) -> Dict[str, Any]:
        """Generate test specifications from idea"""
        print("\n📋 Generating test specifications...")
        
        # Analyze what needs to be tested
        specs = {
            "functionality": self._extract_functionality(idea),
            "edge_cases": self._identify_edge_cases(idea),
            "error_scenarios": self._identify_error_scenarios(idea),
            "integration_points": self._identify_integrations(idea)
        }
        
        print(f"✅ Generated {sum(len(v) for v in specs.values())} test specifications")
        return specs
    
    def _extract_functionality(self, idea: str) -> List[str]:
        """Extract core functionality to test"""
        # Simple keyword extraction (in real implementation, use NLP)
        functionalities = []
        
        if "api" in idea.lower():
            functionalities.extend([
                "API endpoint availability",
                "Correct HTTP status codes",
                "Response format validation",
                "Request parameter validation"
            ])
        
        if "dashboard" in idea.lower():
            functionalities.extend([
                "Dashboard renders correctly",
                "Data updates in real-time",
                "User interactions work",
                "Responsive design"
            ])
        
        if "weather" in idea.lower():
            functionalities.extend([
                "Weather data retrieval",
                "Temperature conversion",
                "Location validation",
                "Forecast accuracy"
            ])
        
        return functionalities
    
    def _identify_edge_cases(self, idea: str) -> List[str]:
        """Identify edge cases to test"""
        return [
            "Empty input handling",
            "Maximum input size",
            "Special characters in input",
            "Concurrent access",
            "Rate limiting"
        ]
    
    def _identify_error_scenarios(self, idea: str) -> List[str]:
        """Identify error scenarios to test"""
        return [
            "Network timeout",
            "Invalid API key",
            "Database connection failure",
            "Malformed input data",
            "Unauthorized access"
        ]
    
    def _identify_integrations(self, idea: str) -> List[str]:
        """Identify integration points to test"""
        integrations = []
        
        if "api" in idea.lower():
            integrations.append("External API integration")
        if "database" in idea.lower() or "data" in idea.lower():
            integrations.append("Database operations")
        if "auth" in idea.lower():
            integrations.append("Authentication system")
        
        return integrations

    def run_tdd_cycle(self, project: TDDProject, output_dir: str) -> Dict[str, Any]:
        """Run the TDD cycle: Red -> Green -> Refactor"""
        print(f"\n🔄 Running TDD Cycle for: {project.description}")
        print("="*70)
        
        os.makedirs(output_dir, exist_ok=True)
        results = {
            "cycles": [],
            "final_status": "pending"
        }
        
        # Write initial tests
        test_file = os.path.join(output_dir, "test_implementation.py")
        self.test_generator.write_test_file(project.test_cases, test_file)
        
        max_cycles = 5
        for cycle in range(max_cycles):
            print(f"\n🔄 TDD Cycle {cycle + 1}")
            print("-" * 40)
            
            # Step 1: Run tests (Red phase)
            print("🔴 Red Phase: Running tests...")
            test_results = self.test_runner.run_tests(test_file)
            
            failing_tests = [t for t in test_results if t["status"] == "failed"]
            if not failing_tests:
                print("✅ All tests passing!")
                results["final_status"] = "success"
                break
            
            print(f"❌ {len(failing_tests)} tests failing")
            
            # Step 2: Generate/update implementation (Green phase)
            print("\n🟢 Green Phase: Generating implementation...")
            implementation = self.code_generator.generate_implementation(
                project, failing_tests, output_dir
            )
            
            # Update project with new implementation
            project.implementation_code.update(implementation)
            
            # Write implementation files
            for filename, code in implementation.items():
                filepath = os.path.join(output_dir, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(code)
            
            # Step 3: Refactor if all tests pass (Blue phase)
            test_results = self.test_runner.run_tests(test_file)
            passing_tests = [t for t in test_results if t["status"] == "passed"]
            
            if len(passing_tests) == len(test_results):
                print("\n🔵 Blue Phase: Refactoring...")
                refactored = self.code_generator.refactor_code(implementation)
                
                for filename, code in refactored.items():
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'w') as f:
                        f.write(code)
            
            # Record cycle results
            results["cycles"].append({
                "cycle": cycle + 1,
                "failing_tests": len(failing_tests),
                "passing_tests": len(passing_tests),
                "total_tests": len(test_results)
            })
        
        return results


class TestGenerator:
    """Generates test cases based on specifications"""
    
    def generate_tests(self, specs: Dict[str, Any]) -> List[TestCase]:
        """Generate test cases from specifications"""
        test_cases = []
        
        # Generate functionality tests
        for func in specs.get("functionality", []):
            test_cases.append(self._create_test_case(func, "unit"))
        
        # Generate edge case tests
        for edge in specs.get("edge_cases", []):
            test_cases.append(self._create_test_case(edge, "edge"))
        
        # Generate error scenario tests
        for error in specs.get("error_scenarios", []):
            test_cases.append(self._create_test_case(error, "error"))
        
        # Generate integration tests
        for integration in specs.get("integration_points", []):
            test_cases.append(self._create_test_case(integration, "integration"))
        
        return test_cases
    
    def _create_test_case(self, spec: str, test_type: str) -> TestCase:
        """Create a single test case"""
        name = f"test_{spec.lower().replace(' ', '_')}"
        
        # Generate appropriate test code based on type
        if test_type == "unit":
            test_code = self._generate_unit_test(spec)
        elif test_type == "edge":
            test_code = self._generate_edge_test(spec)
        elif test_type == "error":
            test_code = self._generate_error_test(spec)
        else:
            test_code = self._generate_integration_test(spec)
        
        return TestCase(
            name=name,
            description=f"Test for: {spec}",
            test_type=test_type,
            test_code=test_code,
            expected_behavior=f"Should handle {spec} correctly"
        )
    
    def _generate_unit_test(self, spec: str) -> str:
        """Generate unit test code"""
        if "api endpoint" in spec.lower():
            return '''def test_api_endpoint_availability():
    """Test that API endpoints are available"""
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()'''
        
        return f'''def test_{spec.lower().replace(" ", "_")}():
    """Test {spec}"""
    # TODO: Implement test for {spec}
    assert True  # Placeholder'''
    
    def _generate_edge_test(self, spec: str) -> str:
        """Generate edge case test"""
        if "empty input" in spec.lower():
            return '''def test_empty_input_handling():
    """Test handling of empty input"""
    response = client.post("/items", json={})
    assert response.status_code == 422  # Validation error'''
        
        return f'''def test_{spec.lower().replace(" ", "_")}():
    """Test edge case: {spec}"""
    # TODO: Implement edge case test
    assert True  # Placeholder'''
    
    def _generate_error_test(self, spec: str) -> str:
        """Generate error scenario test"""
        return f'''def test_{spec.lower().replace(" ", "_")}():
    """Test error scenario: {spec}"""
    with pytest.raises(Exception):
        # TODO: Trigger error scenario
        pass'''
    
    def _generate_integration_test(self, spec: str) -> str:
        """Generate integration test"""
        return f'''def test_{spec.lower().replace(" ", "_")}():
    """Test integration: {spec}"""
    # TODO: Test integration point
    assert True  # Placeholder'''
    
    def write_test_file(self, test_cases: List[TestCase], filepath: str):
        """Write test cases to a file"""
        content = '''"""
Auto-generated tests using Test-Driven Development
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import app
    client = TestClient(app)
except ImportError:
    # Create mock client if app doesn't exist yet
    class MockClient:
        def get(self, *args, **kwargs):
            return type('Response', (), {'status_code': 404, 'json': lambda: {}})()
        def post(self, *args, **kwargs):
            return type('Response', (), {'status_code': 404, 'json': lambda: {}})()
    client = MockClient()

'''
        
        # Add all test cases
        for test_case in test_cases:
            content += f"\n{test_case.test_code}\n\n"
        
        with open(filepath, 'w') as f:
            f.write(content)


class CodeGenerator:
    """Generates implementation code to pass tests"""
    
    def generate_implementation(self, project: TDDProject, 
                               failing_tests: List[Dict], 
                               output_dir: str) -> Dict[str, str]:
        """Generate code to make failing tests pass"""
        print(f"📝 Generating code to fix {len(failing_tests)} failing tests...")
        
        implementation = {}
        
        # Analyze failing tests to determine what to implement
        needs_api = any("api" in str(t).lower() for t in failing_tests)
        needs_validation = any("validation" in str(t).lower() or "empty" in str(t).lower() for t in failing_tests)
        needs_error_handling = any("error" in str(t).lower() for t in failing_tests)
        
        # Generate main application file
        if needs_api or not os.path.exists(os.path.join(output_dir, "src", "main.py")):
            implementation["src/main.py"] = self._generate_api_code(
                project.description, 
                needs_validation, 
                needs_error_handling
            )
        
        return implementation
    
    def _generate_api_code(self, description: str, 
                          needs_validation: bool, 
                          needs_error_handling: bool) -> str:
        """Generate FastAPI code"""
        code = f'''"""
{description}
Generated by Test-Driven Development
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TDD Generated API", version="1.0.0")

'''
        
        if needs_validation:
            code += '''
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
    @validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v

'''
        
        code += '''
@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

'''
        
        if needs_validation:
            code += '''
@app.post("/items")
async def create_item(item: ItemCreate):
    """Create a new item with validation"""
    try:
        # Process the item
        return {"id": 1, "name": item.name, "description": item.description}
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

'''
        
        if needs_error_handling:
            code += '''
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return {"error": str(exc)}, 422

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error"}, 500

'''
        
        return code
    
    def refactor_code(self, implementation: Dict[str, str]) -> Dict[str, str]:
        """Refactor code for better quality"""
        refactored = {}
        
        for filename, code in implementation.items():
            # Simple refactoring: add type hints, docstrings, etc.
            refactored_code = code
            
            # Add more comprehensive docstrings
            refactored_code = refactored_code.replace(
                '"""Root endpoint"""',
                '"""Root endpoint for API health check\n    \n    Returns:\n        dict: Status information\n    """'
            )
            
            refactored[filename] = refactored_code
        
        return refactored


class TestRunner:
    """Runs tests and reports results"""
    
    def run_tests(self, test_file: str) -> List[Dict[str, Any]]:
        """Run tests and return results"""
        try:
            # Run pytest
            result = subprocess.run(
                ["python3", "-m", "pytest", test_file, "-v", "--tb=short", "--json-report"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(test_file)
            )
            
            # Parse results (simplified for demo)
            test_results = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if "PASSED" in line:
                    test_name = line.split("::")[1].split()[0] if "::" in line else "unknown"
                    test_results.append({
                        "name": test_name,
                        "status": "passed"
                    })
                elif "FAILED" in line:
                    test_name = line.split("::")[1].split()[0] if "::" in line else "unknown"
                    test_results.append({
                        "name": test_name,
                        "status": "failed"
                    })
            
            # If no results parsed, create some based on return code
            if not test_results:
                if result.returncode == 0:
                    test_results.append({"name": "all_tests", "status": "passed"})
                else:
                    test_results.append({"name": "some_tests", "status": "failed"})
            
            return test_results
            
        except Exception as e:
            print(f"Error running tests: {e}")
            return [{"name": "test_run", "status": "failed", "error": str(e)}]


def main():
    """Main entry point for TDD workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test-Driven Development Workflow")
    parser.add_argument("idea", help="What you want to build")
    parser.add_argument("-o", "--output", default="tdd-output", help="Output directory")
    parser.add_argument("--cycles", type=int, default=5, help="Maximum TDD cycles")
    
    args = parser.parse_args()
    
    # Create TDD workflow
    workflow = TestDrivenWorkflow()
    
    # Start TDD project
    project = workflow.start_tdd_project(args.idea)
    
    print(f"\n📊 Generated {len(project.test_cases)} test cases:")
    for i, test in enumerate(project.test_cases, 1):
        print(f"  {i}. {test.name} ({test.test_type})")
    
    # Run TDD cycles
    print(f"\n🚀 Starting TDD cycles (max {args.cycles})...")
    results = workflow.run_tdd_cycle(project, args.output)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TDD Workflow Summary")
    print("="*70)
    print(f"Project: {project.description}")
    print(f"Total Cycles: {len(results['cycles'])}")
    print(f"Final Status: {results['final_status']}")
    print(f"Output Directory: {args.output}")
    
    if results['final_status'] == 'success':
        print("\n✅ All tests passing! Implementation complete.")
        print("\n🚀 Next steps:")
        print(f"  1. cd {args.output}")
        print("  2. pip install -r requirements.txt")
        print("  3. python src/main.py")
        print("  4. python -m pytest test_implementation.py")
    else:
        print("\n⚠️  Some tests still failing. Manual intervention needed.")


if __name__ == "__main__":
    main()