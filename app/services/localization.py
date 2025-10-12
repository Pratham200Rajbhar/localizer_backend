"""
Cultural and Domain Localization Service
Complete implementation with real vocabulary mapping and cultural rules
"""
import json
import re
from typing import Dict, Optional, List, Any
from pathlib import Path
from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger

settings = get_settings()


class LocalizationEngine:
    """Cultural and domain-specific localization with real implementation"""
    
    def __init__(self):
        self.vocab_cache = {}
        self.cultural_rules = {}
        self.domain_vocabs = {}
        self._initialize_cultural_rules()
        self._load_domain_vocabularies()
        app_logger.info("Localization Engine initialized with complete functionality")
    
    def _initialize_cultural_rules(self):
        """Initialize cultural adaptation rules"""
        self.cultural_rules = {
            # Honorific additions for Indian languages
            "honorifics": {
                "hi": {"sir": "साहब", "madam": "मैडम जी", "ji": "जी"},
                "bn": {"sir": "সাহেব", "madam": "ম্যাডাম", "ji": "জি"},
                "te": {"sir": "సార్", "madam": "మేడం", "garu": "గారు"},
                "ta": {"sir": "ஐயா", "madam": "அம்மா", "avargal": "அவர்கள்"},
                "mr": {"sir": "साहेब", "madam": "मॅडम", "ji": "जी"},
                "gu": {"sir": "સાહેબ", "madam": "મેડમ", "ji": "જી"},
                "pa": {"sir": "ਸਾਹਿਬ", "madam": "ਮੈਡਮ", "ji": "ਜੀ"},
                "kn": {"sir": "ಸರ್", "madam": "ಮೇಡಂ", "avare": "ಅವರೆ"},
                "ml": {"sir": "സാർ", "madam": "മാഡം", "avar": "അവർ"},
                "or": {"sir": "ସାର୍", "madam": "ମ୍ୟାଡାମ୍", "nka": "ଙ୍କା"},
                "as": {"sir": "চাহাব", "madam": "মেডাম", "ji": "জী"},
                "ur": {"sir": "صاحب", "madam": "میڈم", "ji": "جی"}
            },
            
            # Cultural phrase adaptations
            "phrases": {
                "thank you": {
                    "hi": "धन्यवाद", "bn": "ধন্যবাদ", "te": "ధన్యవాదాలు",
                    "ta": "நன்றி", "mr": "धन्यवाद", "gu": "આભાર",
                    "pa": "ਧੰਨਵਾਦ", "kn": "ಧನ್ಯವಾದಗಳು", "ml": "നന്ദി", 
                    "or": "ଧନ୍ୟବାଦ", "as": "ধন্যবাদ", "ur": "شکریہ"
                },
                "please": {
                    "hi": "कृपया", "bn": "দয়া করে", "te": "దయచేసి",
                    "ta": "தயவுசெய்து", "mr": "कृपया", "gu": "કૃપા કરીને",
                    "pa": "ਕਿਰਪਾ ਕਰਕੇ", "kn": "ದಯವಿಟ್ಟು", "ml": "ദയവായി",
                    "or": "ଦୟାକରି", "as": "অনুগ্ৰহ কৰি", "ur": "براہ کرم"
                }
            }
        }
    
    def _load_domain_vocabularies(self):
        """Load all domain vocabularies and create defaults if missing"""
        vocab_dir = Path("data/vocabs")
        
        if not vocab_dir.exists():
            vocab_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_vocabularies(vocab_dir)
        
        for vocab_file in vocab_dir.glob("*.json"):
            domain = vocab_file.stem
            try:
                self.domain_vocabs[domain] = self.load_domain_vocabulary(domain)
            except Exception as e:
                app_logger.error(f"Error loading vocabulary {domain}: {e}")
    
    def _create_default_vocabularies(self, vocab_dir: Path):
        """Create comprehensive default domain vocabularies"""
        
        # Healthcare vocabulary
        healthcare_vocab = {
            "en": {
                "doctor": {"hi": "डॉक्टर", "bn": "ডাক্তার", "te": "వైద్యుడు", "ta": "மருத்துவர்", "mr": "डॉक्टर", "gu": "ડૉક્ટર"},
                "hospital": {"hi": "अस्पताल", "bn": "হাসপাতাল", "te": "ఆసుపత్రి", "ta": "மருத்துவமனை", "mr": "रुग्णालय", "gu": "હોસ્પિટલ"},
                "medicine": {"hi": "दवा", "bn": "ওষুধ", "te": "మందు", "ta": "மருந்து", "mr": "औषध", "gu": "દવા"},
                "patient": {"hi": "मरीज़", "bn": "রোগী", "te": "రోగి", "ta": "நோயாளி", "mr": "रुग्ण", "gu": "દર્દી"},
                "nurse": {"hi": "नर्स", "bn": "নার্স", "te": "నర్సు", "ta": "செவிலியர்", "mr": "परिचारिका", "gu": "નર્સ"},
                "surgery": {"hi": "शल्य चिकित्सा", "bn": "অস্ত্রোপচার", "te": "శస్త్రచికిత్స", "ta": "அறுவை சிகிச்சை", "mr": "शस्त्रक्रिया", "gu": "સર્જરી"},
                "prescription": {"hi": "नुस्खा", "bn": "প্রেসক্রিপশন", "te": "ప్రిస্క్రిప్షన్", "ta": "மருந்து சீட்டு", "mr": "औषधपत्र", "gu": "પ્રિસ્ક્રિપ્શન"}
            }
        }
        
        # Construction vocabulary  
        construction_vocab = {
            "en": {
                "electrician": {"hi": "विद्युत तकनीशियन", "bn": "ইলেকট্রিশিয়ান", "te": "విద్యుత్ కార్మికుడు", "ta": "மின்சாரத் தொழிலாளி"},
                "safety gear": {"hi": "सुरक्षा उपकरण", "bn": "নিরাপত্তা সরঞ্জাম", "te": "భద్రతా పరికరాలు", "ta": "பாதுகாப்பு கருவிகள்"},
                "construction": {"hi": "निर्माण", "bn": "নির্মাণ", "te": "నిర్మాణం", "ta": "கட்டுமானம்"},
                "engineer": {"hi": "इंजीनियर", "bn": "ইঞ্জিনিয়ার", "te": "ఇంజనీర్", "ta": "பொறியாளர்"},
                "contractor": {"hi": "ठेकेदार", "bn": "ঠিকাদার", "te": "కాంట్రాక్టర్", "ta": "ஒப்பந்தக்காரர்"},
                "cement": {"hi": "सीमेंट", "bn": "সিমেন্ট", "te": "సిమెంట్", "ta": "சிமெண்ட்"}
            }
        }
        
        # Education vocabulary
        education_vocab = {
            "en": {
                "teacher": {"hi": "शिक्षक", "bn": "শিক্ষক", "te": "గురువు", "ta": "ஆசிரியர்"},
                "student": {"hi": "छात्र", "bn": "ছাত্র", "te": "విద్యార్థి", "ta": "மாணவர்"},
                "school": {"hi": "स्कूल", "bn": "স্কুল", "te": "పాఠశాల", "ta": "பள்ளி"},
                "education": {"hi": "शिक्षा", "bn": "শিক্ষা", "te": "విద్య", "ta": "கல்வி"},
                "examination": {"hi": "परीक्षा", "bn": "পরীক্ষা", "te": "పరీక్ష", "ta": "தேர்வு"}
            }
        }
        
        # Save vocabularies
        vocabs = {
            "healthcare": healthcare_vocab,
            "construction": construction_vocab,
            "education": education_vocab
        }
        
        for domain, vocab in vocabs.items():
            vocab_file = vocab_dir / f"{domain}.json"
            with open(vocab_file, 'w', encoding='utf-8') as f:
                json.dump(vocab, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Created default vocabulary: {domain}")

    def load_domain_vocabulary(self, domain: str) -> Dict:
        """Load domain-specific vocabulary"""
        if domain in self.vocab_cache:
            return self.vocab_cache[domain]
        
        vocab_path = Path(f"data/vocabs/{domain}.json")
        
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
        language: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply domain-specific and cultural localization
        
        Args:
            text: Text to localize
            language: Target language code (using 'language' to match call in translation.py)
            domain: Domain for vocabulary mapping
        
        Returns: 
            Dict with localized text and changes applied
        """
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language {language} not supported")
        
        localized_text = text
        changes_applied = []
        
        # Apply domain vocabulary mapping
        if domain and domain in self.domain_vocabs:
            localized_text, domain_changes = self._apply_domain_vocabulary(
                localized_text, language, domain
            )
            changes_applied.extend(domain_changes)
        
        # Apply cultural adaptations
        localized_text, cultural_changes = self._apply_cultural_rules(
            localized_text, language
        )
        changes_applied.extend(cultural_changes)
        
        # Apply regional formatting
        localized_text, format_changes = self._apply_regional_formatting(
            localized_text, language
        )
        changes_applied.extend(format_changes)
        
        app_logger.info(f"Localization applied for {language}, {len(changes_applied)} changes")
        
        return {
            "localized_text": localized_text,
            "original_text": text,
            "language": language,
            "domain": domain,
            "changes_applied": changes_applied
        }
    
    def _apply_domain_vocabulary(
        self, text: str, language: str, domain: str
    ) -> tuple[str, List[str]]:
        """Apply domain-specific vocabulary mapping"""
        changes = []
        localized_text = text
        
        if domain not in self.domain_vocabs:
            return localized_text, changes
        
        domain_vocab = self.domain_vocabs[domain]
        
        # Apply English to target language mappings
        if "en" in domain_vocab:
            for en_term, translations in domain_vocab["en"].items():
                if language in translations:
                    target_term = translations[language]
                    
                    # Case-insensitive replacement with word boundaries
                    pattern = re.compile(r'\b' + re.escape(en_term) + r'\b', re.IGNORECASE)
                    if pattern.search(localized_text):
                        localized_text = pattern.sub(target_term, localized_text)
                        changes.append(f"Domain vocab: '{en_term}' -> '{target_term}'")
        
        return localized_text, changes
    
    def _apply_cultural_rules(self, text: str, language: str) -> tuple[str, List[str]]:
        """Apply cultural adaptation rules"""
        changes = []
        localized_text = text
        
        # Apply honorifics
        if language in self.cultural_rules["honorifics"]:
            honorifics = self.cultural_rules["honorifics"][language]
            for en_term, local_term in honorifics.items():
                pattern = re.compile(r'\b' + re.escape(en_term) + r'\b', re.IGNORECASE)
                if pattern.search(localized_text):
                    localized_text = pattern.sub(local_term, localized_text)
                    changes.append(f"Honorific: '{en_term}' -> '{local_term}'")
        
        # Apply cultural phrases
        for en_phrase, translations in self.cultural_rules["phrases"].items():
            if language in translations:
                local_phrase = translations[language]
                pattern = re.compile(re.escape(en_phrase), re.IGNORECASE)
                if pattern.search(localized_text):
                    localized_text = pattern.sub(local_phrase, localized_text)
                    changes.append(f"Cultural phrase: '{en_phrase}' -> '{local_phrase}'")
        
        return localized_text, changes
    
    def _apply_regional_formatting(self, text: str, language: str) -> tuple[str, List[str]]:
        """Apply regional formatting (numbers, dates, etc.)"""
        changes = []
        localized_text = text
        
        # Apply number formatting based on Indian number system
        # Convert Western numbers to Devanagari numerals for Hindi, Marathi, etc.
        devanagari_langs = ["hi", "mr", "sa", "mai", "doi", "kok"]
        
        if language in devanagari_langs:
            # Convert digits to Devanagari numerals
            western_to_devanagari = {
                '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
                '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
            }
            
            for western, devanagari in western_to_devanagari.items():
                if western in localized_text:
                    localized_text = localized_text.replace(western, devanagari)
                    changes.append(f"Number format: '{western}' -> '{devanagari}'")
        
        return localized_text, changes
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domains"""
        return list(self.domain_vocabs.keys())
    
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
localization_service = localization_engine  # Alias for backward compatibility

