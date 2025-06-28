#!/usr/bin/env python3
"""
Quality Assessment Engine
========================

Comprehensive quality assessment and validation system for Task Master agents.
Provides robust internal testing, validation, and quality scoring.
"""

import re
import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import tempfile

class QualityDimension(Enum):
    """Different dimensions of quality assessment"""
    TASK_COMPLETION = "task_completion"
    CORRECTNESS = "correctness" 
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    DELIVERABLES = "deliverables"
    CODE_QUALITY = "code_quality"
    TEST_COVERAGE = "test_coverage"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"

@dataclass
class QualityMetric:
    """Individual quality metric with scoring"""
    dimension: QualityDimension
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0 
    evidence: List[str]  # Evidence supporting this score
    issues: List[str]  # Issues found
    recommendations: List[str]  # Improvement suggestions

@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    agent_name: str
    request_type: str
    metrics: Dict[QualityDimension, QualityMetric] = field(default_factory=dict)
    overall_score: float = 0.0
    confidence: float = 0.0
    critical_issues: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    def get_weighted_score(self, weights: Dict[QualityDimension, float] = None) -> float:
        """Calculate weighted quality score"""
        if not weights:
            weights = {dim: 1.0 for dim in QualityDimension}
        
        total_score = 0.0
        total_weight = 0.0
        
        for dimension, metric in self.metrics.items():
            weight = weights.get(dimension, 1.0)
            total_score += metric.score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0

