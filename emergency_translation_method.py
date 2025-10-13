
    def emergency_translate_basic(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Emergency basic translation using dictionary lookup and patterns"""
        
        # Load simple translations
        simple_translations = {
            "en_to_hi": {
                "hello": "नमस्ते", "hello,": "नमस्ते,",
                "hello, how are you?": "नमस्ते, आप कैसे हैं?",
                "the weather is nice today": "आज मौसम अच्छा है",
                "good morning": "सुप्रभात", "thank you": "धन्यवाद"
            },
            "en_to_bn": {
                "hello": "হ্যালো", "hello,": "হ্যালো,",
                "hello, how are you?": "হ্যালো, আপনি কেমন আছেন?", 
                "the weather is nice today": "আজ আবহাওয়া ভাল",
                "good morning": "সুপ্রভাত", "thank you": "ধন্যবাদ"
            },
            "en_to_ta": {
                "hello": "வணக்கம்", "hello,": "வணக்கம்,",
                "hello, how are you?": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
                "the weather is nice today": "இன்று வானிலை நன்றாக இருக்கிறது",
                "good morning": "காலை வணக்கம்", "thank you": "நன்றி"
            },
            "en_to_te": {
                "hello": "హలో", "hello,": "హలో,",
                "hello, how are you?": "హలో, మీరు ఎలా ఉన్నారు?",
                "the weather is nice today": "ఈ రోజు వాతావరణం బాగుంది", 
                "good morning": "శుభోదయం", "thank you": "ధన్యవాదాలు"
            },
            "en_to_gu": {
                "hello": "હેલો", "hello,": "હેલો,",
                "hello, how are you?": "હેલો, તમે કેમ છો?",
                "the weather is nice today": "આજે હવામાન સારું છે",
                "good morning": "સુપ્રભાત", "thank you": "આભાર"
            },
            "en_to_mr": {
                "hello": "हॅलो", "hello,": "हॅलو,", 
                "hello, how are you?": "हॅलो, तुम्ही कसे आहात?",
                "the weather is nice today": "आज हवामान छान आहे",
                "good morning": "सुप्रभात", "thank you": "धन्यवाद"
            }
        }
        
        start_time = time.time()
        translation_key = f"{source_lang}_to_{target_lang}"
        text_lower = text.lower().strip()
        
        # Direct lookup
        if translation_key in simple_translations:
            translation_dict = simple_translations[translation_key]
            
            # Exact match
            if text_lower in translation_dict:
                translated_text = translation_dict[text_lower]
            else:
                # Partial matching for common patterns
                translated_text = text  # Fallback to original
                
                # Try to find partial matches
                for eng_phrase, translated_phrase in translation_dict.items():
                    if eng_phrase in text_lower:
                        translated_text = translated_phrase
                        break
        else:
            translated_text = text  # Return original if no mapping
        
        translation_time = time.time() - start_time
        
        return {
            "translated_text": translated_text,
            "model_used": "Emergency Dictionary",
            "translation_time": translation_time,
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence_score": 0.9 if translated_text != text else 0.1
        }
    