"""
TranslateCloud - DeepL Translation Engine
Professional translation using DeepL API
"""

import deepl
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# DeepL language code mapping (deprecated -> new format)
# Based on DeepL API v2 requirements
DEEPL_LANGUAGE_MAP = {
    # English variants
    'EN': 'EN-US',
    'EN-US': 'EN-US',
    'EN-GB': 'EN-GB',

    # Portuguese variants
    'PT': 'PT-BR',
    'PT-BR': 'PT-BR',
    'PT-PT': 'PT-PT',

    # Standard languages (no variants needed)
    'BG': 'BG',     # Bulgarian
    'CS': 'CS',     # Czech
    'DA': 'DA',     # Danish
    'DE': 'DE',     # German
    'EL': 'EL',     # Greek
    'ES': 'ES',     # Spanish
    'ET': 'ET',     # Estonian
    'FI': 'FI',     # Finnish
    'FR': 'FR',     # French
    'HU': 'HU',     # Hungarian
    'ID': 'ID',     # Indonesian
    'IT': 'IT',     # Italian
    'JA': 'JA',     # Japanese
    'KO': 'KO',     # Korean
    'LT': 'LT',     # Lithuanian
    'LV': 'LV',     # Latvian
    'NB': 'NB',     # Norwegian (Bokmål)
    'NL': 'NL',     # Dutch
    'PL': 'PL',     # Polish
    'RO': 'RO',     # Romanian
    'RU': 'RU',     # Russian
    'SK': 'SK',     # Slovak
    'SL': 'SL',     # Slovenian
    'SV': 'SV',     # Swedish
    'TR': 'TR',     # Turkish
    'UK': 'UK',     # Ukrainian
    'ZH': 'ZH',     # Chinese (simplified)
}


class DeepLTranslator:
    """
    DeepL API translator - Primary translation provider

    Features:
    - Professional quality translations
    - 500,000 characters/month free tier
    - Lightweight (API-based, no models to load)
    - Perfect for AWS Lambda deployment
    """

    def __init__(self, api_key: str):
        """
        Initialize DeepL translator

        Args:
            api_key: DeepL API key (get free at https://www.deepl.com/pro-api)
        """
        if not api_key:
            raise ValueError("DeepL API key is required")

        self.translator = deepl.Translator(api_key)
        logger.info("DeepL translator initialized successfully")

    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Translate text using DeepL API

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'es', or 'auto')
            target_lang: Target language code (e.g., 'en', 'es')

        Returns:
            Translated text or None if translation fails
        """
        try:
            # DeepL requires uppercase language codes
            source = source_lang.upper() if source_lang != 'auto' else None

            # Map target language to DeepL format using the mapping
            target_upper = target_lang.upper()
            target = DEEPL_LANGUAGE_MAP.get(target_upper, target_upper)

            if target not in DEEPL_LANGUAGE_MAP.values():
                logger.warning(f"Language code '{target_lang}' not in DeepL map, using as-is")

            logger.info(f"DeepL translating: {source or 'auto'} -> {target}")

            result = self.translator.translate_text(
                text,
                source_lang=source,
                target_lang=target
            )

            logger.info(f"DeepL translation successful ({len(text)} chars)")
            return result.text

        except deepl.DeepLException as e:
            logger.error(f"DeepL API error: {e}")
            return None
        except Exception as e:
            logger.error(f"DeepL translation failed: {e}")
            return None

    def get_usage(self) -> dict:
        """
        Get current DeepL API usage statistics

        Returns:
            dict with character_count and character_limit
        """
        try:
            usage = self.translator.get_usage()

            return {
                'character_count': usage.character.count,
                'character_limit': usage.character.limit,
                'percentage_used': (usage.character.count / usage.character.limit * 100) if usage.character.limit else 0
            }
        except Exception as e:
            logger.error(f"Failed to get DeepL usage: {e}")
            return {
                'character_count': 0,
                'character_limit': 0,
                'percentage_used': 0,
                'error': str(e)
            }

    def check_availability(self) -> bool:
        """
        Check if DeepL API is available and responding

        Returns:
            bool: True if API is available
        """
        try:
            self.translator.get_usage()
            return True
        except Exception as e:
            logger.error(f"DeepL availability check failed: {e}")
            return False
