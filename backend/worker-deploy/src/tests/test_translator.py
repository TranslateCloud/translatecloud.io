"""
Tests para MarianTranslator
"""

import pytest
from src.core.marian_translator import MarianTranslator


def test_translator_initialization():
    """Test que el traductor se inicializa correctamente"""
    translator = MarianTranslator()
    assert translator is not None
    assert translator.device in ['cuda', 'cpu']


def test_load_model():
    """Test carga de modelo"""
    translator = MarianTranslator()
    result = translator.load_model('en', 'es')
    assert result == True


@pytest.mark.asyncio
async def test_translate_simple():
    """Test traducción simple"""
    translator = MarianTranslator()
    result = translator.translate(
        'Hello world',
        'en',
        'es'
    )
    assert result is not None
    assert len(result) > 0
