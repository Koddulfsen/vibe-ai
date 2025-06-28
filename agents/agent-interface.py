#!/usr/bin/env python3
"""
Agent Interface - Light User Experience

Simple interface for users to input natural language prompts and get 
dynamic output from the development automation agent system.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

class AgentInterface:
    """Light interface for agent system interaction"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / "agents"
        self.taskmaster_dir = self.project_root / ".taskmaster"
        
        # Detect project type dynamically
        self.project_type = self._detect_project_type()
        
    def _detect_project_type(self) -> str:
        """Detect project type from actual project files"""
        if (self.project_root / "package.json").exists():
            try:
                with open(self.project_root / "package.json", 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        return 'react'
                    elif 'vue' in deps:
                        return 'vue'
                    elif 'angular' in deps:
                        return 'angular'
                    else:
                        return 'nodejs'
            except:
                return 'nodejs'
        
        if (self.project_root / 'Cargo.toml').exists():
            return 'rust'
        if (self.project_root / 'go.mod').exists():
            return 'go'
        if (self.project_root / 'requirements.txt').exists() or (self.project_root / 'setup.py').exists():
            return 'python'
        
        return 'unknown'
    
    def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Process user prompt and generate dynamic response"""
        print(f"🤖 Processing: '{user_prompt}'")
        print(f"📁 Project Type: {self.project_type}")
        
        # Analyze prompt to determine intent
        intent = self._analyze_intent(user_prompt)
        print(f"🎯 Intent: {intent['action']} ({intent['confidence']:.1%})")
        
        # Create dynamic task from prompt
        task = self._create_task_from_prompt(user_prompt, intent)
        
        # Process through agent system
        result = self._process_with_agents(task, intent)
        
        return {
            "prompt": user_prompt,
            "intent": intent,
            "task": task,
            "result": result,
            "project_type": self.project_type
        }
    
    def _analyze_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze user prompt to determine intent"""
        prompt_lower = prompt.lower()
        
        # Intent patterns with confidence scores
        intent_patterns = {
            "create_component": {
                "patterns": ["create component", "add component", "new component", "component for"],
                "confidence_boost": 0.9
            },
            "create_service": {
                "patterns": ["create service", "add service", "new service", "api service"],
                "confidence_boost": 0.9
            },
            "add_feature": {
                "patterns": ["add feature", "implement feature", "new feature", "feature to"],
                "confidence_boost": 0.8
            },
            "fix_bug": {
                "patterns": ["fix bug", "bug fix", "fix issue", "resolve error"],
                "confidence_boost": 0.8
            },
            "improve_performance": {
                "patterns": ["improve performance", "optimize", "make faster", "speed up"],
                "confidence_boost": 0.7
            },
            "add_tests": {
                "patterns": ["add tests", "create tests", "test coverage", "unit tests"],
                "confidence_boost": 0.8
            },
            "setup_project": {
                "patterns": ["setup", "initialize", "configure", "bootstrap"],
                "confidence_boost": 0.7
            },
            "deploy": {
                "patterns": ["deploy", "deployment", "publish", "release"],
                "confidence_boost": 0.8
            },
            "create_repository": {
                "patterns": ["create repo", "new repo", "github repo", "setup repo", "create repository", "push to github"],
                "confidence_boost": 0.9
            }
        }
        
        # Calculate confidence for each intent
        best_intent = "generic"
        best_confidence = 0.3  # Base confidence for generic
        
        for intent, config in intent_patterns.items():
            confidence = 0.0
            for pattern in config["patterns"]:
                if pattern in prompt_lower:
                    confidence = config["confidence_boost"]
                    break
            
            if confidence > best_confidence:
                best_intent = intent
                best_confidence = confidence
        
        # Extract entities from prompt
        entities = self._extract_entities(prompt)
        
        return {
            "action": best_intent,
            "confidence": best_confidence,
            "entities": entities,
            "complexity": self._estimate_complexity(prompt, best_intent)
        }
    
    def _extract_entities(self, prompt: str) -> Dict[str, List[str]]:
        """Extract entities like component names, feature names, etc."""
        import re
        
        entities = {
            "names": [],
            "technologies": [],
            "files": []
        }
        
        # Extract capitalized words (potential component/service names)
        names = re.findall(r'\b[A-Z][a-zA-Z]+\b', prompt)
        entities["names"] = [name for name in names if len(name) > 2][:3]
        
        # Extract technology mentions
        tech_patterns = [
            r'\b(react|vue|angular|node|python|rust|go|typescript|javascript)\b',
            r'\b(api|database|ui|component|service|hook|util)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, prompt.lower())
            entities["technologies"].extend(matches)
        
        # Extract file extensions or file mentions
        file_patterns = re.findall(r'\b\w+\.(js|ts|py|rs|go|jsx|tsx|css|html)\b', prompt)
        entities["files"] = file_patterns
        
        return entities
    
    def _estimate_complexity(self, prompt: str, intent: str) -> str:
        """Estimate task complexity from prompt content"""
        complexity_indicators = {
            "high": ["complex", "comprehensive", "full", "complete", "advanced", "production", "scalable"],
            "medium": ["feature", "service", "component", "integration", "api"],
            "low": ["simple", "basic", "quick", "minimal", "small"]
        }
        
        prompt_lower = prompt.lower()
        
        # Check for explicit complexity indicators
        for level, indicators in complexity_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                return level
        
        # Intent-based complexity estimation
        if intent in ["setup_project", "deploy", "improve_performance"]:
            return "high"
        elif intent in ["create_component", "create_service", "add_feature"]:
            return "medium"
        else:
            return "low"
    
    def _create_task_from_prompt(self, prompt: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Create a dynamic task structure from user prompt"""
        # Generate unique task ID
        task_id = int(time.time() * 1000) % 100000
        
        # Create task title from intent and entities
        entities = intent["entities"]
        if entities["names"]:
            title_name = entities["names"][0]
        else:
            title_name = "Component"
        
        # Generate title based on intent
        title_templates = {
            "create_component": f"Create {title_name} Component",
            "create_service": f"Create {title_name} Service",
            "add_feature": f"Implement {title_name} Feature",
            "fix_bug": f"Fix Bug in {title_name}",
            "improve_performance": f"Optimize {title_name} Performance",
            "add_tests": f"Add Tests for {title_name}",
            "setup_project": "Setup Project Infrastructure", 
            "deploy": "Deploy Application",
            "create_repository": "Create GitHub Repository",
            "generic": f"Implement {prompt[:30]}..."
        }
        
        title = title_templates.get(intent["action"], title_templates["generic"])
        
        return {
            "id": task_id,
            "title": title,
            "description": prompt,
            "details": f"User requested: {prompt}\\n\\nDetected intent: {intent['action']}\\nComplexity: {intent['complexity']}",
            "priority": "high" if intent["complexity"] == "high" else "medium",
            "type": intent["action"],
            "created_from_prompt": True,
            "project_type": self.project_type,
            "entities": entities
        }
    
    def _process_with_agents(self, task: Dict[str, Any], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Process task through the agent system"""
        result = {
            "analysis": {},
            "execution": {},
            "quality": {},
            "success": False,
            "errors": []
        }
        
        try:
            # Special handling for repository creation
            if intent["action"] == "create_repository":
                print("🚀 Creating GitHub Repository...")
                repo_result = self._run_repo_manager(task, intent)
                result["repository"] = repo_result
                result["success"] = repo_result.get("success", False)
                return result
            
            # 1. Planning & Analysis Agent
            print("🧠 Running Planning & Analysis...")
            analysis_result = self._run_planning_agent(task)
            result["analysis"] = analysis_result
            
            # 2. Execution Agent (if complexity warrants it)
            if intent["complexity"] in ["medium", "high"]:
                print("⚙️  Running Execution Agent...")
                execution_result = self._run_execution_agent(task)
                result["execution"] = execution_result
            
            # 3. Quality & Git Agent
            print("🔍 Running Quality & Git Agent...")
            quality_result = self._run_quality_agent(task)
            result["quality"] = quality_result
            
            result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"❌ Error processing task: {e}")
        
        return result
    
    def _run_planning_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run the planning and analysis agent"""
        # Create a temporary task file for the agent
        temp_task_data = {"temp": {"tasks": [task]}}
        
        temp_file = self.taskmaster_dir / "tasks" / "temp_tasks.json"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_file, 'w') as f:
            json.dump(temp_task_data, f, indent=2)
        
        try:
            # Run planning agent
            cmd = [
                "python3", 
                str(self.agents_dir / "planning-analysis-agent.py"),
                "--tag", "temp",
                "--project-root", str(self.project_root),
                "--verbose"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None
            }
            
        finally:
            # Cleanup temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def _run_execution_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run the universal execution agent"""
        try:
            cmd = [
                "python3",
                str(self.agents_dir / "universal-execution-agent.py"),
                "--project-root", str(self.project_root),
                "--task-data", json.dumps(task)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e)
            }
    
    def _run_quality_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run the quality and git agent"""
        try:
            cmd = [
                "python3",
                str(self.agents_dir / "quality-git-agent.py"),
                "--project-root", str(self.project_root),
                "--skip-git" if task.get("skip_git", False) else "--check-quality"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e)
            }
    
    def _run_repo_manager(self, task: Dict[str, Any], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Run the repository manager agent"""
        try:
            # Extract repository name from entities or prompt
            entities = intent.get("entities", {})
            repo_name = None
            
            # Try to extract repo name from entities
            if entities.get("names"):
                repo_name = entities["names"][0].lower().replace(" ", "-")
            
            # If no name found, suggest one based on project
            if not repo_name:
                repo_name = self.project_root.name
            
            # Extract description from prompt
            description = task.get("description", "Development project with automated tooling")
            
            # Determine if should be private (default to private)
            private = True
            prompt_lower = task.get("description", "").lower()
            if "public" in prompt_lower:
                private = False
            
            cmd = [
                "python3",
                str(self.agents_dir / "repo-manager-agent.py"),
                "--project-root", str(self.project_root),
                "--repo-name", repo_name,
                "--description", description
            ]
            
            if not private:
                cmd.append("--public")
            
            print(f"📋 Repository: {repo_name}")
            print(f"📝 Description: {description}")
            print(f"🔒 Private: {private}")
            print()
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "repo_name": repo_name,
                "description": description,
                "private": private
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
                "repo_name": repo_name if 'repo_name' in locals() else "unknown"
            }

