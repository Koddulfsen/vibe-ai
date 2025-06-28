#!/usr/bin/env python3
"""
Enhanced TaskMaster Bridge
Seamlessly integrates Claude Code with TaskMaster agents using intelligent complexity analysis
and automatic PRD generation with MCP integration.
"""

import json
import subprocess
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
from pathlib import Path

# Import the planning agent for advanced analysis
try:
    from agents.planning_analysis_agent import PlanningAnalysisAgent
    TaskAnalysis = Any  # Type alias for when planning agent not available
    PLANNING_AGENT_AVAILABLE = True
except ImportError:
    PLANNING_AGENT_AVAILABLE = False
    print("Warning: Planning agent not available, using basic analysis")

@dataclass
class EnhancedPRD:
    """Enhanced Product Requirements Document with comprehensive details"""
    title: str
    description: str
    complexity_score: float
    complexity_category: str  # SIMPLE, MODERATE, COMPLEX, MULTI_AGENT
    
    # Core requirements
    objectives: List[str]
    technical_requirements: List[str]
    constraints: List[str]
    success_criteria: List[str]
    
    # Enhanced analysis from planning agent
    missing_files: List[str]
    missing_dependencies: List[str]
    missing_tests: List[str]
    implementation_gaps: List[str]
    discovered_subtasks: List[Dict]
    
    # Workflow and execution
    suggested_agents: List[str]
    workflow_type: str
    estimated_effort: str
    task_id: str
    
    # Innovation and quality
    improvement_suggestions: List[Dict]
    innovation_opportunities: List[str]
    quality_enhancements: List[str]
    implementation_roadmap: List[Dict]
    
    # Git workflow
    git_workflow: List[Dict]
    
    # MCP integration
    mcp_context: Dict[str, Any]
    
    # Metadata
    created_at: str
    project_type: str
    confidence_score: float

