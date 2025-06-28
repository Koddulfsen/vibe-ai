#!/usr/bin/env python3
"""
Agent Coordination System

Robust synchronization and coordination system between all three agents:
- Planning & Analysis Agent
- Universal Execution Agent  
- Quality & Git Agent

Manages shared state, prevents conflicts, enforces quality gates, and handles error recovery.
"""

import json
import time
import threading
import hashlib
import os
import signal
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
import subprocess
import logging

@dataclass
class CoordinationThought:
    """Thought for coordination decisions"""
    step: int
    decision: str
    rationale: str
    impact: str
    agents_affected: List[str]
    confidence: float

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class CoordinationSignal(Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    EMERGENCY_STOP = "emergency_stop"
    QUALITY_GATE_FAILED = "quality_gate_failed"

@dataclass
class AgentState:
    """Current state of an agent"""
    agent_id: str
    status: AgentStatus
    current_task: Optional[str]
    last_activity: float
    error_count: int
    quality_score: float
    sync_version: int

@dataclass
class QualityGate:
    """Quality gate definition"""
    gate_id: str
    description: str
    threshold: float
    current_value: float
    required: bool
    blocking: bool

@dataclass
class CoordinationEvent:
    """Event in the coordination system"""
    event_id: str
    timestamp: float
    agent_id: str
    event_type: str
    data: Dict[str, Any]
    processed: bool

class AgentCoordinator:
    """
    Central coordination system managing all development agents
    """
    
    def __init__(self, project_root: str = ".", config_path: Optional[str] = None):
        self.project_root = Path(project_root)
        self.config = self._load_config(config_path)
        
        # Coordination directories
        self.coordination_dir = self.project_root / ".taskmaster" / "coordination"
        self.agent_sync_dir = self.project_root / ".taskmaster" / "agent_sync"
        self.state_dir = self.coordination_dir / "state"
        self.events_dir = self.coordination_dir / "events"
        self.locks_dir = self.coordination_dir / "locks"
        
        # Create directories
        for dir_path in [self.coordination_dir, self.state_dir, self.events_dir, self.locks_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # State files
        self.project_state_file = self.project_root / ".taskmaster" / "project_state.json"
        self.coordination_state_file = self.coordination_dir / "coordination_state.json"
        self.quality_gates_file = self.coordination_dir / "quality_gates.json"
        
        # Agent definitions
        self.agents = {
            "planning_analysis": {
                "script": "agents/planning-analysis-agent.py",
                "description": "Planning & Analysis Agent",
                "dependencies": [],
                "max_runtime": 300,
                "retry_count": 3
            },
            "universal_execution": {
                "script": "agents/universal-execution-agent.py",
                "description": "Universal Execution Agent",
                "dependencies": ["planning_analysis"],
                "max_runtime": 600,
                "retry_count": 3
            },
            "quality_git": {
                "script": "agents/quality-git-agent.py",
                "description": "Quality & Git Agent",
                "dependencies": ["universal_execution"],
                "max_runtime": 300,
                "retry_count": 2
            }
        }
        
        # Current agent states
        self.agent_states: Dict[str, AgentState] = {}
        self.coordination_state = self._load_coordination_state()
        self.quality_gates = self._load_quality_gates()
        
        # Event queue and processing
        self.event_queue: List[CoordinationEvent] = []
        self.event_lock = threading.Lock()
        self.running = False
        self.shutdown_requested = False
        
        # Initialize agent states
        self._initialize_agent_states()
        
        # Setup logging
        self._setup_logging()
        
        # Sequential thinking for coordination decisions
        self.coordination_thoughts: List[CoordinationThought] = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load coordinator configuration"""
        default_config = {
            "verbose": False,
            "dry_run": False,
            "max_concurrent_agents": 1,
            "quality_gate_enforcement": True,
            "error_recovery": True,
            "sync_interval": 5.0,
            "heartbeat_timeout": 30.0,
            "emergency_stop_timeout": 10.0,
            "conflict_resolution": "latest_wins",
            "backup_state": True
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_logging(self):
        """Setup logging for coordination system"""
        log_dir = self.coordination_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"coordinator_{int(time.time())}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.config['verbose'] else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if self.config['verbose'] else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger('AgentCoordinator')
    
    def think_through_coordination(self, decision_context: str) -> List[CoordinationThought]:
        """Use sequential thinking for coordination decisions"""
        self.coordination_thoughts = []
        
        # Step 1: Assess current state
        thought1 = CoordinationThought(
            step=1,
            decision="Assess current agent states and system health",
            rationale=f"Before making coordination decisions for '{decision_context}', need to understand current system state.",
            impact="Ensures informed decision-making",
            agents_affected=["all"],
            confidence=0.9
        )
        self.coordination_thoughts.append(thought1)
        
        # Step 2: Identify conflicts and dependencies
        thought2 = CoordinationThought(
            step=2,
            decision="Analyze potential conflicts and dependencies",
            rationale="Different agents may have conflicting needs or dependencies that need resolution.",
            impact="Prevents coordination conflicts",
            agents_affected=["planning_analysis", "universal_execution", "quality_git"],
            confidence=0.8
        )
        self.coordination_thoughts.append(thought2)
        
        # Step 3: Determine optimal sequence
        thought3 = CoordinationThought(
            step=3,
            decision="Plan optimal agent execution sequence",
            rationale="Some agents must complete before others can start to ensure proper workflow.",
            impact="Maximizes efficiency and prevents deadlocks",
            agents_affected=["all"],
            confidence=0.85
        )
        self.coordination_thoughts.append(thought3)
        
        # Step 4: Monitor and adapt
        thought4 = CoordinationThought(
            step=4,
            decision="Implement monitoring and adaptation strategy",
            rationale="Coordination decisions may need adjustment based on real-time agent feedback.",
            impact="Ensures robust coordination under changing conditions",
            agents_affected=["coordination_system"],
            confidence=0.75
        )
        self.coordination_thoughts.append(thought4)
        
        if self.config.get('verbose', False):
            self.logger.info(f"🧠 Coordination thinking for: {decision_context}")
            for thought in self.coordination_thoughts:
                self.logger.info(f"   {thought.step}. {thought.decision} (confidence: {thought.confidence:.2f})")
        
        return self.coordination_thoughts
    
    def _load_coordination_state(self) -> Dict[str, Any]:
        """Load coordination state"""
        if self.coordination_state_file.exists():
            try:
                with open(self.coordination_state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load coordination state: {e}")
        
        return {
            "session_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            "started_at": time.time(),
            "total_tasks_processed": 0,
            "total_errors": 0,
            "last_sync": 0,
            "workflow_phase": "idle"
        }
    
    def _save_coordination_state(self):
        """Save coordination state"""
        self.coordination_state["last_sync"] = time.time()
        with open(self.coordination_state_file, 'w') as f:
            json.dump(self.coordination_state, f, indent=2)
    
    def _load_quality_gates(self) -> Dict[str, QualityGate]:
        """Load quality gate definitions"""
        default_gates = {
            "tests_passing": QualityGate(
                gate_id="tests_passing",
                description="All tests must pass",
                threshold=100.0,
                current_value=0.0,
                required=True,
                blocking=True
            ),
            "code_quality": QualityGate(
                gate_id="code_quality",
                description="Code quality score above threshold",
                threshold=8.0,
                current_value=0.0,
                required=True,
                blocking=True
            ),
            "security_score": QualityGate(
                gate_id="security_score",
                description="Security vulnerabilities below threshold",
                threshold=0.0,
                current_value=0.0,
                required=True,
                blocking=True
            ),
            "build_success": QualityGate(
                gate_id="build_success",
                description="Build must succeed",
                threshold=1.0,
                current_value=0.0,
                required=True,
                blocking=True
            )
        }
        
        if self.quality_gates_file.exists():
            try:
                with open(self.quality_gates_file, 'r') as f:
                    data = json.load(f)
                    gates = {}
                    for gate_id, gate_data in data.items():
                        gates[gate_id] = QualityGate(**gate_data)
                    return gates
            except Exception as e:
                self.logger.warning(f"Failed to load quality gates: {e}")
        
        return default_gates
    
    def _save_quality_gates(self):
        """Save quality gate states"""
        gates_data = {}
        for gate_id, gate in self.quality_gates.items():
            gates_data[gate_id] = asdict(gate)
        
        with open(self.quality_gates_file, 'w') as f:
            json.dump(gates_data, f, indent=2)
    
    def _initialize_agent_states(self):
        """Initialize all agent states"""
        for agent_id in self.agents.keys():
            self.agent_states[agent_id] = AgentState(
                agent_id=agent_id,
                status=AgentStatus.IDLE,
                current_task=None,
                last_activity=time.time(),
                error_count=0,
                quality_score=0.0,
                sync_version=0
            )
    
    def acquire_lock(self, resource: str, agent_id: str, timeout: float = 30.0) -> bool:
        """Acquire a coordination lock"""
        lock_file = self.locks_dir / f"{resource}.lock"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if not lock_file.exists():
                    # Create lock
                    lock_data = {
                        "agent_id": agent_id,
                        "resource": resource,
                        "acquired_at": time.time(),
                        "expires_at": time.time() + timeout
                    }
                    with open(lock_file, 'w') as f:
                        json.dump(lock_data, f)
                    
                    self.logger.debug(f"Lock acquired: {resource} by {agent_id}")
                    return True
                else:
                    # Check if lock is expired
                    try:
                        with open(lock_file, 'r') as f:
                            lock_data = json.load(f)
                        
                        if time.time() > lock_data.get('expires_at', 0):
                            # Lock expired, remove it
                            lock_file.unlink()
                            continue
                    except:
                        # Corrupted lock file, remove it
                        lock_file.unlink()
                        continue
                
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error acquiring lock {resource}: {e}")
                return False
        
        self.logger.warning(f"Lock acquisition timeout: {resource} for {agent_id}")
        return False
    
    def release_lock(self, resource: str, agent_id: str) -> bool:
        """Release a coordination lock"""
        lock_file = self.locks_dir / f"{resource}.lock"
        
        try:
            if lock_file.exists():
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                if lock_data.get('agent_id') == agent_id:
                    lock_file.unlink()
                    self.logger.debug(f"Lock released: {resource} by {agent_id}")
                    return True
                else:
                    self.logger.warning(f"Lock release denied: {resource} not owned by {agent_id}")
                    return False
        except Exception as e:
            self.logger.error(f"Error releasing lock {resource}: {e}")
            return False
        
        return True
    
    def add_event(self, agent_id: str, event_type: str, data: Dict[str, Any]) -> str:
        """Add event to coordination queue"""
        event = CoordinationEvent(
            event_id=hashlib.md5(f"{agent_id}{event_type}{time.time()}".encode()).hexdigest()[:8],
            timestamp=time.time(),
            agent_id=agent_id,
            event_type=event_type,
            data=data,
            processed=False
        )
        
        with self.event_lock:
            self.event_queue.append(event)
        
        # Save event to disk for persistence
        event_file = self.events_dir / f"{event.event_id}.json"
        with open(event_file, 'w') as f:
            json.dump(asdict(event), f, indent=2)
        
        self.logger.debug(f"Event added: {event_type} from {agent_id}")
        return event.event_id
    
    def process_events(self):
        """Process all pending events"""
        with self.event_lock:
            events_to_process = [e for e in self.event_queue if not e.processed]
        
        for event in events_to_process:
            try:
                self._process_single_event(event)
                event.processed = True
                
                # Update event file
                event_file = self.events_dir / f"{event.event_id}.json"
                with open(event_file, 'w') as f:
                    json.dump(asdict(event), f, indent=2)
                    
            except Exception as e:
                self.logger.error(f"Error processing event {event.event_id}: {e}")
    
    def _process_single_event(self, event: CoordinationEvent):
        """Process a single coordination event"""
        if event.event_type == "agent_started":
            self._handle_agent_started(event)
        elif event.event_type == "agent_completed":
            self._handle_agent_completed(event)
        elif event.event_type == "agent_failed":
            self._handle_agent_failed(event)
        elif event.event_type == "quality_gate_check":
            self._handle_quality_gate_check(event)
        elif event.event_type == "task_completed":
            self._handle_task_completed(event)
        elif event.event_type == "sync_request":
            self._handle_sync_request(event)
        else:
            self.logger.warning(f"Unknown event type: {event.event_type}")
    
    def _handle_agent_started(self, event: CoordinationEvent):
        """Handle agent started event"""
        agent_id = event.agent_id
        if agent_id in self.agent_states:
            self.agent_states[agent_id].status = AgentStatus.RUNNING
            self.agent_states[agent_id].last_activity = event.timestamp
            self.agent_states[agent_id].current_task = event.data.get('task')
            
            self.logger.info(f"Agent started: {agent_id}")
    
    def _handle_agent_completed(self, event: CoordinationEvent):
        """Handle agent completed event"""
        agent_id = event.agent_id
        if agent_id in self.agent_states:
            self.agent_states[agent_id].status = AgentStatus.COMPLETED
            self.agent_states[agent_id].last_activity = event.timestamp
            self.agent_states[agent_id].current_task = None
            
            self.coordination_state["total_tasks_processed"] += 1
            self.logger.info(f"Agent completed: {agent_id}")
    
    def _handle_agent_failed(self, event: CoordinationEvent):
        """Handle agent failed event"""
        agent_id = event.agent_id
        if agent_id in self.agent_states:
            self.agent_states[agent_id].status = AgentStatus.FAILED
            self.agent_states[agent_id].last_activity = event.timestamp
            self.agent_states[agent_id].error_count += 1
            
            self.coordination_state["total_errors"] += 1
            
            # Trigger error recovery if enabled
            if self.config['error_recovery']:
                self._trigger_error_recovery(agent_id, event.data)
            
            self.logger.error(f"Agent failed: {agent_id} - {event.data.get('error', 'Unknown error')}")
    
    def _handle_quality_gate_check(self, event: CoordinationEvent):
        """Handle quality gate check event"""
        gate_id = event.data.get('gate_id')
        value = event.data.get('value', 0.0)
        
        if gate_id in self.quality_gates:
            gate = self.quality_gates[gate_id]
            gate.current_value = value
            
            if gate.blocking and value < gate.threshold:
                # Quality gate failed - block progression
                self.add_event("coordinator", "quality_gate_failed", {
                    "gate_id": gate_id,
                    "threshold": gate.threshold,
                    "actual": value
                })
                
                self.logger.warning(f"Quality gate failed: {gate_id} ({value} < {gate.threshold})")
            else:
                self.logger.info(f"Quality gate passed: {gate_id} ({value} >= {gate.threshold})")
    
    def _handle_task_completed(self, event: CoordinationEvent):
        """Handle task completed event"""
        task_id = event.data.get('task_id')
        agent_id = event.agent_id
        
        # Update agent state
        if agent_id in self.agent_states:
            self.agent_states[agent_id].last_activity = event.timestamp
        
        # Sync agent states
        self.sync_agent_states()
        
        self.logger.info(f"Task completed: {task_id} by {agent_id}")
    
    def _handle_sync_request(self, event: CoordinationEvent):
        """Handle sync request event"""
        self.sync_agent_states()
        self.logger.debug(f"Sync requested by {event.agent_id}")
    
    def _trigger_error_recovery(self, agent_id: str, error_data: Dict[str, Any]):
        """Trigger error recovery for failed agent"""
        agent_state = self.agent_states.get(agent_id)
        if not agent_state:
            return
        
        # Check if we should retry
        max_retries = self.agents[agent_id].get('retry_count', 3)
        if agent_state.error_count < max_retries:
            self.logger.info(f"Triggering error recovery for {agent_id} (attempt {agent_state.error_count + 1}/{max_retries})")
            
            # Reset agent state for retry
            agent_state.status = AgentStatus.IDLE
            agent_state.error_count += 1
            
            # Add recovery event
            self.add_event("coordinator", "error_recovery", {
                "agent_id": agent_id,
                "attempt": agent_state.error_count,
                "error_data": error_data
            })
        else:
            self.logger.error(f"Max retries exceeded for {agent_id} - marking as permanently failed")
            agent_state.status = AgentStatus.FAILED
    
    def check_quality_gates(self) -> Dict[str, bool]:
        """Check all quality gates"""
        results = {}
        
        for gate_id, gate in self.quality_gates.items():
            passed = gate.current_value >= gate.threshold
            results[gate_id] = passed
            
            if gate.required and not passed:
                self.add_event("coordinator", "quality_gate_failed", {
                    "gate_id": gate_id,
                    "required": True,
                    "threshold": gate.threshold,
                    "actual": gate.current_value
                })
        
        return results
    
    def enforce_quality_gates(self) -> bool:
        """Enforce quality gates and return True if all pass"""
        if not self.config['quality_gate_enforcement']:
            return True
        
        gate_results = self.check_quality_gates()
        required_gates = [
            gate_id for gate_id, gate in self.quality_gates.items() 
            if gate.required and gate.blocking
        ]
        
        for gate_id in required_gates:
            if not gate_results.get(gate_id, False):
                self.logger.warning(f"Required quality gate failed: {gate_id}")
                return False
        
        return True
    
    def sync_agent_states(self):
        """Synchronize states across all agents"""
        # Read sync files from all agents
        sync_data = {}
        
        for sync_file in self.agent_sync_dir.glob("*.json"):
            try:
                with open(sync_file, 'r') as f:
                    agent_sync = json.load(f)
                    agent_name = sync_file.stem
                    sync_data[agent_name] = agent_sync
            except Exception as e:
                self.logger.warning(f"Failed to read sync file {sync_file}: {e}")
        
        # Update coordination state with merged data
        merged_state = self._merge_sync_data(sync_data)
        
        # Save merged state to project state
        if self.project_state_file.exists() or merged_state:
            with open(self.project_state_file, 'w') as f:
                json.dump(merged_state, f, indent=2)
        
        # Update quality gates based on sync data
        self._update_quality_gates_from_sync(sync_data)
        
        self.logger.debug("Agent states synchronized")
    
    def _merge_sync_data(self, sync_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Merge sync data from all agents"""
        merged = {
            "installed_dependencies": set(),
            "created_files": set(),
            "completed_subtasks": set(),
            "project_type": "unknown",
            "build_status": "unknown",
            "test_results": {},
            "errors": [],
            "quality_score": 0.0,
            "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for agent_name, data in sync_data.items():
            project_state = data.get('project_state', {})
            
            # Merge sets
            merged["installed_dependencies"].update(project_state.get('installed_dependencies', []))
            merged["created_files"].update(project_state.get('created_files', []))
            merged["completed_subtasks"].update(project_state.get('completed_subtasks', []))
            
            # Take latest values
            if project_state.get('project_type', 'unknown') != 'unknown':
                merged["project_type"] = project_state['project_type']
            
            if project_state.get('build_status', 'unknown') != 'unknown':
                merged["build_status"] = project_state['build_status']
            
            # Merge test results and errors
            merged["test_results"].update(project_state.get('test_results', {}))
            merged["errors"].extend(project_state.get('errors', []))
            
            # Take highest quality score
            agent_quality = project_state.get('quality_score', 0.0)
            if agent_quality > merged["quality_score"]:
                merged["quality_score"] = agent_quality
        
        # Convert sets back to lists for JSON serialization
        merged["installed_dependencies"] = list(merged["installed_dependencies"])
        merged["created_files"] = list(merged["created_files"])
        merged["completed_subtasks"] = list(merged["completed_subtasks"])
        
        return merged
    
    def _update_quality_gates_from_sync(self, sync_data: Dict[str, Dict]):
        """Update quality gate values from sync data"""
        for agent_name, data in sync_data.items():
            # Update quality gates based on agent data
            if 'quality_gates_status' in data:
                gates_status = data['quality_gates_status']
                
                if 'tests' in gates_status:
                    self.quality_gates['tests_passing'].current_value = 100.0 if gates_status['tests'] else 0.0
                
                if 'build' in gates_status:
                    self.quality_gates['build_success'].current_value = 1.0 if gates_status['build'] else 0.0
    
    def get_next_agent_to_run(self) -> Optional[str]:
        """Determine which agent should run next based on dependencies and state"""
        for agent_id, agent_config in self.agents.items():
            agent_state = self.agent_states[agent_id]
            
            # Skip if already running or failed
            if agent_state.status in [AgentStatus.RUNNING, AgentStatus.FAILED]:
                continue
            
            # Check dependencies
            dependencies_met = True
            for dep_agent in agent_config.get('dependencies', []):
                dep_state = self.agent_states.get(dep_agent)
                if not dep_state or dep_state.status != AgentStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met and agent_state.status != AgentStatus.COMPLETED:
                return agent_id
        
        return None
    
    def run_agent(self, agent_id: str, tag: str = "agents", dry_run: bool = False) -> bool:
        """Run a specific agent"""
        if agent_id not in self.agents:
            self.logger.error(f"Unknown agent: {agent_id}")
            return False
        
        agent_config = self.agents[agent_id]
        script_path = self.project_root / agent_config['script']
        
        if not script_path.exists():
            self.logger.error(f"Agent script not found: {script_path}")
            return False
        
        # Add start event
        self.add_event(agent_id, "agent_started", {"tag": tag, "dry_run": dry_run})
        
        try:
            # Build command
            cmd = [
                "python3", str(script_path),
                "--tag", tag,
                "--verbose" if self.config['verbose'] else "",
                "--dry-run" if dry_run else ""
            ]
            cmd = [arg for arg in cmd if arg]  # Remove empty strings
            
            if self.config['verbose']:
                self.logger.info(f"Running agent {agent_id}: {' '.join(cmd)}")
            
            # Run agent with timeout
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=agent_config.get('max_runtime', 300)
            )
            
            if result.returncode == 0:
                self.add_event(agent_id, "agent_completed", {
                    "exit_code": result.returncode,
                    "output": result.stdout[:1000]  # Truncate output
                })
                self.logger.info(f"Agent {agent_id} completed successfully")
                return True
            else:
                self.add_event(agent_id, "agent_failed", {
                    "exit_code": result.returncode,
                    "error": result.stderr[:1000]
                })
                self.logger.error(f"Agent {agent_id} failed with exit code {result.returncode}")
                return False
        
        except subprocess.TimeoutExpired:
            self.add_event(agent_id, "agent_failed", {
                "error": f"Timeout after {agent_config.get('max_runtime', 300)}s"
            })
            self.logger.error(f"Agent {agent_id} timed out")
            return False
        except Exception as e:
            self.add_event(agent_id, "agent_failed", {"error": str(e)})
            self.logger.error(f"Agent {agent_id} failed with exception: {e}")
            return False
    
    def run_workflow(self, tag: str = "agents", max_cycles: int = 10, dry_run: bool = False) -> bool:
        """Run the complete agent workflow"""
        self.logger.info(f"Starting agent workflow - tag: {tag}, max_cycles: {max_cycles}, dry_run: {dry_run}")
        self.running = True
        
        try:
            # Apply sequential thinking for workflow coordination
            if self.config.get('sequential_thinking', True):
                self.think_through_coordination(f"workflow execution with tag '{tag}'")
            
            for cycle in range(max_cycles):
                if self.shutdown_requested:
                    self.logger.info("Shutdown requested - stopping workflow")
                    break
                
                self.logger.info(f"Workflow cycle {cycle + 1}/{max_cycles}")
                
                # Process pending events
                self.process_events()
                
                # Sync agent states
                self.sync_agent_states()
                
                # Check quality gates
                if not self.enforce_quality_gates():
                    self.logger.warning("Quality gates failed - workflow blocked")
                    continue
                
                # Get next agent to run
                next_agent = self.get_next_agent_to_run()
                if not next_agent:
                    self.logger.info("No more agents to run - workflow complete")
                    break
                
                # Handle git workflow coordination for execution agents
                if next_agent in ["universal_execution", "quality_git"]:
                    self._handle_git_workflow_coordination(next_agent, tag)
                
                # Run the agent
                success = self.run_agent(next_agent, tag, dry_run)
                
                # Finalize git workflow if this was a git-related agent
                if next_agent == "quality_git":
                    self.finalize_git_workflow(success)
                
                if not success and not self.config['error_recovery']:
                    self.logger.error(f"Agent {next_agent} failed and error recovery is disabled")
                    break
                
                # Small delay between agents
                time.sleep(1)
            
            # Final sync
            self.sync_agent_states()
            self._save_coordination_state()
            self._save_quality_gates()
            
            self.logger.info("Workflow completed")
            return True
        
        except KeyboardInterrupt:
            self.logger.info("Workflow interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            return False
        finally:
            self.running = False
    
    def coordinate_git_workflow(self, task: Dict[str, Any]) -> bool:
        """Coordinate git workflow across agents"""
        git_state_file = self.coordination_dir / "git_state.json"
        
        # Load current git state
        git_state = self._load_git_state()
        
        # Check if git workflow coordination is needed
        if not self._requires_git_coordination(task):
            return True
        
        try:
            # Create git coordination lock
            if not self.acquire_lock("git_workflow", "coordinator", timeout=60.0):
                self.logger.warning("Could not acquire git workflow lock")
                return False
            
            # Update git state with task information
            git_state.update({
                "current_task": task,
                "workflow_state": "in_progress",
                "timestamp": time.time(),
                "agents_participating": ["universal_execution", "quality_git"]
            })
            
            # Save git state
            self._save_git_state(git_state)
            
            # Add git coordination event
            self.add_event("coordinator", "git_workflow_started", {
                "task_id": task.get("id"),
                "task_title": task.get("title", ""),
                "branch_strategy": self._determine_branch_strategy(task)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Git workflow coordination failed: {e}")
            return False
        finally:
            self.release_lock("git_workflow", "coordinator")
    
    def _load_git_state(self) -> Dict[str, Any]:
        """Load git coordination state"""
        git_state_file = self.coordination_dir / "git_state.json"
        if git_state_file.exists():
            try:
                with open(git_state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "current_branch": None,
            "current_task": None,
            "workflow_state": "idle",
            "pending_commits": [],
            "last_sync": 0
        }
    
    def _save_git_state(self, git_state: Dict[str, Any]):
        """Save git coordination state"""
        git_state_file = self.coordination_dir / "git_state.json"
        with open(git_state_file, 'w') as f:
            json.dump(git_state, f, indent=2)
    
    def _requires_git_coordination(self, task: Dict[str, Any]) -> bool:
        """Check if task requires git workflow coordination"""
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        # Tasks that typically require git coordination
        git_requiring_patterns = [
            'create', 'implement', 'add', 'update', 'fix', 'refactor',
            'feature', 'bug', 'enhancement', 'build', 'deploy'
        ]
        
        return any(pattern in task_text for pattern in git_requiring_patterns)
    
    def _determine_branch_strategy(self, task: Dict[str, Any]) -> str:
        """Determine appropriate git branch strategy for task"""
        task_text = ' '.join([
            task.get('title', ''),
            task.get('description', ''),
            task.get('details', '') or ''
        ]).lower()
        
        if any(word in task_text for word in ['feature', 'new', 'create', 'implement']):
            return "feature_branch"
        elif any(word in task_text for word in ['fix', 'bug', 'error', 'issue']):
            return "bugfix_branch"
        elif any(word in task_text for word in ['test', 'testing', 'spec']):
            return "test_branch"
        else:
            return "task_branch"
    
    def finalize_git_workflow(self, task_result: bool) -> bool:
        """Finalize git workflow after task completion"""
        try:
            git_state = self._load_git_state()
            
            if git_state.get("workflow_state") != "in_progress":
                return True  # No active workflow to finalize
            
            # Update git state based on task result
            git_state.update({
                "workflow_state": "completed" if task_result else "failed",
                "completion_time": time.time(),
                "success": task_result
            })
            
            # Add finalization event
            self.add_event("coordinator", "git_workflow_completed", {
                "success": task_result,
                "task": git_state.get("current_task", {}),
                "duration": time.time() - git_state.get("timestamp", time.time())
            })
            
            # Save final state
            self._save_git_state(git_state)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Git workflow finalization failed: {e}")
            return False
    
    def _handle_git_workflow_coordination(self, agent_id: str, tag: str):
        """Handle git workflow coordination for specific agents"""
        try:
            # Load current tasks to check if git coordination is needed
            tasks_file = self.project_root / ".taskmaster" / "tasks" / "tasks.json"
            if not tasks_file.exists():
                return
            
            with open(tasks_file, 'r') as f:
                data = json.load(f)
            
            # Get current tasks
            tasks = []
            if isinstance(data, dict) and tag in data:
                tasks = data[tag]['tasks']
            elif isinstance(data, dict) and 'master' in data:
                tasks = data['master']['tasks']
            
            # Find current/pending tasks that need git coordination
            for task in tasks:
                if task.get('status') in ['pending', 'in_progress']:
                    if self._requires_git_coordination(task):
                        self.coordinate_git_workflow(task)
                        break  # Handle one task at a time
                        
        except Exception as e:
            self.logger.warning(f"Git workflow coordination handling failed: {e}")
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        return {
            "coordination": self.coordination_state,
            "agents": {
                agent_id: asdict(state) for agent_id, state in self.agent_states.items()
            },
            "quality_gates": {
                gate_id: asdict(gate) for gate_id, gate in self.quality_gates.items()
            },
            "git_workflow": self._load_git_state(),
            "events": len(self.event_queue),
            "running": self.running
        }
    
    def emergency_stop(self):
        """Emergency stop all agents"""
        self.logger.warning("Emergency stop initiated")
        self.shutdown_requested = True
        self.running = False
        
        # Kill any running processes (simplified)
        for agent_id in self.agent_states:
            if self.agent_states[agent_id].status == AgentStatus.RUNNING:
                self.agent_states[agent_id].status = AgentStatus.BLOCKED
        
        self.add_event("coordinator", "emergency_stop", {"timestamp": time.time()})

def main():
    parser = argparse.ArgumentParser(description='Agent Coordination System')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--project-root', type=str, default='.', help='Project root directory')
    parser.add_argument('--tag', type=str, default='agents', help='Task Master tag to process')
    parser.add_argument('--mode', choices=['workflow', 'status', 'sync', 'monitor'], 
                       default='workflow', help='Operation mode')
    parser.add_argument('--max-cycles', type=int, default=10, help='Maximum workflow cycles')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--no-quality-gates', action='store_true', help='Disable quality gate enforcement')
    
    args = parser.parse_args()
    
    # Create coordinator
    coordinator = AgentCoordinator(args.project_root, args.config)
    coordinator.config.update({
        'verbose': args.verbose,
        'quality_gate_enforcement': not args.no_quality_gates
    })
    
    # Handle interrupt signal
    def signal_handler(signum, frame):
        coordinator.emergency_stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Execute based on mode
    if args.mode == 'workflow':
        success = coordinator.run_workflow(args.tag, args.max_cycles, args.dry_run)
        exit(0 if success else 1)
    elif args.mode == 'status':
        status = coordinator.get_status_report()
        print(json.dumps(status, indent=2, default=str))
    elif args.mode == 'sync':
        coordinator.sync_agent_states()
        print("Agent states synchronized")
    elif args.mode == 'monitor':
        # Simple monitoring loop
        try:
            while True:
                coordinator.process_events()
                coordinator.sync_agent_states()
                time.sleep(coordinator.config['sync_interval'])
        except KeyboardInterrupt:
            print("Monitoring stopped")

if __name__ == "__main__":
    main()