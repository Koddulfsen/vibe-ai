#!/usr/bin/env python3
"""
Claude Code Intelligent Prompt Filter
=====================================

A preprocessing layer that uses sequential thinking to determine whether
the Task Master Agent System should be engaged or if requests should be
handled directly by Claude Code.

This filter improves the overall Claude Code experience by:
- Analyzing prompt complexity and intent
- Using sequential thinking for smart routing decisions
- Only engaging agents when they provide clear value
- Seamless integration with existing workflows

Usage:
    python3 claude-code-filter.py "implement a login system"
    python3 claude-code-filter.py "what is 2+2?"
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum
import re

class PromptComplexity(Enum):
    SIMPLE = "simple"           # Direct questions, calculations, explanations
    MODERATE = "moderate"       # File operations, small code changes
    COMPLEX = "complex"         # Multi-step workflows, system architecture
    MULTI_AGENT = "multi_agent" # Requires coordination between multiple systems

class RoutingDecision(Enum):
    DIRECT = "direct"           # Handle directly in Claude Code
    AGENTS = "agents"           # Route to Task Master Agent System
    HYBRID = "hybrid"           # Partial agent assistance + direct handling
    ESCALATE = "escalate"       # Complex decision, let user choose

@dataclass
class SequentialThought:
    """Represents a step in sequential thinking"""
    step: int
    question: str
    analysis: str
    conclusion: str
    confidence: float

@dataclass
class PromptAnalysis:
    """Complete analysis of a user prompt"""
    original_prompt: str
    intent_category: str
    complexity: PromptComplexity
    estimated_steps: int
    requires_file_operations: bool
    requires_external_tools: bool
    requires_planning: bool
    requires_testing: bool
    sequential_thoughts: List[SequentialThought]
    routing_decision: RoutingDecision
    confidence_score: float
    reasoning: str
    agent_requirements: List[str]

class SequentialThinkingEngine:
    """Core engine that performs step-by-step analysis of prompts"""
    
    def __init__(self):
        self.thinking_patterns = {
            'file_operations': [
                "Does this require reading or writing files?",
                "Are there multiple files involved?", 
                "Does this need file structure analysis?"
            ],
            'code_implementation': [
                "Is this asking to write new code?",
                "Does this require understanding existing code?",
                "Are there dependencies or integrations needed?"
            ],
            'system_analysis': [
                "Does this require analyzing project structure?",
                "Are there quality or testing requirements?",
                "Is this a multi-step development workflow?"
            ],
            'simple_query': [
                "Is this a direct question with a clear answer?",
                "Can this be answered without external tools?",
                "Is this just requesting information or explanation?"
            ]
        }
    
    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """Perform comprehensive analysis using sequential thinking"""
        
        # Step 1: Initial categorization
        intent_category = self._categorize_intent(prompt)
        
        # Step 2: Sequential thinking process
        sequential_thoughts = self._perform_sequential_thinking(prompt, intent_category)
        
        # Step 3: Complexity assessment
        complexity = self._assess_complexity(prompt, sequential_thoughts)
        
        # Step 4: Requirements analysis
        requirements = self._analyze_requirements(prompt, sequential_thoughts)
        
        # Step 5: Routing decision
        routing_decision, confidence, reasoning, agent_reqs = self._make_routing_decision(
            prompt, complexity, requirements, sequential_thoughts
        )
        
        return PromptAnalysis(
            original_prompt=prompt,
            intent_category=intent_category,
            complexity=complexity,
            estimated_steps=len(sequential_thoughts),
            requires_file_operations=requirements['file_ops'],
            requires_external_tools=requirements['external_tools'],
            requires_planning=requirements['planning'],
            requires_testing=requirements['testing'],
            sequential_thoughts=sequential_thoughts,
            routing_decision=routing_decision,
            confidence_score=confidence,
            reasoning=reasoning,
            agent_requirements=agent_reqs
        )
    
    def _categorize_intent(self, prompt: str) -> str:
        """Categorize the user's intent"""
        prompt_lower = prompt.lower()
        
        # Code implementation patterns
        if any(word in prompt_lower for word in ['implement', 'create', 'build', 'develop', 'code']):
            return 'implementation'
        
        # Analysis patterns  
        elif any(word in prompt_lower for word in ['analyze', 'review', 'check', 'examine']):
            return 'analysis'
        
        # File operations
        elif any(word in prompt_lower for word in ['file', 'directory', 'folder', 'read', 'write']):
            return 'file_operations'
        
        # Questions and explanations
        elif any(word in prompt_lower for word in ['what', 'how', 'why', 'explain', 'help']):
            return 'question'
        
        # System operations
        elif any(word in prompt_lower for word in ['setup', 'configure', 'install', 'deploy']):
            return 'system_ops'
        
        return 'general'
    
    def _perform_sequential_thinking(self, prompt: str, intent: str) -> List[SequentialThought]:
        """Perform step-by-step sequential thinking"""
        thoughts = []
        
        # Choose thinking pattern based on intent
        if intent == 'implementation':
            pattern_key = 'code_implementation'
        elif intent == 'analysis':
            pattern_key = 'system_analysis'
        elif intent == 'file_operations':
            pattern_key = 'file_operations'
        else:
            pattern_key = 'simple_query'
        
        questions = self.thinking_patterns.get(pattern_key, self.thinking_patterns['simple_query'])
        
        for i, question in enumerate(questions, 1):
            analysis, conclusion, confidence = self._analyze_question(prompt, question)
            
            thoughts.append(SequentialThought(
                step=i,
                question=question,
                analysis=analysis,
                conclusion=conclusion,
                confidence=confidence
            ))
        
        return thoughts
    
    def _analyze_question(self, prompt: str, question: str) -> Tuple[str, str, float]:
        """Analyze a specific question about the prompt"""
        prompt_lower = prompt.lower()
        
        # File operations analysis
        if "file" in question.lower():
            if any(word in prompt_lower for word in ['file', 'read', 'write', 'directory', 'folder']):
                return ("Prompt mentions file operations", "Yes, file operations required", 0.9)
            else:
                return ("No explicit file operations mentioned", "No file operations needed", 0.8)
        
        # Code implementation analysis
        if "code" in question.lower() or "write" in question.lower():
            if any(word in prompt_lower for word in ['implement', 'create', 'build', 'code', 'function', 'class']):
                return ("Prompt asks for code implementation", "Yes, code implementation required", 0.9)
            else:
                return ("No code implementation requested", "No code implementation needed", 0.8)
        
        # Multi-step analysis
        if "step" in question.lower() or "workflow" in question.lower():
            step_indicators = len(re.findall(r'\b(first|then|next|after|finally|step)\b', prompt_lower))
            if step_indicators > 2:
                return ("Multiple workflow steps detected", "Yes, multi-step process", 0.9)
            else:
                return ("Single or simple request", "No complex workflow needed", 0.7)
        
        # External tools analysis
        if "external" in question.lower() or "tool" in question.lower():
            if any(word in prompt_lower for word in ['git', 'npm', 'pip', 'docker', 'api', 'database']):
                return ("External tools/systems mentioned", "Yes, external tools required", 0.8)
            else:
                return ("No external tools mentioned", "No external tools needed", 0.9)
        
        # Default analysis
        return ("General analysis performed", "Standard handling appropriate", 0.6)
    
    def _assess_complexity(self, prompt: str, thoughts: List[SequentialThought]) -> PromptComplexity:
        """Assess overall complexity based on sequential thinking"""
        
        # Calculate complexity score
        complexity_score = 0
        
        # Length and detail indicators
        if len(prompt) > 200:
            complexity_score += 1
        
        # High confidence "yes" answers indicate complexity
        high_confidence_yes = sum(1 for t in thoughts if t.confidence > 0.8 and "yes" in t.conclusion.lower())
        complexity_score += high_confidence_yes
        
        # Multiple steps or requirements
        if len(thoughts) > 3:
            complexity_score += 1
        
        # Keyword complexity indicators
        complex_keywords = ['architecture', 'system', 'integrate', 'workflow', 'pipeline', 'automation']
        if any(keyword in prompt.lower() for keyword in complex_keywords):
            complexity_score += 2
        
        # Map score to complexity level
        if complexity_score <= 1:
            return PromptComplexity.SIMPLE
        elif complexity_score <= 3:
            return PromptComplexity.MODERATE
        elif complexity_score <= 5:
            return PromptComplexity.COMPLEX
        else:
            return PromptComplexity.MULTI_AGENT
    
    def _analyze_requirements(self, prompt: str, thoughts: List[SequentialThought]) -> Dict[str, bool]:
        """Analyze specific requirements from the prompt"""
        prompt_lower = prompt.lower()
        
        return {
            'file_ops': any(word in prompt_lower for word in ['file', 'read', 'write', 'directory']),
            'external_tools': any(word in prompt_lower for word in ['git', 'npm', 'api', 'database', 'deploy']),
            'planning': any(word in prompt_lower for word in ['plan', 'design', 'architecture', 'structure']),
            'testing': any(word in prompt_lower for word in ['test', 'verify', 'validate', 'check'])
        }
    
    def _make_routing_decision(self, prompt: str, complexity: PromptComplexity, 
                             requirements: Dict[str, bool], thoughts: List[SequentialThought]) -> Tuple[RoutingDecision, float, str, List[str]]:
        """Make intelligent routing decision"""
        
        # Simple queries go direct
        if complexity == PromptComplexity.SIMPLE:
            return (
                RoutingDecision.DIRECT, 
                0.9, 
                "Simple query can be handled directly by Claude Code",
                []
            )
        
        # Complex multi-agent scenarios
        if complexity == PromptComplexity.MULTI_AGENT:
            agent_reqs = ['planning', 'execution', 'quality', 'coordinator']
            return (
                RoutingDecision.AGENTS,
                0.9,
                "Complex multi-step task requires full agent coordination",
                agent_reqs
            )
        
        # Moderate complexity - smart routing based on requirements
        if complexity == PromptComplexity.MODERATE:
            if requirements['file_ops'] and requirements['testing']:
                return (
                    RoutingDecision.AGENTS,
                    0.8,
                    "File operations with testing requirements benefit from agent assistance",
                    ['execution', 'quality']
                )
            elif requirements['planning']:
                return (
                    RoutingDecision.HYBRID,
                    0.7,
                    "Planning component benefits from agent analysis, but direct implementation possible",
                    ['planning']
                )
            else:
                return (
                    RoutingDecision.DIRECT,
                    0.7,
                    "Moderate complexity but can be handled directly",
                    []
                )
        
        # Complex scenarios - detailed analysis
        if complexity == PromptComplexity.COMPLEX:
            required_agents = []
            
            if requirements['planning']:
                required_agents.append('planning')
            if requirements['file_ops'] or 'implement' in prompt.lower():
                required_agents.append('execution')
            if requirements['testing']:
                required_agents.append('quality')
            if requirements['external_tools']:
                required_agents.append('repo')
            
            if len(required_agents) >= 2:
                return (
                    RoutingDecision.AGENTS,
                    0.8,
                    f"Complex task requiring {len(required_agents)} specialized agents",
                    required_agents
                )
            else:
                return (
                    RoutingDecision.HYBRID,
                    0.6,
                    "Complex but may benefit from selective agent assistance",
                    required_agents
                )
        
        # Fallback
        return (RoutingDecision.ESCALATE, 0.5, "Unable to determine optimal routing", [])

