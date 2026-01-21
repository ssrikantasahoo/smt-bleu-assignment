"""
BLEU Score Implementation from Scratch
Implements modified n-gram precision, brevity penalty, and cumulative BLEU
as specified in Papineni et al. (2002)
"""

import math
from collections import Counter
from typing import List, Tuple, Dict


def tokenize(text: str) -> List[str]:
    """
    Simple tokenization by splitting on whitespace.
    For production, use language-specific tokenizers.
    
    Args:
        text: Input text string
        
    Returns:
        List of tokens (words)
    """
    return text.strip().split()


def get_ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    """
    Extract n-grams from a list of tokens.
    
    Args:
        tokens: List of word tokens
        n: N-gram order (1 for unigrams, 2 for bigrams, etc.)
        
    Returns:
        List of n-gram tuples
    """
    if n <= 0:
        return []
    if len(tokens) < n:
        return []
    
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngrams.append(tuple(tokens[i:i+n]))
    return ngrams


def compute_modified_precision(candidate: str, references: List[str], n: int) -> Tuple[int, int, float]:
    """
    Compute modified n-gram precision with clipping.
    
    The modified precision counts clip each candidate n-gram's count
    by the maximum count of that n-gram in any single reference.
    
    Args:
        candidate: Candidate translation (system output)
        references: List of reference translations
        n: N-gram order
        
    Returns:
        Tuple of (clipped_count, total_count, precision)
        - clipped_count: Sum of clipped n-gram matches (numerator)
        - total_count: Total n-grams in candidate (denominator)
        - precision: clipped_count / total_count (0.0 if total_count is 0)
    """
    candidate_tokens = tokenize(candidate)
    candidate_ngrams = get_ngrams(candidate_tokens, n)
    
    # Count candidate n-grams
    candidate_counts = Counter(candidate_ngrams)
    
    # For each reference, count n-grams
    max_ref_counts = Counter()
    for reference in references:
        ref_tokens = tokenize(reference)
        ref_ngrams = get_ngrams(ref_tokens, n)
        ref_counts = Counter(ref_ngrams)
        
        # Update max counts across all references
        for ngram in ref_counts:
            max_ref_counts[ngram] = max(max_ref_counts.get(ngram, 0), ref_counts[ngram])
    
    # Clip candidate counts by max reference counts
    clipped_counts = {}
    for ngram in candidate_counts:
        clipped_counts[ngram] = min(candidate_counts[ngram], max_ref_counts.get(ngram, 0))
    
    # Sum up clipped counts
    clipped_count = sum(clipped_counts.values())
    total_count = len(candidate_ngrams)
    
    # Compute precision
    if total_count == 0:
        precision = 0.0
    else:
        precision = clipped_count / total_count
    
    return clipped_count, total_count, precision


def compute_brevity_penalty(candidate: str, references: List[str]) -> Tuple[float, int, int]:
    """
    Compute brevity penalty to penalize short translations.
    
    BP = 1 if c > r
    BP = exp(1 - r/c) if c <= r
    
    where:
    - c = length of candidate
    - r = effective reference length (closest to candidate)
    
    Args:
        candidate: Candidate translation
        references: List of reference translations
        
    Returns:
        Tuple of (brevity_penalty, c, r)
        - brevity_penalty: BP value
        - c: candidate length
        - r: effective reference length
    """
    candidate_tokens = tokenize(candidate)
    c = len(candidate_tokens)
    
    # Find the reference length closest to candidate length
    ref_lengths = [len(tokenize(ref)) for ref in references]
    
    if not ref_lengths:
        # No references: BP = 0
        return 0.0, c, 0
    
    # Choose r as the reference length closest to c
    r = min(ref_lengths, key=lambda ref_len: abs(ref_len - c))
    
    # Compute brevity penalty
    if c == 0:
        bp = 0.0
    elif c > r:
        bp = 1.0
    else:
        bp = math.exp(1 - r / c)
    
    return bp, c, r


