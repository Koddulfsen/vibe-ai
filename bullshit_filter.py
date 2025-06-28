#!/usr/bin/env python3
"""
Bullshit Filter for vibe.ai
Validates and verifies information found online to ensure quality and accuracy
No hallucinations, only facts!
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
import hashlib

# Rich terminal UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    console = None
    RICH_AVAILABLE = False


class BullshitFilter:
    """Filters out unreliable information and validates claims"""
    
    # Reliable domains (can be extended)
    TRUSTED_DOMAINS = {
        # Documentation sites
        "docs.python.org", "developer.mozilla.org", "docs.microsoft.com",
        "docs.aws.amazon.com", "cloud.google.com/docs", "docs.github.com",
        
        # Academic and research
        "arxiv.org", "scholar.google.com", "ieee.org", "acm.org",
        "nature.com", "sciencedirect.com", "pubmed.ncbi.nlm.nih.gov",
        
        # Official tech sites
        "github.com", "gitlab.com", "stackoverflow.com", "dev.to",
        "medium.com/@official", "react.dev", "vuejs.org", "angular.io",
        
        # News and tech journalism (with caution)
        "techcrunch.com", "wired.com", "arstechnica.com", "theverge.com"
    }
    
    # Suspicious patterns
    BULLSHIT_PATTERNS = [
        # Clickbait
        r"you won't believe",
        r"doctors hate this",
        r"one weird trick",
        r"shocking truth",
        
        # Exaggeration
        r"always works",
        r"100% guaranteed",
        r"never fails",
        r"revolutionary breakthrough",
        
        # Vague claims
        r"studies show",
        r"experts say",
        r"research suggests",
        r"it is known",
        
        # Marketing speak
        r"limited time offer",
        r"act now",
        r"exclusive deal",
        r"transformative solution"
    ]
    
    # Technical accuracy patterns
    TECHNICAL_RED_FLAGS = [
        # Outdated practices
        r"var\s+\w+\s*=.*//\s*javascript",  # Using var in modern JS
        r"mysql_query\(",  # Deprecated PHP MySQL functions
        r"document\.write\(",  # Outdated DOM manipulation
        
        # Security issues
        r"eval\([^)]*user",  # Eval with user input
        r"password.*=.*['\"][^'\"]+['\"]",  # Hardcoded passwords
        r"api_key.*=.*['\"][^'\"]+['\"]",  # Exposed API keys
        
        # Bad practices
        r"catch\s*\(\s*\).*pass",  # Empty catch blocks
        r"sudo\s+rm\s+-rf\s+/",  # Dangerous commands
        r"chmod\s+777",  # Overly permissive permissions
    ]
    
    def __init__(self):
        self.console = console
        self.validation_cache = {}
        self.domain_scores = {}
        
    def filter_search_results(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Filter and validate search results"""
        if self.console:
            self.console.print("\n[cyan]🔍 Applying Bullshit Filter...[/cyan]")
        
        filtered_results = []
        rejected_results = []
        
        for result in search_results:
            validation = self.validate_result(result)
            
            if validation["is_valid"]:
                result["validation_score"] = validation["score"]
                result["trust_level"] = validation["trust_level"]
                filtered_results.append(result)
            else:
                result["rejection_reasons"] = validation["reasons"]
                rejected_results.append(result)
        
        # Sort by validation score
        filtered_results.sort(key=lambda x: x["validation_score"], reverse=True)
        
        report = {
            "total_results": len(search_results),
            "accepted": len(filtered_results),
            "rejected": len(rejected_results),
            "filtered_results": filtered_results,
            "rejected_results": rejected_results,
            "quality_metrics": self._calculate_quality_metrics(filtered_results)
        }
        
        if self.console:
            self._display_filter_report(report)
        
        return report
    
    def validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single search result"""
        validation = {
            "is_valid": True,
            "score": 100.0,
            "trust_level": "high",
            "reasons": [],
            "checks_passed": []
        }
        
        # Extract content
        url = result.get("url", "")
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        content = result.get("content", snippet)
        
        # Check 1: Domain reliability
        domain_check = self._check_domain_reliability(url)
        if domain_check["score"] < 30:
            validation["is_valid"] = False
            validation["reasons"].append(f"Unreliable domain: {domain_check['domain']}")
        validation["score"] *= (domain_check["score"] / 100)
        
        # Check 2: Content quality
        content_check = self._check_content_quality(title, content)
        if content_check["has_bullshit"]:
            validation["score"] *= 0.5
            validation["reasons"].extend(content_check["bullshit_found"])
        
        # Check 3: Technical accuracy (for code snippets)
        if self._contains_code(content):
            code_check = self._check_technical_accuracy(content)
            if code_check["has_issues"]:
                validation["score"] *= 0.7
                validation["reasons"].extend(code_check["issues"])
        
        # Check 4: Freshness
        freshness_check = self._check_freshness(result)
        validation["score"] *= freshness_check["multiplier"]
        
        # Check 5: Cross-reference validation
        if validation["score"] > 70:
            cross_check = self._cross_reference_check(content)
            validation["score"] *= cross_check["confidence"]
        
        # Determine trust level
        if validation["score"] >= 80:
            validation["trust_level"] = "high"
        elif validation["score"] >= 60:
            validation["trust_level"] = "medium"
        elif validation["score"] >= 40:
            validation["trust_level"] = "low"
        else:
            validation["is_valid"] = False
            validation["trust_level"] = "rejected"
        
        return validation
    
    def _check_domain_reliability(self, url: str) -> Dict[str, Any]:
        """Check if the domain is reliable"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Check if in trusted list
            if domain in self.TRUSTED_DOMAINS:
                return {"domain": domain, "score": 100, "status": "trusted"}
            
            # Check if subdomain of trusted domain
            for trusted in self.TRUSTED_DOMAINS:
                if domain.endswith("." + trusted):
                    return {"domain": domain, "score": 90, "status": "trusted_subdomain"}
            
            # Check domain characteristics
            score = 50  # Start neutral
            
            # Penalize suspicious TLDs
            suspicious_tlds = [".tk", ".ml", ".ga", ".cf"]
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                score -= 30
            
            # Bonus for .edu, .gov, .org
            if domain.endswith(".edu"):
                score += 30
            elif domain.endswith(".gov"):
                score += 25
            elif domain.endswith(".org"):
                score += 15
            
            # Penalize very short or very long domains
            domain_parts = domain.split(".")
            if len(domain_parts[0]) < 3:
                score -= 10
            elif len(domain_parts[0]) > 30:
                score -= 15
            
            return {"domain": domain, "score": max(0, score), "status": "unknown"}
            
        except Exception as e:
            return {"domain": "unknown", "score": 20, "status": "error", "error": str(e)}
    
    def _check_content_quality(self, title: str, content: str) -> Dict[str, Any]:
        """Check content for bullshit patterns"""
        result = {
            "has_bullshit": False,
            "bullshit_found": [],
            "quality_score": 100
        }
        
        combined_text = f"{title} {content}".lower()
        
        # Check for bullshit patterns
        for pattern in self.BULLSHIT_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                result["has_bullshit"] = True
                result["bullshit_found"].append(f"Contains pattern: '{pattern}'")
                result["quality_score"] -= 20
        
        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.3:
            result["has_bullshit"] = True
            result["bullshit_found"].append("Excessive capitalization")
            result["quality_score"] -= 15
        
        # Check for excessive punctuation
        punct_count = content.count("!") + content.count("?")
        if punct_count > len(content.split()) / 10:
            result["has_bullshit"] = True
            result["bullshit_found"].append("Excessive punctuation")
            result["quality_score"] -= 10
        
        return result
    
    def _check_technical_accuracy(self, content: str) -> Dict[str, Any]:
        """Check technical content for red flags"""
        result = {
            "has_issues": False,
            "issues": [],
            "accuracy_score": 100
        }
        
        # Check for technical red flags
        for pattern in self.TECHNICAL_RED_FLAGS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result["has_issues"] = True
                result["issues"].append(f"Technical issue: {pattern}")
                result["accuracy_score"] -= 25
        
        # Check for obviously wrong code patterns
        # Example: Python 2 print statements in Python 3 context
        if "python3" in content.lower() and re.search(r"print\s+['\"]", content):
            result["has_issues"] = True
            result["issues"].append("Outdated Python 2 syntax in Python 3 context")
            result["accuracy_score"] -= 20
        
        return result
    
    def _contains_code(self, content: str) -> bool:
        """Check if content contains code snippets"""
        code_indicators = [
            r"```",  # Markdown code blocks
            r"<code>",  # HTML code tags
            r"function\s*\(",  # JavaScript functions
            r"def\s+\w+\(",  # Python functions
            r"class\s+\w+",  # Class definitions
            r"import\s+\w+",  # Import statements
            r"{\s*\n",  # Code blocks
        ]
        
        return any(re.search(pattern, content) for pattern in code_indicators)
    
    def _check_freshness(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Check content freshness"""
        freshness = {
            "is_fresh": True,
            "age_days": None,
            "multiplier": 1.0
        }
        
        # Try to extract date from result
        date_str = result.get("date") or result.get("published_date")
        if date_str:
            try:
                # Parse date (simplified - would need better parsing in production)
                published = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                age = datetime.now() - published
                freshness["age_days"] = age.days
                
                # Apply freshness multiplier
                if age.days < 30:
                    freshness["multiplier"] = 1.0
                elif age.days < 180:
                    freshness["multiplier"] = 0.95
                elif age.days < 365:
                    freshness["multiplier"] = 0.9
                elif age.days < 730:
                    freshness["multiplier"] = 0.8
                else:
                    freshness["multiplier"] = 0.7
                    freshness["is_fresh"] = False
                    
            except:
                pass
        
        return freshness
    
    def _cross_reference_check(self, content: str) -> Dict[str, Any]:
        """Check if claims can be cross-referenced"""
        check = {
            "confidence": 1.0,
            "verifiable_claims": 0,
            "unverifiable_claims": 0
        }
        
        # Look for specific claims that should be verifiable
        claim_patterns = [
            r"version (\d+\.?\d*)",  # Version numbers
            r"released in (\d{4})",  # Release years
            r"(\d+)% faster",  # Performance claims
            r"supports? ([\w\s,]+)",  # Feature support claims
        ]
        
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # In production, we'd actually verify these
                check["verifiable_claims"] += len(matches)
        
        # Look for unverifiable vague claims
        vague_patterns = [
            r"many developers",
            r"most users",
            r"widely considered",
            r"generally accepted"
        ]
        
        for pattern in vague_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                check["unverifiable_claims"] += 1
                check["confidence"] *= 0.95
        
        return check
    
    def _calculate_quality_metrics(self, filtered_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall quality metrics"""
        if not filtered_results:
            return {
                "average_score": 0,
                "high_trust_percentage": 0,
                "domain_diversity": 0
            }
        
        scores = [r["validation_score"] for r in filtered_results]
        high_trust = sum(1 for r in filtered_results if r["trust_level"] == "high")
        domains = set(urlparse(r.get("url", "")).netloc for r in filtered_results)
        
        return {
            "average_score": sum(scores) / len(scores),
            "high_trust_percentage": (high_trust / len(filtered_results)) * 100,
            "domain_diversity": len(domains),
            "score_distribution": {
                "high": sum(1 for s in scores if s >= 80),
                "medium": sum(1 for s in scores if 60 <= s < 80),
                "low": sum(1 for s in scores if s < 60)
            }
        }
    
    def _display_filter_report(self, report: Dict[str, Any]):
        """Display filtering report"""
        if not self.console:
            return
        
        # Summary
        self.console.print(Panel(
            f"[bold]Filtered Results[/bold]\n"
            f"Total: {report['total_results']}\n"
            f"Accepted: [green]{report['accepted']}[/green]\n"
            f"Rejected: [red]{report['rejected']}[/red]",
            title="🚦 Filter Summary",
            border_style="blue"
        ))
        
        # Quality metrics
        metrics = report["quality_metrics"]
        if metrics["average_score"] > 0:
            self.console.print(f"\n[bold]Quality Metrics:[/bold]")
            self.console.print(f"  Average Score: {metrics['average_score']:.1f}%")
            self.console.print(f"  High Trust: {metrics['high_trust_percentage']:.1f}%")
            self.console.print(f"  Domain Diversity: {metrics['domain_diversity']} sources")
        
        # Top results
        if report["filtered_results"]:
            self.console.print("\n[bold]Top Validated Results:[/bold]")
            for i, result in enumerate(report["filtered_results"][:3], 1):
                trust_color = {
                    "high": "green",
                    "medium": "yellow", 
                    "low": "red"
                }.get(result["trust_level"], "white")
                
                self.console.print(
                    f"\n{i}. [bold]{result.get('title', 'Untitled')}[/bold]\n"
                    f"   Score: {result['validation_score']:.1f} | "
                    f"   Trust: [{trust_color}]{result['trust_level']}[/{trust_color}]\n"
                    f"   URL: [dim]{result.get('url', 'N/A')}[/dim]"
                )
    
    def validate_claim(self, claim: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Validate a specific claim"""
        validation = {
            "claim": claim,
            "source": source,
            "is_valid": None,
            "confidence": 0.5,
            "evidence": [],
            "warnings": []
        }
        
        # Check for obvious bullshit patterns
        for pattern in self.BULLSHIT_PATTERNS:
            if re.search(pattern, claim, re.IGNORECASE):
                validation["warnings"].append(f"Contains suspicious pattern: {pattern}")
                validation["confidence"] *= 0.7
        
        # Check for technical claims
        if self._contains_code(claim):
            tech_check = self._check_technical_accuracy(claim)
            if tech_check["has_issues"]:
                validation["warnings"].extend(tech_check["issues"])
                validation["confidence"] *= 0.6
        
        # Would need actual verification in production
        validation["is_valid"] = validation["confidence"] > 0.5
        
        return validation


def main():
    """Test the bullshit filter"""
    filter = BullshitFilter()
    
    # Test with sample search results
    test_results = [
        {
            "title": "Python Best Practices 2024",
            "url": "https://docs.python.org/3/tutorial/",
            "snippet": "Official Python documentation with comprehensive guides"
        },
        {
            "title": "You Won't Believe This One Weird Python Trick!",
            "url": "https://clickbait-site.tk/python-tricks",
            "snippet": "Doctors hate this! Make Python 100% faster always!"
        },
        {
            "title": "Understanding React Hooks",
            "url": "https://react.dev/learn/hooks",
            "snippet": "Learn how to use hooks in React applications"
        },
        {
            "title": "Revolutionary AI Breakthrough Changes Everything!!!",
            "url": "https://fake-news.ml/ai-hype",
            "snippet": "This shocking truth about AI will transform your life! Limited time!"
        }
    ]
    
    if console:
        console.print("\n[bold]🧹 Testing Bullshit Filter[/bold]\n")
    
    report = filter.filter_search_results(test_results)
    
    if console:
        console.print(f"\n[bold]Filter Performance:[/bold]")
        console.print(f"  Caught {report['rejected']} bullshit results")
        console.print(f"  Validated {report['accepted']} quality results")


if __name__ == "__main__":
    main()