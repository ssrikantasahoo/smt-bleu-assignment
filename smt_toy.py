"""
Toy Statistical Machine Translation System
===========================================
A simplified SMT system for demonstration purposes.

This implements a phrase-based SMT system with:
- Phrase table with translation probabilities
- N-gram language model scoring
- Beam search decoding
- Log-linear model combination

This is a fallback when Moses is not available, demonstrating SMT principles.
"""

import json
import math
from typing import List, Tuple, Dict, Set
from collections import defaultdict
import os


class PhraseTable:
    """Phrase translation table with probabilities."""

    def __init__(self, phrase_table_path: str = None):
        """
        Initialize phrase table.

        Args:
            phrase_table_path: Path to phrase table JSON file
        """
        self.table = {}
        if phrase_table_path and os.path.exists(phrase_table_path):
            with open(phrase_table_path, 'r', encoding='utf-8') as f:
                self.table = json.load(f)

    def get_translations(self, source_phrase: str) -> List[Tuple[str, float]]:
        """
        Get possible translations for a source phrase.

        Args:
            source_phrase: Source language phrase

        Returns:
            List of (target_phrase, probability) tuples
        """
        return self.table.get(source_phrase, [])

    def add_phrase(self, source: str, target: str, prob: float):
        """Add a phrase pair to the table."""
        if source not in self.table:
            self.table[source] = []
        self.table[source].append((target, prob))


