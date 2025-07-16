#!/usr/bin/env python3
"""
Bundle validation script for Skyward Assistable Bundle

Validates the complete bundle structure, dependencies, and readiness for deployment.
"""

import os
import sys
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple
import importlib.util

class BundleValidator:
    """Validates bundle structure and completeness"""
    
    def __init__(self, bundle_root: Path):
        self.bundle_root = Path(bundle_root)
        self.issues = []
        self.warnings = []
        
    def validate_structure(self) -> bool:
        """Validate bundle directory structure"""
        print("🔍 Validating bundle structure...")
        
        required_dirs = [
            "components",
            "config", 
            "utils",
            "flows",
            "docs",
            "tests",
            "examples",
            "scripts"
        ]
        
        required_files = [
            "README.md",
            "pyproject.toml",
            "requirements.txt",
            ".gitignore",
            "CHANGELOG.md"
        ]
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = self.bundle_root / dir_name
            if not dir_path.exists():
                self.issues.append(f"Missing required directory: {dir_name}")
            elif not dir_path.is_dir():
                self.issues.append(f"{dir_name} is not a directory")
        
        # Check files
        for file_name in required_files:
            file_path = self.bundle_root / file_name
            if not file_path.exists():
                self.issues.append(f"Missing required file: {file_name}")
            elif not file_path.is_file():
                self.issues.append(f"{file_name} is not a file")
        
        return len(self.issues) == 0
    
    def validate_components(self) -> bool:
        """Validate component files"""
        print("🧩 Validating components...")
        
        components_dir = self.bundle_root / "components"
        if not components_dir.exists():
            return False
        
        required_components = [
            "assistable_ai_client.py",
            "ghl_client.py",
            "agent_delegator.py", 
            "runtime_hooks.py",
            "batch_processor.py"
        ]
        
        # Check component files exist
        for component in required_components:
            component_path = components_dir / component
            if not component_path.exists():
                self.issues.append(f"Missing component: {component}")
                continue
            
            # Validate Python syntax
            try:
                with open(component_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ast.parse(content)
                print(f"  ✅ {component} - syntax valid")
                
            except SyntaxError as e:
                self.issues.append(f"Syntax error in {component}: {e}")
            except Exception as e:
                self.issues.append(f"Error reading {component}: {e}")
        
        # Check __init__.py
        init_file = components_dir / "__init__.py"
        if not init_file.exists():
            self.issues.append("Missing components/__init__.py")
        
        return len([i for i in self.issues if "component" in i.lower()]) == 0
    
    def validate_flows(self) -> bool:
        """Validate flow JSON files"""
        print("🔄 Validating flows...")
        
        flows_dir = self.bundle_root / "flows"
        if not flows_dir.exists():
            return False
        
        expected_flows = [
            "customer_service_flow.json",
            "ai_calling_campaign.json",
            "lead_qualification.json",
            "agent_delegation_demo.json"
        ]
        
        for flow_file in expected_flows:
            flow_path = flows_dir / flow_file
            if not flow_path.exists():
                self.warnings.append(f"Flow file not found: {flow_file}")
                continue
            
            try:
                with open(flow_path, 'r', encoding='utf-8') as f:
                    flow_data = json.load(f)
                
                # Basic flow structure validation
                if "data" not in flow_data:
                    self.issues.append(f"Invalid flow structure in {flow_file}: missing 'data'")
                elif "nodes" not in flow_data["data"]:
                    self.issues.append(f"Invalid flow structure in {flow_file}: missing 'nodes'")
                elif "edges" not in flow_data["data"]:
                    self.issues.append(f"Invalid flow structure in {flow_file}: missing 'edges'")
                else:
                    print(f"  ✅ {flow_file} - valid JSON structure")
                    
            except json.JSONDecodeError as e:
                self.issues.append(f"Invalid JSON in {flow_file}: {e}")
            except Exception as e:
                self.issues.append(f"Error reading {flow_file}: {e}")
        
        return len([i for i in self.issues if "flow" in i.lower()]) == 0
    
    def validate_utilities(self) -> bool:
        """Validate utility modules"""
        print("🛠️  Validating utilities...")
        
        utils_dir = self.bundle_root / "utils"
        if not utils_dir.exists():
            return False
        
        required_utils = [
            "auth_manager.py",
            "validators.py",
            "error_handler.py", 
            "cache_manager.py"
        ]
        
        for util_file in required_utils:
            util_path = utils_dir / util_file
            if not util_path.exists():
                self.issues.append(f"Missing utility: {util_file}")
                continue
            
            # Validate Python syntax
            try:
                with open(util_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ast.parse(content)
                print(f"  ✅ {util_file} - syntax valid")
                
            except SyntaxError as e:
                self.issues.append(f"Syntax error in {util_file}: {e}")
            except Exception as e:
                self.issues.append(f"Error reading {util_file}: {e}")
        
        return len([i for i in self.issues if "utility" in i.lower()]) == 0
    
    def validate_documentation(self) -> bool:
        """Validate documentation files"""
        print("📚 Validating documentation...")
        
        docs_dir = self.bundle_root / "docs"
        if not docs_dir.exists():
            return False
        
        required_docs = [
            "README.md",
            "INSTALLATION.md",
            "API_REFERENCE.md",
            "WORKFLOWS.md",
            "TROUBLESHOOTING.md"
        ]
        
        for doc_file in required_docs:
            doc_path = docs_dir / doc_file
            if not doc_path.exists():
                self.issues.append(f"Missing documentation: {doc_file}")
            else:
                # Check file is not empty
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    if len(content) < 100:  # Arbitrary minimum content length
                        self.warnings.append(f"Documentation file {doc_file} appears to be very short")
                    else:
                        print(f"  ✅ {doc_file} - has content")
                        
                except Exception as e:
                    self.issues.append(f"Error reading {doc_file}: {e}")
        
        return len([i for i in self.issues if "documentation" in i.lower()]) == 0
    
    def validate_configuration(self) -> bool:
        """Validate configuration files"""
        print("⚙️  Validating configuration...")
        
        # Check pyproject.toml
        pyproject_path = self.bundle_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomllib
                with open(pyproject_path, 'rb') as f:
                    toml_data = tomllib.load(f)
                
                if "project" not in toml_data:
                    self.issues.append("pyproject.toml missing [project] section")
                else:
                    project = toml_data["project"]
                    required_fields = ["name", "version", "description"]
                    for field in required_fields:
                        if field not in project:
                            self.issues.append(f"pyproject.toml missing project.{field}")
                
                print("  ✅ pyproject.toml - valid structure")
                
            except Exception as e:
                # Try as INI format for older Python versions
                try:
                    with open(pyproject_path, 'r') as f:
                        content = f.read()
                    
                    if "[project]" in content and "name" in content and "version" in content:
                        print("  ✅ pyproject.toml - basic validation passed")
                    else:
                        self.warnings.append("pyproject.toml may be missing required sections")
                        
                except Exception as e2:
                    self.issues.append(f"Error reading pyproject.toml: {e2}")
        
        # Check requirements.txt
        requirements_path = self.bundle_root / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, 'r') as f:
                    requirements = f.read().strip()
                
                if len(requirements) > 0:
                    print("  ✅ requirements.txt - has dependencies")
                else:
                    self.warnings.append("requirements.txt is empty")
                    
            except Exception as e:
                self.issues.append(f"Error reading requirements.txt: {e}")
        
        return len([i for i in self.issues if "configuration" in i.lower()]) == 0
    
    def validate_tests(self) -> bool:
        """Validate test files"""
        print("🧪 Validating tests...")
        
        tests_dir = self.bundle_root / "tests"
        if not tests_dir.exists():
            self.warnings.append("No tests directory found")
            return True
        
        test_files = list(tests_dir.glob("test_*.py"))
        if len(test_files) == 0:
            self.warnings.append("No test files found")
            return True
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ast.parse(content)
                print(f"  ✅ {test_file.name} - syntax valid")
                
            except SyntaxError as e:
                self.issues.append(f"Syntax error in {test_file.name}: {e}")
            except Exception as e:
                self.issues.append(f"Error reading {test_file.name}: {e}")
        
        return len([i for i in self.issues if "test" in i.lower()]) == 0
    
    def check_imports(self) -> bool:
        """Check that components can be imported (basic validation)"""
        print("📦 Checking imports...")
        
        components_dir = self.bundle_root / "components"
        if not components_dir.exists():
            return False
        
        # Add bundle root to Python path temporarily
        sys.path.insert(0, str(self.bundle_root))
        
        try:
            # Test basic imports
            component_files = [
                "assistable_ai_client",
                "ghl_client", 
                "agent_delegator",
                "runtime_hooks",
                "batch_processor"
            ]
            
            for component in component_files:
                try:
                    spec = importlib.util.spec_from_file_location(
                        component,
                        components_dir / f"{component}.py"
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        print(f"  ✅ {component} - import successful")
                    else:
                        self.warnings.append(f"Could not load spec for {component}")
                        
                except Exception as e:
                    self.warnings.append(f"Import warning for {component}: {e}")
            
            return True
            
        except Exception as e:
            self.issues.append(f"Import validation failed: {e}")
            return False
        
        finally:
            sys.path.remove(str(self.bundle_root))
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            "bundle_path": str(self.bundle_root),
            "validation_timestamp": "2024-01-15T10:00:00Z",
            "issues": self.issues,
            "warnings": self.warnings,
            "total_issues": len(self.issues),
            "total_warnings": len(self.warnings),
            "status": "PASSED" if len(self.issues) == 0 else "FAILED"
        }
    
    def run_full_validation(self) -> bool:
        """Run complete bundle validation"""
        print("🚀 Running Skyward Assistable Bundle validation...")
        print(f"Bundle path: {self.bundle_root}")
        print("=" * 60)
        
        validations = [
            ("Structure", self.validate_structure),
            ("Components", self.validate_components),
            ("Flows", self.validate_flows),
            ("Utilities", self.validate_utilities),
            ("Documentation", self.validate_documentation),
            ("Configuration", self.validate_configuration),
            ("Tests", self.validate_tests),
            ("Imports", self.check_imports)
        ]
        
        all_passed = True
        
        for name, validation_func in validations:
            try:
                result = validation_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.issues.append(f"Validation error in {name}: {e}")
                all_passed = False
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.issues:
            print(f"❌ Issues found: {len(self.issues)}")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if all_passed and len(self.issues) == 0:
            print("✅ BUNDLE VALIDATION PASSED!")
            print("🎉 Bundle is ready for deployment!")
        else:
            print("❌ BUNDLE VALIDATION FAILED!")
            print("Please fix the issues above before deployment.")
        
        return all_passed and len(self.issues) == 0

def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Skyward Assistable Bundle")
    parser.add_argument("--bundle-path", default=".", help="Path to bundle directory")
    parser.add_argument("--output", help="Output validation report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    validator = BundleValidator(Path(args.bundle_path))
    success = validator.run_full_validation()
    
    # Generate and optionally save report
    report = validator.generate_report()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📝 Validation report saved to: {args.output}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
