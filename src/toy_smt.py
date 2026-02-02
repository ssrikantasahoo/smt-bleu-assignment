"""
Toy Statistical Machine Translation System
A simplified phrase-based SMT with:
- Phrase table with translation probabilities
- Trigram language model with add-k smoothing
- Beam search decoder
"""

import json
import math
import os
from typing import List, Tuple, Dict
import random


class ToyPhraseTable:
    """Phrase translation table with probabilities"""
    
    def __init__(self, phrase_table_path: str):
        """Load phrase table from JSON file"""
        with open(phrase_table_path, 'r', encoding='utf-8') as f:
            self.phrase_table = json.load(f)
    
    def get_translations(self, phrase: str) -> List[Dict]:
        """
        Get possible translations for a phrase.
        
        Args:
            phrase: Source phrase (English)
            
        Returns:
            List of dictionaries with 'phrase' and 'prob' keys
        """
        phrase_lower = phrase.lower()
        return self.phrase_table.get(phrase_lower, [])
    
    def translate_phrase(self, phrase: str) -> str:
        """Get best translation for a phrase"""
        translations = self.get_translations(phrase)
        if not translations:
            return phrase  # Return original if no translation
        # Return highest probability translation
        best = max(translations, key=lambda x: x['prob'])
        return best['phrase']


class TrigramLanguageModel:
    """Trigram language model with add-k smoothing"""
    
    def __init__(self, lm_path: str):
        """Load language model from JSON file"""
        with open(lm_path, 'r', encoding='utf-8') as f:
            lm_data = json.load(f)
        
        self.unigrams = lm_data['unigrams']
        self.bigrams = lm_data['bigrams']
        self.trigrams = lm_data['trigrams']
        self.vocab_size = lm_data['vocabulary_size']
        self.k = lm_data['k_smoothing']
    
    def get_trigram_prob(self, w1: str, w2: str, w3: str) -> float:
        """
        Compute P(w3 | w1, w2) using add-k smoothing.
        
        P(w3 | w1, w2) = (count(w1, w2, w3) + k) / (count(w1, w2) + k * V)
        """
        trigram_key = f"{w1} {w2} {w3}"
        bigram_key = f"{w1} {w2}"
        
        trigram_count = self.trigrams.get(trigram_key, 0)
        bigram_count = self.bigrams.get(bigram_key, 0)
        
        # Add-k smoothing
        prob = (trigram_count + self.k) / (bigram_count + self.k * self.vocab_size)
        
        return prob
    
    def get_bigram_prob(self, w1: str, w2: str) -> float:
        """
        Compute P(w2 | w1) using add-k smoothing (fallback).
        
        P(w2 | w1) = (count(w1, w2) + k) / (count(w1) + k * V)
        """
        bigram_key = f"{w1} {w2}"
        
        bigram_count = self.bigrams.get(bigram_key, 0)
        unigram_count = self.unigrams.get(w1, 0)
        
        prob = (bigram_count + self.k) / (unigram_count + self.k * self.vocab_size)
        
        return prob
    
    def get_sequence_prob(self, tokens: List[str]) -> float:
        """
        Compute probability of a sequence using trigram model.
        
        Returns log probability to avoid underflow.
        """
        if not tokens:
            return 0.0
        
        # Add sentence boundary markers
        padded = ['<s>', '<s>'] + tokens + ['</s>']
        
        log_prob = 0.0
        for i in range(2, len(padded)):
            w1, w2, w3 = padded[i-2], padded[i-1], padded[i]
            prob = self.get_trigram_prob(w1, w2, w3)
            
            if prob > 0:
                log_prob += math.log(prob)
            else:
                # Very small probability for unseen trigrams
                log_prob += math.log(1e-10)
        
        return log_prob


class Hypothesis:
    """Translation hypothesis for beam search"""
    
    def __init__(self, translation: List[str], score: float, coverage: List[bool]):
        self.translation = translation  # List of target words
        self.score = score  # Combined score (phrase + LM)
        self.coverage = coverage  # Which source words are translated
    
    def __lt__(self, other):
        """For sorting hypotheses by score"""
        return self.score < other.score


