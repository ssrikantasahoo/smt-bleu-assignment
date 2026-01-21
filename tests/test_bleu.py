"""
Unit tests for BLEU implementation
Tests all components: n-gram extraction, modified precision, brevity penalty, BLEU computation
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bleu import (
    tokenize, get_ngrams, compute_modified_precision,
    compute_brevity_penalty, compute_bleu, bleu_score
)


class TestTokenization:
    """Test tokenization function"""
    
    def test_basic_tokenization(self):
        assert tokenize("hello world") == ["hello", "world"]
        assert tokenize("one two three") == ["one", "two", "three"]
    
    def test_empty_string(self):
        assert tokenize("") == []
        assert tokenize("   ") == []
    
    def test_extra_spaces(self):
        assert tokenize("  hello   world  ") == ["hello", "world"]


class TestNgramExtraction:
    """Test n-gram extraction"""
    
    def test_unigrams(self):
        tokens = ["the", "cat", "sat"]
        ngrams = get_ngrams(tokens, 1)
        assert ngrams == [("the",), ("cat",), ("sat",)]
    
    def test_bigrams(self):
        tokens = ["the", "cat", "sat"]
        ngrams = get_ngrams(tokens, 2)
        assert ngrams == [("the", "cat"), ("cat", "sat")]
    
    def test_trigrams(self):
        tokens = ["the", "cat", "sat"]
        ngrams = get_ngrams(tokens, 3)
        assert ngrams == [("the", "cat", "sat")]
    
    def test_ngram_longer_than_tokens(self):
        tokens = ["the", "cat"]
        ngrams = get_ngrams(tokens, 5)
        assert ngrams == []
    
    def test_empty_tokens(self):
        assert get_ngrams([], 1) == []
        assert get_ngrams([], 2) == []


class TestModifiedPrecision:
    """Test modified n-gram precision with clipping"""
    
    def test_perfect_match(self):
        candidate = "the cat sat on the mat"
        references = ["the cat sat on the mat"]
        clipped, total, precision = compute_modified_precision(candidate, references, 1)
        assert precision == 1.0
        assert clipped == total
    
    def test_partial_match(self):
        candidate = "the the the"
        references = ["the cat"]
        # Candidate has 3 "the", but reference has only 1
        # Clipped count should be 1
        clipped, total, precision = compute_modified_precision(candidate, references, 1)
        assert total == 3
        assert clipped == 1
        assert precision == 1/3
    
    def test_multiple_references(self):
        candidate = "the cat"
        references = ["a cat", "the dog", "the cat"]
        # "the": max in refs is 1, candidate has 1 -> 1
        # "cat": max in refs is 1, candidate has 1 -> 1
        clipped, total, precision = compute_modified_precision(candidate, references, 1)
        assert clipped == 2
        assert total == 2
        assert precision == 1.0
    
    def test_no_match(self):
        candidate = "xyz abc"
        references = ["the cat sat"]
        clipped, total, precision = compute_modified_precision(candidate, references, 1)
        assert clipped == 0
        assert total == 2
        assert precision == 0.0
    
    def test_empty_candidate(self):
        candidate = ""
        references = ["the cat"]
        clipped, total, precision = compute_modified_precision(candidate, references, 1)
        assert total == 0
        assert clipped == 0
        assert precision == 0.0
    
    def test_bigram_precision(self):
        candidate = "the cat sat on the mat"
        references = ["the cat sat on the mat"]
        clipped, total, precision = compute_modified_precision(candidate, references, 2)
        # Bigrams: ("the", "cat"), ("cat", "sat"), ("sat", "on"), ("on", "the"), ("the", "mat")
        # All match
        assert precision == 1.0
        assert total == 5


class TestBrevityPenalty:
    """Test brevity penalty computation"""
    
    def test_candidate_longer_than_reference(self):
        candidate = "the cat sat on the mat"  # 6 words
        references = ["the cat"]  # 2 words
        bp, c, r = compute_brevity_penalty(candidate, references)
        assert bp == 1.0
        assert c == 6
        assert r == 2
    
    def test_candidate_equal_to_reference(self):
        candidate = "the cat sat"
        references = ["the dog sat"]
        bp, c, r = compute_brevity_penalty(candidate, references)
        assert bp == 1.0
        assert c == 3
        assert r == 3
    
    def test_candidate_shorter_than_reference(self):
        candidate = "the cat"  # 2 words
        references = ["the cat sat on the mat"]  # 6 words
        bp, c, r = compute_brevity_penalty(candidate, references)
        assert c == 2
        assert r == 6
        # BP = exp(1 - 6/2) = exp(1 - 3) = exp(-2) ≈ 0.135
        assert bp == pytest.approx(0.135, abs=0.01)
    
    def test_multiple_references_choose_closest(self):
        candidate = "the cat sat"  # 3 words
        references = ["the cat", "the cat sat on the mat"]  # 2 and 6 words
        bp, c, r = compute_brevity_penalty(candidate, references)
        # Should choose r=2 (closest to c=3, diff=1) not r=6 (diff=3)
        # Wait, actually closest means minimum absolute difference
        # |3-2| = 1, |3-6| = 3, so r=2
        assert c == 3
        assert r == 2
        # c > r, so BP = 1
        assert bp == 1.0
    
    def test_empty_candidate(self):
        candidate = ""
        references = ["the cat"]
        bp, c, r = compute_brevity_penalty(candidate, references)
        assert c == 0
        assert bp == 0.0


class TestBLEUScore:
    """Test complete BLEU score computation"""
    
    def test_perfect_translation(self):
        candidate = "the cat sat on the mat"
        references = ["the cat sat on the mat"]
        result = compute_bleu(candidate, references, max_n=4)
        assert result['bleu_score'] == 1.0
        assert all(p == 1.0 for p in result['precisions'])
        assert result['bp'] == 1.0
    
    def test_empty_candidate(self):
        candidate = ""
        references = ["the cat"]
        result = compute_bleu(candidate, references, max_n=4)
        assert result['bleu_score'] == 0.0
    
    def test_no_ngram_match(self):
        candidate = "xyz abc def ghi"
        references = ["the cat sat on the mat"]
        result = compute_bleu(candidate, references, max_n=4)
        # No unigram matches, so BLEU = 0
        assert result['bleu_score'] == 0.0
        assert result['precisions'][0] == 0.0
    
    def test_partial_match_with_bp(self):
        candidate = "the cat"
        references = ["the cat sat on the mat"]
        result = compute_bleu(candidate, references, max_n=4)
        # Unigram: 2/2 = 1.0
        # Bigram: 1/1 = 1.0
        # Trigram: 0/0 = 0.0 (no trigrams in candidate)
        # 4-gram: 0/0 = 0.0
        # c=2, r=6, BP = exp(1-3) ≈ 0.135
        assert result['bp'] == pytest.approx(0.135, abs=0.01)
        # Since trigram and 4-gram have 0 counts, precision is 0, BLEU = 0
        assert result['bleu_score'] == 0.0
    
    def test_hindi_example(self):
        # Test with actual Hindi text
        candidate = "नमस्ते आप कैसे हैं"
        references = ["नमस्ते आप कैसे हैं"]
        result = compute_bleu(candidate, references, max_n=4)
        assert result['bleu_score'] == 1.0
    
    def test_multiple_references(self):
        candidate = "the cat sat"
        references = [
            "the cat sat on the mat",
            "a cat was sitting",
            "the cat sat"
        ]
        result = compute_bleu(candidate, references, max_n=4)
        # Third reference is exact match for unigrams, bigrams, trigrams
        # But candidate has no 4-grams, so BLEU will be 0
        # This is correct behavior - BLEU needs all n-grams
        # For sentence-level, use smaller max_n
        assert result['precisions'][0] == 1.0  # Unigram perfect
        assert result['precisions'][1] == 1.0  # Bigram perfect
        assert result['precisions'][2] == 1.0  # Trigram perfect
    
    def test_ngram_stats_structure(self):
        candidate = "the cat sat"
        references = ["the cat sat on mat"]
        result = compute_bleu(candidate, references, max_n=4)
        
        assert len(result['ngram_stats']) == 4
        for i, stat in enumerate(result['ngram_stats']):
            assert stat['n'] == i + 1
            assert 'clipped_count' in stat
            assert 'total_count' in stat
            assert 'precision' in stat
    
    def test_individual_bleu_scores(self):
        candidate = "the cat sat on the mat"
        references = ["the cat sat on the mat"]
        result = compute_bleu(candidate, references, max_n=4)
        
        assert 'bleu_1' in result
        assert 'bleu_2' in result
        assert 'bleu_3' in result
        assert 'bleu_4' in result


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_single_word_candidate_and_reference(self):
        candidate = "cat"
        references = ["cat"]
        result = compute_bleu(candidate, references, max_n=4)
        # Unigram matches, but no bi/tri/4-grams possible
        # BLEU should be 0 due to missing higher-order n-grams
        assert result['bleu_score'] == 0.0
    
    def test_different_length_candidates(self):
        # Use longer sentences to ensure 4-grams exist
        candidate1 = "the cat sat on"  # Partial match
        candidate2 = "the cat sat on the mat"  # Exact match
        references = ["the cat sat on the mat"]

        score1 = bleu_score(candidate1, references)
        score2 = bleu_score(candidate2, references)

        # Score2 should be higher (exact match, better BP)
        assert score2 > score1
    
    def test_repeated_words(self):
        candidate = "the the the the"
        references = ["the cat sat on the mat"]
        result = compute_bleu(candidate, references, max_n=4)
        # Modified precision should clip "the" count
        # Reference has 2 "the"s, candidate has 4
        # Clipped count = 2, total = 4, precision = 0.5
        assert result['precisions'][0] == 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
