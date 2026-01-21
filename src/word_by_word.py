"""
Word-by-Word Baseline Translator
Simple dictionary-based translation (baseline for comparison)
"""

import json
import os
from typing import Dict, List


class WordByWordTranslator:
    """Simple word-by-word dictionary-based translator"""
    
    def __init__(self, dictionary_path: str = None):
        """
        Initialize translator with dictionary.
        
        Args:
            dictionary_path: Path to JSON dictionary file
        """
        if dictionary_path is None:
            # Default to ../data/dictionary.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dictionary_path = os.path.join(current_dir, '..', 'data', 'dictionary.json')
        
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
    
    def translate_word(self, word: str) -> str:
        """
        Translate a single word.
        
        Args:
            word: English word
            
        Returns:
            Hindi translation (or original word if not in dictionary)
        """
        word_lower = word.lower()
        
        # Check dictionary
        if word_lower in self.dictionary:
            translation = self.dictionary[word_lower]
            # Return translation if not empty, otherwise empty string
            return translation if translation else ""
        else:
            # Keep unknown words as-is (might be proper nouns)
            return word
    
    def translate(self, sentence: str) -> str:
        """
        Translate sentence word-by-word.
        
        Args:
            sentence: English sentence
            
        Returns:
            Hindi translation
        """
        # Tokenize (simple split on whitespace and punctuation)
        tokens = []
        current_word = ""
        
        for char in sentence:
            if char.isalnum():
                current_word += char
            else:
                if current_word:
                    tokens.append(('word', current_word))
                    current_word = ""
                if char.strip():  # Preserve non-whitespace punctuation
                    tokens.append(('punct', char))
        
        if current_word:
            tokens.append(('word', current_word))
        
        # Translate words
        translated_tokens = []
        for token_type, token in tokens:
            if token_type == 'word':
                translated = self.translate_word(token)
                if translated:  # Only add if not empty
                    translated_tokens.append(translated)
            elif token_type == 'punct':
                # Keep punctuation but adjust spacing for Hindi
                if token in ',.!?;:':
                    translated_tokens.append(token)
        
        # Join tokens
        result = ' '.join(translated_tokens)
        
        # Clean up extra spaces
        result = ' '.join(result.split())
        
        return result
    
    def translate_batch(self, sentences: List[str]) -> List[str]:
        """
        Translate multiple sentences.
        
        Args:
            sentences: List of English sentences
            
        Returns:
            List of Hindi translations
        """
        return [self.translate(sent) for sent in sentences]


# Demo
def demo():
    """Demonstrate word-by-word translator"""
    translator = WordByWordTranslator()
    
    test_sentences = [
        "Hello, how are you?",
        "I love programming.",
        "The weather is nice today.",
        "What is your name?",
        "This is a pen."
    ]
    
    print("Word-by-Word Baseline Translator (English → Hindi)\n")
    for sent in test_sentences:
        translation = translator.translate(sent)
        print(f"Source: {sent}")
        print(f"Translation: {translation}\n")


if __name__ == '__main__':
    demo()
