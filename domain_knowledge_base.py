#!/usr/bin/env python3
"""
Domain Knowledge Base for Deep Understanding Engine
Contains comprehensive domain knowledge for automatic requirement inference
"""

from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass, field


@dataclass
class DomainKnowledge:
    """Encapsulates domain-specific knowledge"""
    name: str
    implicit_features: List[str]
    required_technologies: Dict[str, List[str]]
    security_requirements: List[str]
    performance_requirements: Dict[str, Any]
    best_practices: List[str]
    common_integrations: List[str]
    data_models: Dict[str, List[str]]
    user_roles: List[str]
    compliance_requirements: List[str] = field(default_factory=list)


class DomainKnowledgeBase:
    """Comprehensive knowledge base for various domains"""
    
    def __init__(self):
        self.domains = self._initialize_domains()
        self.pattern_matchers = self._initialize_pattern_matchers()
        
    def _initialize_domains(self) -> Dict[str, DomainKnowledge]:
        """Initialize domain knowledge base"""
        return {
            "e-commerce": DomainKnowledge(
                name="E-commerce",
                implicit_features=[
                    "user_authentication",
                    "product_catalog",
                    "shopping_cart",
                    "checkout_process",
                    "payment_processing",
                    "order_management",
                    "inventory_tracking",
                    "customer_reviews",
                    "search_functionality",
                    "product_recommendations",
                    "wishlist",
                    "email_notifications",
                    "shipping_integration",
                    "tax_calculation",
                    "discount_management",
                    "return_processing",
                    "customer_support",
                    "analytics_dashboard",
                    "mobile_responsive",
                    "multi_language_support"
                ],
                required_technologies={
                    "payment": ["stripe", "paypal", "square"],
                    "search": ["elasticsearch", "algolia", "meilisearch"],
                    "email": ["sendgrid", "mailgun", "ses"],
                    "analytics": ["google_analytics", "mixpanel", "segment"],
                    "cdn": ["cloudflare", "fastly", "cloudfront"],
                    "database": ["postgresql", "mysql", "mongodb"],
                    "cache": ["redis", "memcached"],
                    "queue": ["rabbitmq", "sqs", "celery"]
                },
                security_requirements=[
                    "PCI_DSS_compliance",
                    "SSL_certificate",
                    "secure_payment_gateway",
                    "data_encryption",
                    "fraud_detection",
                    "two_factor_auth",
                    "secure_password_storage",
                    "session_management",
                    "XSS_prevention",
                    "SQL_injection_prevention",
                    "CSRF_protection"
                ],
                performance_requirements={
                    "page_load_time": "< 3 seconds",
                    "api_response_time": "< 200ms",
                    "concurrent_users": 10000,
                    "uptime": "99.9%",
                    "database_queries": "optimized with indexes",
                    "image_optimization": True,
                    "lazy_loading": True,
                    "caching_strategy": "multi-level"
                },
                best_practices=[
                    "Implement progressive web app",
                    "Use microservices for scalability",
                    "Implement A/B testing",
                    "Use event-driven architecture",
                    "Implement circuit breakers",
                    "Use CDN for static assets",
                    "Implement rate limiting",
                    "Use message queues for async tasks",
                    "Implement database sharding",
                    "Use containerization"
                ],
                common_integrations=[
                    "Google Shopping",
                    "Facebook Pixel",
                    "Shipping carriers API",
                    "Tax calculation services",
                    "Inventory management systems",
                    "CRM systems",
                    "Accounting software",
                    "Marketing automation"
                ],
                data_models={
                    "User": ["id", "email", "password_hash", "profile", "addresses", "payment_methods"],
                    "Product": ["id", "name", "description", "price", "sku", "inventory", "categories", "images"],
                    "Order": ["id", "user_id", "items", "total", "status", "shipping_address", "tracking"],
                    "Cart": ["id", "user_id", "items", "expires_at"],
                    "Review": ["id", "product_id", "user_id", "rating", "comment", "verified_purchase"],
                    "Category": ["id", "name", "parent_id", "slug", "description"],
                    "Vendor": ["id", "name", "commission_rate", "products", "payouts"]
                },
                user_roles=["customer", "vendor", "admin", "support_agent"],
                compliance_requirements=["GDPR", "CCPA", "PCI_DSS"]
            ),
            
            "social_media": DomainKnowledge(
                name="Social Media Platform",
                implicit_features=[
                    "user_profiles",
                    "friend_connections",
                    "news_feed",
                    "post_creation",
                    "commenting_system",
                    "like_reactions",
                    "share_functionality",
                    "messaging_system",
                    "notification_system",
                    "privacy_settings",
                    "content_moderation",
                    "hashtag_system",
                    "trending_topics",
                    "user_search",
                    "media_upload",
                    "story_feature",
                    "live_streaming",
                    "groups_communities",
                    "event_creation",
                    "advertising_platform"
                ],
                required_technologies={
                    "realtime": ["websockets", "socket.io", "pusher"],
                    "media_storage": ["s3", "cloudinary", "imgix"],
                    "video_processing": ["ffmpeg", "aws_elemental", "mux"],
                    "database": ["postgresql", "cassandra", "redis"],
                    "search": ["elasticsearch", "typesense"],
                    "ml": ["tensorflow", "pytorch", "scikit-learn"],
                    "cache": ["redis", "memcached"],
                    "cdn": ["cloudflare", "akamai"]
                },
                security_requirements=[
                    "end_to_end_encryption",
                    "privacy_controls",
                    "content_filtering",
                    "spam_detection",
                    "account_verification",
                    "report_system",
                    "COPPA_compliance",
                    "age_verification",
                    "data_portability",
                    "right_to_deletion"
                ],
                performance_requirements={
                    "feed_load_time": "< 1 second",
                    "message_delivery": "< 100ms",
                    "concurrent_connections": 1000000,
                    "video_streaming": "adaptive_bitrate",
                    "image_processing": "on_the_fly",
                    "search_speed": "< 50ms"
                },
                best_practices=[
                    "Implement infinite scroll",
                    "Use GraphQL for flexible queries",
                    "Implement real-time updates",
                    "Use event sourcing",
                    "Implement recommendation algorithms",
                    "Use edge computing",
                    "Implement content delivery network",
                    "Use distributed caching"
                ],
                common_integrations=[
                    "OAuth providers",
                    "Analytics platforms",
                    "Ad networks",
                    "Payment processors",
                    "Email services",
                    "SMS gateways",
                    "Cloud storage",
                    "AI/ML services"
                ],
                data_models={
                    "User": ["id", "username", "email", "profile", "privacy_settings", "blocked_users"],
                    "Post": ["id", "user_id", "content", "media", "likes", "comments", "shares", "visibility"],
                    "Comment": ["id", "post_id", "user_id", "content", "likes", "replies"],
                    "Message": ["id", "sender_id", "recipient_id", "content", "read_status", "encrypted"],
                    "Notification": ["id", "user_id", "type", "content", "read_status", "action_url"],
                    "Friendship": ["id", "user1_id", "user2_id", "status", "created_at"]
                },
                user_roles=["user", "moderator", "admin", "advertiser"],
                compliance_requirements=["GDPR", "COPPA", "CCPA"]
            ),
            
            "healthcare": DomainKnowledge(
                name="Healthcare System",
                implicit_features=[
                    "patient_records",
                    "appointment_scheduling",
                    "medical_history",
                    "prescription_management",
                    "lab_results",
                    "billing_system",
                    "insurance_verification",
                    "doctor_portal",
                    "patient_portal",
                    "telemedicine",
                    "emergency_alerts",
                    "medication_reminders",
                    "health_monitoring",
                    "referral_system",
                    "report_generation",
                    "audit_trails",
                    "consent_management",
                    "clinical_decision_support",
                    "inventory_management",
                    "staff_scheduling"
                ],
                required_technologies={
                    "ehr": ["epic", "cerner", "allscripts"],
                    "video": ["twilio", "zoom_sdk", "webrtc"],
                    "database": ["postgresql", "mongodb"],
                    "security": ["vault", "hsm", "encryption_services"],
                    "integration": ["hl7", "fhir", "mirth"],
                    "backup": ["aws_backup", "azure_backup"],
                    "monitoring": ["datadog", "new_relic"]
                },
                security_requirements=[
                    "HIPAA_compliance",
                    "end_to_end_encryption",
                    "access_control_lists",
                    "audit_logging",
                    "data_anonymization",
                    "secure_messaging",
                    "biometric_authentication",
                    "role_based_access",
                    "data_loss_prevention",
                    "secure_file_transfer",
                    "session_timeout",
                    "password_policies"
                ],
                performance_requirements={
                    "system_availability": "99.99%",
                    "data_retrieval": "< 2 seconds",
                    "backup_frequency": "hourly",
                    "disaster_recovery": "< 4 hours",
                    "concurrent_users": 5000,
                    "data_retention": "7 years"
                },
                best_practices=[
                    "Implement HL7/FHIR standards",
                    "Use medical coding systems",
                    "Implement clinical workflows",
                    "Use secure communication",
                    "Implement data governance",
                    "Use medical terminology services",
                    "Implement interoperability",
                    "Use clinical decision support"
                ],
                common_integrations=[
                    "Laboratory systems",
                    "Pharmacy systems",
                    "Insurance providers",
                    "Medical devices",
                    "Billing systems",
                    "Government registries",
                    "Clinical trials systems",
                    "Research databases"
                ],
                data_models={
                    "Patient": ["id", "mrn", "demographics", "allergies", "medications", "conditions"],
                    "Provider": ["id", "npi", "specialties", "credentials", "schedule"],
                    "Appointment": ["id", "patient_id", "provider_id", "datetime", "type", "status"],
                    "Prescription": ["id", "patient_id", "provider_id", "medication", "dosage", "refills"],
                    "LabResult": ["id", "patient_id", "test_type", "results", "reference_range"],
                    "Insurance": ["id", "patient_id", "provider", "policy_number", "coverage"]
                },
                user_roles=["patient", "doctor", "nurse", "admin", "billing_staff", "lab_technician"],
                compliance_requirements=["HIPAA", "HITECH", "FDA", "DEA"]
            ),
            
            "fintech": DomainKnowledge(
                name="Financial Technology",
                implicit_features=[
                    "account_management",
                    "transaction_processing",
                    "balance_tracking",
                    "payment_transfers",
                    "bill_payments",
                    "investment_portfolio",
                    "budgeting_tools",
                    "expense_tracking",
                    "financial_reports",
                    "fraud_detection",
                    "kyc_verification",
                    "aml_compliance",
                    "credit_scoring",
                    "loan_processing",
                    "interest_calculation",
                    "currency_exchange",
                    "mobile_banking",
                    "atm_locator",
                    "customer_support",
                    "audit_system"
                ],
                required_technologies={
                    "payment": ["plaid", "stripe", "dwolla"],
                    "blockchain": ["ethereum", "stellar", "ripple"],
                    "kyc": ["jumio", "onfido", "trulioo"],
                    "database": ["postgresql", "cassandra"],
                    "security": ["hsm", "vault", "tokenization"],
                    "analytics": ["tableau", "looker", "powerbi"],
                    "queue": ["kafka", "rabbitmq"],
                    "ml": ["tensorflow", "h2o", "datarobot"]
                },
                security_requirements=[
                    "PCI_DSS_compliance",
                    "SOC2_compliance",
                    "multi_factor_auth",
                    "encryption_at_rest",
                    "encryption_in_transit",
                    "tokenization",
                    "fraud_monitoring",
                    "secure_key_management",
                    "penetration_testing",
                    "security_audits",
                    "data_masking",
                    "secure_apis"
                ],
                performance_requirements={
                    "transaction_speed": "< 100ms",
                    "system_uptime": "99.99%",
                    "concurrent_transactions": 100000,
                    "data_consistency": "strong",
                    "settlement_time": "real-time",
                    "report_generation": "< 5 seconds"
                },
                best_practices=[
                    "Implement double-entry bookkeeping",
                    "Use event sourcing",
                    "Implement CQRS pattern",
                    "Use distributed ledger",
                    "Implement rate limiting",
                    "Use circuit breakers",
                    "Implement idempotency",
                    "Use message queuing"
                ],
                common_integrations=[
                    "Banking APIs",
                    "Payment gateways",
                    "Credit bureaus",
                    "Tax services",
                    "Accounting software",
                    "Compliance services",
                    "Market data feeds",
                    "Identity verification"
                ],
                data_models={
                    "Account": ["id", "user_id", "type", "balance", "currency", "status"],
                    "Transaction": ["id", "from_account", "to_account", "amount", "type", "status"],
                    "User": ["id", "kyc_status", "risk_score", "accounts", "limits"],
                    "Payment": ["id", "account_id", "amount", "recipient", "method", "status"],
                    "Investment": ["id", "account_id", "symbol", "quantity", "purchase_price"],
                    "Loan": ["id", "user_id", "amount", "interest_rate", "term", "status"]
                },
                user_roles=["customer", "teller", "manager", "compliance_officer", "auditor"],
                compliance_requirements=["PCI_DSS", "SOC2", "GDPR", "PSD2", "AML", "KYC"]
            ),
            
            "education": DomainKnowledge(
                name="Educational Platform",
                implicit_features=[
                    "course_management",
                    "student_enrollment",
                    "lesson_delivery",
                    "assignment_submission",
                    "grading_system",
                    "progress_tracking",
                    "quiz_assessment",
                    "discussion_forums",
                    "video_lectures",
                    "resource_library",
                    "calendar_scheduling",
                    "attendance_tracking",
                    "parent_portal",
                    "teacher_dashboard",
                    "analytics_reporting",
                    "certificate_generation",
                    "plagiarism_detection",
                    "breakout_rooms",
                    "whiteboard_tools",
                    "mobile_learning"
                ],
                required_technologies={
                    "video": ["zoom", "webrtc", "agora"],
                    "lms": ["moodle", "canvas", "blackboard"],
                    "content": ["scorm", "xapi", "lti"],
                    "database": ["postgresql", "mongodb"],
                    "storage": ["s3", "azure_blob"],
                    "search": ["elasticsearch", "algolia"],
                    "email": ["sendgrid", "mailgun"],
                    "analytics": ["google_analytics", "mixpanel"]
                },
                security_requirements=[
                    "FERPA_compliance",
                    "COPPA_compliance",
                    "student_data_privacy",
                    "secure_assessments",
                    "proctoring_security",
                    "content_protection",
                    "access_control",
                    "data_encryption",
                    "secure_file_sharing",
                    "session_management"
                ],
                performance_requirements={
                    "video_quality": "1080p",
                    "concurrent_users": 10000,
                    "page_load": "< 2 seconds",
                    "video_latency": "< 150ms",
                    "file_upload": "100MB",
                    "system_uptime": "99.9%"
                },
                best_practices=[
                    "Implement adaptive learning",
                    "Use microlearning approach",
                    "Implement gamification",
                    "Use responsive design",
                    "Implement offline mode",
                    "Use content versioning",
                    "Implement accessibility",
                    "Use learning analytics"
                ],
                common_integrations=[
                    "Google Workspace",
                    "Microsoft 365",
                    "Turnitin",
                    "Library systems",
                    "Student information systems",
                    "Payment gateways",
                    "Calendar systems",
                    "Video platforms"
                ],
                data_models={
                    "User": ["id", "role", "profile", "preferences", "accessibility_needs"],
                    "Course": ["id", "title", "description", "instructor_id", "schedule", "capacity"],
                    "Lesson": ["id", "course_id", "title", "content", "resources", "duration"],
                    "Assignment": ["id", "course_id", "title", "due_date", "rubric", "submissions"],
                    "Grade": ["id", "student_id", "assignment_id", "score", "feedback"],
                    "Enrollment": ["id", "student_id", "course_id", "status", "progress"]
                },
                user_roles=["student", "teacher", "admin", "parent", "teaching_assistant"],
                compliance_requirements=["FERPA", "COPPA", "ADA", "GDPR"]
            ),
            
            "real_estate": DomainKnowledge(
                name="Real Estate Platform",
                implicit_features=[
                    "property_listings",
                    "search_filters",
                    "map_integration",
                    "virtual_tours",
                    "appointment_scheduling",
                    "mortgage_calculator",
                    "neighborhood_info",
                    "school_ratings",
                    "crime_statistics",
                    "price_history",
                    "market_analysis",
                    "saved_searches",
                    "agent_profiles",
                    "lead_management",
                    "document_management",
                    "offer_management",
                    "contract_generation",
                    "commission_tracking",
                    "mls_integration",
                    "mobile_app"
                ],
                required_technologies={
                    "maps": ["google_maps", "mapbox", "here"],
                    "mls": ["rets", "mls_api", "idx"],
                    "virtual_tour": ["matterport", "zillow_3d"],
                    "database": ["postgresql", "elasticsearch"],
                    "storage": ["s3", "cloudinary"],
                    "email": ["sendgrid", "mailchimp"],
                    "sms": ["twilio", "messagebird"],
                    "analytics": ["google_analytics", "hotjar"]
                },
                security_requirements=[
                    "data_privacy",
                    "secure_document_storage",
                    "agent_verification",
                    "financial_data_protection",
                    "access_control",
                    "audit_trails",
                    "secure_messaging",
                    "compliance_reporting"
                ],
                performance_requirements={
                    "search_speed": "< 500ms",
                    "image_loading": "progressive",
                    "map_rendering": "< 1 second",
                    "concurrent_searches": 50000,
                    "data_freshness": "15 minutes",
                    "mobile_performance": "optimized"
                },
                best_practices=[
                    "Implement IDX compliance",
                    "Use geospatial indexing",
                    "Implement SEO optimization",
                    "Use responsive images",
                    "Implement lead routing",
                    "Use automated valuation",
                    "Implement CRM integration",
                    "Use predictive analytics"
                ],
                common_integrations=[
                    "MLS systems",
                    "CRM platforms",
                    "Mortgage lenders",
                    "Title companies",
                    "Home inspection services",
                    "Moving companies",
                    "Utility providers",
                    "Insurance companies"
                ],
                data_models={
                    "Property": ["id", "address", "price", "bedrooms", "bathrooms", "sqft", "features"],
                    "Listing": ["id", "property_id", "agent_id", "status", "list_date", "photos"],
                    "Agent": ["id", "name", "license", "brokerage", "ratings", "specialties"],
                    "Lead": ["id", "name", "email", "phone", "preferences", "agent_id"],
                    "Showing": ["id", "property_id", "lead_id", "agent_id", "datetime"],
                    "Offer": ["id", "property_id", "buyer_id", "amount", "terms", "status"]
                },
                user_roles=["buyer", "seller", "agent", "broker", "admin"],
                compliance_requirements=["Fair_Housing_Act", "RESPA", "TILA", "ADA"]
            )
        }
    
    def _initialize_pattern_matchers(self) -> Dict[str, List[str]]:
        """Initialize pattern matching for domain detection"""
        return {
            "e-commerce": [
                "shop", "store", "marketplace", "product", "cart", "checkout",
                "payment", "order", "inventory", "catalog", "merchant", "vendor"
            ],
            "social_media": [
                "social", "network", "post", "feed", "friend", "follow", "share",
                "like", "comment", "profile", "timeline", "status", "tweet"
            ],
            "healthcare": [
                "medical", "health", "patient", "doctor", "hospital", "clinic",
                "appointment", "prescription", "diagnosis", "treatment", "ehr"
            ],
            "fintech": [
                "banking", "finance", "payment", "transaction", "account", "wallet",
                "investment", "trading", "loan", "credit", "debit", "transfer"
            ],
            "education": [
                "learning", "education", "course", "student", "teacher", "lesson",
                "quiz", "assignment", "grade", "curriculum", "school", "university"
            ],
            "real_estate": [
                "property", "real estate", "listing", "house", "apartment", "rent",
                "buy", "sell", "agent", "broker", "mortgage", "realty"
            ]
        }
    
    def detect_domains(self, user_input: str) -> List[str]:
        """Detect applicable domains from user input"""
        detected_domains = []
        input_lower = user_input.lower()
        
        for domain, patterns in self.pattern_matchers.items():
            if any(pattern in input_lower for pattern in patterns):
                detected_domains.append(domain)
        
        return detected_domains
    
    def get_domain_knowledge(self, domain: str) -> Optional[DomainKnowledge]:
        """Get knowledge for a specific domain"""
        return self.domains.get(domain)
    
    def get_implicit_requirements(self, domains: List[str]) -> Set[str]:
        """Get all implicit requirements for detected domains"""
        implicit_reqs = set()
        
        for domain in domains:
            if knowledge := self.get_domain_knowledge(domain):
                implicit_reqs.update(knowledge.implicit_features)
        
        return implicit_reqs
    
    def get_security_requirements(self, domains: List[str]) -> Set[str]:
        """Get all security requirements for detected domains"""
        security_reqs = set()
        
        for domain in domains:
            if knowledge := self.get_domain_knowledge(domain):
                security_reqs.update(knowledge.security_requirements)
        
        return security_reqs
    
    def get_technology_recommendations(self, domains: List[str]) -> Dict[str, Set[str]]:
        """Get technology recommendations for detected domains"""
        tech_recommendations = {}
        
        for domain in domains:
            if knowledge := self.get_domain_knowledge(domain):
                for category, techs in knowledge.required_technologies.items():
                    if category not in tech_recommendations:
                        tech_recommendations[category] = set()
                    tech_recommendations[category].update(techs)
        
        return tech_recommendations
    
    def get_compliance_requirements(self, domains: List[str]) -> Set[str]:
        """Get compliance requirements for detected domains"""
        compliance_reqs = set()
        
        for domain in domains:
            if knowledge := self.get_domain_knowledge(domain):
                compliance_reqs.update(knowledge.compliance_requirements)
        
        return compliance_reqs
    
    def get_data_models(self, domains: List[str]) -> Dict[str, List[str]]:
        """Get suggested data models for detected domains"""
        data_models = {}
        
        for domain in domains:
            if knowledge := self.get_domain_knowledge(domain):
                for model, fields in knowledge.data_models.items():
                    if model not in data_models:
                        data_models[model] = []
                    data_models[model].extend(fields)
        
        # Remove duplicates
        for model in data_models:
            data_models[model] = list(set(data_models[model]))
        
        return data_models
    
    def get_integration_suggestions(self, domains: List[str]) -> Set[str]:
        """Get integration suggestions for detected domains"""
        integrations = set()
        
        for domain in domains:
            if knowledge := self.get_domain_knowledge(domain):
                integrations.update(knowledge.common_integrations)
        
        return integrations


