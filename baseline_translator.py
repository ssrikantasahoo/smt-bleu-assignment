"""
Baseline Word-by-Word Translation
==================================
Simple baseline translator using bilingual dictionary.

This provides a naive translation baseline for comparison:
- Direct word-for-word translation using dictionary
- No reordering (maintains source word order)
- Unknown words are copied from source
- No phrase-level translation

This demonstrates why SMT is necessary - word-by-word translation
produces poor quality output due to lack of:
- Phrase translations
- Word reordering
- Context-aware selection
- Target language fluency
"""

import json
import os
from typing import Dict, List, Optional


class BilingualDictionary:
    """Simple bilingual dictionary for word-by-word translation."""

    def __init__(self, dict_path: Optional[str] = None):
        """
        Initialize bilingual dictionary.

        Args:
            dict_path: Path to dictionary JSON file
        """
        self.dictionary = {}

        if dict_path and os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                self.dictionary = json.load(f)

    def translate_word(self, word: str) -> str:
        """
        Translate a single word.

        Args:
            word: Source word

        Returns:
            Translated word (or original if not in dictionary)
        """
        word_lower = word.lower()
        if word_lower in self.dictionary:
            # Return first (most common) translation
            translations = self.dictionary[word_lower]
            if isinstance(translations, list):
                return translations[0]
            else:
                return translations
        return word  # Return original if not found

    def add_translation(self, source_word: str, target_word: str):
        """Add a word translation to the dictionary."""
        source_lower = source_word.lower()
        if source_lower not in self.dictionary:
            self.dictionary[source_lower] = []
        if isinstance(self.dictionary[source_lower], str):
            self.dictionary[source_lower] = [self.dictionary[source_lower]]
        if target_word not in self.dictionary[source_lower]:
            self.dictionary[source_lower].append(target_word)


class BaselineTranslator:
    """
    Baseline word-by-word translator.

    This is intentionally simplistic to demonstrate the need for SMT.
    """

    def __init__(self, dictionary_path: Optional[str] = None):
        """
        Initialize baseline translator.

        Args:
            dictionary_path: Path to bilingual dictionary
        """
        self.dictionary = BilingualDictionary(dictionary_path)

    def translate(self, source_text: str) -> str:
        """
        Translate text word-by-word.

        Args:
            source_text: Source language text

        Returns:
            Word-by-word translation
        """
        tokens = source_text.lower().split()
        translated_tokens = []

        for token in tokens:
            # Remove punctuation for dictionary lookup
            clean_token = token.strip('.,!?;:')
            punctuation = token[len(clean_token):] if len(token) > len(clean_token) else ''

            # Translate word
            translated = self.dictionary.translate_word(clean_token)
            translated_tokens.append(translated + punctuation)

        return ' '.join(translated_tokens)

    def translate_with_alignment(self, source_text: str) -> Dict:
        """
        Translate with word alignment information.

        Args:
            source_text: Source text

        Returns:
            Dictionary with translation and alignment
        """
        source_tokens = source_text.lower().split()
        target_tokens = []
        alignments = []

        for i, token in enumerate(source_tokens):
            clean_token = token.strip('.,!?;:')
            punctuation = token[len(clean_token):] if len(token) > len(clean_token) else ''

            translated = self.dictionary.translate_word(clean_token)
            target_tokens.append(translated + punctuation)
            alignments.append((i, len(target_tokens) - 1, clean_token, translated))

        return {
            'source_tokens': source_tokens,
            'target_tokens': target_tokens,
            'translation': ' '.join(target_tokens),
            'alignments': alignments  # (src_idx, tgt_idx, src_word, tgt_word)
        }


