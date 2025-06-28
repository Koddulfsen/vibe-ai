#!/usr/bin/env python3
"""
Service Integrator - Central Hub for All External Services
=========================================================

Handles authentication, setup, and management of external services like:
- GitHub/GitLab repositories
- Cloud platforms (AWS, Vercel, Netlify)
- API services and databases
- CI/CD pipelines
- Monitoring and analytics

Makes the Task Master system the central control panel for everything.
"""

import os
import sys
import json
import subprocess
import webbrowser
import secrets
import base64
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import tempfile
import time
import urllib.parse

class ServiceType(Enum):
    """Types of external services"""
    GIT_HOSTING = "git_hosting"          # GitHub, GitLab
    CLOUD_PLATFORM = "cloud_platform"   # AWS, Azure, GCP
    DEPLOYMENT = "deployment"            # Vercel, Netlify, Heroku
    DATABASE = "database"                # MongoDB, PostgreSQL, Redis
    API_SERVICE = "api_service"          # OpenAI, Stripe, SendGrid
    MONITORING = "monitoring"            # DataDog, Sentry, LogRocket
    CI_CD = "ci_cd"                     # GitHub Actions, Jenkins

class AuthMethod(Enum):
    """Authentication methods for services"""
    OAUTH = "oauth"
    API_KEY = "api_key"
    USERNAME_PASSWORD = "username_password"
    SSH_KEY = "ssh_key"
    TOKEN = "token"

@dataclass
class ServiceCredential:
    """Represents stored credentials for a service"""
    service_name: str
    service_type: ServiceType
    auth_method: AuthMethod
    credentials: Dict[str, str]  # Encrypted storage
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_used: str = ""
    is_active: bool = True

@dataclass
class ServiceDefinition:
    """Definition of an external service and how to integrate with it"""
    name: str
    display_name: str
    service_type: ServiceType
    auth_method: AuthMethod
    auth_url: Optional[str] = None
    api_base_url: Optional[str] = None
    required_scopes: List[str] = field(default_factory=list)
    setup_instructions: str = ""
    capabilities: List[str] = field(default_factory=list)
    
