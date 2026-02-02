# Task B: Strategy to Improve BLEU in Statistical Machine Translation

## Objective
This note explains practical, conceptually grounded methods to improve BLEU for an SMT system (English->Hindi), aligned with assignment requirements.

## 1) More Training Data and Larger Parallel Corpora
BLEU improves when the phrase table and translation probabilities are estimated from larger parallel corpora. More aligned sentence pairs increase phrase coverage and reduce sparsity.

**Example:**
If the training corpus rarely contains "take off" in an aviation context, SMT may translate word-by-word incorrectly. Adding more parallel aviation sentences allows the phrase table to learn the correct phrase-level mapping.

**Why BLEU rises:**
- higher unigram and bigram overlap (better lexical coverage)
- improved higher-order overlap through better phrase selection

## 2) Better Vocabulary Coverage
Unknown words (OOVs) harm adequacy and reduce n-gram matches. Coverage improves via:
- larger bilingual lexicons
- proper tokenization/normalization
- transliteration/backoff for named entities

**Example:**
If "microcontroller" is missing, the system may copy English text. Adding domain vocabulary yields better candidate-reference alignment and higher BLEU precision counts.

## 3) Better Language Models
In phrase-based SMT, the language model (LM) drives target-side fluency and disambiguation.

### 3.1 Higher-order n-grams
Moving from trigram to 5-gram LM generally improves local fluency and phrase continuity.

### 3.2 Stronger smoothing
Smoothing (e.g., Kneser-Ney) avoids zero-probability spikes and supports robust decoding.

### 3.3 Neural LM integration (optional)
Neural LMs can improve long-range coherence beyond count-based n-grams.

**Why BLEU rises:**
Fluency improvements increase 2-gram/3-gram/4-gram overlap with references.

## 4) Domain-Specific Parallel Corpora and Domain Adaptation
SMT quality drops under domain mismatch (e.g., training on news, testing on medical text). Domain adaptation aligns terminology and style.

**Approaches:**
- in-domain fine-tuning of phrase/reordering models
- interpolation of in-domain and general-domain LMs
- data weighting to prioritize in-domain sentence pairs

**Example:**
"discharge" in medical domain should map to clinical meaning, not general "release" sense. Domain-specific data reduces ambiguity and improves BLEU.

## 5) Reducing Ambiguity
Ambiguity can be reduced by:
- richer phrase context (longer phrase entries)
- reordering features and lexicalized models
- better target LM context

**Example:**
English "bank" in financial vs river context should produce different Hindi translations. Context-aware decoding improves adequacy and metric overlap.

## Practical Recommendation (Submission-Oriented)
For this assignment, the highest-impact and realistic sequence is:
1. Expand clean parallel corpus first.
2. Upgrade LM (higher order + better smoothing).
3. Add in-domain corpus and tune feature weights on dev data.
4. Report BLEU with 1-gram to 4-gram precision and brevity penalty before/after each step.

## Conclusion
BLEU improvement in SMT is primarily data- and modeling-driven. Larger high-quality parallel corpora improve adequacy, stronger language models improve fluency, and domain adaptation reduces ambiguity. Together, these changes raise modified n-gram precision and reduce brevity/coverage errors, yielding more reliable BLEU gains.
