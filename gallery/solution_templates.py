#!/usr/bin/env python3
"""
Solution Gallery and Templates for vibe.ai
Pre-built solutions that users can browse and instantly create
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


@dataclass
class SolutionTemplate:
    """Represents a solution template in the gallery"""
    id: str
    name: str
    category: str
    description: str
    prompt: str
    tags: List[str]
    difficulty: str  # beginner, intermediate, advanced
    estimated_time: str
    features: List[str]
    tech_stack: List[str]
    preview_code: Dict[str, str]  # filename -> code snippet
    use_cases: List[str]
    created_by: str = "vibe.ai team"
    rating: float = 0.0
    downloads: int = 0


class SolutionGallery:
    """Gallery of pre-built solution templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.categories = self._get_categories()
        
    def _load_templates(self) -> List[SolutionTemplate]:
        """Load all solution templates"""
        templates = [
            # API Templates
            SolutionTemplate(
                id="rest-api-basic",
                name="Basic REST API",
                category="Backend",
                description="Simple REST API with CRUD operations",
                prompt="Create a basic REST API with CRUD operations for a resource management system",
                tags=["api", "rest", "crud", "backend"],
                difficulty="beginner",
                estimated_time="5 minutes",
                features=[
                    "RESTful endpoints",
                    "Data validation",
                    "Error handling",
                    "API documentation"
                ],
                tech_stack=["FastAPI", "SQLite", "Pydantic"],
                preview_code={
                    "main.py": '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Basic REST API")

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float

items_db = []

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    item.id = len(items_db) + 1
    items_db.append(item)
    return item

@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db'''
                },
                use_cases=[
                    "Quick API prototyping",
                    "Learning REST principles",
                    "Small applications"
                ],
                rating=4.5,
                downloads=1250
            ),
            
            SolutionTemplate(
                id="rest-api-auth",
                name="REST API with Authentication",
                category="Backend",
                description="Production-ready API with JWT authentication and database",
                prompt="Build a REST API with JWT authentication, PostgreSQL database, role-based access control, and comprehensive testing",
                tags=["api", "rest", "auth", "jwt", "postgresql", "production"],
                difficulty="intermediate",
                estimated_time="10 minutes",
                features=[
                    "JWT authentication",
                    "Role-based access control",
                    "PostgreSQL with migrations",
                    "Password hashing",
                    "Rate limiting",
                    "Comprehensive tests"
                ],
                tech_stack=["FastAPI", "PostgreSQL", "SQLAlchemy", "Alembic", "JWT", "pytest"],
                preview_code={
                    "auth.py": '''from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)'''
                },
                use_cases=[
                    "SaaS applications",
                    "Enterprise APIs",
                    "Secure data access"
                ],
                rating=4.8,
                downloads=3420
            ),
            
            # Frontend Templates
            SolutionTemplate(
                id="react-dashboard",
                name="React Admin Dashboard",
                category="Frontend",
                description="Modern admin dashboard with charts and data tables",
                prompt="Create a React admin dashboard with TypeScript, Material-UI, charts, data tables, and responsive design",
                tags=["react", "dashboard", "typescript", "material-ui", "charts"],
                difficulty="intermediate",
                estimated_time="8 minutes",
                features=[
                    "Responsive layout",
                    "Interactive charts",
                    "Data tables with sorting",
                    "Dark mode support",
                    "TypeScript",
                    "Material-UI components"
                ],
                tech_stack=["React", "TypeScript", "Material-UI", "Recharts", "React Router"],
                preview_code={
                    "Dashboard.tsx": '''import React from 'react';
import { Grid, Paper, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface DashboardProps {
  data: ChartData[];
}

export const Dashboard: React.FC<DashboardProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Sales Overview
          </Typography>
          <LineChart width={600} height={300} data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="sales" stroke="#8884d8" />
          </LineChart>
        </Paper>
      </Grid>
    </Grid>
  );
};'''
                },
                use_cases=[
                    "Admin panels",
                    "Analytics dashboards",
                    "Business intelligence"
                ],
                rating=4.7,
                downloads=2890
            ),
            
            SolutionTemplate(
                id="nextjs-blog",
                name="Next.js Blog Platform",
                category="Frontend",
                description="SEO-optimized blog with markdown support",
                prompt="Build a Next.js blog platform with markdown support, SEO optimization, dark mode, and static site generation",
                tags=["nextjs", "blog", "markdown", "seo", "react"],
                difficulty="intermediate",
                estimated_time="7 minutes",
                features=[
                    "Markdown blog posts",
                    "SEO optimization",
                    "Static site generation",
                    "Dark mode",
                    "RSS feed",
                    "Search functionality"
                ],
                tech_stack=["Next.js", "React", "Tailwind CSS", "MDX", "TypeScript"],
                preview_code={
                    "pages/blog/[slug].tsx": '''import { GetStaticProps, GetStaticPaths } from 'next';
import { MDXRemote } from 'next-mdx-remote';
import { getPostBySlug, getAllPosts } from '../../lib/posts';

interface PostPageProps {
  post: Post;
  source: MDXRemoteSerializeResult;
}

export default function PostPage({ post, source }: PostPageProps) {
  return (
    <article className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
      <time className="text-gray-500">{post.date}</time>
      <div className="prose prose-lg mt-8">
        <MDXRemote {...source} />
      </div>
    </article>
  );
}'''
                },
                use_cases=[
                    "Personal blogs",
                    "Company blogs",
                    "Documentation sites"
                ],
                rating=4.6,
                downloads=1980
            ),
            
            # Full Stack Templates
            SolutionTemplate(
                id="saas-starter",
                name="SaaS Starter Kit",
                category="Full Stack",
                description="Complete SaaS application with payments and subscriptions",
                prompt="Create a full-stack SaaS starter kit with authentication, Stripe payments, subscription management, admin panel, and multi-tenancy",
                tags=["saas", "fullstack", "payments", "stripe", "subscriptions"],
                difficulty="advanced",
                estimated_time="15 minutes",
                features=[
                    "User authentication",
                    "Stripe integration",
                    "Subscription tiers",
                    "Admin dashboard",
                    "Multi-tenancy",
                    "Email notifications",
                    "API rate limiting"
                ],
                tech_stack=["Next.js", "FastAPI", "PostgreSQL", "Stripe", "Redis", "Docker"],
                preview_code={
                    "billing.py": '''from stripe import stripe
from sqlalchemy.orm import Session
from fastapi import HTTPException

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingService:
    def create_checkout_session(self, user_id: int, price_id: str, db: Session):
        user = db.query(User).filter(User.id == user_id).first()
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{BASE_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{BASE_URL}/billing/cancel',
            customer_email=user.email,
            metadata={'user_id': str(user_id)}
        )
        
        return session'''
                },
                use_cases=[
                    "SaaS products",
                    "Subscription services",
                    "Multi-tenant platforms"
                ],
                rating=4.9,
                downloads=4560
            ),
            
            # Mobile/Desktop Templates
            SolutionTemplate(
                id="electron-app",
                name="Electron Desktop App",
                category="Desktop",
                description="Cross-platform desktop application",
                prompt="Build an Electron desktop application with React, auto-updates, system tray integration, and native notifications",
                tags=["electron", "desktop", "react", "cross-platform"],
                difficulty="intermediate",
                estimated_time="10 minutes",
                features=[
                    "Cross-platform (Windows, Mac, Linux)",
                    "Auto-updates",
                    "System tray integration",
                    "Native notifications",
                    "File system access",
                    "React UI"
                ],
                tech_stack=["Electron", "React", "TypeScript", "electron-builder"],
                preview_code={
                    "main.js": '''const { app, BrowserWindow, Tray, Menu, nativeImage } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');

let mainWindow;
let tray;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      enableRemoteModule: false
    }
  });

  mainWindow.loadFile('index.html');
  
  // Auto-updater
  autoUpdater.checkForUpdatesAndNotify();
}