class ClaudeCodeFilter:
    """Main filter interface for Claude Code integration"""
    
    def __init__(self):
        self.thinking_engine = SequentialThinkingEngine()
        self.agent_system_path = Path(__file__).parent / "master-agent.py"
        
    def filter_prompt(self, prompt: str, verbose: bool = False) -> Dict[str, Any]:
        """Main entry point for prompt filtering"""
        
        start_time = time.time()
        
        # Perform analysis
        analysis = self.thinking_engine.analyze_prompt(prompt)
        
        # Generate response
        response = self._generate_response(analysis, verbose)
        
        # Add timing
        response['processing_time'] = time.time() - start_time
        
        return response
    
    def _generate_response(self, analysis: PromptAnalysis, verbose: bool = False) -> Dict[str, Any]:
        """Generate structured response based on analysis"""
        
        response = {
            'decision': analysis.routing_decision.value,
            'confidence': analysis.confidence_score,
            'reasoning': analysis.reasoning,
            'complexity': analysis.complexity.value,
            'estimated_steps': analysis.estimated_steps
        }
        
        # Add routing instructions
        if analysis.routing_decision == RoutingDecision.DIRECT:
            response['action'] = 'handle_directly'
            response['message'] = "✅ This can be handled directly by Claude Code"
            
        elif analysis.routing_decision == RoutingDecision.AGENTS:
            response['action'] = 'route_to_agents'
            response['agent_command'] = self._build_agent_command(analysis)
            response['message'] = f"🤖 Routing to {len(analysis.agent_requirements)} specialized agents"
            
        elif analysis.routing_decision == RoutingDecision.HYBRID:
            response['action'] = 'hybrid_approach'
            response['agent_command'] = self._build_agent_command(analysis)
            response['message'] = "🔄 Using hybrid approach: agent assistance + direct handling"
            
        else:  # ESCALATE
            response['action'] = 'user_choice'
            response['message'] = "🤔 Would you like to use agents for this task? (y/n)"
        
        # Add verbose details
        if verbose:
            response['analysis'] = {
                'intent_category': analysis.intent_category,
                'requirements': {
                    'file_operations': analysis.requires_file_operations,
                    'external_tools': analysis.requires_external_tools,
                    'planning': analysis.requires_planning,
                    'testing': analysis.requires_testing
                },
                'sequential_thoughts': [
                    {
                        'step': t.step,
                        'question': t.question,
                        'conclusion': t.conclusion,
                        'confidence': t.confidence
                    } for t in analysis.sequential_thoughts
                ]
            }
        
        return response
    
    def _build_agent_command(self, analysis: PromptAnalysis) -> str:
        """Build command to execute agent system"""
        if not analysis.agent_requirements:
            return f"python3 {self.agent_system_path} analyze"
        
        # Determine workflow type based on agents needed
        agents = set(analysis.agent_requirements)
        
        if 'planning' in agents and 'execution' in agents and 'quality' in agents:
            return f"python3 {self.agent_system_path} workflow --type full-dev"
        elif 'planning' in agents:
            return f"python3 {self.agent_system_path} analyze"
        elif 'execution' in agents:
            return f"python3 {self.agent_system_path} workflow --type execute"
        elif 'quality' in agents:
            return f"python3 {self.agent_system_path} quality"
        else:
            return f"python3 {self.agent_system_path} analyze"

