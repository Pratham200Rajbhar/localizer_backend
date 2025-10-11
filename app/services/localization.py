"""
Cultural and Domain Localization Service
"""
import json
from typing import Dict, Optional
from pathlib import Path
from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger

settings = get_settings()


class LocalizationEngine:
    """Cultural and domain-specific localization"""
    
    def __init__(self):
        self.vocab_cache = {}
        self.cultural_rules = {}
        app_logger.info("Localization Engine initialized")
    
    def load_domain_vocabulary(self, domain: str) -> Dict:
        """
        Load domain-specific vocabulary
        
        Args:
            domain: Domain name (healthcare, construction, education, etc.)
        
        Returns:
            Domain vocabulary dictionary
        """
        if domain in self.vocab_cache:
            return self.vocab_cache[domain]
        
        vocab_path = Path(f"/app/data/vocabs/{domain}.json")
        
        if not vocab_path.exists():
            app_logger.warning(f"Domain vocabulary not found: {domain}")
            return {}
        
        try:
            with open(vocab_path, "r", encoding="utf-8") as f:
                vocab = json.load(f)
            
            self.vocab_cache[domain] = vocab
            app_logger.info(f"Loaded domain vocabulary: {domain}")
            return vocab
        
        except Exception as e:
            app_logger.error(f"Error loading vocabulary for {domain}: {e}")
            return {}
    
    def apply_domain_terms(
        self,
        text: str,
        domain: str,
        target_language: str
    ) -> str:
        """
        Apply domain-specific terminology
        
        Args:
            text: Translated text
            domain: Domain name
            target_language: Target language code
        
        Returns:
            Text with domain-specific terms applied
        """
        vocab = self.load_domain_vocabulary(domain)
        
        if not vocab or target_language not in vocab:
            return text
        
        terms = vocab[target_language]
        
        # Replace generic terms with domain-specific terms
        modified_text = text
        for generic, specific in terms.items():
            # Simple replacement (in production, use more sophisticated NLP)
            modified_text = modified_text.replace(generic, specific)
        
        return modified_text
    
    def apply_cultural_adaptation(
        self,
        text: str,
        target_language: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Apply cultural adaptations
        
        Args:
            text: Text to adapt
            target_language: Target language code
            context: Optional context information
        
        Returns:
            Culturally adapted text
        """
        # Cultural adaptation rules
        # In production, this would be much more sophisticated
        
        cultural_mappings = {
            "hi": {
                # Hindi cultural adaptations
                "hello": "नमस्ते",
                "thank you": "धन्यवाद",
                "please": "कृपया"
            },
            "ta": {
                # Tamil cultural adaptations
                "hello": "வணக்கம்",
                "thank you": "நன்றி"
            },
            "bn": {
                # Bengali cultural adaptations
                "hello": "নমস্কার",
                "thank you": "ধন্যবাদ"
            }
        }
        
        if target_language not in cultural_mappings:
            return text
        
        adapted_text = text
        for english, local in cultural_mappings[target_language].items():
            adapted_text = adapted_text.replace(english, local)
        
        return adapted_text
    
    def localize(
        self,
        text: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Complete localization pipeline
        
        Args:
            text: Text to localize
            target_language: Target language code
            domain: Optional domain
            context: Optional context
        
        Returns:
            Dict with localized text and metadata
        """
        localized_text = text
        
        # Apply domain-specific terms
        if domain:
            localized_text = self.apply_domain_terms(
                localized_text,
                domain,
                target_language
            )
        
        # Apply cultural adaptations
        localized_text = self.apply_cultural_adaptation(
            localized_text,
            target_language,
            context
        )
        
        app_logger.info(
            f"Localization applied: language={target_language}, domain={domain}"
        )
        
        return {
            "localized_text": localized_text,
            "original_text": text,
            "language": target_language,
            "domain": domain,
            "adaptations_applied": True
        }
    
    def create_domain_vocabulary(
        self,
        domain: str,
        vocabulary: Dict
    ) -> bool:
        """
        Create new domain vocabulary file
        
        Args:
            domain: Domain name
            vocabulary: Vocabulary dictionary
        
        Returns:
            Success status
        """
        vocab_dir = Path("/app/data/vocabs")
        vocab_dir.mkdir(parents=True, exist_ok=True)
        
        vocab_path = vocab_dir / f"{domain}.json"
        
        try:
            with open(vocab_path, "w", encoding="utf-8") as f:
                json.dump(vocabulary, f, indent=2, ensure_ascii=False)
            
            app_logger.info(f"Created domain vocabulary: {domain}")
            return True
        
        except Exception as e:
            app_logger.error(f"Error creating vocabulary for {domain}: {e}")
            return False


# Global localization engine instance
localization_engine = LocalizationEngine()

