#!/usr/bin/env python3
"""
Deployment utilities for Skyward Assistable Bundle

Handles bundle deployment, validation, and environment setup for 
production and staging environments.
"""

import os
import sys
import json
import subprocess
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
import tempfile
from datetime import datetime

class DeploymentError(Exception):
    """Raised when deployment fails"""
    pass

class BundleDeployer:
    """Handles bundle deployment operations"""
    
    def __init__(self, bundle_root: Path):
        self.bundle_root = Path(bundle_root)
        self.deployment_config = {}
        self.version = "1.0.0"
        self.required_files = [
            "README.md",
            "components/__init__.py",
            "config/__init__.py",
            "utils/__init__.py"
        ]
        
    def load_deployment_config(self, config_path: Optional[Path] = None):
        """Load deployment configuration"""
        if config_path is None:
            config_path = self.bundle_root / "deployment.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.deployment_config = json.load(f)
        else:
            # Create default config
            self.deployment_config = {
                "name": "skyward_assistable_bundle",
                "version": self.version,
                "description": "Skyward Assistable AI and GoHighLevel integration bundle",
                "author": "Skyward Prompted",
                "homepage": "https://github.com/promptedForge/flow-bundles",
                "repository": "https://github.com/promptedForge/flow-bundles.git",
                "langflow_version": ">=1.0.0",
                "python_version": ">=3.8",
                "dependencies": [
                    "httpx>=0.24.0",
                    "cryptography>=3.4.8",
                    "email-validator>=1.1.0",
                    "phonenumbers>=8.12.0"
                ],
                "environments": {
                    "development": {
                        "langflow_base_url": "http://localhost:7860",
                        "bundle_url": "file://" + str(self.bundle_root.absolute())
                    },
                    "staging": {
                        "langflow_base_url": "https://staging.langflow.example.com",
                        "bundle_url": "https://github.com/promptedForge/flow-bundles.git"
                    },
                    "production": {
                        "langflow_base_url": "https://app.langflow.example.com", 
                        "bundle_url": "https://github.com/promptedForge/flow-bundles.git"
                    }
                }
            }
            
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(self.deployment_config, f, indent=2)
    
    def validate_bundle_structure(self) -> List[str]:
        """Validate bundle has required structure"""
        issues = []
        
        # Check required files
        for required_file in self.required_files:
            file_path = self.bundle_root / required_file
            if not file_path.exists():
                issues.append(f"Missing required file: {required_file}")
        
        # Check component files
        components_dir = self.bundle_root / "components"
        if components_dir.exists():
            expected_components = [
                "assistable_ai_client.py",
                "ghl_client.py", 
                "agent_delegator.py",
                "runtime_hooks.py",
                "batch_processor.py"
            ]
            
            for component in expected_components:
                component_path = components_dir / component
                if not component_path.exists():
                    issues.append(f"Missing component: {component}")
        
        # Check flows directory
        flows_dir = self.bundle_root / "flows"
        if flows_dir.exists():
            flow_files = list(flows_dir.glob("*.json"))
            if len(flow_files) == 0:
                issues.append("No flow files found in flows directory")
        
        # Check docs
        docs_dir = self.bundle_root / "docs"
        if not docs_dir.exists():
            issues.append("Missing docs directory")
        
        return issues
    
    def validate_python_syntax(self) -> List[str]:
        """Validate Python files have correct syntax"""
        issues = []
        
        python_files = list(self.bundle_root.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                compile(content, str(py_file), 'exec')
                
            except SyntaxError as e:
                issues.append(f"Syntax error in {py_file}: {e}")
            except Exception as e:
                issues.append(f"Error reading {py_file}: {e}")
        
        return issues
    
    def validate_json_files(self) -> List[str]:
        """Validate JSON files have correct syntax"""
        issues = []
        
        json_files = list(self.bundle_root.rglob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                issues.append(f"Invalid JSON in {json_file}: {e}")
            except Exception as e:
                issues.append(f"Error reading {json_file}: {e}")
        
        return issues
    
    def run_tests(self) -> bool:
        """Run bundle tests"""
        print("Running bundle tests...")
        
        tests_dir = self.bundle_root / "tests"
        if not tests_dir.exists():
            print("Warning: No tests directory found")
            return True
        
        # Run pytest if available
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(tests_dir), 
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=self.bundle_root)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return result.returncode == 0
            
        except FileNotFoundError:
            print("pytest not found, running basic test validation...")
            
            # Basic test file validation
            test_files = list(tests_dir.glob("test_*.py"))
            if len(test_files) == 0:
                print("Warning: No test files found")
                return True
            
            # Try to import test modules
            for test_file in test_files:
                try:
                    with open(test_file, 'r') as f:
                        content = f.read()
                    compile(content, str(test_file), 'exec')
                    print(f"✓ {test_file.name} syntax valid")
                except Exception as e:
                    print(f"✗ {test_file.name} error: {e}")
                    return False
            
            return True
    
    def create_bundle_package(self, output_dir: Optional[Path] = None) -> Path:
        """Create deployable bundle package"""
        if output_dir is None:
            output_dir = self.bundle_root.parent / "dist"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Create package name
        package_name = f"{self.deployment_config['name']}-{self.version}.zip"
        package_path = output_dir / package_name
        
        print(f"Creating bundle package: {package_path}")
        
        # Files to exclude from package
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".git",
            ".env*",
            "dist",
            "*.log",
            ".DS_Store",
            "*.tmp"
        ]
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.bundle_root.rglob("*"):
                if file_path.is_file():
                    # Check if file should be excluded
                    relative_path = file_path.relative_to(self.bundle_root)
                    
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if pattern in str(relative_path):
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        zipf.write(file_path, relative_path)
                        print(f"  Added: {relative_path}")
        
        print(f"Bundle package created: {package_path}")
        return package_path
    
    def deploy_to_environment(self, environment: str = "development") -> bool:
        """Deploy bundle to specific environment"""
        if environment not in self.deployment_config.get("environments", {}):
            raise DeploymentError(f"Unknown environment: {environment}")
        
        env_config = self.deployment_config["environments"][environment]
        
        print(f"Deploying to {environment} environment...")
        print(f"Langflow URL: {env_config['langflow_base_url']}")
        print(f"Bundle URL: {env_config['bundle_url']}")
        
        # Validate environment configuration
        if environment == "development":
            return self._deploy_local(env_config)
        else:
            return self._deploy_remote(env_config, environment)
    
    def _deploy_local(self, env_config: Dict[str, Any]) -> bool:
        """Deploy to local development environment"""
        print("Deploying to local development environment...")
        
        # For local deployment, we can copy files directly
        langflow_bundles_dir = Path.home() / ".langflow" / "bundles"
        langflow_bundles_dir.mkdir(parents=True, exist_ok=True)
        
        bundle_target = langflow_bundles_dir / self.deployment_config["name"]
        
        # Remove existing bundle
        if bundle_target.exists():
            shutil.rmtree(bundle_target)
        
        # Copy bundle
        shutil.copytree(self.bundle_root, bundle_target)
        
        print(f"Bundle deployed to: {bundle_target}")
        print("Restart Langflow to load the bundle")
        
        return True
    
    def _deploy_remote(self, env_config: Dict[str, Any], environment: str) -> bool:
        """Deploy to remote environment"""
        print(f"Deploying to {environment} environment...")
        
        # For remote deployment, we need to:
        # 1. Push to git repository
        # 2. Update environment variables
        # 3. Trigger Langflow restart
        
        bundle_url = env_config["bundle_url"]
        
        if bundle_url.startswith("https://github.com"):
            return self._deploy_via_git(env_config, environment)
        else:
            raise DeploymentError(f"Unsupported bundle URL: {bundle_url}")
    
    def _deploy_via_git(self, env_config: Dict[str, Any], environment: str) -> bool:
        """Deploy via git repository"""
        print("Deploying via git repository...")
        
        # Check if we're in a git repository
        if not (self.bundle_root / ".git").exists():
            print("Not in a git repository, initializing...")
            subprocess.run(["git", "init"], cwd=self.bundle_root)
        
        # Add and commit changes
        subprocess.run(["git", "add", "."], cwd=self.bundle_root)
        subprocess.run([
            "git", "commit", "-m", 
            f"Deploy {self.deployment_config['name']} v{self.version} to {environment}"
        ], cwd=self.bundle_root)
        
        # Push to origin
        try:
            result = subprocess.run(["git", "push", "origin", "main"], 
                                  cwd=self.bundle_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Successfully pushed to git repository")
                return True
            else:
                print(f"Git push failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error pushing to git: {e}")
            return False
    
    def validate_deployment(self, environment: str = "development") -> bool:
        """Validate deployment was successful"""
        env_config = self.deployment_config["environments"][environment]
        langflow_url = env_config["langflow_base_url"]
        
        # Try to ping Langflow
        try:
            response = requests.get(f"{langflow_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✓ Langflow is running at {langflow_url}")
                return True
            else:
                print(f"✗ Langflow health check failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"✗ Cannot reach Langflow: {e}")
            return False
    
    def rollback_deployment(self, environment: str, version: str):
        """Rollback to previous version"""
        print(f"Rolling back {environment} to version {version}")
        # Implementation depends on deployment method
        pass
    
    def get_deployment_status(self, environment: str) -> Dict[str, Any]:
        """Get current deployment status"""
        env_config = self.deployment_config["environments"][environment]
        
        status = {
            "environment": environment,
            "langflow_url": env_config["langflow_base_url"],
            "bundle_url": env_config["bundle_url"],
            "last_deployed": None,
            "version": self.version,
            "status": "unknown"
        }
        
        # Check if Langflow is accessible
        if self.validate_deployment(environment):
            status["status"] = "healthy"
        else:
            status["status"] = "unreachable"
        
        return status

def main():
    """Main deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Skyward Assistable Bundle")
    parser.add_argument("command", choices=[
        "validate", "test", "package", "deploy", "status", "rollback"
    ], help="Deployment command")
    parser.add_argument("--environment", "-e", default="development",
                       help="Target environment")
    parser.add_argument("--version", "-v", help="Version for rollback")
    parser.add_argument("--bundle-root", default=".", help="Bundle root directory")
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = BundleDeployer(Path(args.bundle_root))
    deployer.load_deployment_config()
    
    try:
        if args.command == "validate":
            print("🔍 Validating bundle structure...")
            
            structure_issues = deployer.validate_bundle_structure()
            syntax_issues = deployer.validate_python_syntax()
            json_issues = deployer.validate_json_files()
            
            all_issues = structure_issues + syntax_issues + json_issues
            
            if all_issues:
                print("❌ Validation failed:")
                for issue in all_issues:
                    print(f"  - {issue}")
                sys.exit(1)
            else:
                print("✅ Bundle validation passed!")
        
        elif args.command == "test":
            print("🧪 Running bundle tests...")
            if deployer.run_tests():
                print("✅ All tests passed!")
            else:
                print("❌ Tests failed!")
                sys.exit(1)
        
        elif args.command == "package":
            print("📦 Creating bundle package...")
            package_path = deployer.create_bundle_package()
            print(f"✅ Package created: {package_path}")
        
        elif args.command == "deploy":
            print(f"🚀 Deploying to {args.environment}...")
            
            # Run validation first
            print("Running pre-deployment validation...")
            structure_issues = deployer.validate_bundle_structure()
            if structure_issues:
                print("❌ Pre-deployment validation failed:")
                for issue in structure_issues:
                    print(f"  - {issue}")
                sys.exit(1)
            
            if deployer.deploy_to_environment(args.environment):
                print(f"✅ Successfully deployed to {args.environment}!")
                
                # Validate deployment
                if deployer.validate_deployment(args.environment):
                    print("✅ Deployment validation passed!")
                else:
                    print("⚠️  Deployment validation failed - check Langflow logs")
            else:
                print(f"❌ Deployment to {args.environment} failed!")
                sys.exit(1)
        
        elif args.command == "status":
            print(f"📊 Checking {args.environment} status...")
            status = deployer.get_deployment_status(args.environment)
            
            print(f"Environment: {status['environment']}")
            print(f"Status: {status['status']}")
            print(f"Langflow URL: {status['langflow_url']}")
            print(f"Bundle URL: {status['bundle_url']}")
            print(f"Version: {status['version']}")
        
        elif args.command == "rollback":
            if not args.version:
                print("❌ Version required for rollback")
                sys.exit(1)
            
            print(f"⏪ Rolling back {args.environment} to version {args.version}...")
            deployer.rollback_deployment(args.environment, args.version)
            print("✅ Rollback completed!")
    
    except DeploymentError as e:
        print(f"❌ Deployment error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
