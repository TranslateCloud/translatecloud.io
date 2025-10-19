#!/usr/bin/env python3
"""
Add footer to all HTML pages that don't have it
"""

import os
import re
from pathlib import Path

# Footer HTML templates
FOOTER_EN = '''
    <footer class="footer">
        <p class="footer-text">© 2025 TranslateCloud. All rights reserved.</p>
    </footer>
'''

FOOTER_ES = '''
    <footer class="footer">
        <p class="footer-text">© 2025 TranslateCloud. Todos los derechos reservados.</p>
    </footer>
'''

# Footer CSS
FOOTER_CSS = '''
        .footer {
            background-color: var(--color-gray-900);
            color: var(--color-gray-400);
            padding: var(--space-12) var(--space-8);
            text-align: center;
        }

        .footer-text {
            font-size: var(--text-sm);
        }
'''

def add_footer_to_file(file_path):
    """Add footer to a single HTML file if it doesn't have one"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if footer already exists
    if '<footer' in content:
        print(f"OK: {file_path.name} already has footer")
        return False

    # Determine language
    is_spanish = '/es/' in str(file_path) or '\\es\\' in str(file_path)
    footer_html = FOOTER_ES if is_spanish else FOOTER_EN

    # Check if footer CSS exists
    has_footer_css = '.footer {' in content

    # Add footer CSS if missing
    if not has_footer_css and '</style>' in content:
        # Find last </style> tag
        style_pos = content.rfind('</style>')
        if style_pos != -1:
            content = content[:style_pos] + FOOTER_CSS + content[style_pos:]
            print(f"  + Added footer CSS to {file_path.name}")

    # Add footer HTML before </body>
    if '</body>' in content:
        body_pos = content.rfind('</body>')
        content = content[:body_pos] + footer_html + content[body_pos:]

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"DONE: Added footer to {file_path.name}")
        return True
    else:
        print(f"WARN: No </body> tag found in {file_path.name}")
        return False

def main():
    """Main function"""
    public_dir = Path(__file__).parent / 'public'

    # Find all HTML files
    html_files = []
    for lang in ['en', 'es']:
        lang_dir = public_dir / lang
        if lang_dir.exists():
            html_files.extend(lang_dir.glob('*.html'))

    print(f"Found {len(html_files)} HTML files")
    print("=" * 60)

    added_count = 0
    for file_path in sorted(html_files):
        # Skip if it's a directory
        if file_path.is_dir():
            print(f"SKIP: Directory {file_path.name}")
            continue

        if add_footer_to_file(file_path):
            added_count += 1

    print("=" * 60)
    print(f"\nSUCCESS: Added footer to {added_count} files")
    print(f"Total files processed: {len(html_files)}")

if __name__ == '__main__':
    main()
