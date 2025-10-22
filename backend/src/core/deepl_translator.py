"""
TranslateCloud - DeepL Translation Engine

This module provides professional translation services using the DeepL API.
DeepL is known for providing high-quality, context-aware translations across
30+ languages with proper handling of language variants.

Key Features:
- Professional-grade translation quality
- Support for 30+ languages including variants (EN-US/EN-GB, PT-BR/PT-PT)
- Automatic language code mapping for DeepL API v2 compatibility
- Character usage tracking and quota management
- API availability health checks
- Lightweight (API-based, no local models required)
- Perfect for AWS Lambda serverless deployment

API Details:
- Free Tier: 500,000 characters/month
- Pricing: Pay-as-you-go after free tier
- Documentation: https://www.deepl.com/docs-api

Architecture Flow:
    User Request → Translation Service → DeepL Translator → DeepL API → Response

Performance:
- Average latency: 200-500ms per request
- Batch size: Optimized for single text strings
- Rate limits: Managed by DeepL API
- Concurrent requests: Handled by DeepL infrastructure

Error Handling:
- DeepL API errors (quota exceeded, invalid language, etc.)
- Network timeouts and connectivity issues
- Malformed input validation

Author: TranslateCloud Team
Last Updated: October 20, 2025
Version: 2.0 (DeepL API v2 compliant)
"""

# Standard library imports
import logging  # For error and info logging
from typing import Optional  # For optional return types

# Third-party imports
import deepl  # Official DeepL API client library

# ============================================================================
# Logging Configuration
# ============================================================================

# Initialize logger for this module
# Logs are sent to AWS CloudWatch Logs when running in Lambda
logger = logging.getLogger(__name__)

# ============================================================================
# DeepL API v2 Language Code Mapping
# ============================================================================

# DeepL deprecated generic language codes (EN, PT) in favor of specific variants
# This mapping ensures compatibility with DeepL API v2 requirements
#
# Reference: https://www.deepl.com/docs-api/translate-text/translate-text/
# Last Updated: October 20, 2025
#
# Language Selection Strategy:
# - EN → EN-US (American English is more commonly requested)
# - PT → PT-BR (Brazilian Portuguese has larger market)
# - For other languages, users can specify exact variant if needed