class EnhancedTaskMasterBridge:
    """Enhanced bridge between Claude Code and TaskMaster with intelligent routing"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.agents_dir = Path(__file__).parent / "agents"
        self.master_agent = Path(__file__).parent / "master-agent.py"
        
        # Initialize planning agent if available
        if PLANNING_AGENT_AVAILABLE:
            self.planning_agent = PlanningAnalysisAgent(project_root=".")
        else:
            self.planning_agent = None
            
        # MCP server configuration
        self.mcp_config = {
            "server": "taskmaster-ai",
            "enabled": self.config.get("mcp_integration", True),
            "context_depth": self.config.get("mcp_context_depth", 3)
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with enhanced defaults"""
        default_config = {
            "prd_generation_threshold": 5.0,
            "auto_taskmaster_threshold": 6.0,
            "require_confirmation_threshold": 9.0,
            "use_planning_agent": True,
            "generate_innovation_suggestions": True,
            "auto_select_agents": True,
            "mcp_integration": True,
            "mcp_context_depth": 3,
            "verbose": False
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
    
    def analyze_task_complexity(self, task_description: str, additional_context: Dict = None) -> Tuple[float, Dict]:
        """Analyze task complexity using planning agent or fallback"""
        if self.planning_agent and self.config["use_planning_agent"]:
            # Create task dict for planning agent
            task = {
                "title": task_description[:100],
                "description": task_description,
                "details": additional_context.get("details", "") if additional_context else "",
                "id": self._generate_task_id(task_description)
            }
            
            # Get comprehensive analysis
            analysis = self.planning_agent.analyze_task_intelligently(task)
            
            return analysis.complexity_score.total_score, {
                "analysis": analysis,
                "indicators": analysis.complexity_score.indicators,
                "recommendation": analysis.complexity_score.recommendation,
                "should_expand": analysis.complexity_score.should_expand,
                "suggested_subtasks": analysis.complexity_score.suggested_subtasks
            }
        else:
            # Fallback to basic analysis
            return self._basic_complexity_analysis(task_description)
    
    def _basic_complexity_analysis(self, task_description: str) -> Tuple[float, Dict]:
        """Basic complexity analysis as fallback"""
        complexity_keywords = {
            'implement': 2, 'create': 2, 'build': 2, 'integrate': 3,
            'api': 3, 'database': 3, 'authentication': 3, 'testing': 2,
            'deployment': 4, 'architecture': 4, 'refactor': 3, 'optimize': 3
        }
        
        score = 3.0  # Base score
        indicators = {}
        
        text_lower = task_description.lower()
        for keyword, weight in complexity_keywords.items():
            if keyword in text_lower:
                score += weight
                indicators[keyword] = weight
                
        # Length modifier
        if len(task_description) > 200:
            score += 2
        elif len(task_description) > 100:
            score += 1
            
        return score, {
            "indicators": indicators,
            "recommendation": f"Complexity score: {score}",
            "should_expand": score >= self.config["prd_generation_threshold"]
        }
    
    def generate_enhanced_prd(self, task_description: str, complexity_info: Dict, 
                            additional_context: Dict = None) -> EnhancedPRD:
        """Generate comprehensive PRD with all enhancements"""
        # Extract analysis if available
        analysis = complexity_info.get("analysis")
        
        # Generate task ID
        task_id = self._generate_task_id(task_description)
        
        # Determine complexity category
        score = complexity_info.get("score", 0)
        if score < 3:
            category = "SIMPLE"
        elif score < 6:
            category = "MODERATE"
        elif score < 9:
            category = "COMPLEX"
        else:
            category = "MULTI_AGENT"
            
        # Build PRD with all available information
        prd = EnhancedPRD(
            title=self._extract_title(task_description),
            description=task_description,
            complexity_score=score,
            complexity_category=category,
            objectives=self._extract_objectives(task_description, analysis),
            technical_requirements=self._extract_technical_requirements(task_description, analysis),
            constraints=self._extract_constraints(task_description, additional_context),
            success_criteria=self._extract_success_criteria(task_description, analysis),
            missing_files=analysis.missing_files if analysis else [],
            missing_dependencies=analysis.missing_dependencies if analysis else [],
            missing_tests=analysis.missing_tests if analysis else [],
            implementation_gaps=analysis.implementation_gaps if analysis else [],
            discovered_subtasks=analysis.discovered_subtasks if analysis else [],
            suggested_agents=self._suggest_agents(complexity_info, analysis),
            workflow_type=self._determine_workflow_type(complexity_info, analysis),
            estimated_effort=self._estimate_effort(score),
            task_id=task_id,
            improvement_suggestions=analysis.improvement_suggestions if analysis else [],
            innovation_opportunities=analysis.innovation_opportunities if analysis else [],
            quality_enhancements=analysis.quality_enhancements if analysis else [],
            implementation_roadmap=analysis.implementation_roadmap if analysis else [],
            git_workflow=self._format_git_workflow(analysis),
            mcp_context=self._gather_mcp_context(task_description, additional_context),
            created_at=datetime.now().isoformat(),
            project_type=self.planning_agent.project_type if self.planning_agent else "unknown",
            confidence_score=self._calculate_confidence(complexity_info, analysis)
        )
        
        return prd
    
    def _extract_title(self, description: str) -> str:
        """Extract a concise title from description"""
        # Take first sentence or first 80 chars
        first_sentence = description.split('.')[0]
        if len(first_sentence) <= 80:
            return first_sentence
        return description[:77] + "..."
    
    def _extract_objectives(self, description: str, analysis: Optional[Any]) -> List[str]:
        """Extract objectives from description and analysis"""
        objectives = []
        
        # Basic objective from description
        objectives.append(f"Complete the task: {self._extract_title(description)}")
        
        # Add objectives based on discovered work
        if analysis:
            if analysis.missing_files:
                objectives.append(f"Create {len(analysis.missing_files)} missing files")
            if analysis.missing_dependencies:
                objectives.append(f"Install {len(analysis.missing_dependencies)} required dependencies")
            if analysis.missing_tests:
                objectives.append(f"Implement {len(analysis.missing_tests)} test files")
            if analysis.implementation_gaps:
                objectives.append(f"Address {len(analysis.implementation_gaps)} implementation gaps")
                
        return objectives
    
    def _extract_technical_requirements(self, description: str, analysis: Optional[Any]) -> List[str]:
        """Extract technical requirements"""
        requirements = []
        
        # From analysis
        if analysis:
            if analysis.missing_dependencies:
                requirements.append(f"Dependencies: {', '.join(analysis.missing_dependencies[:5])}")
            if analysis.missing_files:
                requirements.append(f"Files to create: {len(analysis.missing_files)} files")
            if analysis.implementation_gaps:
                for gap in analysis.implementation_gaps[:3]:
                    requirements.append(f"Implement: {gap}")
                    
        # From description keywords
        tech_keywords = ['api', 'database', 'authentication', 'testing', 'deployment']
        for keyword in tech_keywords:
            if keyword in description.lower():
                requirements.append(f"{keyword.capitalize()} implementation required")
                
        return requirements
    
    def _extract_constraints(self, description: str, context: Dict = None) -> List[str]:
        """Extract constraints from description and context"""
        constraints = []
        
        # Standard constraints
        constraints.append("Follow existing code conventions and patterns")
        constraints.append("Ensure backward compatibility")
        constraints.append("Write comprehensive tests")
        
        # Context-based constraints
        if context:
            if context.get("deadline"):
                constraints.append(f"Complete by {context['deadline']}")
            if context.get("performance_requirements"):
                constraints.append("Meet performance requirements")
                
        return constraints
    
    def _extract_success_criteria(self, description: str, analysis: Optional[Any]) -> List[str]:
        """Extract success criteria"""
        criteria = []
        
        # Basic criteria
        criteria.append("All code compiles/runs without errors")
        criteria.append("All tests pass")
        criteria.append("Code follows project conventions")
        
        # From analysis
        if analysis:
            if analysis.missing_tests:
                criteria.append("All new code has test coverage")
            if analysis.implementation_gaps:
                criteria.append("All identified gaps are addressed")
                
        return criteria
    
    def _suggest_agents(self, complexity_info: Dict, analysis: Optional[Any]) -> List[str]:
        """Suggest appropriate agents based on analysis"""
        agents = []
        score = complexity_info.get("score", 0)
        
        # Always include planning agent for complex tasks
        if score >= 6:
            agents.append("planning-analysis-agent")
            
        # Execution agents
        if analysis and (analysis.missing_files or analysis.discovered_subtasks):
            agents.append("universal-execution-agent")
        elif score >= 3:
            agents.append("universal-dev-agent")
            
        # Quality agents
        if analysis and analysis.missing_tests:
            agents.append("test-sync-agent")
        if score >= 5:
            agents.append("quality-git-agent")
            
        # Specialized agents
        if analysis and analysis.missing_dependencies:
            agents.append("dependency_manager")
        if "api" in str(complexity_info.get("indicators", {})):
            agents.append("service_integrator")
            
        # Coordinator for complex workflows
        if score >= 7 or len(agents) >= 3:
            agents.append("agent-coordinator")
            
        return agents
    
    def _determine_workflow_type(self, complexity_info: Dict, analysis: Optional[Any]) -> str:
        """Determine optimal workflow type"""
        score = complexity_info.get("score", 0)
        indicators = complexity_info.get("indicators", {})
        
        # Check for specific patterns
        if score >= 8 or (analysis and len(analysis.discovered_subtasks) >= 5):
            return "full-dev"
        elif analysis and (analysis.missing_files or analysis.implementation_gaps):
            return "execute"
        elif analysis and analysis.missing_tests:
            return "quality"
        elif "planning" in str(indicators) or "architecture" in str(indicators):
            return "planning"
        elif score < 4:
            return "quick-fix"
        else:
            return "execute"
    
    def _estimate_effort(self, score: float) -> str:
        """Estimate effort based on complexity score"""
        if score < 3:
            return "30 minutes - 1 hour"
        elif score < 6:
            return "1-3 hours"
        elif score < 9:
            return "3-8 hours"
        else:
            return "1-3 days"
    
    def _format_git_workflow(self, analysis: Optional[Any]) -> List[Dict]:
        """Format git workflow suggestions"""
        if not analysis or not analysis.git_workflow_suggestions:
            return []
            
        return [
            {
                "action": suggestion.action,
                "description": suggestion.description,
                "commands": suggestion.commands,
                "rationale": suggestion.rationale
            }
            for suggestion in analysis.git_workflow_suggestions
        ]
    
    def _gather_mcp_context(self, description: str, context: Dict = None) -> Dict[str, Any]:
        """Gather context for MCP integration"""
        mcp_context = {
            "task_description": description,
            "timestamp": datetime.now().isoformat(),
            "session_id": self._generate_session_id(),
            "tools_available": ["file_operations", "code_analysis", "testing", "git"],
            "environment": {
                "project_type": self.planning_agent.project_type if self.planning_agent else "unknown",
                "has_tests": Path("tests").exists() or Path("test").exists(),
                "has_ci": Path(".github/workflows").exists() or Path(".gitlab-ci.yml").exists()
            }
        }
        
        if context:
            mcp_context["additional_context"] = context
            
        return mcp_context
    
    def _calculate_confidence(self, complexity_info: Dict, analysis: Optional[Any]) -> float:
        """Calculate confidence in the PRD and recommendations"""
        base_confidence = 0.7
        
        # Boost for planning agent analysis
        if analysis:
            base_confidence += 0.1
            
        # Boost for clear indicators
        if complexity_info.get("indicators"):
            base_confidence += min(len(complexity_info["indicators"]) * 0.02, 0.1)
            
        # Reduce for very high complexity
        score = complexity_info.get("score", 0)
        if score > 10:
            base_confidence -= 0.1
            
        return min(max(base_confidence, 0.5), 0.95)
    
    def _generate_task_id(self, description: str) -> str:
        """Generate unique task ID"""
        return hashlib.md5(description.encode()).hexdigest()[:8]
    
    def _generate_session_id(self) -> str:
        """Generate session ID for tracking"""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    def execute_with_taskmaster(self, prd: EnhancedPRD, auto_execute: bool = True) -> Dict:
        """Execute the task using TaskMaster agents"""
        # Save PRD to file for agents to access
        prd_path = Path(f".taskmaster/prds/prd_{prd.task_id}.json")
        prd_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(prd_path, 'w') as f:
            json.dump(asdict(prd), f, indent=2)
            
        # Build command for master agent
        cmd = [
            str(self.master_agent),
            "workflow",
            "--type", prd.workflow_type,
            "--prd", str(prd_path)
        ]
        
        if auto_execute:
            cmd.append("--auto")
            
        if self.config.get("verbose"):
            cmd.append("--verbose")
            
        # Execute workflow
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "prd_path": str(prd_path),
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prd_path": str(prd_path)
            }
    
    def send_to_mcp_server(self, prd: EnhancedPRD) -> Dict:
        """Send PRD to taskmaster-ai MCP server"""
        if not self.mcp_config["enabled"]:
            return {"status": "mcp_disabled"}
            
        # Format for MCP server
        mcp_message = {
            "type": "task_request",
            "prd": asdict(prd),
            "context": prd.mcp_context,
            "agents": prd.suggested_agents,
            "workflow": prd.workflow_type
        }
        
        # TODO: Implement actual MCP server communication
        # For now, save to file that MCP server can read
        mcp_path = Path(f".taskmaster/mcp/task_{prd.task_id}.json")
        mcp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mcp_path, 'w') as f:
            json.dump(mcp_message, f, indent=2)
            
        return {
            "status": "sent_to_mcp",
            "mcp_path": str(mcp_path),
            "task_id": prd.task_id
        }
    
    def process_task(self, task_description: str, additional_context: Dict = None,
                    auto_execute: bool = None) -> Dict:
        """Main entry point for processing tasks"""
        print("🔍 Enhanced TaskMaster Bridge - Analyzing task complexity...")
        
        # Analyze complexity
        complexity_score, complexity_info = self.analyze_task_complexity(task_description, additional_context)
        complexity_info["score"] = complexity_score
        
        print(f"📊 Complexity Score: {complexity_score:.1f} ({complexity_info.get('recommendation', '')})")
        
        # Check thresholds
        if complexity_score < self.config["prd_generation_threshold"]:
            return {
                "action": "direct_handling",
                "complexity_score": complexity_score,
                "reason": "Task is simple enough for direct handling"
            }
            
        # Generate enhanced PRD
        print("📝 Generating Enhanced PRD...")
        prd = self.generate_enhanced_prd(task_description, complexity_info, additional_context)
        
        # Send to MCP if enabled
        mcp_result = self.send_to_mcp_server(prd)
        
        # Display PRD summary
        print(f"\n📋 Enhanced PRD Generated:")
        print(f"   Title: {prd.title}")
        print(f"   Complexity: {prd.complexity_category} (score: {prd.complexity_score:.1f})")
        print(f"   Workflow: {prd.workflow_type}")
        print(f"   Agents: {', '.join(prd.suggested_agents[:3])}...")
        print(f"   Effort: {prd.estimated_effort}")
        print(f"   Confidence: {prd.confidence_score:.2%}")
        
        if prd.missing_dependencies:
            print(f"   📦 Missing Dependencies: {len(prd.missing_dependencies)}")
        if prd.discovered_subtasks:
            print(f"   🎯 Discovered Subtasks: {len(prd.discovered_subtasks)}")
        if prd.improvement_suggestions:
            print(f"   ✨ Improvement Suggestions: {len(prd.improvement_suggestions)}")
            
        # Determine if we should auto-execute
        if auto_execute is None:
            auto_execute = (complexity_score >= self.config["auto_taskmaster_threshold"] and
                          complexity_score < self.config["require_confirmation_threshold"])
                          
        if complexity_score >= self.config["require_confirmation_threshold"]:
            print(f"\n⚠️  High complexity task (score: {complexity_score:.1f})")
            print("This task requires user confirmation before proceeding.")
            try:
                response = input("Execute with TaskMaster? (y/n): ")
                if response.lower() != 'y':
                    return {
                        "action": "user_cancelled",
                        "prd": asdict(prd),
                        "mcp_result": mcp_result
                    }
            except (EOFError, KeyboardInterrupt):
                # Auto-cancel on EOFError
                print("\nAuto-cancelling due to no input available")
                return {
                    "action": "auto_cancelled",
                    "prd": asdict(prd),
                    "mcp_result": mcp_result,
                    "reason": "No interactive input available"
                }
                
        # Execute if appropriate
        if auto_execute:
            print(f"\n🚀 Executing with TaskMaster ({prd.workflow_type} workflow)...")
            execution_result = self.execute_with_taskmaster(prd, auto_execute=True)
            
            return {
                "action": "executed",
                "prd": asdict(prd),
                "execution_result": execution_result,
                "mcp_result": mcp_result
            }
        else:
            return {
                "action": "prd_generated",
                "prd": asdict(prd),
                "mcp_result": mcp_result,
                "next_steps": [
                    f"Review PRD at: .taskmaster/prds/prd_{prd.task_id}.json",
                    f"Execute manually: {self.master_agent} workflow --type {prd.workflow_type} --prd .taskmaster/prds/prd_{prd.task_id}.json"
                ]
            }