def create_default_dictionary(output_path: str):
    """
    Create a default English-French dictionary.

    This is a subset of the phrase table for word-level translations.
    """
    dictionary = {
        # Common words
        "hello": ["bonjour", "salut"],
        "world": ["monde"],
        "the": ["le", "la", "les"],
        "cat": ["chat"],
        "dog": ["chien"],
        "is": ["est"],
        "are": ["sont"],
        "on": ["sur"],
        "in": ["dans"],
        "at": ["à"],
        "mat": ["tapis"],
        "table": ["table"],
        "house": ["maison"],
        "book": ["livre"],
        "car": ["voiture"],
        "blue": ["bleu"],
        "red": ["rouge"],
        "green": ["vert"],
        "yellow": ["jaune"],
        "black": ["noir"],
        "white": ["blanc"],
        "big": ["grand", "gros"],
        "small": ["petit"],
        "good": ["bon", "bien"],
        "bad": ["mauvais"],
        "man": ["homme"],
        "woman": ["femme"],
        "boy": ["garçon"],
        "girl": ["fille"],
        "child": ["enfant"],
        "children": ["enfants"],
        "eat": ["manger"],
        "drink": ["boire"],
        "run": ["courir"],
        "walk": ["marcher"],
        "sleep": ["dormir"],
        "work": ["travailler"],
        "play": ["jouer"],
        "read": ["lire"],
        "write": ["écrire"],
        "speak": ["parler"],
        "listen": ["écouter"],
        "see": ["voir"],
        "look": ["regarder"],
        "hear": ["entendre"],
        "today": ["aujourd'hui"],
        "yesterday": ["hier"],
        "tomorrow": ["demain"],
        "now": ["maintenant"],
        "later": ["plus tard"],
        "yes": ["oui"],
        "no": ["non"],
        "please": ["s'il vous plaît"],
        "thank": ["merci"],
        "thanks": ["merci"],
        "you": ["vous", "tu"],
        "i": ["je"],
        "we": ["nous"],
        "they": ["ils", "elles"],
        "he": ["il"],
        "she": ["elle"],
        "it": ["il", "elle", "ce"],
        "my": ["mon", "ma", "mes"],
        "your": ["votre", "ton", "ta"],
        "his": ["son", "sa"],
        "her": ["son", "sa"],
        "our": ["notre", "nos"],
        "their": ["leur", "leurs"],
        "this": ["ce", "ceci"],
        "that": ["cela", "ça"],
        "these": ["ces"],
        "those": ["ces"],
        "here": ["ici"],
        "there": ["là"],
        "where": ["où"],
        "when": ["quand"],
        "what": ["quoi", "que"],
        "who": ["qui"],
        "why": ["pourquoi"],
        "how": ["comment"],
        "very": ["très"],
        "too": ["trop", "aussi"],
        "also": ["aussi"],
        "not": ["ne", "pas"],
        "never": ["jamais"],
        "always": ["toujours"],
        "sometimes": ["parfois"],
        "often": ["souvent"],
        "with": ["avec"],
        "without": ["sans"],
        "for": ["pour"],
        "from": ["de"],
        "to": ["à"],
        "of": ["de"],
        "and": ["et"],
        "or": ["ou"],
        "but": ["mais"],
        "because": ["parce que"],
        "if": ["si"],
        "then": ["alors"],
        "so": ["donc"],
        "one": ["un", "une"],
        "two": ["deux"],
        "three": ["trois"],
        "four": ["quatre"],
        "five": ["cinq"],
        "six": ["six"],
        "seven": ["sept"],
        "eight": ["huit"],
        "nine": ["neuf"],
        "ten": ["dix"],
        "first": ["premier"],
        "second": ["deuxième"],
        "last": ["dernier"],
        "next": ["prochain"],
        "new": ["nouveau"],
        "old": ["vieux", "ancien"],
        "young": ["jeune"],
        "long": ["long"],
        "short": ["court"],
        "tall": ["grand"],
        "high": ["haut"],
        "low": ["bas"],
        "hot": ["chaud"],
        "cold": ["froid"],
        "warm": ["chaud"],
        "cool": ["frais"],
        "happy": ["heureux", "content"],
        "sad": ["triste"],
        "angry": ["en colère"],
        "tired": ["fatigué"],
        "hungry": ["affamé"],
        "thirsty": ["assoiffé"],
        "food": ["nourriture"],
        "water": ["eau"],
        "coffee": ["café"],
        "tea": ["thé"],
        "bread": ["pain"],
        "meat": ["viande"],
        "fish": ["poisson"],
        "fruit": ["fruit"],
        "vegetable": ["légume"],
        "time": ["temps", "heure"],
        "day": ["jour"],
        "night": ["nuit"],
        "morning": ["matin"],
        "afternoon": ["après-midi"],
        "evening": ["soir"],
        "week": ["semaine"],
        "month": ["mois"],
        "year": ["année", "an"],
        "city": ["ville"],
        "country": ["pays"],
        "street": ["rue"],
        "road": ["route"],
        "friend": ["ami"],
        "family": ["famille"],
        "father": ["père"],
        "mother": ["mère"],
        "brother": ["frère"],
        "sister": ["sœur"],
        "son": ["fils"],
        "daughter": ["fille"],
        "love": ["amour", "aimer"],
        "like": ["aimer"],
        "want": ["vouloir"],
        "need": ["avoir besoin"],
        "have": ["avoir"],
        "has": ["a"],
        "had": ["avait"],
        "make": ["faire"],
        "made": ["fait"],
        "take": ["prendre"],
        "give": ["donner"],
        "get": ["obtenir"],
        "go": ["aller"],
        "come": ["venir"],
        "know": ["savoir", "connaître"],
        "think": ["penser"],
        "can": ["pouvoir"],
        "will": ["volonté"],
        "would": ["voudrais"],
        "should": ["devrait"],
        "must": ["doit"],
        "may": ["peut"],
        "might": ["pourrait"],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Create default dictionary
    create_default_dictionary("data/bilingual_dict.json")

    # Test baseline translator
    translator = BaselineTranslator("data/bilingual_dict.json")

    test_sentences = [
        "hello world",
        "the cat is on the mat",
        "thank you very much",
        "i love this book",
        "the big dog runs fast"
    ]

    print("Baseline Word-by-Word Translation Test")
    print("=" * 60)

    for sentence in test_sentences:
        result = translator.translate_with_alignment(sentence)
        print(f"\nSource: {sentence}")
        print(f"Target: {result['translation']}")
        print("Alignment:")
        for src_idx, tgt_idx, src_word, tgt_word in result['alignments']:
            print(f"  {src_word} ({src_idx}) -> {tgt_word} ({tgt_idx})")