app.whenReady().then(() => {
  createWindow();
  createTray();
});'''
                },
                use_cases=[
                    "Productivity tools",
                    "Development tools",
                    "Media applications"
                ],
                rating=4.4,
                downloads=1670
            ),
            
            # CLI Templates
            SolutionTemplate(
                id="cli-tool",
                name="CLI Tool Framework",
                category="CLI",
                description="Feature-rich command-line tool with subcommands",
                prompt="Create a CLI tool with multiple subcommands, configuration file support, colorful output, and progress bars",
                tags=["cli", "terminal", "automation", "devtools"],
                difficulty="beginner",
                estimated_time="5 minutes",
                features=[
                    "Multiple subcommands",
                    "Configuration files",
                    "Colorful output",
                    "Progress bars",
                    "Interactive prompts",
                    "Shell completion"
                ],
                tech_stack=["Python", "Click", "Rich", "TOML"],
                preview_code={
                    "cli.py": '''import click
from rich.console import Console
from rich.progress import track
import toml

console = Console()

@click.group()
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, config):
    """A powerful CLI tool for automation"""
    ctx.ensure_object(dict)
    if config:
        ctx.obj['config'] = toml.load(config)

@cli.command()
@click.argument('files', nargs=-1, type=click.Path())
def process(files):
    """Process files with progress tracking"""
    for file in track(files, description="Processing..."):
        # Process each file
        console.print(f"✓ Processed [green]{file}[/green]")

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'toml']))
def export(format):
    """Export data in various formats"""
    console.print(f"Exporting as [bold]{format}[/bold]...")'''
                },
                use_cases=[
                    "Build tools",
                    "Development utilities",
                    "System automation"
                ],
                rating=4.3,
                downloads=890
            ),
            
            # Data/ML Templates
            SolutionTemplate(
                id="ml-api",
                name="Machine Learning API",
                category="AI/ML",
                description="Production ML model serving with monitoring",
                prompt="Build a machine learning API with model serving, versioning, monitoring, and automatic retraining pipeline",
                tags=["ml", "ai", "api", "tensorflow", "monitoring"],
                difficulty="advanced",
                estimated_time="12 minutes",
                features=[
                    "Model serving",
                    "Model versioning",
                    "Performance monitoring",
                    "A/B testing",
                    "Automatic retraining",
                    "Feature preprocessing"
                ],
                tech_stack=["FastAPI", "TensorFlow", "Redis", "Prometheus", "Docker"],
                preview_code={
                    "model_service.py": '''import tensorflow as tf
