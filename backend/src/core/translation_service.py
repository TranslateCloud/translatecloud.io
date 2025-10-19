"""
TranslateCloud - Translation Service Orchestrator
Manages DeepL (primary) and MarianMT (fallback) translators
"""

import logging
from typing import Optional, Dict, Any
from src.core.deepl_translator import DeepLTranslator

logger = logging.getLogger(__name__)

# Try to import MarianMT (optional, requires PyTorch)
try:
    from src.core.marian_translator import MarianTranslator
    MARIAN_AVAILABLE = True
except ImportError:
    logger.warning("MarianMT not available (PyTorch not installed). Only DeepL will be used.")
    MarianTranslator = None
    MARIAN_AVAILABLE = False


class TranslationService:
    """
    Translation orchestration service with automatic fallback

    Priority order:
    1. DeepL API (if API key provided) - Professional quality, fast, lightweight
    2. MarianMT (fallback) - Local models, slower, requires more resources

    Usage:
        service = TranslationService(deepl_api_key="your_key")
        result = await service.translate("Hello", "en", "es")
        # result = {'text': 'Hola', 'provider': 'deepl', 'success': True}
    """

    def __init__(self, deepl_api_key: Optional[str] = None):
        """
        Initialize translation service

        Args:
            deepl_api_key: DeepL API key (optional, enables DeepL translator)
        """
        # Initialize DeepL if API key provided
        self.deepl: Optional[DeepLTranslator] = None
        if deepl_api_key:
            try:
                self.deepl = DeepLTranslator(deepl_api_key)
                logger.info("DeepL translator enabled (primary)")
            except Exception as e:
                logger.warning(f"DeepL initialization failed: {e}")
                self.deepl = None

        # Initialize MarianMT as fallback (if available)
        self.marian = None
        if MARIAN_AVAILABLE and MarianTranslator:
            try:
                self.marian = MarianTranslator()
                logger.info("MarianMT translator enabled (fallback)")
            except Exception as e:
                logger.error(f"MarianMT initialization failed: {e}")
                self.marian = None
        else:
            logger.info("MarianMT not available - DeepL will be the only translator")

        if not self.deepl and not self.marian:
            logger.warning("No translators available - DeepL API key required for functionality")

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Translate text using best available translator

        Process:
        1. Try DeepL (if available)
        2. Fall back to MarianMT if DeepL fails
        3. Return error if both fail

        Args:
            text: Text to translate
            source_lang: Source language code ('en', 'es', 'auto', etc.)
            target_lang: Target language code ('en', 'es', etc.)

        Returns:
            dict: {
                'text': translated_text or None,
                'provider': 'deepl' | 'marian' | None,
                'success': True | False,
                'error': error_message (only if success=False)
            }
        """
        if not text or not text.strip():
            return {
                'text': text,
                'provider': None,
                'success': False,
                'error': 'Empty text provided'
            }

        # STRATEGY 1: Try DeepL (primary)
        if self.deepl:
            logger.info(f"Attempting DeepL translation: {source_lang} -> {target_lang}")
            result = await self.deepl.translate_text(text, source_lang, target_lang)

            if result:
                logger.info(f"✓ DeepL translation successful ({len(result)} chars)")
                return {
                    'text': result,
                    'provider': 'deepl',
                    'success': True
                }
            else:
                logger.warning("✗ DeepL failed, falling back to MarianMT")

        # STRATEGY 2: Fall back to MarianMT
        if self.marian:
            logger.info(f"Attempting MarianMT translation: {source_lang} -> {target_lang}")
            try:
                result = self.marian.translate(text, source_lang, target_lang)

                if result:
                    logger.info(f"✓ MarianMT translation successful (fallback)")
                    return {
                        'text': result,
                        'provider': 'marian',
                        'success': True
                    }
                else:
                    logger.error("✗ MarianMT returned None")

            except Exception as e:
                logger.error(f"✗ MarianMT exception: {e}")

        # STRATEGY 3: Both failed
        error_msg = "All translation providers failed"
        logger.error(f"✗ {error_msg}")

        return {
            'text': None,
            'provider': None,
            'success': False,
            'error': error_msg
        }

    async def translate_batch(
        self,
        texts: list[str],
        source_lang: str,
        target_lang: str
    ) -> list[Dict[str, Any]]:
        """
        Translate multiple texts

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            list: List of translation results (same format as translate())
        """
        results = []

        for text in texts:
            result = await self.translate(text, source_lang, target_lang)
            results.append(result)

        return results

    def get_status(self) -> Dict[str, Any]:
        """
        Get service status and translator availability

        Returns:
            dict: {
                'deepl_available': bool,
                'marian_available': bool,
                'primary_provider': 'deepl' | 'marian' | None
            }
        """
        deepl_available = self.deepl is not None and (
            self.deepl.check_availability() if hasattr(self.deepl, 'check_availability') else True
        )

        marian_available = self.marian is not None

        primary = None
        if deepl_available:
            primary = 'deepl'
        elif marian_available:
            primary = 'marian'

        return {
            'deepl_available': deepl_available,
            'marian_available': marian_available,
            'primary_provider': primary
        }

    def get_deepl_usage(self) -> Optional[Dict[str, Any]]:
        """
        Get DeepL API usage statistics

        Returns:
            dict or None: Usage stats if DeepL is available
        """
        if self.deepl:
            return self.deepl.get_usage()
        return None
