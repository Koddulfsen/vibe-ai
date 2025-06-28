#!/usr/bin/env python3
"""
Create GitHub repository using the API
Requires: GITHUB_TOKEN environment variable
"""

import os
import sys
import json
import subprocess
import requests
from typing import Optional

def create_github_repo(repo_name: str, description: str = "", private: bool = False, token: Optional[str] = None):
    """Create a GitHub repository"""
    
    # Try to get token from environment
    if not token:
        token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("❌ No GitHub token found!")
        print("\nTo set up automated repo creation:")
        print("1. Go to: https://github.com/settings/tokens/new")
        print("2. Create a token with 'repo' scope")
        print("3. Run: export GITHUB_TOKEN='your-token-here'")
        print("4. Run this script again")
        return False
    
    # API endpoint
    url = "https://api.github.com/user/repos"
    
    # Request data
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False
    }
    
    # Headers
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Make request
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        repo_info = response.json()
        print(f"✅ Repository created: {repo_info['html_url']}")
        
        # Set up remote
        subprocess.run(["git", "remote", "set-url", "origin", repo_info['ssh_url']], check=True)
        print(f"✅ Remote updated to: {repo_info['ssh_url']}")
        
        # Push
        print("\n📤 Pushing to GitHub...")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub!")
            print(f"\n🎉 Your repo is live at: {repo_info['html_url']}")
        else:
            print(f"❌ Push failed: {result.stderr}")
            
        return True
    else:
        error = response.json().get('message', 'Unknown error')
        print(f"❌ Failed to create repo: {error}")
        
        if response.status_code == 422 and "already exists" in error:
            print("\n💡 Repo already exists! Try pushing directly:")
            print("   git push -u origin main")
            
        return False


if __name__ == "__main__":
    # Check if we're in a git repo
    if not os.path.exists(".git"):
        print("❌ Not in a git repository!")
        sys.exit(1)
    
    # Create the repo
    success = create_github_repo(
        "vibe-ai",
        "AI-powered development assistant with UltraDeep thinking and intelligent agents",
        private=True  # Changed to create private repos by default
    )
    
    if not success:
        print("\n🔧 Manual steps:")
        print("1. Go to: https://github.com/new")
        print("2. Create repo: vibe-ai")
        print("3. Run: git push -u origin main")