class QualityValidator:
    """Validates agent outputs and deliverables"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        
    def validate_files_created(self, expected_files: List[str], 
                             context: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate that expected files were created"""
        evidence = []
        issues = []
        created_count = 0
        
        for file_path in expected_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                created_count += 1
                evidence.append(f"✓ Created: {file_path}")
                
                # Check file size and content
                if full_path.stat().st_size > 0:
                    evidence.append(f"  - Non-empty ({full_path.stat().st_size} bytes)")
                else:
                    issues.append(f"⚠ Empty file: {file_path}")
            else:
                issues.append(f"✗ Missing: {file_path}")
        
        score = created_count / len(expected_files) if expected_files else 1.0
        return score, evidence, issues
    
    def validate_code_syntax(self, file_paths: List[str]) -> Tuple[float, List[str], List[str]]:
        """Validate syntax of code files"""
        evidence = []
        issues = []
        valid_count = 0
        
        for file_path in file_paths:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue
                
            # Check Python syntax
            if file_path.endswith('.py'):
                try:
                    with open(full_path, 'r') as f:
                        compile(f.read(), file_path, 'exec')
                    valid_count += 1
                    evidence.append(f"✓ Valid Python syntax: {file_path}")
                except SyntaxError as e:
                    issues.append(f"✗ Syntax error in {file_path}: {e}")
                except Exception as e:
                    issues.append(f"⚠ Could not validate {file_path}: {e}")
            
            # Check JavaScript syntax (basic)
            elif file_path.endswith('.js'):
                try:
                    result = subprocess.run(['node', '-c', str(full_path)], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        valid_count += 1
                        evidence.append(f"✓ Valid JavaScript syntax: {file_path}")
                    else:
                        issues.append(f"✗ JS syntax error in {file_path}: {result.stderr}")
                except:
                    issues.append(f"⚠ Could not validate JS file: {file_path}")
            else:
                # Assume valid for other file types
                valid_count += 1
                evidence.append(f"✓ File exists: {file_path}")
        
        score = valid_count / len(file_paths) if file_paths else 1.0
        return score, evidence, issues
    
    def validate_tests_executable(self, test_commands: List[str]) -> Tuple[float, List[str], List[str]]:
        """Validate that tests can be executed"""
        evidence = []
        issues = []
        passed_count = 0
        
        for cmd in test_commands:
            try:
                result = subprocess.run(cmd.split(), 
                                      capture_output=True, text=True, 
                                      timeout=30, cwd=self.project_root)
                if result.returncode == 0:
                    passed_count += 1
                    evidence.append(f"✓ Test passed: {cmd}")
                    # Parse test output for more details
                    if 'passed' in result.stdout.lower():
                        evidence.append(f"  - Test results: {result.stdout.split()[0]} tests")
                else:
                    issues.append(f"✗ Test failed: {cmd}")
                    issues.append(f"  - Error: {result.stderr[:100]}")
            except subprocess.TimeoutExpired:
                issues.append(f"⚠ Test timeout: {cmd}")
            except Exception as e:
                issues.append(f"⚠ Could not run test: {cmd} ({e})")
        
        score = passed_count / len(test_commands) if test_commands else 1.0
        return score, evidence, issues

class SemanticAnalyzer:
    """Analyzes output for semantic quality and relevance"""
    
    def analyze_task_completion(self, output: str, expected_keywords: List[str]) -> Tuple[float, List[str], List[str]]:
        """Analyze if task appears to be completed based on output"""
        evidence = []
        issues = []
        
        # Look for completion indicators
        completion_patterns = [
            r'\b(completed?|finished|done|success|implemented)\b',
            r'\b(created?|built|generated|added)\b',
            r'✅|✓',
            r'\bpassed\b'
        ]
        
        completion_score = 0.0
        for pattern in completion_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                completion_score += 0.2
                evidence.append(f"Found completion indicator: {matches[0]}")
        
        # Check for expected keywords
        keyword_score = 0.0
        if expected_keywords:
            found_keywords = []
            for keyword in expected_keywords:
                if keyword.lower() in output.lower():
                    found_keywords.append(keyword)
                    keyword_score += 1.0 / len(expected_keywords)
            
            if found_keywords:
                evidence.append(f"Found expected keywords: {', '.join(found_keywords)}")
            else:
                issues.append("No expected keywords found in output")
        
        # Look for error indicators
        error_patterns = [
            r'\b(error|failed|failure|exception|traceback)\b',
            r'❌|✗',
            r'\btimeout\b',
            r'\bcrash\b'
        ]
        
        error_penalty = 0.0
        for pattern in error_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                error_penalty += 0.1
                issues.append(f"Found error indicator: {matches[0]}")
        
        final_score = min(1.0, max(0.0, completion_score + keyword_score - error_penalty))
        return final_score, evidence, issues
    
    def analyze_output_relevance(self, output: str, request_context: str) -> Tuple[float, List[str], List[str]]:
        """Analyze how relevant the output is to the original request"""
        evidence = []
        issues = []
        
        # Extract key terms from request
        request_words = set(re.findall(r'\b\w+\b', request_context.lower()))
        output_words = set(re.findall(r'\b\w+\b', output.lower()))
        
        # Calculate overlap
        common_words = request_words.intersection(output_words)
        relevance_score = len(common_words) / len(request_words) if request_words else 0.0
        
        if relevance_score > 0.3:
            evidence.append(f"Good keyword overlap: {len(common_words)}/{len(request_words)} words")
            evidence.append(f"Common terms: {', '.join(list(common_words)[:5])}")
        else:
            issues.append(f"Low relevance: only {len(common_words)}/{len(request_words)} keywords match")
        
        # Check output length appropriateness
        if len(output) < 50:
            issues.append("Output very brief, may be incomplete")
            relevance_score *= 0.8
        elif len(output) > 5000:
            evidence.append("Detailed output provided")
            relevance_score *= 1.1
        
        return min(1.0, relevance_score), evidence, issues

class QualityAssessmentEngine:
    """Main engine for comprehensive quality assessment"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.validator = QualityValidator(project_root)
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Quality dimension weights for different agent types
        self.agent_weights = {
            'planning': {
                QualityDimension.TASK_COMPLETION: 0.3,
                QualityDimension.RELEVANCE: 0.3,
                QualityDimension.COMPLETENESS: 0.2,
                QualityDimension.DOCUMENTATION: 0.2
            },
            'execution': {
                QualityDimension.DELIVERABLES: 0.3,
                QualityDimension.CODE_QUALITY: 0.25,
                QualityDimension.TEST_COVERAGE: 0.2,
                QualityDimension.TASK_COMPLETION: 0.25
            },
            'quality': {
                QualityDimension.TEST_COVERAGE: 0.4,
                QualityDimension.CODE_QUALITY: 0.3,
                QualityDimension.ERROR_HANDLING: 0.3
            }
        }
    
    def assess_agent_output(self, agent_name: str, output: str, 
                          request_context: str, result_context: Dict[str, Any]) -> QualityReport:
        """Perform comprehensive quality assessment of agent output"""
        
        report = QualityReport(
            agent_name=agent_name,
            request_type=result_context.get('request_type', 'unknown')
        )
        
        # Assess different quality dimensions
        self._assess_task_completion(report, output, request_context, result_context)
        self._assess_deliverables(report, output, result_context)
        self._assess_code_quality(report, output, result_context)
        self._assess_relevance(report, output, request_context)
        self._assess_completeness(report, output, result_context)
        self._assess_error_handling(report, output, result_context)
        
        # Calculate overall scores
        weights = self.agent_weights.get(agent_name, {})
        report.overall_score = report.get_weighted_score(weights)
        report.confidence = self._calculate_confidence(report)
        
        # Classify issues
        self._classify_issues(report)
        
        return report
    
    def _assess_task_completion(self, report: QualityReport, output: str, 
                              request_context: str, result_context: Dict[str, Any]):
        """Assess task completion quality"""
        
        # Extract expected keywords from request
        expected_keywords = self._extract_keywords(request_context)
        
        score, evidence, issues = self.semantic_analyzer.analyze_task_completion(
            output, expected_keywords)
        
        # Additional completion checks
        if result_context.get('success', False):
            evidence.append("Agent reported success")
            score += 0.1
        
        if result_context.get('duration', 0) > 0:
            evidence.append(f"Task executed in {result_context['duration']:.1f}s")
        
        metric = QualityMetric(
            dimension=QualityDimension.TASK_COMPLETION,
            score=min(1.0, score),
            confidence=0.8,
            evidence=evidence,
            issues=issues,
            recommendations=self._generate_completion_recommendations(issues)
        )
        
        report.metrics[QualityDimension.TASK_COMPLETION] = metric
    
    def _assess_deliverables(self, report: QualityReport, output: str, 
                           result_context: Dict[str, Any]):
        """Assess quality of deliverables created"""
        
        evidence = []
        issues = []
        score = 0.5  # Base score
        
        # Check for file creation mentions
        file_patterns = [
            r'created?\s+(?:file\s+)?([^\s]+\.(?:py|js|md|json|txt))',
            r'(?:wrote|generated|built)\s+([^\s]+\.(?:py|js|md|json|txt))',
            r'added?\s+([^\s]+\.(?:py|js|md|json|txt))'
        ]
        
        created_files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            created_files.extend(matches)
        
        if created_files:
            evidence.append(f"Files mentioned: {', '.join(created_files)}")
            
            # Validate actual files exist
            file_score, file_evidence, file_issues = self.validator.validate_files_created(
                created_files, result_context)
            score += file_score * 0.3
            evidence.extend(file_evidence)
            issues.extend(file_issues)
            
            # Validate code syntax
            code_files = [f for f in created_files if f.endswith(('.py', '.js'))]
            if code_files:
                syntax_score, syntax_evidence, syntax_issues = self.validator.validate_code_syntax(
                    code_files)
                score += syntax_score * 0.2
                evidence.extend(syntax_evidence)
                issues.extend(syntax_issues)
        
        # Check for test execution
        test_patterns = [
            r'(pytest|npm test|python -m pytest|jest|mocha)',
            r'tests?\s+(?:passed|ran|executed)'
        ]
        
        for pattern in test_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                evidence.append("Tests mentioned in output")
                score += 0.1
                break
        
        metric = QualityMetric(
            dimension=QualityDimension.DELIVERABLES,
            score=min(1.0, score),
            confidence=0.7,
            evidence=evidence,
            issues=issues,
            recommendations=self._generate_deliverable_recommendations(issues)
        )
        
        report.metrics[QualityDimension.DELIVERABLES] = metric
    
    def _assess_code_quality(self, report: QualityReport, output: str, 
                           result_context: Dict[str, Any]):
        """Assess code quality aspects"""
        
        evidence = []
        issues = []
        score = 0.5
        
        # Look for quality indicators
        quality_indicators = [
            (r'\blint\b.*(?:passed|clean|no errors)', 0.2, "Linting passed"),
            (r'\btype.*check.*(?:passed|clean)', 0.15, "Type checking passed"),
            (r'\bformat.*(?:applied|fixed)', 0.1, "Code formatting applied"),
            (r'\bdocstring|comment.*added', 0.1, "Documentation added"),
            (r'\brefactor', 0.1, "Code refactoring mentioned")
        ]
        
        for pattern, weight, description in quality_indicators:
            if re.search(pattern, output, re.IGNORECASE):
                score += weight
                evidence.append(description)
        
        # Look for quality issues
        quality_issues = [
            (r'\blint.*(?:error|fail|warn)', "Linting issues found"),
            (r'\btype.*(?:error|fail)', "Type checking issues"),
            (r'\bsyntax.*error', "Syntax errors detected"),
            (r'\bundefined.*variable', "Undefined variables")
        ]
        
        for pattern, description in quality_issues:
            if re.search(pattern, output, re.IGNORECASE):
                issues.append(description)
                score -= 0.1
        
        metric = QualityMetric(
            dimension=QualityDimension.CODE_QUALITY,
            score=max(0.0, min(1.0, score)),
            confidence=0.6,
            evidence=evidence,
            issues=issues,
            recommendations=self._generate_code_quality_recommendations(issues)
        )
        
        report.metrics[QualityDimension.CODE_QUALITY] = metric
    
    def _assess_relevance(self, report: QualityReport, output: str, request_context: str):
        """Assess output relevance to request"""
        
        score, evidence, issues = self.semantic_analyzer.analyze_output_relevance(
            output, request_context)
        
        metric = QualityMetric(
            dimension=QualityDimension.RELEVANCE,
            score=score,
            confidence=0.7,
            evidence=evidence,
            issues=issues,
            recommendations=self._generate_relevance_recommendations(issues)
        )
        
        report.metrics[QualityDimension.RELEVANCE] = metric
    
    def _assess_completeness(self, report: QualityReport, output: str, 
                           result_context: Dict[str, Any]):
        """Assess completeness of the work"""
        
        evidence = []
        issues = []
        score = 0.3  # Base score
        
        # Check output length and detail
        if len(output) > 200:
            score += 0.2
            evidence.append("Substantial output provided")
        
        if output.count('\n') > 10:
            score += 0.1
            evidence.append("Detailed multi-line output")
        
        # Look for completion phrases
        completion_phrases = [
            r'\bcomplete[d]?\b',
            r'\bfinished\b',
            r'\ball\s+(?:steps|tasks|requirements).*(?:done|complete)',
            r'\bfully\s+implemented\b'
        ]
        
        for phrase in completion_phrases:
            if re.search(phrase, output, re.IGNORECASE):
                score += 0.2
                evidence.append(f"Completion phrase found: {phrase}")
                break
        
        # Check for incomplete indicators
        incomplete_phrases = [
            r'\btodo\b|TODO',
            r'\bpartial(?:ly)?\s+(?:complete|implement)',
            r'\bnext\s+steps?\b',
            r'\bremaining\s+work\b'
        ]
        
        for phrase in incomplete_phrases:
            if re.search(phrase, output, re.IGNORECASE):
                issues.append(f"Incomplete indicator: {phrase}")
                score -= 0.1
        
        metric = QualityMetric(
            dimension=QualityDimension.COMPLETENESS,
            score=max(0.0, min(1.0, score)),
            confidence=0.6,
            evidence=evidence,
            issues=issues,
            recommendations=self._generate_completeness_recommendations(issues)
        )
        
        report.metrics[QualityDimension.COMPLETENESS] = metric
    
    def _assess_error_handling(self, report: QualityReport, output: str, 
                             result_context: Dict[str, Any]):
        """Assess error handling and robustness"""
        
        evidence = []
        issues = []
        score = 0.5
        
        # Look for error handling
        error_handling_indicators = [
            (r'\btry.*except\b', "Exception handling found"),
            (r'\berror.*handling\b', "Error handling mentioned"),
            (r'\bvalidation\b', "Validation implemented"),
            (r'\bfallback\b', "Fallback mechanism")
        ]
        
        for pattern, description in error_handling_indicators:
            if re.search(pattern, output, re.IGNORECASE):
                score += 0.15
                evidence.append(description)
        
        # Look for unhandled errors
        error_indicators = [
            (r'\btraceback\b', "Unhandled exception traceback"),
            (r'\berror:(?!\s*handling)', "Error messages"),
            (r'\bfailed\s+to\b', "Failure without handling"),
            (r'\bcrash\b', "System crash mentioned")
        ]
        
        for pattern, description in error_indicators:
            if re.search(pattern, output, re.IGNORECASE):
                issues.append(description)
                score -= 0.2
        
        metric = QualityMetric(
            dimension=QualityDimension.ERROR_HANDLING,
            score=max(0.0, min(1.0, score)),
            confidence=0.5,
            evidence=evidence,
            issues=issues,
            recommendations=self._generate_error_handling_recommendations(issues)
        )
        
        report.metrics[QualityDimension.ERROR_HANDLING] = metric
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from request text"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                    'before', 'after', 'above', 'below', 'between', 'among', 'through',
                    'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we',
                    'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself'}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return list(set(keywords))[:10]  # Top 10 unique keywords
    
    def _calculate_confidence(self, report: QualityReport) -> float:
        """Calculate overall confidence in assessment"""
        if not report.metrics:
            return 0.0
        
        total_confidence = sum(metric.confidence for metric in report.metrics.values())
        return total_confidence / len(report.metrics)
    
    def _classify_issues(self, report: QualityReport):
        """Classify issues into different severity levels"""
        
        for metric in report.metrics.values():
            for issue in metric.issues:
                if any(word in issue.lower() for word in ['error', 'fail', 'crash', 'missing']):
                    if metric.score < 0.3:
                        report.critical_issues.append(f"{metric.dimension.value}: {issue}")
                    elif metric.score < 0.6:
                        report.blockers.append(f"{metric.dimension.value}: {issue}")
                    else:
                        report.warnings.append(f"{metric.dimension.value}: {issue}")
    
    # Recommendation generators
    def _generate_completion_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any('keyword' in issue.lower() for issue in issues):
            recommendations.append("Include more specific task-related keywords in output")
        if any('indicator' in issue.lower() for issue in issues):
            recommendations.append("Add explicit completion status indicators")
        return recommendations
    
    def _generate_deliverable_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Ensure all expected files are created")
        if any('empty' in issue.lower() for issue in issues):
            recommendations.append("Add meaningful content to created files")
        if any('syntax' in issue.lower() for issue in issues):
            recommendations.append("Validate code syntax before completion")
        return recommendations
    
    def _generate_code_quality_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any('lint' in issue.lower() for issue in issues):
            recommendations.append("Run linting tools and fix issues")
        if any('type' in issue.lower() for issue in issues):
            recommendations.append("Add type annotations and run type checker")
        if any('syntax' in issue.lower() for issue in issues):
            recommendations.append("Fix syntax errors before submission")
        return recommendations
    
    def _generate_relevance_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any('relevance' in issue.lower() for issue in issues):
            recommendations.append("Focus output more closely on the original request")
        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Provide more detailed explanations")
        return recommendations
    
    def _generate_completeness_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any('incomplete' in issue.lower() for issue in issues):
            recommendations.append("Complete all remaining work before finishing")
        if any('todo' in issue.lower() for issue in issues):
            recommendations.append("Resolve all TODO items")
        return recommendations
    
    def _generate_error_handling_recommendations(self, issues: List[str]) -> List[str]:
        recommendations = []
        if any('exception' in issue.lower() for issue in issues):
            recommendations.append("Add proper exception handling")
        if any('error' in issue.lower() for issue in issues):
            recommendations.append("Implement error recovery mechanisms")
        if any('crash' in issue.lower() for issue in issues):
            recommendations.append("Add robustness checks to prevent crashes")
        return recommendations