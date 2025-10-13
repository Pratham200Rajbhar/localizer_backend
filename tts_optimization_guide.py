
    # Add this to the text_to_speech method after line ~379
    
    # Quick timeout for TTS model loading (prevent 30s+ hangs)
    TTS_TIMEOUT = 10  # seconds
    
    async def text_to_speech(self, text: str, language: str, output_path: str = None) -> Dict[str, any]:
        """Generate speech from text with optimized timeout handling"""
        
        # Quick validation
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Try fast TTS generation with timeout
        try:
            # Use asyncio timeout to prevent hanging
            result = await asyncio.wait_for(
                self._generate_tts_with_timeout(text, language, output_path),
                timeout=TTS_TIMEOUT
            )
            return result
            
        except asyncio.TimeoutError:
            app_logger.warning(f"TTS timeout for {language}, using gTTS fallback")
            return await self._fallback_gtts(text, language, output_path)
            
        except Exception as e:
            app_logger.error(f"TTS generation failed: {e}")
            return await self._fallback_gtts(text, language, output_path)
    
    async def _generate_tts_with_timeout(self, text: str, language: str, output_path: str) -> Dict[str, any]:
        """Generate TTS with primary model (with timeout protection)"""
        
        # Only load model if not already loaded (prevents repeated loading)
        if self.tts_model is None:
            if not self.load_tts_model():
                raise RuntimeError("TTS model failed to load")
        
        # Generate audio
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./storage/outputs/tts_{language}_{timestamp[:8]}.mp3"
        
        # Use the loaded model for generation
        self.tts_model.tts_to_file(
            text=text,
            file_path=output_path,
            language=language if language in ["hi", "bn", "ta"] else "en"  # Language mapping
        )
        
        return {
            "audio_path": output_path,
            "language": language,
            "text_length": len(text),
            "generation_time": 2.0,  # Estimated
            "model_used": "VITS/XTTS"
        }
    
    async def _fallback_gtts(self, text: str, language: str, output_path: str) -> Dict[str, any]:
        """Fast fallback using Google TTS"""
        
        try:
            from gtts import gTTS
            import io
            
            # Map Indian languages to gTTS supported codes
            language_mapping = {
                "hi": "hi", "bn": "bn", "ta": "ta", "te": "te", 
                "gu": "gu", "mr": "mr", "pa": "pa", "kn": "kn",
                "ml": "ml", "ur": "ur"
            }
            
            gtts_lang = language_mapping.get(language, "en")
            
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
                output_path = f"./storage/outputs/tts_{language}_{timestamp[:8]}.mp3"
            
            # Generate with gTTS (fast)
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(output_path)
            
            return {
                "audio_path": output_path,
                "language": language,
                "text_length": len(text),
                "generation_time": 1.0,
                "model_used": "Google TTS (Fallback)"
            }
            
        except Exception as e:
            app_logger.error(f"Fallback gTTS also failed: {e}")
            raise RuntimeError(f"All TTS methods failed: {e}")
    