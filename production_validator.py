
"""
Production Configuration Validator
Ensures all required components are properly configured
"""
import os
import sys
import torch
from pathlib import Path
from typing import Dict, List, Tuple

class ProductionConfigValidator:
    def __init__(self):
        self.validation_results = []
        self.critical_errors = []
        self.warnings = []
    
    def validate_gpu_setup(self) -> bool:
        """Validate GPU configuration"""
        try:
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                current_device = torch.cuda.current_device()
                gpu_name = torch.cuda.get_device_name(current_device)
                
                self.validation_results.append(f"✅ GPU Available: {gpu_name}")
                self.validation_results.append(f"✅ GPU Count: {gpu_count}")
                return True
            else:
                self.warnings.append("⚠️ No GPU available, using CPU only")
                return True
                
        except Exception as e:
            self.critical_errors.append(f"❌ GPU validation failed: {e}")
            return False
    
    def validate_models(self) -> bool:
        """Validate model availability"""
        model_paths = [
            "saved_model/IndicTrans2-en-indic-1B",
            "saved_model/IndicTrans2-indic-en-1B",
            "saved_model/whisper-large-v3"
        ]
        
        all_models_exist = True
        for model_path in model_paths:
            full_path = Path(model_path)
            if full_path.exists():
                self.validation_results.append(f"✅ Model found: {model_path}")
            else:
                self.critical_errors.append(f"❌ Model missing: {model_path}")
                all_models_exist = False
        
        return all_models_exist
    
    def validate_dependencies(self) -> bool:
        """Validate Python dependencies"""
        required_packages = [
            "torch", "transformers", "whisper", "TTS", 
            "fastapi", "sqlalchemy", "psycopg2", "python-docx"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                self.validation_results.append(f"✅ Package available: {package}")
            except ImportError:
                missing_packages.append(package)
                self.critical_errors.append(f"❌ Package missing: {package}")
        
        return len(missing_packages) == 0
    
    def validate_storage_setup(self) -> bool:
        """Validate storage directories"""
        required_dirs = [
            "storage/uploads", 
            "storage/outputs",
            "data/vocabs",
            "logs"
        ]
        
        all_dirs_exist = True
        for dir_path in required_dirs:
            full_path = Path(dir_path)
            if full_path.exists():
                self.validation_results.append(f"✅ Directory exists: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                self.validation_results.append(f"✅ Directory created: {dir_path}")
        
        return all_dirs_exist
    
    def run_full_validation(self) -> Dict[str, any]:
        """Run complete production validation"""
        print("🔍 Running Production System Validation...")
        
        results = {
            "gpu_ok": self.validate_gpu_setup(),
            "models_ok": self.validate_models(),
            "dependencies_ok": self.validate_dependencies(),
            "storage_ok": self.validate_storage_setup()
        }
        
        results["overall_status"] = all(results.values())
        results["validation_results"] = self.validation_results
        results["critical_errors"] = self.critical_errors
        results["warnings"] = self.warnings
        
        return results

if __name__ == "__main__":
    validator = ProductionConfigValidator()
    results = validator.run_full_validation()
    
    print("\n" + "="*60)
    print("PRODUCTION SYSTEM VALIDATION REPORT")
    print("="*60)
    
    for result in results["validation_results"]:
        print(result)
    
    if results["warnings"]:
        print("\nWarnings:")
        for warning in results["warnings"]:
            print(warning)
    
    if results["critical_errors"]:
        print("\nCritical Errors:")
        for error in results["critical_errors"]:
            print(error)
    
    if results["overall_status"]:
        print("\n🎉 PRODUCTION SYSTEM READY!")
    else:
        print("\n❌ PRODUCTION SYSTEM NOT READY - Fix critical errors first")
