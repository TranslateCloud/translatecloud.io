"""
FileParser - Universal localization file format parser
Supports: JSON, XML (Android), strings (iOS), ARB (Flutter)
"""

import json
import re
import xml.etree.ElementTree as ET
from enum import Enum
from typing import Dict, Any, List, Tuple
from xml.dom import minidom


class FileFormat(Enum):
    """Supported localization file formats"""
    JSON = "json"
    XML = "xml"
    STRINGS = "strings"
    ARB = "arb"
    UNKNOWN = "unknown"


class FileParser:
    """Universal parser for localization file formats"""

    @staticmethod
    def detect_format(filename: str, content: str) -> FileFormat:
        """
        Auto-detect file format based on filename and content

        Args:
            filename: Name of the file
            content: File content as string

        Returns:
            FileFormat enum value
        """
        filename_lower = filename.lower()

        # Check by extension first
        if filename_lower.endswith('.json'):
            return FileFormat.JSON
        elif filename_lower.endswith('.xml'):
            return FileFormat.XML
        elif filename_lower.endswith('.strings'):
            return FileFormat.STRINGS
        elif filename_lower.endswith('.arb'):
            return FileFormat.ARB

        # Fallback to content analysis
        content_stripped = content.strip()

        if content_stripped.startswith('{') and content_stripped.endswith('}'):
            try:
                json.loads(content)
                return FileFormat.JSON
            except:
                pass

        if content_stripped.startswith('<?xml') or content_stripped.startswith('<resources'):
            return FileFormat.XML

        if '"' in content and '=' in content and ';' in content:
            return FileFormat.STRINGS

        return FileFormat.UNKNOWN

    @staticmethod
    def parse(content: str, file_format: FileFormat) -> Dict[str, str]:
        """
        Parse file content based on format

        Args:
            content: File content as string
            file_format: FileFormat enum value

        Returns:
            Dictionary with key-value pairs (flattened)
        """
        if file_format == FileFormat.JSON:
            return FileParser.parse_json(content)
        elif file_format == FileFormat.XML:
            return FileParser.parse_xml(content)
        elif file_format == FileFormat.STRINGS:
            return FileParser.parse_strings(content)
        elif file_format == FileFormat.ARB:
            return FileParser.parse_arb(content)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @staticmethod
    def parse_json(content: str) -> Dict[str, str]:
        """
        Parse JSON localization files (React Native, i18n, generic)
        Supports nested objects - flattens with dot notation

        Example:
            {"user": {"name": "Name", "email": "Email"}}
            → {"user.name": "Name", "user.email": "Email"}
        """
        data = json.loads(content)
        return FileParser._flatten_dict(data)

    @staticmethod
    def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
        """
        Recursively flatten nested dictionary

        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys

        Returns:
            Flattened dictionary with string values only
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(FileParser._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, str):
                items.append((new_key, v))
            else:
                # Convert non-string values to strings (numbers, booleans)
                items.append((new_key, str(v)))

        return dict(items)

    @staticmethod
    def _unflatten_dict(d: Dict[str, str], sep: str = '.') -> Dict[str, Any]:
        """
        Reconstruct nested dictionary from flattened keys

        Args:
            d: Flattened dictionary
            sep: Separator used in keys

        Returns:
            Nested dictionary
        """
        result = {}
        for key, value in d.items():
            parts = key.split(sep)
            current = result

            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

        return result

    @staticmethod
    def parse_xml(content: str) -> Dict[str, str]:
        """
        Parse Android strings.xml format

        Example:
            <resources>
                <string name="app_name">MyApp</string>
                <string name="welcome">Welcome!</string>
            </resources>
        """
        root = ET.fromstring(content)
        strings = {}

        for string_elem in root.findall('.//string'):
            name = string_elem.get('name')
            value = string_elem.text or ""
            if name:
                strings[name] = value

        return strings

    @staticmethod
    def parse_strings(content: str) -> Dict[str, str]:
        """
        Parse iOS Localizable.strings format

        Example:
            "app_name" = "MyApp";
            "welcome" = "Welcome!";
            /* Comment */
            "goodbye" = "Goodbye";
        """
        strings = {}

        # Remove comments (/* ... */ and // ...)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

        # Pattern: "key" = "value";
        pattern = r'"([^"]+)"\s*=\s*"([^"]*)"\s*;'

        for match in re.finditer(pattern, content):
            key = match.group(1)
            value = match.group(2)
            strings[key] = value

        return strings

    @staticmethod
    def parse_arb(content: str) -> Dict[str, str]:
        """
        Parse Flutter ARB (Application Resource Bundle) format
        ARB is JSON-based but has special metadata keys starting with @

        Example:
            {
                "@@locale": "en",
                "title": "Title",
                "@title": {
                    "description": "The title of the page"
                },
                "welcome": "Welcome"
            }

        Returns only translatable strings (ignores @ metadata keys)
        """
        data = json.loads(content)

        # Filter out metadata keys (start with @)
        strings = {
            key: value
            for key, value in data.items()
            if not key.startswith('@') and isinstance(value, str)
        }

        return strings

    @staticmethod
    def reconstruct(translations: Dict[str, str], file_format: FileFormat,
                   original_content: str = None) -> str:
        """
        Reconstruct file content from translated strings

        Args:
            translations: Dictionary with translated key-value pairs
            file_format: Target file format
            original_content: Original file content (for preserving metadata, comments)

        Returns:
            Reconstructed file content as string
        """
        if file_format == FileFormat.JSON:
            return FileParser._reconstruct_json(translations)
        elif file_format == FileFormat.XML:
            return FileParser._reconstruct_xml(translations)
        elif file_format == FileFormat.STRINGS:
            return FileParser._reconstruct_strings(translations, original_content)
        elif file_format == FileFormat.ARB:
            return FileParser._reconstruct_arb(translations, original_content)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @staticmethod
    def _reconstruct_json(translations: Dict[str, str]) -> str:
        """
        Reconstruct JSON file from flattened translations
        Unflattens nested structures
        """
        nested = FileParser._unflatten_dict(translations)
        return json.dumps(nested, indent=2, ensure_ascii=False)

    @staticmethod
    def _reconstruct_xml(translations: Dict[str, str]) -> str:
        """
        Reconstruct Android strings.xml
        """
        root = ET.Element('resources')

        for key, value in translations.items():
            string_elem = ET.SubElement(root, 'string')
            string_elem.set('name', key)
            string_elem.text = value

        # Pretty print XML
        xml_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent='    ')

    @staticmethod
    def _reconstruct_strings(translations: Dict[str, str], original_content: str = None) -> str:
        """
        Reconstruct iOS .strings file
        Preserves comments from original if provided
        """
        lines = []

        # If original content provided, try to preserve structure and comments
        if original_content:
            original_lines = original_content.split('\n')
            used_keys = set()

            for line in original_lines:
                # Check if line is a translation
                match = re.match(r'"([^"]+)"\s*=\s*"[^"]*"\s*;', line)
                if match:
                    key = match.group(1)
                    if key in translations:
                        lines.append(f'"{key}" = "{translations[key]}";')
                        used_keys.add(key)
                    else:
                        lines.append(line)
                else:
                    # Preserve comments and empty lines
                    lines.append(line)

            # Add any new keys not in original
            for key, value in translations.items():
                if key not in used_keys:
                    lines.append(f'"{key}" = "{value}";')
        else:
            # Simple reconstruction without original
            for key, value in translations.items():
                lines.append(f'"{key}" = "{value}";')

        return '\n'.join(lines)

    @staticmethod
    def _reconstruct_arb(translations: Dict[str, str], original_content: str = None) -> str:
        """
        Reconstruct Flutter ARB file
        Preserves metadata (@) from original if provided
        """
        if original_content:
            # Parse original to preserve metadata
            original_data = json.loads(original_content)
            result = {}

            # Preserve @@locale and other @@ keys
            for key, value in original_data.items():
                if key.startswith('@@'):
                    result[key] = value

            # Add translations and their metadata
            for key, value in translations.items():
                result[key] = value

                # Preserve metadata if it exists in original
                metadata_key = f'@{key}'
                if metadata_key in original_data:
                    result[metadata_key] = original_data[metadata_key]

            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # Simple reconstruction without metadata
            return json.dumps(translations, indent=2, ensure_ascii=False)


class TranslationStatistics:
    """Track statistics about parsed files"""

    def __init__(self):
        self.total_keys = 0
        self.total_characters = 0
        self.keys_by_type = {}

    @staticmethod
    def analyze(strings: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze parsed strings for statistics

        Returns:
            Dictionary with statistics
        """
        total_keys = len(strings)
        total_chars = sum(len(value) for value in strings.values())

        # Estimate translation cost (DeepL charges per character)
        estimated_cost = total_chars * 0.00002  # ~$20 per 1M characters

        return {
            'total_keys': total_keys,
            'total_characters': total_chars,
            'average_length': total_chars / total_keys if total_keys > 0 else 0,
            'estimated_cost_usd': round(estimated_cost, 4)
        }
