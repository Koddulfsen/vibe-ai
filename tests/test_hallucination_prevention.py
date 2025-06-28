#!/usr/bin/env python3
"""
Test suite for hallucination prevention in vibe.ai
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification_layer import (
    VerificationLayer, FileSystemVerifier, CodeVerifier,
    HallucinationPatternDetector, EvidenceChain, CrossAgentValidator,
    UncertaintyHandler
)


class TestFileSystemVerifier(unittest.TestCase):
    """Test file system verification capabilities"""
    
    def setUp(self):
        self.verifier = FileSystemVerifier()
        self.temp_dir = tempfile.mkdtemp()
        
    def test_verify_existing_file(self):
        """Test verification of existing file"""
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("print('hello')")
        
        self.assertTrue(self.verifier.verify_file_reference(test_file))
    
    def test_verify_nonexistent_file(self):
        """Test verification fails for non-existent file"""
        fake_file = os.path.join(self.temp_dir, "fake.py")
        self.assertFalse(self.verifier.verify_file_reference(fake_file))
    
    def test_verify_code_snippet_exists(self):
        """Test verification of existing code snippet"""
        test_file = os.path.join(self.temp_dir, "test.py")
        content = "def hello():\n    print('world')"
        with open(test_file, 'w') as f:
            f.write(content)
        
        self.assertTrue(self.verifier.verify_code_snippet(test_file, "def hello():"))
        self.assertTrue(self.verifier.verify_code_snippet(test_file, "print('world')"))
    
    def test_verify_code_snippet_not_exists(self):
        """Test verification fails for non-existent snippet"""
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def hello():\n    print('world')")
        
        self.assertFalse(self.verifier.verify_code_snippet(test_file, "def goodbye():"))
    
    def test_verify_directory_structure(self):
        """Test directory structure verification"""
        os.makedirs(os.path.join(self.temp_dir, "subdir"))
        file_path = os.path.join(self.temp_dir, "file.txt")
        with open(file_path, 'w') as f:
            f.write("test")
        
        structure = {
            self.temp_dir: "directory",
            os.path.join(self.temp_dir, "subdir"): "directory",
            file_path: "file"
        }
        
        self.assertTrue(self.verifier.verify_directory_structure(structure))
        
        # Add non-existent path
        structure[os.path.join(self.temp_dir, "fake")] = "directory"
        self.assertFalse(self.verifier.verify_directory_structure(structure))


class TestCodeVerifier(unittest.TestCase):
    """Test code verification using AST"""
    
    def setUp(self):
        self.verifier = CodeVerifier()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_verify_function_exists(self):
        """Test function existence verification"""
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("""
def existing_function():
    pass

class MyClass:
    def method(self):
        pass
""")
        
        self.assertTrue(self.verifier.verify_function_exists(test_file, "existing_function"))
        self.assertFalse(self.verifier.verify_function_exists(test_file, "nonexistent_function"))
        # Note: Our current AST implementation finds all function definitions, including methods
        # This is actually useful for comprehensive verification
        self.assertTrue(self.verifier.verify_function_exists(test_file, "method"))
    
    def test_verify_class_exists(self):
        """Test class existence verification"""
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("""
class ExistingClass:
    pass

def not_a_class():
    pass