def compute_bleu(candidate: str, references: List[str], max_n: int = 4) -> Dict:
    """
    Compute BLEU score with all intermediate statistics.
    
    BLEU = BP * exp(sum_{n=1}^{N} w_n * log(p_n))
    
    where:
    - BP = brevity penalty
    - p_n = modified n-gram precision
    - w_n = uniform weights (1/N for each n)
    - N = max_n (typically 4)
    
    Args:
        candidate: Candidate translation
        references: List of reference translations (can be multiple)
        max_n: Maximum n-gram order (default 4 for BLEU-4)
        
    Returns:
        Dictionary containing:
        - bleu_score: Cumulative BLEU score
        - bleu_1, bleu_2, bleu_3, bleu_4: Individual BLEU-n scores
        - precisions: List of n-gram precisions
        - bp: Brevity penalty
        - length_ratio: c/r
        - candidate_length: c
        - reference_length: r
        - ngram_stats: Detailed n-gram statistics
    """
    # Compute brevity penalty
    bp, c, r = compute_brevity_penalty(candidate, references)
    
    # Compute modified precisions for n=1 to max_n
    precisions = []
    ngram_stats = []
    
    for n in range(1, max_n + 1):
        clipped_count, total_count, precision = compute_modified_precision(candidate, references, n)
        precisions.append(precision)
        ngram_stats.append({
            'n': n,
            'clipped_count': clipped_count,
            'total_count': total_count,
            'precision': precision
        })
    
    # Compute cumulative BLEU score (geometric mean of precisions)
    # Use log-space to avoid underflow
    if all(p > 0 for p in precisions):
        # Geometric mean: exp(sum(log(p_n)) / N)
        log_precisions = [math.log(p) for p in precisions]
        avg_log_precision = sum(log_precisions) / len(log_precisions)
        bleu_score = bp * math.exp(avg_log_precision)
    else:
        # If any precision is 0, BLEU is 0
        bleu_score = 0.0
    
    # Compute individual BLEU-n scores
    bleu_scores_individual = {}
    for i, n in enumerate(range(1, max_n + 1)):
        if precisions[i] > 0:
            bleu_n = bp * precisions[i]
        else:
            bleu_n = 0.0
        bleu_scores_individual[f'bleu_{n}'] = bleu_n
    
    result = {
        'bleu_score': bleu_score,
        **bleu_scores_individual,
        'precisions': precisions,
        'bp': bp,
        'length_ratio': c / r if r > 0 else 0.0,
        'candidate_length': c,
        'reference_length': r,
        'ngram_stats': ngram_stats
    }
    
    return result


def compute_corpus_bleu(candidates: List[str], references_list: List[List[str]], max_n: int = 4) -> Dict:
    """
    Compute corpus-level BLEU score.
    
    This aggregates statistics across all sentences before computing BLEU,
    which is the standard corpus BLEU computation.
    
    Args:
        candidates: List of candidate translations
        references_list: List of reference lists (one list per candidate)
        max_n: Maximum n-gram order
        
    Returns:
        Dictionary with corpus BLEU and statistics
    """
    # Aggregate counts across corpus
    total_clipped_counts = [0] * max_n
    total_counts = [0] * max_n
    total_c = 0
    total_r = 0
    
    for candidate, references in zip(candidates, references_list):
        # Accumulate n-gram statistics
        for n in range(1, max_n + 1):
            clipped_count, total_count, _ = compute_modified_precision(candidate, references, n)
            total_clipped_counts[n-1] += clipped_count
            total_counts[n-1] += total_count
        
        # Accumulate lengths
        _, c, r = compute_brevity_penalty(candidate, references)
        total_c += c
        total_r += r
    
    # Compute corpus-level precisions
    precisions = []
    for i in range(max_n):
        if total_counts[i] == 0:
            precisions.append(0.0)
        else:
            precisions.append(total_clipped_counts[i] / total_counts[i])
    
    # Compute corpus-level BP
    if total_c > total_r:
        bp = 1.0
    elif total_c == 0:
        bp = 0.0
    else:
        bp = math.exp(1 - total_r / total_c)
    
    # Compute corpus BLEU
    if all(p > 0 for p in precisions):
        log_precisions = [math.log(p) for p in precisions]
        avg_log_precision = sum(log_precisions) / len(log_precisions)
        bleu_score = bp * math.exp(avg_log_precision)
    else:
        bleu_score = 0.0
    
    return {
        'corpus_bleu': bleu_score,
        'precisions': precisions,
        'bp': bp,
        'total_candidate_length': total_c,
        'total_reference_length': total_r
    }


# Convenience functions for testing
def bleu_score(candidate: str, references: List[str]) -> float:
    """Quick function to get just the BLEU score"""
    result = compute_bleu(candidate, references)
    return result['bleu_score']
