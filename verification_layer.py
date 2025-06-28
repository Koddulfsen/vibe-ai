#!/usr/bin/env python3
"""
Verification Layer for vibe.ai - Prevents hallucinations through multi-level verification
"""

import os
import ast
import re
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


class VerificationLayer:
    """Core verification system for all agent outputs"""
    
    def __init__(self, config_path: str = "config/zero_hallucination.json"):
        self.config = self._load_config(config_path)
        self.evidence_chain = EvidenceChain()
        self.file_verifier = FileSystemVerifier()
        self.code_verifier = CodeVerifier()
        self.pattern_detector = HallucinationPatternDetector()
        
    def _load_config(self, config_path: str) -> dict:
        """Load zero-hallucination configuration"""
        default_config = {
            "strict_mode": True,
            "require_evidence_chain": True,
            "minimum_verification_sources": 2,
            "allow_assumptions": False,
            "allow_interpolation": False,
            "require_explicit_uncertainty": True,
            "fail_on_unverified_claims": True,
            "cross_validation_required": True,
            "confidence_threshold": 0.95,
            "user_confirmation_threshold": 0.8
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return {**default_config, **json.load(f)}
        return default_config
    
    def verify_output(self, agent_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Main verification entry point for agent outputs"""
        verification_result = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "original_output": output,
            "verified_facts": [],
            "unverified_claims": [],
            "hallucination_warnings": [],
            "evidence_chains": [],
            "overall_confidence": 0.0,
            "verification_status": "pending"
        }
        
        # Extract and verify facts
        facts = self._extract_facts(output)
        for fact in facts:
            if self._verify_fact(fact):
                verification_result["verified_facts"].append(fact)
                verification_result["evidence_chains"].append(
                    self.evidence_chain.get_evidence_for_fact(fact)
                )
            else:
                verification_result["unverified_claims"].append(fact)
        
        # Detect hallucination patterns in all text content
        text_to_scan = []
        if isinstance(output, dict):
            # Scan analysis text
            if "analysis" in output:
                text_to_scan.append(output["analysis"])
            # Scan any other text fields
            for key, value in output.items():
                if isinstance(value, str) and key not in ["agent", "timestamp"]:
                    text_to_scan.append(value)
        
        all_warnings = []
        for text in text_to_scan:
            warnings = self.pattern_detector.scan_output(text)
            all_warnings.extend(warnings)
        
        verification_result["hallucination_warnings"] = all_warnings
        
        # Calculate confidence
        verification_result["overall_confidence"] = self._calculate_confidence(
            verification_result
        )
        
        # Determine status
        if verification_result["unverified_claims"] and self.config["fail_on_unverified_claims"]:
            verification_result["verification_status"] = "failed"
        elif verification_result["overall_confidence"] < self.config["confidence_threshold"]:
            verification_result["verification_status"] = "low_confidence"
        else:
            verification_result["verification_status"] = "verified"
        
        return verification_result
    
    def _extract_facts(self, output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract verifiable facts from agent output"""
        facts = []
        
        # Extract file references
        if "files" in output:
            for file_ref in output["files"]:
                facts.append({
                    "type": "file_reference",
                    "content": file_ref,
                    "verifiable": True
                })
        
        # Extract function references
        if "functions" in output:
            for func_ref in output["functions"]:
                facts.append({
                    "type": "function_reference",
                    "content": func_ref,
                    "verifiable": True
                })
        
        # Extract code snippets
        if "code_snippets" in output:
            for snippet in output["code_snippets"]:
                facts.append({
                    "type": "code_snippet",
                    "content": snippet,
                    "verifiable": True
                })
        
        # Extract general claims
        if "analysis" in output:
            claims = self._extract_claims_from_text(output["analysis"])
            facts.extend(claims)
        
        return facts
    
    def _verify_fact(self, fact: Dict[str, Any]) -> bool:
        """Verify a single fact"""
        fact_type = fact.get("type")
        content = fact.get("content")
        
        if fact_type == "file_reference":
            return self.file_verifier.verify_file_reference(content)
        elif fact_type == "function_reference":
            file_path, func_name = self._parse_function_reference(content)
            return self.code_verifier.verify_function_exists(file_path, func_name)
        elif fact_type == "code_snippet":
            file_path, snippet = self._parse_code_snippet(content)
            return self.file_verifier.verify_code_snippet(file_path, snippet)
        else:
            # For unstructured claims, we need more context
            return self._verify_general_claim(fact)
    
    def _calculate_confidence(self, verification_result: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        verified_count = len(verification_result["verified_facts"])
        unverified_count = len(verification_result["unverified_claims"])
        warning_count = len(verification_result["hallucination_warnings"])
        
        if verified_count + unverified_count == 0:
            return 0.0
        
        base_confidence = verified_count / (verified_count + unverified_count)
        
        # Reduce confidence for warnings
        confidence_penalty = warning_count * 0.1
        final_confidence = max(0.0, base_confidence - confidence_penalty)
        
        return final_confidence
    
    def _extract_claims_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract claims from unstructured text"""
        claims = []
        
        # Look for specific patterns
        patterns = [
            (r"file\s+(\S+)\s+contains\s+(\w+)", "file_content_claim"),
            (r"function\s+(\w+)\s+in\s+(\S+)", "function_claim"),
            (r"import\s+(\w+)\s+from\s+(\S+)", "import_claim"),
            (r"class\s+(\w+)\s+in\s+(\S+)", "class_claim")
        ]
        
        for pattern, claim_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append({
                    "type": claim_type,
                    "content": match,
                    "verifiable": True,
                    "source_text": text
                })
        
        return claims
    
    def _parse_function_reference(self, content: str) -> Tuple[str, str]:
        """Parse function reference into file path and function name"""
        # Handle format: "file.py:function_name" or {"file": "path", "function": "name"}
        if isinstance(content, dict):
            return content.get("file", ""), content.get("function", "")
        elif ":" in content:
            parts = content.split(":")
            return parts[0], parts[1] if len(parts) > 1 else ""
        return "", content
    
    def _parse_code_snippet(self, content: Dict[str, Any]) -> Tuple[str, str]:
        """Parse code snippet reference"""
        return content.get("file", ""), content.get("snippet", "")
    
    def _verify_general_claim(self, fact: Dict[str, Any]) -> bool:
        """Verify general claims that don't fit specific patterns"""
        claim_type = fact.get("type")
        content = fact.get("content")
        
        if claim_type == "file_content_claim" and isinstance(content, tuple):
            # content is (file_path, content_name)
            file_path, content_name = content
            if self.file_verifier.verify_file_reference(file_path):
                # Try to verify the content exists in the file
                try:
                    with open(file_path, 'r') as f:
                        file_content = f.read()
                        return content_name in file_content
                except Exception:
                    return False
        
        # For other general claims, mark as unverified
        return False


class FileSystemVerifier:
    """Verify file system related claims"""
    
    def verify_file_reference(self, file_path: str) -> bool:
        """Check if file actually exists"""
        if not file_path:
            return False
        return os.path.exists(file_path)
    
    def verify_code_snippet(self, file_path: str, snippet: str) -> bool:
        """Verify code snippet exists in file"""
        if not self.verify_file_reference(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Normalize whitespace for comparison
                normalized_content = ' '.join(content.split())
                normalized_snippet = ' '.join(snippet.split())
                return normalized_snippet in normalized_content
        except Exception:
            return False
    
    def verify_directory_structure(self, structure: Dict[str, Any]) -> bool:
        """Verify claimed directory structure exists"""
        for path, expected_type in structure.items():
            if expected_type == "directory":
                if not os.path.isdir(path):
                    return False
            elif expected_type == "file":
                if not os.path.isfile(path):
                    return False
        return True


class CodeVerifier:
    """Verify code-related claims using AST"""
    
    def verify_function_exists(self, file_path: str, function_name: str) -> bool:
        """Use AST to verify function existence"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    return True
            return False
        except Exception:
            return False
    
    def verify_class_exists(self, file_path: str, class_name: str) -> bool:
        """Verify class existence in file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    return True
            return False
        except Exception:
            return False
    
    def verify_import_statement(self, file_path: str, import_name: str) -> bool:
        """Verify import exists in file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == import_name:
                            return True
                elif isinstance(node, ast.ImportFrom):
                    if node.module == import_name:
                        return True
                    for alias in node.names:
                        if alias.name == import_name:
                            return True
            return False
        except Exception:
            return False


class HallucinationPatternDetector:
    """Detect patterns that indicate potential hallucinations"""
    
    def __init__(self):
        self.hallucination_patterns = [
            (r"\bshould\b", "assumption", 0.7),
            (r"\blikely\b", "probability_without_evidence", 0.8),
            (r"\btypically\b", "generalization", 0.6),
            (r"\bprobably\b", "speculation", 0.7),
            (r"\busually\s+means\b", "generalization", 0.6),
            (r"\boften\s+indicates\b", "speculation", 0.7),
            (r"\bcommonly\s+used\s+for\b", "generalization", 0.5),
            (r"\bexpected\s+to\b", "assumption", 0.7),
            (r"\bassuming\s+that\b", "explicit_assumption", 0.9),
            (r"\bif\s+.*\s+then\s+.*\s+might\b", "conditional_speculation", 0.8)
        ]
    
    def scan_output(self, output_text: str) -> List[Dict[str, Any]]:
        """Scan output for hallucination patterns"""
        warnings = []
        
        for pattern, pattern_type, severity in self.hallucination_patterns:
            matches = re.finditer(pattern, output_text, re.IGNORECASE)
            for match in matches:
                warnings.append({
                    "pattern": pattern,
                    "type": pattern_type,
                    "severity": severity,
                    "context": output_text[max(0, match.start()-50):match.end()+50],
                    "position": match.start()
                })
        
        return warnings


class EvidenceChain:
    """Track evidence for all claims"""
    
    def __init__(self):
        self.chain = []
    
    def add_evidence(self, fact: str, source: str, verification_method: str, 
                    verified: bool = True) -> str:
        """Add evidence to chain and return evidence ID"""
        evidence_id = hashlib.md5(f"{fact}{source}{datetime.now()}".encode()).hexdigest()[:8]
        
        self.chain.append({
            "id": evidence_id,
            "fact": fact,
            "source": source,
            "verification_method": verification_method,
            "timestamp": datetime.now().isoformat(),
            "verified": verified
        })
        
        return evidence_id
    
    def get_evidence_for_fact(self, fact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all evidence supporting a fact"""
        fact_str = json.dumps(fact, sort_keys=True)
        matching_evidence = []
        for e in self.chain:
            # Check if the fact string appears in the evidence fact
            if fact_str in e["fact"] or e["fact"] == fact_str:
                matching_evidence.append(e)
            # Also check for partial matches on content
            elif isinstance(fact, dict) and "content" in fact:
                if str(fact["content"]) in e["fact"]:
                    matching_evidence.append(e)
        return matching_evidence
    
    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific evidence by ID"""
        for evidence in self.chain:
            if evidence["id"] == evidence_id:
                return evidence
        return None
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """Export the full evidence chain"""
        return self.chain.copy()


class CrossAgentValidator:
    """Validate claims across multiple agents"""
    
    def __init__(self, min_validations: int = 2):
        self.min_validations = min_validations
        self.validation_cache = {}
    
    def validate_claim(self, claim: Dict[str, Any], agent_outputs: List[Dict[str, Any]]) -> bool:
        """Validate a claim across multiple agent outputs"""
        claim_hash = hashlib.md5(json.dumps(claim).encode()).hexdigest()
        
        # Check cache
        if claim_hash in self.validation_cache:
            return self.validation_cache[claim_hash]
        
        # Count independent validations
        validation_count = 0
        for output in agent_outputs:
            if self._independently_validates(claim, output):
                validation_count += 1
        
        result = validation_count >= self.min_validations
        self.validation_cache[claim_hash] = result
        return result
    
    def _independently_validates(self, claim: Dict[str, Any], 
                                output: Dict[str, Any]) -> bool:
        """Check if output independently validates claim"""
        # Look for the claim in the output's verified facts
        if "verified_facts" in output:
            for fact in output["verified_facts"]:
                if self._facts_match(claim, fact):
                    return True
        return False
    
    def _facts_match(self, claim: Dict[str, Any], fact: Dict[str, Any]) -> bool:
        """Check if two facts match"""
        # Simple matching for now - can be made more sophisticated
        return (claim.get("type") == fact.get("type") and 
                claim.get("content") == fact.get("content"))


class UncertaintyHandler:
    """Handle and express uncertainty appropriately"""
    
    def __init__(self):
        self.uncertainty_levels = {
            0.0: "[UNVERIFIED]",
            0.5: "[UNCERTAIN]",
            0.7: "[LIKELY]",
            0.9: "[VERIFIED]",
            0.95: "[CONFIRMED]"
        }
    
    def express_uncertainty(self, statement: str, confidence: float) -> str:
        """Add uncertainty marker to statement"""
        marker = "[UNKNOWN]"
        for threshold, label in sorted(self.uncertainty_levels.items()):
            if confidence >= threshold:
                marker = label
        
        return f"{marker} {statement}"
    
    def require_user_confirmation(self, uncertain_facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create user confirmation request"""
        return {
            "status": "user_verification_required",
            "uncertain_facts": uncertain_facts,
            "message": "Cannot proceed without verifying these facts:",
            "suggested_actions": [
                "Manually verify the facts",
                "Provide additional context",
                "Skip uncertain operations",
                "Proceed with explicit acknowledgment of uncertainty"
            ]
        }
    
    def create_safe_response(self, original_response: str, confidence: float) -> str:
        """Create a safe version of response based on confidence"""
        if confidence < 0.5:
            return f"I cannot verify this information: {original_response}"
        elif confidence < 0.8:
            return f"Based on limited verification: {original_response}"
        else:
            return original_response


# Example usage and integration point
if __name__ == "__main__":
    # Initialize verification layer
    verifier = VerificationLayer()
    
    # Example agent output
    agent_output = {
        "agent": "test_agent",
        "files": ["main.py", "config.json"],
        "functions": [{"file": "main.py", "function": "process_data"}],
        "analysis": "The main.py file contains a process_data function that typically handles data transformation",
        "code_snippets": [{"file": "main.py", "snippet": "def process_data():"}]
    }
    
    # Verify the output
    result = verifier.verify_output("test_agent", agent_output)
    
    print(json.dumps(result, indent=2))