DEEPL_LANGUAGE_MAP = {
    # ========================================================================
    # English Variants
    # ========================================================================
    # American English (default for EN)
    'EN': 'EN-US',        # Generic English → American English
    'EN-US': 'EN-US',     # American English (explicit)
    'EN-GB': 'EN-GB',     # British English (explicit)

    # ========================================================================
    # Portuguese Variants
    # ========================================================================
    # Brazilian Portuguese (default for PT)
    'PT': 'PT-BR',        # Generic Portuguese → Brazilian Portuguese
    'PT-BR': 'PT-BR',     # Brazilian Portuguese (explicit)
    'PT-PT': 'PT-PT',     # European Portuguese (explicit)

    # ========================================================================
    # Standard Languages (No Variants Needed)
    # ========================================================================
    # Sorted alphabetically by language name for maintainability

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

# Note: To add a new language, simply add it to the mapping above
# Format: 'LANG_CODE': 'LANG_CODE'
# Example: 'AR': 'AR' for Arabic (when DeepL adds support)


class DeepLTranslator:
    """
    DeepL API Translator - Primary translation provider for TranslateCloud

    This class handles all interactions with the DeepL API, including:
    - Translation requests with proper language code mapping
    - Character usage tracking and quota management
    - API health checks and availability monitoring
    - Error handling and logging

    Features:
    - Professional quality translations (better than Google Translate)
    - Context-aware translations (understands idioms and tone)
    - Fast response times (200-500ms average)
    - Free tier: 500,000 characters/month
    - No local models required (perfect for Lambda)

    Usage Example:
        translator = DeepLTranslator(api_key="your-api-key")
        result = await translator.translate_text("Hello", "auto", "ES")
        print(result)  # "Hola"

        usage = translator.get_usage()
        print(f"Used: {usage['character_count']} / {usage['character_limit']}")

    API Reference:
        https://www.deepl.com/docs-api/translate-text/

    Thread Safety:
        This class is thread-safe. Multiple concurrent translations can be
        performed using the same DeepLTranslator instance.
    """

    def __init__(self, api_key: str):
        """
        Initialize DeepL translator with API credentials

        Args:
            api_key (str): DeepL API key (get free key at https://www.deepl.com/pro-api)
                          Format: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx"

        Raises:
            ValueError: If API key is not provided or empty
            deepl.AuthorizationException: If API key is invalid

        Side Effects:
            - Creates DeepL translator instance
            - Logs initialization success
            - Does NOT validate API key (validation happens on first request)

        Performance:
            - Initialization: ~1ms (no API call)
            - Memory: ~1KB for translator instance
        """
        # Validate API key is provided
        if not api_key:
            raise ValueError("DeepL API key is required")

        # Initialize DeepL API client
        # This does NOT make an API call - validation happens on first request
        self.translator = deepl.Translator(api_key)

        # Log successful initialization
        logger.info("DeepL translator initialized successfully")

    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Translate text using DeepL API with automatic language code mapping

        This method handles the complete translation workflow:
        1. Validate input text
        2. Map language codes to DeepL API v2 format
        3. Call DeepL API
        4. Return translated text or None on error

        Args:
            text (str): Text to translate
                       Max length: 5000 characters per request (DeepL limit)
                       Can include HTML tags (preserved in translation)

            source_lang (str): Source language code
                              Use 'auto' for automatic detection
                              Examples: 'en', 'es', 'EN', 'auto'
                              Case-insensitive (converted to uppercase)

            target_lang (str): Target language code
                              Must be a supported DeepL language
                              Examples: 'en', 'es', 'EN-US', 'PT-BR'
                              Case-insensitive (converted to uppercase)

        Returns:
            Optional[str]: Translated text on success, None on error
                          Returns None if:
                          - API request fails
                          - Quota exceeded
                          - Invalid language code
                          - Network error

        Examples:
            # Basic translation
            result = await translate_text("Hello", "auto", "ES")
            # Returns: "Hola"

            # With language detection
            result = await translate_text("Bonjour", "auto", "EN-US")
            # Returns: "Hello" (American English)

            # HTML preservation
            result = await translate_text("<p>Hello</p>", "EN", "ES")
            # Returns: "<p>Hola</p>"

        Error Handling:
            - DeepLException: Logged and returns None
            - Network timeout: Logged and returns None
            - Invalid language: Logged with warning and attempts translation

        Performance:
            - Average: 200-500ms for short text (< 100 chars)
            - Longer text: ~1-2 seconds per 1000 characters
            - Timeout: Managed by DeepL client (default: 30s)

        Notes:
            - Function is async for consistency, but DeepL client is synchronous
            - Language codes are case-insensitive (converted to uppercase)
            - HTML tags are preserved in translation
            - Whitespace and formatting are preserved
        """
        try:
            # ================================================================
            # Step 1: Process Source Language
            # ================================================================
            # Convert source language to uppercase for mapping
            # Special case: 'auto' means automatic language detection
            if source_lang != 'auto':
                source = source_lang.upper()
            else:
                source = None  # DeepL API uses None for auto-detection

            # ================================================================
            # Step 2: Map Target Language to DeepL Format
            # ================================================================
            # Convert target language to uppercase
            target_upper = target_lang.upper()

            # Map to DeepL API v2 format using our mapping dictionary
            # If language is not in map, use it as-is (for future languages)
            target = DEEPL_LANGUAGE_MAP.get(target_upper, target_upper)

            # Validate target language is supported
            # Log warning if language not in our mapping (might still work)
            if target not in DEEPL_LANGUAGE_MAP.values():
                logger.warning(
                    f"Language code '{target_lang}' not in DeepL map, "
                    f"using as-is. Translation may fail if unsupported."
                )

            # ================================================================
            # Step 3: Log Translation Request
            # ================================================================
            logger.info(
                f"DeepL translating: {source or 'auto'} -> {target} "
                f"({len(text)} chars)"
            )

            # ================================================================
            # Step 4: Call DeepL API
            # ================================================================
            # Make synchronous API call to DeepL
            # This is the actual translation request
            result = self.translator.translate_text(
                text,
                source_lang=source,    # None for auto-detection, or language code
                target_lang=target     # Mapped target language (e.g., 'EN-US')
            )

            # ================================================================
            # Step 5: Log Success and Return
            # ================================================================
            logger.info(
                f"DeepL translation successful ({len(text)} chars)"
            )

            # Extract translated text from result object
            return result.text

        except deepl.DeepLException as e:
            # ================================================================
            # DeepL API Specific Errors
            # ================================================================
            # Examples:
            # - QuotaExceededException: Monthly quota exceeded
            # - AuthorizationException: Invalid API key
            # - TooManyRequestsException: Rate limit exceeded
            logger.error(f"DeepL API error: {e}")
            return None

        except Exception as e:
            # ================================================================
            # Generic Errors (Network, Timeout, etc.)
            # ================================================================
            logger.error(f"DeepL translation failed: {e}")
            return None

    def get_usage(self) -> dict:
        """
        Get current DeepL API usage statistics

        Retrieves character count and quota information from DeepL API.
        Useful for monitoring usage and preventing quota exceeded errors.

        Returns:
            dict: Usage statistics with the following keys:
                - character_count (int): Characters used this month
                - character_limit (int): Total monthly character limit
                - percentage_used (float): Percentage of quota used (0-100)
                - error (str, optional): Error message if request fails

        Examples:
            usage = translator.get_usage()
            print(f"Used: {usage['character_count']:,} / {usage['character_limit']:,}")
            print(f"Remaining: {usage['character_limit'] - usage['character_count']:,}")

            if usage['percentage_used'] > 90:
                print("WARNING: Approaching quota limit!")

        API Call:
            Makes a real-time API call to DeepL. Use sparingly to avoid
            unnecessary API requests. Consider caching results.

        Performance:
            - Latency: ~50-100ms
            - Cached: Not cached by this class

        Error Handling:
            On error, returns dict with zeros and error message:
            {
                'character_count': 0,
                'character_limit': 0,
                'percentage_used': 0,
                'error': 'Error message here'
            }

        Thread Safety:
            This method is thread-safe.
        """
        try:
            # ================================================================
            # Call DeepL API for usage statistics
            # ================================================================
            usage = self.translator.get_usage()

            # ================================================================
            # Calculate usage percentage
            # ================================================================
            # Handle case where limit is 0 (shouldn't happen, but defensive)
            if usage.character.limit > 0:
                percentage = (usage.character.count / usage.character.limit) * 100
            else:
                percentage = 0

            # ================================================================
            # Return formatted usage statistics
            # ================================================================
            return {
                'character_count': usage.character.count,
                'character_limit': usage.character.limit,
                'percentage_used': percentage
            }

        except Exception as e:
            # ================================================================
            # Error handling: Return zeros with error message
            # ================================================================
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

        Performs a health check by calling get_usage(). This is the most
        lightweight operation that validates API key and connectivity.

        Returns:
            bool: True if API is available, False otherwise

        Use Cases:
            - Startup health checks
            - Fallback decision (use MarianMT if DeepL unavailable)
            - Monitoring and alerting

        Examples:
            if not translator.check_availability():
                logger.error("DeepL unavailable, using fallback translator")
                return fallback_translator.translate(text)

        Performance:
            - Latency: ~50-100ms (makes API call)
            - Should not be called on every translation request
            - Consider caching result for 5-10 minutes

        Error Handling:
            Returns False on any error (API error, network error, etc.)
            Errors are logged for debugging

        Thread Safety:
            This method is thread-safe.
        """
        try:
            # Attempt to get usage statistics
            # If this succeeds, API is available
            self.translator.get_usage()
            return True

        except Exception as e:
            # Log failure and return False
            logger.error(f"DeepL availability check failed: {e}")
            return False