class CredentialManager:
    """Secure storage and management of service credentials"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".task-master"
        self.credentials_file = self.config_dir / "credentials.json"
        self.master_key_file = self.config_dir / ".master_key"
        self._ensure_config_dir()
        self._init_encryption()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(exist_ok=True)
        # Set secure permissions (user only)
        os.chmod(self.config_dir, 0o700)
    
    def _init_encryption(self):
        """Initialize encryption for credential storage"""
        if not self.master_key_file.exists():
            # Generate new master key
            key = secrets.token_bytes(32)
            with open(self.master_key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.master_key_file, 0o600)
        
        with open(self.master_key_file, 'rb') as f:
            self.master_key = f.read()
    
    def _encrypt_data(self, data: str) -> str:
        """Simple encryption for demonstration (use proper crypto in production)"""
        # This is a simplified encryption - use cryptography library in production
        encoded = base64.b64encode(data.encode()).decode()
        return encoded
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt credential data"""
        try:
            return base64.b64decode(encrypted_data.encode()).decode()
        except Exception:
            return ""
    
    def store_credential(self, credential: ServiceCredential) -> bool:
        """Store a service credential securely"""
        try:
            # Load existing credentials
            credentials = self._load_credentials()
            
            # Encrypt sensitive data
            encrypted_creds = {}
            for key, value in credential.credentials.items():
                encrypted_creds[key] = self._encrypt_data(str(value))
            
            credential.credentials = encrypted_creds
            credential.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Store credential
            credentials[credential.service_name] = asdict(credential)
            
            # Save to file
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            os.chmod(self.credentials_file, 0o600)
            return True
            
        except Exception as e:
            print(f"Error storing credential: {e}")
            return False
    
    def get_credential(self, service_name: str) -> Optional[ServiceCredential]:
        """Retrieve and decrypt a service credential"""
        try:
            credentials = self._load_credentials()
            
            if service_name not in credentials:
                return None
            
            cred_data = credentials[service_name]
            
            # Decrypt credentials
            decrypted_creds = {}
            for key, value in cred_data['credentials'].items():
                decrypted_creds[key] = self._decrypt_data(value)
            
            cred_data['credentials'] = decrypted_creds
            
            # Convert back to dataclass
            return ServiceCredential(
                service_name=cred_data['service_name'],
                service_type=ServiceType(cred_data['service_type']),
                auth_method=AuthMethod(cred_data['auth_method']),
                credentials=decrypted_creds,
                metadata=cred_data.get('metadata', {}),
                created_at=cred_data.get('created_at', ''),
                last_used=cred_data.get('last_used', ''),
                is_active=cred_data.get('is_active', True)
            )
            
        except Exception as e:
            print(f"Error retrieving credential: {e}")
            return None
    
    def list_credentials(self) -> List[str]:
        """List all stored service credentials"""
        try:
            credentials = self._load_credentials()
            return list(credentials.keys())
        except Exception:
            return []
    
    def delete_credential(self, service_name: str) -> bool:
        """Delete a stored credential"""
        try:
            credentials = self._load_credentials()
            if service_name in credentials:
                del credentials[service_name]
                with open(self.credentials_file, 'w') as f:
                    json.dump(credentials, f, indent=2)
                return True
            return False
        except Exception:
            return False
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from storage"""
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

class GitHubIntegrator:
    """GitHub integration for repository management"""
    
    def __init__(self, credential_manager: CredentialManager):
        self.credential_manager = credential_manager
        self.service_name = "github"
    
    def setup_authentication(self) -> bool:
        """Set up GitHub authentication via personal access token"""
        print("🔐 GitHub Integration Setup")
        print("=" * 40)
        print()
        print("To connect GitHub, you need a Personal Access Token.")
        print("This allows the system to create repos, manage code, etc.")
        print()
        
        # Guide user through token creation
        print("📋 Steps to create token:")
        print("   1. Go to: https://github.com/settings/tokens")
        print("   2. Click 'Generate new token (classic)'")
        print("   3. Select scopes: repo, workflow, write:packages")
        print("   4. Copy the generated token")
        print()
        
        open_browser = input("🌐 Open GitHub in browser? (Y/n): ").strip().lower()
        if not open_browser or open_browser == 'y':
            webbrowser.open("https://github.com/settings/tokens")
            print("✅ Opened GitHub in browser")
        
        print()
        token = input("🔑 Paste your GitHub token: ").strip()
        
        if not token:
            print("❌ No token provided")
            return False
        
        # Validate token
        if self._validate_github_token(token):
            # Store credential
            credential = ServiceCredential(
                service_name=self.service_name,
                service_type=ServiceType.GIT_HOSTING,
                auth_method=AuthMethod.TOKEN,
                credentials={"token": token},
                metadata={"scopes": ["repo", "workflow"]}
            )
            
            if self.credential_manager.store_credential(credential):
                print("✅ GitHub authentication configured!")
                return True
            else:
                print("❌ Failed to store GitHub credentials")
                return False
        else:
            print("❌ Invalid GitHub token")
            return False
    
    def _validate_github_token(self, token: str) -> bool:
        """Validate GitHub token by making API call"""
        try:
            result = subprocess.run([
                "curl", "-s", "-H", f"Authorization: token {token}",
                "https://api.github.com/user"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return "login" in data
            return False
        except Exception:
            return False
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> bool:
        """Create a new GitHub repository"""
        credential = self.credential_manager.get_credential(self.service_name)
        if not credential:
            print("❌ GitHub not configured. Run setup first.")
            return False
        
        token = credential.credentials.get("token")
        
        # Create repository via GitHub API
        repo_data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True,
            "gitignore_template": "Python"  # Could be made configurable
        }
        
        try:
            result = subprocess.run([
                "curl", "-s", "-X", "POST",
                "-H", f"Authorization: token {token}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(repo_data),
                "https://api.github.com/user/repos"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if "clone_url" in response:
                    print(f"✅ Repository created: {response['html_url']}")
                    return True
                else:
                    print(f"❌ Repository creation failed: {response.get('message', 'Unknown error')}")
                    return False
            else:
                print("❌ Failed to create repository")
                return False
                
        except Exception as e:
            print(f"❌ Error creating repository: {e}")
            return False
    
    def clone_and_setup_local(self, repo_name: str, local_path: Path) -> bool:
        """Clone repository and set up local development"""
        credential = self.credential_manager.get_credential(self.service_name)
        if not credential:
            return False
        
        # Get user info to construct clone URL
        token = credential.credentials.get("token")
        
        try:
            # Get username
            result = subprocess.run([
                "curl", "-s", "-H", f"Authorization: token {token}",
                "https://api.github.com/user"
            ], capture_output=True, text=True, timeout=10)
            
            user_data = json.loads(result.stdout)
            username = user_data.get("login")
            
            if not username:
                print("❌ Could not get GitHub username")
                return False
            
            # Clone repository
            clone_url = f"https://{token}@github.com/{username}/{repo_name}.git"
            
            result = subprocess.run([
                "git", "clone", clone_url, str(local_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ Repository cloned to: {local_path}")
                return True
            else:
                print(f"❌ Clone failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error cloning repository: {e}")
            return False

class CloudDeploymentIntegrator:
    """Integration with cloud deployment platforms"""
    
    def __init__(self, credential_manager: CredentialManager):
        self.credential_manager = credential_manager
        
    def setup_vercel(self) -> bool:
        """Set up Vercel deployment integration"""
        print("🚀 Vercel Deployment Setup")
        print("=" * 40)
        print()
        print("Vercel provides instant deployment for frontend applications.")
        print()
        
        print("📋 Steps to get Vercel token:")
        print("   1. Go to: https://vercel.com/account/tokens")
        print("   2. Create a new token")
        print("   3. Copy the token")
        print()
        
        open_browser = input("🌐 Open Vercel in browser? (Y/n): ").strip().lower()
        if not open_browser or open_browser == 'y':
            webbrowser.open("https://vercel.com/account/tokens")
        
        token = input("🔑 Paste your Vercel token: ").strip()
        
        if token:
            credential = ServiceCredential(
                service_name="vercel",
                service_type=ServiceType.DEPLOYMENT,
                auth_method=AuthMethod.TOKEN,
                credentials={"token": token}
            )
            
            if self.credential_manager.store_credential(credential):
                print("✅ Vercel configured!")
                return True
        
        print("❌ Vercel setup failed")
        return False
    
    def deploy_to_vercel(self, project_path: Path) -> bool:
        """Deploy project to Vercel"""
        credential = self.credential_manager.get_credential("vercel")
        if not credential:
            print("❌ Vercel not configured")
            return False
        
        token = credential.credentials.get("token")
        
        try:
            # Use Vercel CLI for deployment
            env = os.environ.copy()
            env["VERCEL_TOKEN"] = token
            
            result = subprocess.run([
                "npx", "vercel", "--prod", "--yes"
            ], cwd=project_path, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Extract deployment URL from output
                lines = result.stdout.split('\n')
                deployment_url = None
                for line in lines:
                    if "https://" in line and "vercel.app" in line:
                        deployment_url = line.strip()
                        break
                
                if deployment_url:
                    print(f"✅ Deployed to: {deployment_url}")
                else:
                    print("✅ Deployment successful!")
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False

class ProjectGenerator:
    """Generates complete project templates with integrations"""
    
    def __init__(self, credential_manager: CredentialManager):
        self.credential_manager = credential_manager
        self.github = GitHubIntegrator(credential_manager)
        self.cloud = CloudDeploymentIntegrator(credential_manager)
    
    def create_react_app(self, project_name: str, target_dir: Path) -> bool:
        """Create a complete React application with full setup"""
        print(f"🎯 Creating React App: {project_name}")
        print("=" * 50)
        
        # Step 1: Create local project
        print("📁 Step 1: Creating local React project...")
        if not self._generate_react_template(project_name, target_dir):
            return False
        
        # Step 2: GitHub integration
        print("🐙 Step 2: Setting up GitHub repository...")
        if not self._setup_github_repo(project_name, "React application created with Task Master"):
            print("⚠️  Continuing without GitHub integration")
        
        # Step 3: Deployment setup
        print("🚀 Step 3: Setting up deployment...")
        if not self._setup_deployment(target_dir):
            print("⚠️  Continuing without deployment setup")
        
        print(f"✅ React app '{project_name}' created successfully!")
        print(f"📁 Location: {target_dir}")
        
        return True
    
    def _generate_react_template(self, project_name: str, target_dir: Path) -> bool:
        """Generate React project template"""
        try:
            # Use create-react-app
            result = subprocess.run([
                "npx", "create-react-app", project_name
            ], cwd=target_dir.parent, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ React project created")
                
                # Add additional setup files
                self._add_project_enhancements(target_dir)
                return True
            else:
                print(f"❌ React creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating React project: {e}")
            return False
    
    def _add_project_enhancements(self, project_dir: Path):
        """Add additional project files and configurations"""
        # Add .env.example
        env_example = """# Environment Variables