def main():
    """CLI interface for testing the filter"""
    if len(sys.argv) < 2:
        print("Usage: python3 claude-code-filter.py '<prompt>' [--verbose]")
        print("\nExamples:")
        print("  python3 claude-code-filter.py 'implement a login system'")
        print("  python3 claude-code-filter.py 'what is 2+2?' --verbose")
        sys.exit(1)
    
    prompt = sys.argv[1]
    verbose = '--verbose' in sys.argv
    
    # Create filter and analyze
    filter_system = ClaudeCodeFilter()
    result = filter_system.filter_prompt(prompt, verbose)
    
    # Display results
    print(f"\n🧠 Claude Code Intelligent Filter")
    print("=" * 50)
    print(f"📝 Prompt: {prompt}")
    print(f"🎯 Decision: {result['decision'].upper()}")
    print(f"🔮 Confidence: {result['confidence']:.1%}")
    print(f"📊 Complexity: {result['complexity']}")
    print(f"⏱️  Processing: {result['processing_time']:.3f}s")
    print()
    print(f"💭 Reasoning: {result['reasoning']}")
    print(f"✨ {result['message']}")
    
    if 'agent_command' in result:
        print(f"\n🤖 Agent Command:")
        print(f"   {result['agent_command']}")
    
    if verbose and 'analysis' in result:
        print(f"\n🔍 Detailed Analysis:")
        analysis = result['analysis']
        print(f"   Intent: {analysis['intent_category']}")
        print(f"   Requirements: {analysis['requirements']}")
        print(f"\n💭 Sequential Thinking:")
        for thought in analysis['sequential_thoughts']:
            print(f"   {thought['step']}. {thought['question']}")
            print(f"      → {thought['conclusion']} ({thought['confidence']:.1%})")

if __name__ == "__main__":
    main()