def main():
    """Main interface function"""
    parser = argparse.ArgumentParser(description='Agent Interface - Light User Experience')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--prompt', type=str, help='Direct prompt input')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    interface = AgentInterface(args.project_root)
    
    print("🚀 Development Automation Agent Interface")
    print("=" * 50)
    print(f"Project: {interface.project_root.absolute()}")
    print(f"Type: {interface.project_type}")
    print()
    
    if args.prompt:
        # Process single prompt
        result = interface.process_prompt(args.prompt)
        print("\\n📋 RESULT:")
        print(f"Success: {result['result']['success']}")
        if result['result']['analysis'].get('output'):
            print("Analysis:", result['result']['analysis']['output'][:200] + "...")
        if result['result']['errors']:
            print("Errors:", result['result']['errors'])
    
    elif args.interactive:
        # Interactive mode
        print("Interactive mode - type 'quit' to exit")
        print("Example prompts:")
        print("  - Create a UserProfile component")
        print("  - Add authentication service") 
        print("  - Improve performance of data loading")
        print("  - Add tests for the dashboard")
        print("  - Create GitHub repository")
        print("  - Setup private repo for this project")
        print()
        
        while True:
            try:
                prompt = input("💭 Enter your request: ").strip()
                if prompt.lower() in ['quit', 'exit', 'q']:
                    break
                if not prompt:
                    continue
                
                print()
                result = interface.process_prompt(prompt)
                
                print("\\n📋 SUMMARY:")
                print(f"✅ Task Created: {result['task']['title']}")
                print(f"🎯 Intent: {result['intent']['action']} ({result['intent']['confidence']:.1%})")
                print(f"📊 Complexity: {result['intent']['complexity']}")
                print(f"🔧 Success: {result['result']['success']}")
                
                if result['result']['errors']:
                    print(f"❌ Errors: {len(result['result']['errors'])}")
                
                print("\\n" + "-" * 50 + "\\n")
                
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    else:
        # Show usage
        print("Usage:")
        print("  --prompt 'Create a login component'")
        print("  --interactive  (for interactive mode)")

if __name__ == "__main__":
    main()