""")
        
        self.assertTrue(self.verifier.verify_class_exists(test_file, "ExistingClass"))
        self.assertFalse(self.verifier.verify_class_exists(test_file, "NonexistentClass"))
        self.assertFalse(self.verifier.verify_class_exists(test_file, "not_a_class"))
    
    def test_verify_import_statement(self):
        """Test import verification"""
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("""
import os
import json
from pathlib import Path
from typing import List, Dict
""")
        
        self.assertTrue(self.verifier.verify_import_statement(test_file, "os"))
        self.assertTrue(self.verifier.verify_import_statement(test_file, "json"))
        self.assertTrue(self.verifier.verify_import_statement(test_file, "pathlib"))
        self.assertTrue(self.verifier.verify_import_statement(test_file, "Path"))
        self.assertTrue(self.verifier.verify_import_statement(test_file, "typing"))
        self.assertFalse(self.verifier.verify_import_statement(test_file, "numpy"))


class TestHallucinationPatternDetector(unittest.TestCase):
    """Test hallucination pattern detection"""
    
    def setUp(self):
        self.detector = HallucinationPatternDetector()
    
    def test_detect_assumption_patterns(self):
        """Test detection of assumption patterns"""
        text = "The file should contain user data"
        warnings = self.detector.scan_output(text)
        
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["type"], "assumption")
        # Pattern is a regex, not the literal text
        self.assertEqual(warnings[0]["pattern"], r"\bshould\b")
    
    def test_detect_speculation_patterns(self):
        """Test detection of speculation patterns"""
        text = "This function probably needs error handling"
        warnings = self.detector.scan_output(text)
        
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["type"], "speculation")
    
    def test_detect_multiple_patterns(self):
        """Test detection of multiple patterns"""
        text = """
        The configuration file should contain API keys.
        This typically includes authentication tokens.
        The service probably needs to be restarted.
        """
        warnings = self.detector.scan_output(text)
        
        self.assertGreaterEqual(len(warnings), 3)
        pattern_types = [w["type"] for w in warnings]
        self.assertIn("assumption", pattern_types)
        self.assertIn("generalization", pattern_types)
        self.assertIn("speculation", pattern_types)
    
    def test_no_patterns_in_clean_text(self):
        """Test no warnings for factual statements"""
        text = "The file exists at /path/to/file.py"
        warnings = self.detector.scan_output(text)
        
        self.assertEqual(len(warnings), 0)


class TestEvidenceChain(unittest.TestCase):
    """Test evidence chain tracking"""
    
    def setUp(self):
        self.chain = EvidenceChain()
    
    def test_add_evidence(self):
        """Test adding evidence to chain"""
        evidence_id = self.chain.add_evidence(
            fact="File main.py exists",
            source="file_system",
            verification_method="os.path.exists"
        )
        
        self.assertIsNotNone(evidence_id)
        self.assertEqual(len(self.chain.chain), 1)
        self.assertTrue(self.chain.chain[0]["verified"])
    
    def test_get_evidence_for_fact(self):
        """Test retrieving evidence for a fact"""
        fact = {"type": "file_reference", "content": "main.py"}
        
        self.chain.add_evidence(
            fact=json.dumps(fact),
            source="file_system",
            verification_method="os.path.exists"
        )
        
        evidence = self.chain.get_evidence_for_fact(fact)
        self.assertEqual(len(evidence), 1)
        self.assertIn("main.py", evidence[0]["fact"])
    
    def test_get_evidence_by_id(self):
        """Test retrieving evidence by ID"""
        evidence_id = self.chain.add_evidence(
            fact="Test fact",
            source="test",
            verification_method="test_method"
        )
        
        evidence = self.chain.get_evidence_by_id(evidence_id)
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence["fact"], "Test fact")
        
        # Test non-existent ID
        self.assertIsNone(self.chain.get_evidence_by_id("fake_id"))


class TestCrossAgentValidator(unittest.TestCase):
    """Test cross-agent validation"""
    
    def setUp(self):
        self.validator = CrossAgentValidator(min_validations=2)
    
    def test_validate_with_sufficient_confirmations(self):
        """Test validation passes with enough confirmations"""
        claim = {"type": "file_reference", "content": "main.py"}
        
        agent_outputs = [
            {"verified_facts": [{"type": "file_reference", "content": "main.py"}]},
            {"verified_facts": [{"type": "file_reference", "content": "main.py"}]},
            {"verified_facts": [{"type": "file_reference", "content": "config.json"}]}
        ]
        
        self.assertTrue(self.validator.validate_claim(claim, agent_outputs))
    
    def test_validate_with_insufficient_confirmations(self):
        """Test validation fails without enough confirmations"""
        claim = {"type": "file_reference", "content": "main.py"}
        
        agent_outputs = [
            {"verified_facts": [{"type": "file_reference", "content": "main.py"}]},
            {"verified_facts": [{"type": "file_reference", "content": "config.json"}]},
            {"verified_facts": [{"type": "file_reference", "content": "other.py"}]}
        ]
        
        self.assertFalse(self.validator.validate_claim(claim, agent_outputs))
    
    def test_caching(self):
        """Test validation results are cached"""
        claim = {"type": "file_reference", "content": "main.py"}
        agent_outputs = [
            {"verified_facts": [{"type": "file_reference", "content": "main.py"}]},
            {"verified_facts": [{"type": "file_reference", "content": "main.py"}]}
        ]
        
        # First call
        result1 = self.validator.validate_claim(claim, agent_outputs)
        # Second call should use cache
        result2 = self.validator.validate_claim(claim, agent_outputs)
        
        self.assertEqual(result1, result2)
        self.assertEqual(len(self.validator.validation_cache), 1)


class TestUncertaintyHandler(unittest.TestCase):
    """Test uncertainty handling"""
    
    def setUp(self):
        self.handler = UncertaintyHandler()
    
    def test_express_uncertainty_levels(self):
        """Test different uncertainty expressions"""
        tests = [
            (0.0, "[UNVERIFIED]"),
            (0.3, "[UNVERIFIED]"),
            (0.5, "[UNCERTAIN]"),
            (0.7, "[LIKELY]"),
            (0.9, "[VERIFIED]"),
            (0.95, "[CONFIRMED]"),
            (1.0, "[CONFIRMED]")
        ]
        
        for confidence, expected_prefix in tests:
            result = self.handler.express_uncertainty("Test statement", confidence)
            self.assertTrue(result.startswith(expected_prefix))
            self.assertIn("Test statement", result)
    
    def test_require_user_confirmation(self):
        """Test user confirmation request generation"""
        uncertain_facts = [
            {"type": "file_reference", "content": "maybe_exists.py"},
            {"type": "function_reference", "content": "uncertain_func"}
        ]
        
        result = self.handler.require_user_confirmation(uncertain_facts)
        
        self.assertEqual(result["status"], "user_verification_required")
        self.assertEqual(len(result["uncertain_facts"]), 2)
        self.assertIn("suggested_actions", result)
    
    def test_create_safe_response(self):
        """Test safe response generation based on confidence"""
        original = "The function processes data"
        
        # Low confidence
        result = self.handler.create_safe_response(original, 0.3)
        self.assertIn("cannot verify", result)
        
        # Medium confidence
        result = self.handler.create_safe_response(original, 0.7)
        self.assertIn("limited verification", result)
        
        # High confidence
        result = self.handler.create_safe_response(original, 0.9)
        self.assertEqual(result, original)


class TestVerificationLayerIntegration(unittest.TestCase):
    """Test full verification layer integration"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(self.temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump({"strict_mode": True}, f)
        
        self.verifier = VerificationLayer(config_path)
        
        # Create test file
        self.test_file = os.path.join(self.temp_dir, "test.py")
        with open(self.test_file, 'w') as f:
            f.write("""
def real_function():
    return True

class RealClass:
    pass
""")
    
    def test_verify_valid_output(self):
        """Test verification of valid agent output"""
        agent_output = {
            "files": [self.test_file],
            "functions": [{"file": self.test_file, "function": "real_function"}],
            "analysis": f"The file {self.test_file} contains real_function"
        }
        
        result = self.verifier.verify_output("test_agent", agent_output)
        
        
        self.assertEqual(result["verification_status"], "verified")
        self.assertGreater(len(result["verified_facts"]), 0)
        self.assertEqual(len(result["unverified_claims"]), 0)
    
    def test_verify_invalid_output(self):
        """Test verification catches invalid claims"""
        agent_output = {
            "files": ["/fake/path/file.py"],
            "functions": [{"file": self.test_file, "function": "fake_function"}],
            "analysis": "The file should contain important data"
        }
        
        result = self.verifier.verify_output("test_agent", agent_output)
        
        self.assertEqual(result["verification_status"], "failed")
        self.assertGreater(len(result["unverified_claims"]), 0)
        self.assertGreater(len(result["hallucination_warnings"]), 0)
    
    def test_verify_mixed_output(self):
        """Test verification of output with both valid and invalid claims"""
        agent_output = {
            "files": [self.test_file, "/fake/file.py"],
            "functions": [
                {"file": self.test_file, "function": "real_function"},
                {"file": self.test_file, "function": "fake_function"}
            ],
            "analysis": "Processing typically includes validation"
        }
        
        result = self.verifier.verify_output("test_agent", agent_output)
        
        # Should have both verified and unverified claims
        self.assertGreater(len(result["verified_facts"]), 0)
        self.assertGreater(len(result["unverified_claims"]), 0)
        self.assertIn(result["verification_status"], ["failed", "low_confidence"])


