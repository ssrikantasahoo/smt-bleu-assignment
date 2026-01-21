"""
BLEU Score Implementation from Scratch
===========================================
Implements the BLEU (Bilingual Evaluation Understudy) metric for evaluating
machine translation quality as described in Papineni et al. (2002).

This implementation includes:
- Modified n-gram precision with clipping
- Brevity penalty
- Geometric mean of n-gram precisions
- Detailed statistics for transparency
"""

from collections import Counter, defaultdict
from typing import List, Tuple, Dict
import math


class BLEUScorer:
    """
    BLEU Score calculator with detailed statistics.

    Implements modified n-gram precision with clipping and brevity penalty.
    """

    def __init__(self, max_n: int = 4, weights: List[float] = None, smoothing: bool = True):
        """
        Initialize BLEU scorer.

        Args:
            max_n: Maximum n-gram order (default: 4 for BLEU-4)
            weights: Weights for each n-gram order (default: uniform weights)
            smoothing: Apply smoothing for zero precisions (default: True)
        """
        self.max_n = max_n
        self.smoothing = smoothing
        if weights is None:
            # Uniform weights: 1/n for each n-gram
            self.weights = [1.0 / max_n] * max_n
        else:
            assert len(weights) == max_n, "Weights must match max_n"
            assert abs(sum(weights) - 1.0) < 1e-6, "Weights must sum to 1"
            self.weights = weights

    def get_ngrams(self, tokens: List[str], n: int) -> Counter:
        """
        Extract n-grams from tokenized sentence.

        Args:
            tokens: List of tokens
            n: N-gram order

        Returns:
            Counter of n-grams
        """
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams.append(ngram)
        return Counter(ngrams)

    def compute_modified_precision(
        self,
        candidate_tokens: List[str],
        reference_tokens_list: List[List[str]],
        n: int
    ) -> Tuple[int, int, float]:
        """
        Compute modified n-gram precision with clipping.

        Modified precision counts n-grams in candidate but clips the count
        to the maximum count in any reference translation.

        Args:
            candidate_tokens: Tokenized candidate translation
            reference_tokens_list: List of tokenized reference translations
            n: N-gram order

        Returns:
            Tuple of (numerator, denominator, precision)
        """
        candidate_ngrams = self.get_ngrams(candidate_tokens, n)

        # Get maximum counts from all references
        max_ref_counts = Counter()
        for ref_tokens in reference_tokens_list:
            ref_ngrams = self.get_ngrams(ref_tokens, n)
            for ngram in ref_ngrams:
                max_ref_counts[ngram] = max(max_ref_counts[ngram], ref_ngrams[ngram])

        # Clip candidate counts
        clipped_counts = {}
        for ngram in candidate_ngrams:
            clipped_counts[ngram] = min(candidate_ngrams[ngram], max_ref_counts[ngram])

        # Calculate precision
        numerator = sum(clipped_counts.values())
        denominator = sum(candidate_ngrams.values())

        # For precision calculation, avoid division by zero
        # But return actual denominator (even if 0) for corpus-level aggregation
        precision = numerator / denominator if denominator > 0 else 0.0

        return numerator, denominator, precision

    def compute_brevity_penalty(
        self,
        candidate_length: int,
        reference_lengths: List[int]
    ) -> float:
        """
        Compute brevity penalty.

        The brevity penalty penalizes candidates that are shorter than references.
        BP = 1 if c > r, else exp(1 - r/c)
        where c is candidate length and r is reference length (closest to c).

        Args:
            candidate_length: Length of candidate translation
            reference_lengths: Lengths of reference translations

        Returns:
            Brevity penalty (0 < BP <= 1)
        """
        if candidate_length == 0:
            return 0.0

        # Find reference length closest to candidate length
        closest_ref_length = min(reference_lengths,
                                  key=lambda ref_len: abs(ref_len - candidate_length))

        if candidate_length >= closest_ref_length:
            return 1.0
        else:
            return math.exp(1 - closest_ref_length / candidate_length)

    def compute_bleu(
        self,
        candidate: str,
        references: List[str],
        tokenize: bool = True
    ) -> Dict:
        """
        Compute BLEU score with detailed statistics.

        Args:
            candidate: Candidate translation (string)
            references: List of reference translations (strings)
            tokenize: Whether to tokenize inputs (default: True)

        Returns:
            Dictionary containing:
                - bleu: Final BLEU score
                - precisions: List of n-gram precisions
                - precision_details: List of (numerator, denominator, precision) tuples
                - brevity_penalty: BP value
                - candidate_length: Length of candidate
                - reference_length: Closest reference length
                - geometric_mean: Geometric mean of precisions
        """
        # Tokenization (simple whitespace tokenization + lowercase)
        if tokenize:
            candidate_tokens = candidate.lower().split()
            reference_tokens_list = [ref.lower().split() for ref in references]
        else:
            candidate_tokens = candidate
            reference_tokens_list = references

        # Handle edge cases
        if len(candidate_tokens) == 0:
            return {
                'bleu': 0.0,
                'precisions': [0.0] * self.max_n,
                'precision_details': [(0, 0, 0.0)] * self.max_n,
                'brevity_penalty': 0.0,
                'candidate_length': 0,
                'reference_length': min([len(ref) for ref in reference_tokens_list]) if reference_tokens_list else 0,
                'geometric_mean': 0.0
            }

        # Compute modified precisions for all n-grams
        precisions = []
        precision_details = []

        # Use only n-gram orders up to candidate length (avoid zero denominators)
        effective_max_n = min(self.max_n, len(candidate_tokens))

        for n in range(1, self.max_n + 1):
            if n <= len(candidate_tokens):
                num, denom, prec = self.compute_modified_precision(
                    candidate_tokens, reference_tokens_list, n
                )
                precisions.append(prec)
                precision_details.append((num, denom, prec))
            else:
                # For n-grams longer than candidate, use smoothed precision
                # This prevents BLEU from being zero for short candidates
                precisions.append(0.0)
                precision_details.append((0, 0, 0.0))

        # Compute geometric mean of precisions
        # Use log to avoid numerical issues
        # Only consider non-zero precisions for effective max_n
        effective_precisions = precisions[:effective_max_n]
        effective_weights = self.weights[:effective_max_n]

        if effective_max_n > 0:
            # Renormalize weights
            weight_sum = sum(effective_weights)
            if weight_sum > 0:
                normalized_weights = [w / weight_sum for w in effective_weights]
            else:
                normalized_weights = [1.0 / effective_max_n] * effective_max_n

            # Apply smoothing if enabled (add small epsilon to zero precisions)
            if self.smoothing:
                smoothed_precisions = [max(p, 1e-10) for p in effective_precisions]
            else:
                smoothed_precisions = effective_precisions

            # Check if all precisions are zero (even after smoothing attempt with actual values)
            if all(p == 0 for p in effective_precisions):
                geometric_mean = 0.0
            else:
                log_precision_sum = sum(w * math.log(p) for w, p in zip(normalized_weights, smoothed_precisions))
                geometric_mean = math.exp(log_precision_sum)
        else:
            # If effective_max_n is 0, BLEU is 0
            geometric_mean = 0.0

        # Compute brevity penalty
        candidate_length = len(candidate_tokens)
        reference_lengths = [len(ref) for ref in reference_tokens_list]
        bp = self.compute_brevity_penalty(candidate_length, reference_lengths)

        # Final BLEU score
        bleu_score = bp * geometric_mean

        # Find closest reference length for reporting
        closest_ref_length = min(reference_lengths,
                                  key=lambda ref_len: abs(ref_len - candidate_length))

        return {
            'bleu': bleu_score,
            'precisions': precisions,
            'precision_details': precision_details,
            'brevity_penalty': bp,
            'candidate_length': candidate_length,
            'reference_length': closest_ref_length,
            'geometric_mean': geometric_mean,
            'weights': self.weights
        }

    def compute_bleu_corpus(
        self,
        candidates: List[str],
        references_list: List[List[str]]
    ) -> Dict:
        """
        Compute corpus-level BLEU score.

        Args:
            candidates: List of candidate translations
            references_list: List of reference lists (one list per candidate)

        Returns:
            Dictionary with BLEU score and statistics
        """
        assert len(candidates) == len(references_list), \
            "Number of candidates must match number of reference lists"

        # Aggregate counts across corpus
        total_numerators = [0] * self.max_n
        total_denominators = [0] * self.max_n
        total_candidate_length = 0
        total_reference_length = 0

        for candidate, references in zip(candidates, references_list):
            candidate_tokens = candidate.lower().split()
            reference_tokens_list = [ref.lower().split() for ref in references]

            total_candidate_length += len(candidate_tokens)

            reference_lengths = [len(ref) for ref in reference_tokens_list]
            closest_ref_length = min(reference_lengths,
                                      key=lambda ref_len: abs(ref_len - len(candidate_tokens)))
            total_reference_length += closest_ref_length

            for n in range(1, self.max_n + 1):
                num, denom, _ = self.compute_modified_precision(
                    candidate_tokens, reference_tokens_list, n
                )
                total_numerators[n-1] += num
                total_denominators[n-1] += denom

        # Compute precisions
        precisions = []
        for num, denom in zip(total_numerators, total_denominators):
            precisions.append(num / denom if denom > 0 else 0.0)

        # Apply smoothing if enabled
        if self.smoothing:
            smoothed_precisions = [max(p, 1e-10) if d > 0 else 0.0
                                   for p, d in zip(precisions, total_denominators)]
        else:
            smoothed_precisions = precisions

        # Geometric mean (only use n-gram orders with valid denominators)
        valid_indices = [i for i, d in enumerate(total_denominators) if d > 0]

        if valid_indices and not all(precisions[i] == 0 for i in valid_indices):
            # Use only valid n-gram orders
            valid_precisions = [smoothed_precisions[i] for i in valid_indices]
            valid_weights = [self.weights[i] for i in valid_indices]

            # Renormalize weights
            weight_sum = sum(valid_weights)
            if weight_sum > 0:
                normalized_weights = [w / weight_sum for w in valid_weights]
            else:
                normalized_weights = [1.0 / len(valid_weights)] * len(valid_weights)

            log_precision_sum = sum(w * math.log(p) for w, p in zip(normalized_weights, valid_precisions))
            geometric_mean = math.exp(log_precision_sum)
        else:
            geometric_mean = 0.0

        # Brevity penalty (corpus level)
        if total_candidate_length >= total_reference_length:
            bp = 1.0
        else:
            bp = math.exp(1 - total_reference_length / total_candidate_length) \
                if total_candidate_length > 0 else 0.0

        bleu_score = bp * geometric_mean

        return {
            'bleu': bleu_score,
            'precisions': precisions,
            'brevity_penalty': bp,
            'candidate_length': total_candidate_length,
            'reference_length': total_reference_length,
            'geometric_mean': geometric_mean
        }