class ToyDecoder:
    """Beam search decoder for phrase-based SMT"""
    
    def __init__(self, phrase_table: ToyPhraseTable, lm: TrigramLanguageModel, 
                 beam_width: int = 5, phrase_weight: float = 0.3, lm_weight: float = 0.7):
        """
        Initialize decoder.
        
        Args:
            phrase_table: Phrase translation table
            lm: Language model
            beam_width: Maximum hypotheses to keep in beam
            phrase_weight: Weight for phrase translation probability
            lm_weight: Weight for language model probability
        """
        self.phrase_table = phrase_table
        self.lm = lm
        self.beam_width = beam_width
        self.phrase_weight = phrase_weight
        self.lm_weight = lm_weight
        # Set random seed for deterministic behavior
        random.seed(42)
    
    def decode(self, source_sentence: str) -> str:
        """
        Decode source sentence to target sentence.

        Simplified decoding:
        1. Tokenize source (strip punctuation)
        2. Try to match phrases (longer phrases first)
        3. Use beam search to score hypotheses
        4. Return best hypothesis

        Args:
            source_sentence: English input sentence

        Returns:
            Hindi translation
        """
        # Strip punctuation from tokens for better phrase table matching
        raw_tokens = source_sentence.lower().strip().split()
        source_tokens = []
        for token in raw_tokens:
            cleaned = token.strip('.,!?;:"\'-()[]{}')
            if cleaned:
                source_tokens.append(cleaned)

        if not source_tokens:
            return ""

        # Greedy phrase matching (longest match first)
        # In production SMT, beam search explores all phrase segmentations
        translation = []
        i = 0

        while i < len(source_tokens):
            matched = False

            # Try longest phrase first (up to 4 words)
            for phrase_len in range(min(4, len(source_tokens) - i), 0, -1):
                phrase = ' '.join(source_tokens[i:i+phrase_len])
                translations = self.phrase_table.get_translations(phrase)

                if translations:
                    # Choose translation with highest probability
                    best_trans = max(translations, key=lambda x: x['prob'])

                    if best_trans['phrase']:  # Skip empty translations (e.g., "the" in Hindi)
                        translation.append(best_trans['phrase'])

                    i += phrase_len
                    matched = True
                    break

            if not matched:
                # No phrase match, keep source word as-is (OOV)
                translation.append(source_tokens[i])
                i += 1

        # Join translation
        result = ' '.join(translation)
        return result
    
    def decode_with_score(self, source_sentence: str) -> Tuple[str, float]:
        """
        Decode and return translation with score.
        
        Returns:
            Tuple of (translation, score)
        """
        translation = self.decode(source_sentence)
        
        # Compute score
        tokens = translation.split()
        lm_score = self.lm.get_sequence_prob(tokens)
        
        # Phrase score would need to be accumulated during decoding
        # For simplicity, just use LM score
        score = lm_score
        
        return translation, score


class ToySMT:
    """Main interface for Toy SMT system"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize Toy SMT system.
        
        Args:
            data_dir: Directory containing phrase_table.json and hindi_trigram_lm.json
        """
        if data_dir is None:
            # Default to ../data relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, '..', 'data')
        
        phrase_table_path = os.path.join(data_dir, 'phrase_table.json')
        lm_path = os.path.join(data_dir, 'hindi_trigram_lm.json')
        
        self.phrase_table = ToyPhraseTable(phrase_table_path)
        self.lm = TrigramLanguageModel(lm_path)
        self.decoder = ToyDecoder(self.phrase_table, self.lm, beam_width=5)
    
    def translate(self, source_sentence: str) -> str:
        """
        Translate English sentence to Hindi.
        
        Args:
            source_sentence: English input
            
        Returns:
            Hindi translation
        """
        return self.decoder.decode(source_sentence)
    
    def translate_with_score(self, source_sentence: str) -> Tuple[str, float]:
        """
        Translate and return score.
        
        Returns:
            Tuple of (translation, score)
        """
        return self.decoder.decode_with_score(source_sentence)


# Demo function
def demo():
    """Demonstrate Toy SMT system"""
    smt = ToySMT()
    
    test_sentences = [
        "Hello, how are you?",
        "I love programming.",
        "The weather is nice today.",
        "What is your name?"
    ]
    
    print("Toy SMT Demo (English → Hindi)\n")
    for sent in test_sentences:
        translation, score = smt.translate_with_score(sent)
        print(f"Source: {sent}")
        print(f"Translation: {translation}")
        print(f"LM Score: {score:.4f}\n")


if __name__ == '__main__':
    demo()