# Cross-domain patterns and requirements
class CrossDomainKnowledge:
    """Knowledge that applies across multiple domains"""
    
    @staticmethod
    def get_universal_requirements() -> Dict[str, List[str]]:
        """Requirements that apply to almost all domains"""
        return {
            "security": [
                "authentication",
                "authorization", 
                "data_encryption",
                "secure_apis",
                "audit_logging",
                "session_management",
                "password_policies"
            ],
            "performance": [
                "caching_strategy",
                "database_optimization",
                "load_balancing",
                "cdn_usage",
                "code_minification",
                "image_optimization",
                "lazy_loading"
            ],
            "quality": [
                "error_handling",
                "logging_system",
                "monitoring_alerts",
                "automated_testing",
                "documentation",
                "code_review_process",
                "ci_cd_pipeline"
            ],
            "user_experience": [
                "responsive_design",
                "accessibility_compliance",
                "internationalization",
                "offline_capability",
                "progressive_web_app",
                "intuitive_navigation",
                "search_functionality"
            ],
            "scalability": [
                "horizontal_scaling",
                "microservices_ready",
                "database_sharding",
                "async_processing",
                "message_queuing",
                "containerization",
                "auto_scaling"
            ],
            "compliance": [
                "data_privacy",
                "cookie_consent",
                "terms_of_service",
                "privacy_policy",
                "data_retention",
                "right_to_deletion",
                "data_portability"
            ]
        }
    
    @staticmethod
    def get_technology_stack_patterns() -> Dict[str, Dict[str, List[str]]]:
        """Common technology stack patterns"""
        return {
            "modern_web": {
                "frontend": ["react", "vue", "angular", "svelte"],
                "backend": ["node", "python", "go", "rust"],
                "database": ["postgresql", "mongodb", "redis"],
                "deployment": ["docker", "kubernetes", "vercel", "netlify"]
            },
            "enterprise": {
                "frontend": ["angular", "react"],
                "backend": ["java", "dotnet", "python"],
                "database": ["oracle", "sqlserver", "postgresql"],
                "deployment": ["kubernetes", "openshift", "aws", "azure"]
            },
            "startup": {
                "frontend": ["react", "nextjs"],
                "backend": ["node", "python", "ruby"],
                "database": ["postgresql", "mongodb"],
                "deployment": ["heroku", "vercel", "railway", "render"]
            },
            "high_performance": {
                "frontend": ["react", "solid"],
                "backend": ["go", "rust", "cpp"],
                "database": ["postgresql", "cassandra", "redis"],
                "deployment": ["kubernetes", "bare_metal"]
            }
        }


# Usage example
if __name__ == "__main__":
    kb = DomainKnowledgeBase()
    
    # Test domain detection
    test_inputs = [
        "Build an e-commerce platform with AI recommendations",
        "Create a social media app for doctors",
        "Develop a fintech solution for small businesses",
        "Make an online learning platform for kids"
    ]
    
    for input_text in test_inputs:
        print(f"\nInput: {input_text}")
        domains = kb.detect_domains(input_text)
        print(f"Detected domains: {domains}")
        
        if domains:
            implicit = kb.get_implicit_requirements(domains)
            print(f"Implicit requirements: {len(implicit)} items")
            print(f"Sample: {list(implicit)[:5]}")
            
            security = kb.get_security_requirements(domains)
            print(f"Security requirements: {len(security)} items")
            
            tech = kb.get_technology_recommendations(domains)
            print(f"Technology categories: {list(tech.keys())}")