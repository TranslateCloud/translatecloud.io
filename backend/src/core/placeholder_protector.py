"""
PlaceholderProtector - Preserves code placeholders during translation
Prevents translation of variables like %s, {name}, {{count}}, etc.
"""

import re
from typing import Dict, Tuple, List
import uuid


class PlaceholderProtector:
    """
    Protects code placeholders from being translated

    Supported patterns:
    - C-style: %s, %d, %i, %f, %@
    - Positional: %1$s, %2$d, {0}, {1}
    - Named: {name}, {count}, {{variable}}
    - Template strings: ${variable}
    - React/Vue: {t('key')}
    """

    # Pattern definitions with priority (higher priority = replace first)
    PATTERNS = [
        # React/Vue interpolation with functions
        (r'\{[a-zA-Z_$][\w$]*\([^)]*\)\}', 'REACT_FUNC', 10),

        # Template literals ${variable}
        (r'\$\{[^}]+\}', 'TEMPLATE_LITERAL', 9),

        # Double braces {{variable}} (Vue, Handlebars)
        (r'\{\{[^}]+\}\}', 'DOUBLE_BRACE', 8),

        # Positional with dollar sign: %1$s, %2$d
        (r'%\d+\$[sdifDFuUxXoOeEgGcpn]', 'POSITIONAL_FORMAT', 7),

        # C-style format specifiers with precision: %.2f, %10s
        (r'%[+-]?\d*\.?\d*[sdifDFuUxXoOeEgGcpn@]', 'C_FORMAT', 6),

        # Single braces with numbers {0}, {1}, {2}
        (r'\{\d+\}', 'POSITIONAL_BRACE', 5),

        # Single braces with names {name}, {count}
        (r'\{[a-zA-Z_]\w*\}', 'NAMED_BRACE', 4),

        # XML/HTML entities: &nbsp;, &#160;, &#x00A0;
        (r'&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;', 'HTML_ENTITY', 3),

        # Simple percent format: %s, %d, %f, %@
        (r'%[sdif@]', 'SIMPLE_FORMAT', 2),

        # URLs (protect from translation)
        (r'https?://[^\s<>"{}|\\^`\[\]]+', 'URL', 11),

        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL', 11),
    ]

    @staticmethod
    def protect(text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replace placeholders with unique tokens before translation

        Args:
            text: Original text with placeholders

        Returns:
            Tuple of (protected_text, placeholder_map)
            - protected_text: Text with placeholders replaced by tokens
            - placeholder_map: Dictionary mapping tokens back to original placeholders
        """
        protected_text = text
        placeholder_map = {}

        # Sort patterns by priority (highest first)
        sorted_patterns = sorted(
            PlaceholderProtector.PATTERNS,
            key=lambda x: x[2],
            reverse=True
        )

        for pattern, pattern_type, _ in sorted_patterns:
            matches = list(re.finditer(pattern, protected_text))

            # Process matches in reverse order to maintain positions
            for match in reversed(matches):
                original = match.group(0)

                # Generate unique token
                token = f"__PLACEHOLDER_{uuid.uuid4().hex[:8].upper()}__"

                # Store mapping
                placeholder_map[token] = original

                # Replace in text
                start, end = match.span()
                protected_text = protected_text[:start] + token + protected_text[end:]

        return protected_text, placeholder_map

    @staticmethod
    def restore(text: str, placeholder_map: Dict[str, str]) -> str:
        """
        Restore original placeholders after translation

        Args:
            text: Translated text with tokens
            placeholder_map: Dictionary mapping tokens to original placeholders

        Returns:
            Text with placeholders restored
        """
        restored_text = text

        for token, original in placeholder_map.items():
            restored_text = restored_text.replace(token, original)

        return restored_text

    @staticmethod
    def protect_batch(strings: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
        """
        Protect placeholders in a batch of strings

        Args:
            strings: Dictionary of key-value pairs to protect

        Returns:
            Tuple of (protected_strings, maps_by_key)
            - protected_strings: Dictionary with protected values
            - maps_by_key: Dictionary mapping each key to its placeholder map
        """
        protected_strings = {}
        maps_by_key = {}

        for key, value in strings.items():
            protected_value, placeholder_map = PlaceholderProtector.protect(value)
            protected_strings[key] = protected_value

            # Only store map if there were placeholders
            if placeholder_map:
                maps_by_key[key] = placeholder_map

        return protected_strings, maps_by_key

    @staticmethod
    def restore_batch(
        strings: Dict[str, str],
        maps_by_key: Dict[str, Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Restore placeholders in a batch of translated strings

        Args:
            strings: Dictionary of translated strings with tokens
            maps_by_key: Dictionary mapping each key to its placeholder map

        Returns:
            Dictionary with placeholders restored
        """
        restored_strings = {}

        for key, value in strings.items():
            if key in maps_by_key:
                restored_value = PlaceholderProtector.restore(value, maps_by_key[key])
                restored_strings[key] = restored_value
            else:
                # No placeholders to restore
                restored_strings[key] = value

        return restored_strings

    @staticmethod
    def validate_preservation(
        original: str,
        translated: str,
        placeholder_map: Dict[str, str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all placeholders were preserved in translation

        Args:
            original: Original text
            translated: Translated text (with placeholders restored)
            placeholder_map: Map of tokens to placeholders

        Returns:
            Tuple of (is_valid, missing_placeholders)
        """
        missing = []

        for token, placeholder in placeholder_map.items():
            if placeholder not in translated:
                missing.append(placeholder)

        is_valid = len(missing) == 0
        return is_valid, missing

    @staticmethod
    def analyze_placeholders(text: str) -> Dict[str, List[str]]:
        """
        Analyze text to identify all placeholders by type

        Args:
            text: Text to analyze

        Returns:
            Dictionary mapping pattern types to lists of found placeholders
        """
        results = {}

        for pattern, pattern_type, _ in PlaceholderProtector.PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                results[pattern_type] = matches

        return results


class PlaceholderStats:
    """Statistics about placeholder usage"""

    @staticmethod
    def count_by_type(strings: Dict[str, str]) -> Dict[str, int]:
        """
        Count placeholders by type across all strings

        Args:
            strings: Dictionary of strings to analyze

        Returns:
            Dictionary mapping placeholder types to counts
        """
        type_counts = {}

        for value in strings.values():
            analysis = PlaceholderProtector.analyze_placeholders(value)

            for pattern_type, matches in analysis.items():
                if pattern_type not in type_counts:
                    type_counts[pattern_type] = 0
                type_counts[pattern_type] += len(matches)

        return type_counts

    @staticmethod
    def get_complexity_score(strings: Dict[str, str]) -> float:
        """
        Calculate complexity score based on placeholder usage
        Higher score = more complex translations (more risk)

        Args:
            strings: Dictionary of strings to analyze

        Returns:
            Complexity score (0.0 to 1.0)
        """
        total_strings = len(strings)
        if total_strings == 0:
            return 0.0

        strings_with_placeholders = 0
        total_placeholders = 0

        for value in strings.values():
            analysis = PlaceholderProtector.analyze_placeholders(value)
            if analysis:
                strings_with_placeholders += 1
                total_placeholders += sum(len(matches) for matches in analysis.values())

        # Metrics
        placeholder_density = strings_with_placeholders / total_strings
        avg_placeholders = total_placeholders / total_strings if total_strings > 0 else 0

        # Weighted score
        complexity = (placeholder_density * 0.6) + (min(avg_placeholders / 3, 1.0) * 0.4)

        return round(complexity, 3)