REACT_APP_API_URL=http://localhost:3001
REACT_APP_VERSION=$npm_package_version
"""
        (project_dir / ".env.example").write_text(env_example)
        
        # Add README with instructions
        readme_addition = """

## 🚀 Created with Task Master Agent System

This project was generated with intelligent automation and includes:
- ✅ React application with modern setup
- 🐙 GitHub integration (if configured)
- 🚀 Deployment pipeline (if configured)
- 📦 Optimized build configuration

### Quick Start
```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
```

### Deployment
This project is configured for automatic deployment. Push to main branch to deploy.
"""
        
        readme_file = project_dir / "README.md"
        if readme_file.exists():
            content = readme_file.read_text()
            readme_file.write_text(content + readme_addition)
    
    def _setup_github_repo(self, repo_name: str, description: str) -> bool:
        """Set up GitHub repository for the project"""
        # Check if GitHub is configured
        if "github" not in self.credential_manager.list_credentials():
            print("GitHub not configured - skipping repository creation")
            return False
        
        return self.github.create_repository(repo_name, description, private=False)
    
    def _setup_deployment(self, project_dir: Path) -> bool:
        """Set up deployment pipeline"""
        # Check if deployment services are configured
        services = self.credential_manager.list_credentials()
        
        if "vercel" in services:
            print("Setting up Vercel deployment...")
            return self.cloud.deploy_to_vercel(project_dir)
        
        print("No deployment services configured")
        return False

class ServiceIntegrator:
    """Main class that orchestrates all service integrations"""
    
    def __init__(self, config_dir: Path = None):
        self.credential_manager = CredentialManager(config_dir)
        self.github = GitHubIntegrator(self.credential_manager)
        self.cloud = CloudDeploymentIntegrator(self.credential_manager)
        self.project_generator = ProjectGenerator(self.credential_manager)
        
        # Define available services
        self.available_services = {
            "github": ServiceDefinition(
                name="github",
                display_name="GitHub",
                service_type=ServiceType.GIT_HOSTING,
                auth_method=AuthMethod.TOKEN,
                setup_instructions="Personal Access Token with repo permissions",
                capabilities=["repo_creation", "code_management", "ci_cd"]
            ),
            "vercel": ServiceDefinition(
                name="vercel",
                display_name="Vercel",
                service_type=ServiceType.DEPLOYMENT,
                auth_method=AuthMethod.TOKEN,
                setup_instructions="Deployment token from Vercel dashboard",
                capabilities=["frontend_deployment", "serverless_functions"]
            )
        }
    
    def show_integration_menu(self) -> str:
        """Show service integration menu"""
        print("\n🔌 SERVICE INTEGRATIONS")
        print("=" * 40)
        
        configured_services = self.credential_manager.list_credentials()
        
        print("📋 Available Services:")
        for i, (service_id, service_def) in enumerate(self.available_services.items(), 1):
            status = "✅ Configured" if service_id in configured_services else "⚪ Not configured"
            print(f"   {i}) {service_def.display_name} - {status}")
        
        print()
        print("🛠️  Actions:")
        print("   c) Configure new service")
        print("   s) Show configured services")
        print("   r) Remove service")
        print("   b) Back to main menu")
        
        return input("\n🤔 Choose option: ").strip().lower()
    
    def configure_service(self, service_name: str) -> bool:
        """Configure a specific service"""
        if service_name == "github":
            return self.github.setup_authentication()
        elif service_name == "vercel":
            return self.cloud.setup_vercel()
        else:
            print(f"❌ Service '{service_name}' not implemented yet")
            return False
    
    def show_configured_services(self):
        """Show all configured services"""
        services = self.credential_manager.list_credentials()
        
        if not services:
            print("📭 No services configured yet")
            return
        
        print("✅ Configured Services:")
        for service in services:
            credential = self.credential_manager.get_credential(service)
            if credential:
                print(f"   🔌 {service} ({credential.service_type.value})")
                print(f"      Auth: {credential.auth_method.value}")
                print(f"      Created: {credential.created_at}")
    
    def create_full_project(self, project_type: str, project_name: str, target_dir: Path) -> bool:
        """Create a complete project with all integrations"""
        if project_type == "react":
            return self.project_generator.create_react_app(project_name, target_dir)
        else:
            print(f"❌ Project type '{project_type}' not implemented yet")
            return False