class LanguageModel:
    """N-gram language model for target language."""

    def __init__(self, lm_path: str = None):
        """
        Initialize language model.

        Args:
            lm_path: Path to language model JSON file
        """
        self.ngrams = defaultdict(lambda: defaultdict(float))
        self.vocab_size = 0

        if lm_path and os.path.exists(lm_path):
            with open(lm_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.ngrams = {
                    int(n): {tuple(k.split()): v for k, v in ngrams.items()}
                    for n, ngrams in data.items()
                }
                self.vocab_size = len(set(word for ngram_dict in self.ngrams.values()
                                          for ngram in ngram_dict.keys()
                                          for word in ngram))

    def score_sequence(self, tokens: List[str]) -> float:
        """
        Score a token sequence using n-gram LM.

        Args:
            tokens: List of tokens

        Returns:
            Log probability of sequence
        """
        if not tokens:
            return 0.0

        log_prob = 0.0
        # Use trigram model with backoff
        for i in range(len(tokens)):
            # Try trigram
            if i >= 2:
                trigram = tuple(tokens[i-2:i+1])
                if trigram in self.ngrams.get(3, {}):
                    log_prob += math.log(self.ngrams[3][trigram])
                    continue

            # Backoff to bigram
            if i >= 1:
                bigram = tuple(tokens[i-1:i+1])
                if bigram in self.ngrams.get(2, {}):
                    log_prob += math.log(self.ngrams[2][bigram])
                    continue

            # Backoff to unigram
            unigram = (tokens[i],)
            if unigram in self.ngrams.get(1, {}):
                log_prob += math.log(self.ngrams[1][unigram])
            else:
                # Unknown word penalty
                log_prob += math.log(1e-10)

        return log_prob


class ToyTranslationHypothesis:
    """Translation hypothesis for beam search."""

    def __init__(self,
                 target_tokens: List[str],
                 source_coverage: Set[int],
                 translation_score: float,
                 lm_score: float,
                 source_length: int):
        """
        Initialize hypothesis.

        Args:
            target_tokens: Current target translation tokens
            source_coverage: Set of covered source positions
            translation_score: Log probability from phrase table
            lm_score: Log probability from language model
            source_length: Length of source sentence
        """
        self.target_tokens = target_tokens
        self.source_coverage = source_coverage
        self.translation_score = translation_score
        self.lm_score = lm_score
        self.source_length = source_length

    def total_score(self, lm_weight: float = 0.5) -> float:
        """Compute weighted total score."""
        return self.translation_score + lm_weight * self.lm_score

    def is_complete(self) -> bool:
        """Check if all source words are covered."""
        return len(self.source_coverage) == self.source_length


class ToySMT:
    """
    Toy Statistical Machine Translation system.

    Implements phrase-based SMT with beam search decoding.
    """

    def __init__(self,
                 phrase_table_path: str,
                 lm_path: str,
                 beam_size: int = 10,
                 max_phrase_length: int = 4,
                 lm_weight: float = 0.5):
        """
        Initialize toy SMT system.

        Args:
            phrase_table_path: Path to phrase table
            lm_path: Path to language model
            beam_size: Beam size for decoding
            max_phrase_length: Maximum phrase length
            lm_weight: Weight for language model score
        """
        self.phrase_table = PhraseTable(phrase_table_path)
        self.lm = LanguageModel(lm_path)
        self.beam_size = beam_size
        self.max_phrase_length = max_phrase_length
        self.lm_weight = lm_weight

    def translate(self, source_sentence: str) -> str:
        """
        Translate source sentence to target language.

        Args:
            source_sentence: Source language sentence

        Returns:
            Target language translation
        """
        source_tokens = source_sentence.lower().split()
        source_length = len(source_tokens)

        if source_length == 0:
            return ""

        # Initialize beam with empty hypothesis
        beam = [ToyTranslationHypothesis(
            target_tokens=[],
            source_coverage=set(),
            translation_score=0.0,
            lm_score=0.0,
            source_length=source_length
        )]

        # Beam search
        for _ in range(source_length * 2):  # Max iterations
            new_beam = []

            for hyp in beam:
                if hyp.is_complete():
                    new_beam.append(hyp)
                    continue

                # Try extending with each uncovered source phrase
                for start_pos in range(source_length):
                    if start_pos in hyp.source_coverage:
                        continue

                    # Try different phrase lengths
                    for length in range(1, min(self.max_phrase_length + 1,
                                               source_length - start_pos + 1)):
                        # Check if all positions are uncovered
                        positions = set(range(start_pos, start_pos + length))
                        if positions & hyp.source_coverage:
                            continue

                        # Get source phrase
                        source_phrase = ' '.join(source_tokens[start_pos:start_pos + length])

                        # Get translations
                        translations = self.phrase_table.get_translations(source_phrase)

                        if not translations:
                            # Fallback: copy source phrase
                            translations = [(source_phrase, 0.01)]

                        for target_phrase, phrase_prob in translations:
                            # Create new hypothesis
                            new_target_tokens = hyp.target_tokens + target_phrase.split()
                            new_coverage = hyp.source_coverage | positions
                            new_translation_score = hyp.translation_score + math.log(phrase_prob + 1e-10)
                            new_lm_score = self.lm.score_sequence(new_target_tokens)

                            new_hyp = ToyTranslationHypothesis(
                                target_tokens=new_target_tokens,
                                source_coverage=new_coverage,
                                translation_score=new_translation_score,
                                lm_score=new_lm_score,
                                source_length=source_length
                            )

                            new_beam.append(new_hyp)

            # Prune beam
            new_beam.sort(key=lambda h: h.total_score(self.lm_weight), reverse=True)
            beam = new_beam[:self.beam_size]

            # Check if best hypothesis is complete
            if beam and beam[0].is_complete():
                break

        # Return best complete hypothesis
        complete_hyps = [h for h in beam if h.is_complete()]
        if complete_hyps:
            best_hyp = max(complete_hyps, key=lambda h: h.total_score(self.lm_weight))
            return ' '.join(best_hyp.target_tokens)
        elif beam:
            # Return best partial hypothesis if no complete one
            return ' '.join(beam[0].target_tokens)
        else:
            return ""

    def translate_with_score(self, source_sentence: str) -> Tuple[str, float]:
        """
        Translate and return translation with score.

        Args:
            source_sentence: Source sentence

        Returns:
            Tuple of (translation, score)
        """
        translation = self.translate(source_sentence)
        tokens = translation.split()
        lm_score = self.lm.score_sequence(tokens)
        return translation, lm_score


def create_default_phrase_table(output_path: str):
    """Create a default English-French phrase table."""
    phrase_table = {
        # Single words
        "hello": [("bonjour", 0.8), ("salut", 0.2)],
        "world": [("monde", 0.9)],
        "the": [("le", 0.4), ("la", 0.4), ("les", 0.2)],
        "cat": [("chat", 0.9)],
        "dog": [("chien", 0.9)],
        "is": [("est", 0.9)],
        "on": [("sur", 0.8)],
        "in": [("dans", 0.8)],
        "mat": [("tapis", 0.9)],
        "table": [("table", 0.9)],
        "house": [("maison", 0.9)],
        "book": [("livre", 0.9)],
        "car": [("voiture", 0.9)],
        "blue": [("bleu", 0.7), ("bleue", 0.3)],
        "red": [("rouge", 0.9)],
        "big": [("grand", 0.5), ("grande", 0.3), ("gros", 0.2)],
        "small": [("petit", 0.5), ("petite", 0.4)],
        "good": [("bon", 0.5), ("bonne", 0.3), ("bien", 0.2)],
        "man": [("homme", 0.9)],
        "woman": [("femme", 0.9)],
        "child": [("enfant", 0.9)],
        "eat": [("manger", 0.9)],
        "drink": [("boire", 0.9)],
        "run": [("courir", 0.9)],
        "walk": [("marcher", 0.9)],
        "today": [("aujourd'hui", 0.9)],
        "yesterday": [("hier", 0.9)],
        "tomorrow": [("demain", 0.9)],
        "yes": [("oui", 0.9)],
        "no": [("non", 0.9)],
        "please": [("s'il vous plaît", 0.6), ("s'il te plaît", 0.3)],
        "thank": [("merci", 0.9)],
        "you": [("vous", 0.5), ("tu", 0.3), ("toi", 0.2)],
        "i": [("je", 0.7), ("j'", 0.3)],
        "we": [("nous", 0.9)],
        "they": [("ils", 0.5), ("elles", 0.4)],

        # Common phrases
        "the cat": [("le chat", 0.9)],
        "the dog": [("le chien", 0.9)],
        "on the": [("sur le", 0.5), ("sur la", 0.4)],
        "in the": [("dans le", 0.5), ("dans la", 0.4)],
        "thank you": [("merci", 0.9)],
        "good morning": [("bonjour", 0.9)],
        "good evening": [("bonsoir", 0.9)],
        "good night": [("bonne nuit", 0.9)],
        "how are": [("comment allez", 0.5), ("comment vas", 0.4)],
        "i am": [("je suis", 0.9)],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(phrase_table, f, indent=2, ensure_ascii=False)


def create_default_lm(output_path: str):
    """Create a default French language model."""
    lm = {
        "1": {  # Unigrams
            "le": 0.05, "la": 0.04, "les": 0.03,
            "chat": 0.01, "chien": 0.01, "est": 0.02,
            "sur": 0.015, "dans": 0.015, "tapis": 0.005,
            "bonjour": 0.01, "monde": 0.005,
            "table": 0.008, "maison": 0.008, "livre": 0.007,
            "voiture": 0.006, "bleu": 0.005, "rouge": 0.005,
            "grand": 0.005, "petit": 0.005, "bon": 0.005,
            "homme": 0.008, "femme": 0.008, "enfant": 0.007,
            "merci": 0.01, "oui": 0.01, "non": 0.01,
        },
        "2": {  # Bigrams
            "le chat": 0.3, "le chien": 0.25, "la table": 0.2,
            "sur le": 0.3, "sur la": 0.25, "dans le": 0.3,
            "dans la": 0.25, "est sur": 0.2, "chat est": 0.15,
            "bonjour le": 0.1, "merci beaucoup": 0.5,
        },
        "3": {  # Trigrams
            "le chat est": 0.4, "est sur le": 0.3,
            "sur le tapis": 0.5, "dans la maison": 0.4,
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lm, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Create default models
    create_default_phrase_table("data/phrase_table.json")
    create_default_lm("data/lm_trigrams.json")

    # Test translation
    smt = ToySMT("data/phrase_table.json", "data/lm_trigrams.json")
    test_sentences = [
        "hello world",
        "the cat is on the mat",
        "thank you"
    ]

    for sentence in test_sentences:
        translation = smt.translate(sentence)
        print(f"EN: {sentence}")
        print(f"FR: {translation}\n")