class TestHallucinationPrevention(unittest.TestCase):
    """Test complete hallucination prevention scenarios"""
    
    def test_agent_cannot_reference_nonexistent_files(self):
        """Ensure agents cannot successfully reference non-existent files"""
        verifier = VerificationLayer()
        
        # Agent tries to reference non-existent file
        output = {
            "files": ["/completely/fake/path/to/file.py"],
            "analysis": "I analyzed the file and found important functions"
        }
        
        result = verifier.verify_output("hallucinating_agent", output)
        
        self.assertEqual(result["verification_status"], "failed")
        self.assertEqual(len(result["verified_facts"]), 0)
        self.assertGreater(len(result["unverified_claims"]), 0)
    
    def test_agent_cannot_invent_function_names(self):
        """Ensure agents cannot invent function names"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write("def real_function(): pass")
        temp_file.close()
        
        verifier = VerificationLayer()
        
        output = {
            "functions": [
                {"file": temp_file.name, "function": "real_function"},
                {"file": temp_file.name, "function": "invented_function"},
                {"file": temp_file.name, "function": "another_fake_function"}
            ]
        }
        
        result = verifier.verify_output("test_agent", output)
        
        # Only the real function should be verified
        verified_contents = [f["content"] for f in result["verified_facts"]]
        self.assertEqual(len([f for f in result["verified_facts"] 
                             if f.get("content", {}).get("function") == "real_function"]), 1)
        
        os.unlink(temp_file.name)
    
    def test_speculation_triggers_warnings(self):
        """Test that speculative language triggers warnings"""
        # Create a minimal config that doesn't require file paths
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"strict_mode": true}')
            config_path = f.name
        
        verifier = VerificationLayer(config_path)
        
        output = {
            "analysis": """This file probably contains user authentication.
The system should include error handling.
Functions typically need to validate input."""
        }
        
        result = verifier.verify_output("speculative_agent", output)
        
        
        self.assertGreater(len(result["hallucination_warnings"]), 0)
        warning_types = [w["type"] for w in result["hallucination_warnings"]]
        self.assertIn("speculation", warning_types)
        self.assertIn("assumption", warning_types)
        self.assertIn("generalization", warning_types)
        
        os.unlink(config_path)


if __name__ == "__main__":
    unittest.main()