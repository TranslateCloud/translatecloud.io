"""
TranslateCloud - MarianMT Translation Engine
Core translation module using Helsinki-NLP models
"""

import torch
from transformers import MarianMTModel, MarianTokenizer
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MarianTranslator:
    """
    Gestor principal de traducción usando modelos MarianMT
    """
    
    def __init__(self):
        self.models: Dict[str, MarianMTModel] = {}
        self.tokenizers: Dict[str, MarianTokenizer] = {}
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f'MarianTranslator initialized on device: {self.device}')
    
    def load_model(self, source_lang: str, target_lang: str) -> bool:
        """
        Carga el modelo de traducción para un par de idiomas
        
        Args:
            source_lang: Código del idioma origen (ej: 'en', 'es')
            target_lang: Código del idioma destino
            
        Returns:
            bool: True si se cargó correctamente
        """
        model_key = f'{source_lang}-{target_lang}'
        
        if model_key in self.models:
            logger.info(f'Model {model_key} already loaded')
            return True
        
        try:
            model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
            
            logger.info(f'Loading model: {model_name}')
            self.tokenizers[model_key] = MarianTokenizer.from_pretrained(model_name)
            self.models[model_key] = MarianMTModel.from_pretrained(model_name).to(self.device)
            
            logger.info(f'Model {model_key} loaded successfully')
            return True
            
        except Exception as e:
            logger.error(f'Error loading model {model_key}: {str(e)}')
            return False
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 512
    ) -> Optional[str]:
        """
        Traduce un texto del idioma origen al destino
        
        Args:
            text: Texto a traducir
            source_lang: Idioma origen
            target_lang: Idioma destino
            max_length: Longitud máxima del texto generado
            
        Returns:
            str: Texto traducido o None si falla
        """
        model_key = f'{source_lang}-{target_lang}'
        
        # Cargar modelo si no está cargado
        if model_key not in self.models:
            if not self.load_model(source_lang, target_lang):
                return None
        
        try:
            # Tokenizar
            inputs = self.tokenizers[model_key](
                text,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=max_length
            ).to(self.device)
            
            # Traducir
            with torch.no_grad():
                outputs = self.models[model_key].generate(**inputs)
            
            # Decodificar
            translated = self.tokenizers[model_key].decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            return translated
            
        except Exception as e:
            logger.error(f'Translation error: {str(e)}')
            return None
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        batch_size: int = 8
    ) -> List[Optional[str]]:
        """
        Traduce múltiples textos en batch para mayor eficiencia
        
        Args:
            texts: Lista de textos a traducir
            source_lang: Idioma origen
            target_lang: Idioma destino
            batch_size: Tamaño del batch
            
        Returns:
            List[str]: Lista de textos traducidos
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = [
                self.translate(text, source_lang, target_lang)
                for text in batch
            ]
            results.extend(batch_results)
        
        return results


def translate_content(text: str, source_lang: str, target_lang: str) -> str:
    """
    Simple wrapper for translation

    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Translated text
    """
    result = translator.translate(text, source_lang, target_lang)
    return result if result else text  # Return original if translation fails


# Instancia global del traductor
translator = MarianTranslator()