def main():
    """CLI interface for enhanced bridge"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced TaskMaster Bridge')
    parser.add_argument('action', choices=['analyze', 'process'], 
                       help='Action to perform')
    parser.add_argument('task', nargs='+', help='Task description')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--auto', action='store_true', 
                       help='Auto-execute if complexity warrants')
    parser.add_argument('--no-mcp', action='store_true',
                       help='Disable MCP integration')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Create bridge
    bridge = EnhancedTaskMasterBridge(args.config)
    
    if args.no_mcp:
        bridge.mcp_config["enabled"] = False
    if args.verbose:
        bridge.config["verbose"] = True
        
    # Process task
    task_description = ' '.join(args.task)
    
    if args.action == 'analyze':
        # Just analyze complexity
        score, info = bridge.analyze_task_complexity(task_description)
        print(f"Complexity Score: {score:.1f}")
        print(f"Category: {info.get('recommendation', 'Unknown')}")
        if info.get('indicators'):
            print(f"Indicators: {', '.join(info['indicators'].keys())}")
    else:
        # Full processing
        result = bridge.process_task(task_description, auto_execute=args.auto)
        
        # Display result
        print(f"\n✅ Processing complete!")
        print(f"Action taken: {result['action']}")
        
        if result.get('prd'):
            print(f"PRD ID: {result['prd']['task_id']}")

if __name__ == "__main__":
    main()