from typing import Dict, List
import numpy as np
from datetime import datetime

class ModelService:
    def __init__(self):
        self.models = {}
        self.current_version = "v1.0"
        self.load_models()
    
    def load_models(self):
        """Load all model versions"""
        self.models["v1.0"] = tf.keras.models.load_model("models/v1.0")
        self.models["v1.1"] = tf.keras.models.load_model("models/v1.1")
    
    def predict(self, features: Dict, version: str = None) -> Dict:
        """Make prediction with specified model version"""
        version = version or self.current_version
        model = self.models.get(version)
        
        if not model:
            raise ValueError(f"Model version {version} not found")
        
        # Preprocess features
        input_data = self.preprocess(features)
        
        # Make prediction
        start_time = datetime.now()
        prediction = model.predict(input_data)
        inference_time = (datetime.now() - start_time).total_seconds()
        
        # Log metrics
        self.log_metrics(version, inference_time)
        
        return {
            "prediction": float(prediction[0][0]),
            "version": version,
            "inference_time": inference_time
        }'''
                },
                use_cases=[
                    "ML model deployment",
                    "AI services",
                    "Predictive APIs"
                ],
                rating=4.7,
                downloads=2340
            )
        ]
        
        return templates
    
    def _get_categories(self) -> List[str]:
        """Get unique categories"""
        categories = set()
        for template in self.templates:
            categories.add(template.category)
        return sorted(list(categories))
    
    def browse_gallery(self):
        """Interactive gallery browsing"""
        if RICH_AVAILABLE:
            self._rich_browse()
        else:
            self._simple_browse()
    
    def _rich_browse(self):
        """Rich interactive gallery browser"""
        console.clear()
        
        # Header
        header = """
# 🎨 vibe.ai Solution Gallery

Browse our collection of production-ready solution templates.
Each template is crafted by experts and ready to use!
"""
        console.print(Panel(Markdown(header), border_style="cyan"))
        
        # Category selection
        console.print("\n[bold]Browse by Category:[/bold]\n")
        categories = ["All"] + self.categories
        
        for i, cat in enumerate(categories):
            count = len([t for t in self.templates if cat == "All" or t.category == cat])
            console.print(f"  {i+1}. {cat} ({count} templates)")
        
        cat_choice = Prompt.ask("\nSelect category", default="1")
        
        try:
            selected_cat = categories[int(cat_choice) - 1]
        except:
            selected_cat = "All"
        
        # Show templates in category
        self._show_templates(selected_cat)
    
    def _show_templates(self, category: str):
        """Show templates in a category"""
        console.clear()
        
        templates = self.templates if category == "All" else [
            t for t in self.templates if t.category == category
        ]
        
        console.print(f"\n[bold]{category} Templates[/bold]\n")
        
        # Create cards for each template
        for i, template in enumerate(templates, 1):
            # Create template card
            card_content = f"""
[bold cyan]{template.name}[/bold cyan]
{template.description}

[yellow]Difficulty:[/yellow] {template.difficulty.title()}
[yellow]Time:[/yellow] {template.estimated_time}
[yellow]Rating:[/yellow] {"⭐" * int(template.rating)} ({template.rating})
[yellow]Downloads:[/yellow] {template.downloads:,}

[dim]Tags: {', '.join(template.tags)}[/dim]
"""
            console.print(Panel(card_content.strip(), box=box.ROUNDED))
        
        # Template selection
        console.print("\n[bold]Actions:[/bold]")
        console.print("  • Enter template number to view details")
        console.print("  • 'b' to go back")
        console.print("  • 'q' to quit")
        
        choice = Prompt.ask("\nYour choice")
        
        if choice.lower() == 'b':
            self._rich_browse()
        elif choice.lower() == 'q':
            return
        else:
            try:
                template_idx = int(choice) - 1
                if 0 <= template_idx < len(templates):
                    self._show_template_details(templates[template_idx])
            except:
                self._show_templates(category)
    
    def _show_template_details(self, template: SolutionTemplate):
        """Show detailed template information"""
        console.clear()
        
        # Header
        console.print(Panel(
            f"[bold cyan]{template.name}[/bold cyan]\n{template.description}",
            title=f"📦 {template.category} Template",
            border_style="green"
        ))
        
        # Features
        console.print("\n[bold]Features:[/bold]")
        feature_cols = [f"• {feat}" for feat in template.features]
        console.print(Columns(feature_cols, equal=True, expand=True))
        
        # Tech Stack
        console.print("\n[bold]Technology Stack:[/bold]")
        tech_badges = " ".join([f"[cyan]{tech}[/cyan]" for tech in template.tech_stack])
        console.print(f"  {tech_badges}")
        
        # Use Cases
        console.print("\n[bold]Perfect for:[/bold]")
        for use_case in template.use_cases:
            console.print(f"  • {use_case}")
        
        # Code Preview
        if template.preview_code:
            console.print("\n[bold]Code Preview:[/bold]")
            for filename, code in list(template.preview_code.items())[:1]:  # Show first file
                syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title=filename, border_style="blue"))
        
        # Actions
        console.print("\n[bold green]Ready to build this?[/bold green]")
        
        if Confirm.ask("Create this solution now?"):
            output_dir = Prompt.ask("Output directory", default=f"{template.id}-project")
            self._create_from_template(template, output_dir)
        else:
            self._show_templates("All")
    
    def _create_from_template(self, template: SolutionTemplate, output_dir: str):
        """Create solution from template"""
        console.print(f"\n[bold cyan]Creating {template.name}...[/bold cyan]")
        
        # Import and run the agent engine
        from pathlib import Path
        import subprocess
        import sys
        
        vibe_dir = Path(__file__).parent.parent
        agent_engine = vibe_dir / "agent_based_solution_engine.py"
        
        cmd = [
            sys.executable,
            str(agent_engine),
            template.prompt,
            "-o", output_dir
        ]
        
        with console.status("Building your solution...", spinner="dots"):
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"\n[bold green]✅ Solution created in {output_dir}![/bold green]")
            console.print(f"\nNext steps:")
            console.print(f"  1. cd {output_dir}")
            console.print(f"  2. Follow the README.md")
        else:
            console.print(f"\n[red]Error creating solution[/red]")
    
    def _simple_browse(self):
        """Simple gallery browser for non-rich terminals"""
        print("\n🎨 vibe.ai Solution Gallery")
        print("=" * 50)
        
        print("\nCategories:")
        categories = ["All"] + self.categories
        for i, cat in enumerate(categories, 1):
            count = len([t for t in self.templates if cat == "All" or t.category == cat])
            print(f"{i}. {cat} ({count} templates)")
        
        cat_choice = input("\nSelect category (number): ")
        
        try:
            selected_cat = categories[int(cat_choice) - 1]
        except:
            selected_cat = "All"
        
        # Show templates
        templates = self.templates if selected_cat == "All" else [
            t for t in self.templates if t.category == selected_cat
        ]
        
        print(f"\n{selected_cat} Templates:")
        print("-" * 50)
        
        for i, template in enumerate(templates, 1):
            print(f"\n{i}. {template.name}")
            print(f"   {template.description}")
            print(f"   Difficulty: {template.difficulty} | Time: {template.estimated_time}")
            print(f"   Rating: {'★' * int(template.rating)} ({template.rating})")
        
        template_choice = input("\nSelect template for details (number): ")
        
        try:
            template = templates[int(template_choice) - 1]
            print(f"\n{template.name}")
            print("=" * len(template.name))
            print(f"\nPrompt: {template.prompt}")
            print(f"\nFeatures:")
            for feat in template.features:
                print(f"  • {feat}")
            
            create = input("\nCreate this solution? (y/n): ")
            if create.lower() == 'y':
                output_dir = input(f"Output directory (default: {template.id}-project): ") or f"{template.id}-project"
                print(f"Creating solution in {output_dir}...")
                # Would run the actual creation here
        except:
            print("Invalid selection")
    
    def get_template_by_id(self, template_id: str) -> Optional[SolutionTemplate]:
        """Get a specific template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
    
    def search_templates(self, query: str) -> List[SolutionTemplate]:
        """Search templates by query"""
        query = query.lower()
        results = []
        
        for template in self.templates:
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag for tag in template.tags) or
                query in template.category.lower()):
                results.append(template)
        
        return results


def main():
    """Main entry point for gallery"""
    gallery = SolutionGallery()
    gallery.browse_gallery()


if __name__ == "__main__":
    main()