def compute_bleu(candidate: str, references: List[str], max_n: int = 4) -> float:
    """
    Convenience function to compute BLEU score.

    Args:
        candidate: Candidate translation
        references: List of reference translations
        max_n: Maximum n-gram order

    Returns:
        BLEU score (float between 0 and 1)
    """
    scorer = BLEUScorer(max_n=max_n)
    result = scorer.compute_bleu(candidate, references)
    return result['bleu']


if __name__ == "__main__":
    # Example usage
    scorer = BLEUScorer(max_n=4)

    # Example 1: Perfect match
    candidate = "the cat is on the mat"
    references = ["the cat is on the mat"]
    result = scorer.compute_bleu(candidate, references)
    print(f"Example 1 - Perfect match:")
    print(f"BLEU score: {result['bleu']:.4f}")
    print(f"Precisions: {result['precisions']}")
    print(f"BP: {result['brevity_penalty']:.4f}\n")

    # Example 2: Partial match
    candidate = "the cat sat on the mat"
    references = ["the cat is on the mat", "there is a cat on the mat"]
    result = scorer.compute_bleu(candidate, references)
    print(f"Example 2 - Partial match:")
    print(f"BLEU score: {result['bleu']:.4f}")
    print(f"Precisions: {result['precisions']}")
    print(f"BP: {result['brevity_penalty']:.4f}\n")

    # Example 3: Short candidate (brevity penalty)
    candidate = "the cat"
    references = ["the cat is on the mat"]
    result = scorer.compute_bleu(candidate, references)
    print(f"Example 3 - Short candidate:")
    print(f"BLEU score: {result['bleu']:.4f}")
    print(f"Precisions: {result['precisions']}")
    print(f"BP: {result['brevity_penalty']:.4f}\n")
