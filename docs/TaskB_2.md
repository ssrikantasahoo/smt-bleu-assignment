# Task B: Improving BLEU Scores in Statistical Machine Translation

**Course:** Statistical Machine Translation  
**Assignment:** Part 1 - Task B  
**Topic:** Strategies for BLEU Score Improvement  
**Language Pair:** English → Hindi

---

## Abstract

BLEU (Bilingual Evaluation Understudy) is the most widely used automatic metric for evaluating machine translation quality. This document explores practical strategies to improve BLEU scores in statistical machine translation systems, focusing on data-driven approaches, language model enhancements, and domain adaptation techniques. We provide concrete experimental designs that can be empirically validated on English→Hindi translation tasks.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Strategy 1: Increase Training Data](#strategy-1-increase-training-data)
3. [Strategy 2: Improve Language Model Quality](#strategy-2-improve-language-model-quality)
4. [Strategy 3: Domain-Specific Parallel Corpora](#strategy-3-domain-specific-parallel-corpora)
5. [Strategy 4: Advanced Preprocessing](#strategy-4-advanced-preprocessing)
6. [Strategy 5: Tuning and Optimization](#strategy-5-tuning-and-optimization)
7. [Experimental Design](#experimental-design)
8. [Expected Results](#expected-results)
9. [Conclusion](#conclusion)
10. [References](#references)

---

## Introduction

### Understanding BLEU

BLEU measures translation quality through n-gram precision with a brevity penalty:

$$
\text{BLEU} = \text{BP} \cdot \exp\left(\sum_{n=1}^{4} \frac{1}{4} \log p_n\right)
$$

Where:
- $p_n$ = modified n-gram precision
- $\text{BP} = \min(1, e^{1-r/c})$ = brevity penalty

### Factors Affecting BLEU

BLEU scores are influenced by:
1. **Translation accuracy** (word choice)
2. **Fluency** (word order, grammar)
3. **Coverage** (completeness, no omissions)
4. **Length** (avoiding too short/long translations)

**Goal:** Improve these factors through systematic enhancements to the SMT pipeline.

---

## Strategy 1: Increase Training Data

### Rationale

More parallel data → better phrase table coverage → more accurate translations

**Why it works:**
- Increases phrase pair diversity
- Improves probability estimates
- Covers more vocabulary
- Reduces data sparsity

### Quantitative Analysis

#### Experiment 1A: Scaling Training Data Size

| Training Size | Vocabulary Coverage | Expected BLEU | Improvement |
|---------------|---------------------|---------------|-------------|
| 10K sentences | ~5K words/lang | 15-20 | Baseline |
| 50K sentences | ~15K words/lang | 25-30 | +8-12 |
| 100K sentences | ~25K words/lang | 30-35 | +13-18 |
| 500K sentences | ~50K words/lang | 35-40 | +18-23 |
| 1M+ sentences | ~70K words/lang | 40-45 | +23-28 |

**Data Source Recommendations for English-Hindi:**
- **IITB Hindi-English Corpus**: 1.5M sentence pairs
- **OPUS OpenSubtitles**: 300K+ pairs
- **PIB (Press Information Bureau)**: Government documents
- **Wikipedia parallel articles**: ~50K pairs
- **Tatoeba**: 10K+ pairs

### Implementation Steps

```bash
# Step 1: Download IITB corpus
wget http://www.cfilt.iitb.ac.in/iitb_parallel/iitb_corpus_download/parallel.tgz
tar -xzf parallel.tgz

# Step 2: Concatenate with existing data
cat existing_train.en iitb_parallel.en > combined_train.en
cat existing_train.hi iitb_parallel.hi > combined_train.hi

# Step 3: Retrain Moses model
# (Follow training pipeline in README.md)

# Step 4: Evaluate BLEU improvement
moses -f new_model/moses.ini < test.en > test.hyp
perl multi-bleu.perl test.ref < test.hyp
```

### Expected BLEU Gains

- **10K → 50K sentences**: +8-12 BLEU points
- **50K → 100K sentences**: +5-8 BLEU points
- **100K → 500K sentences**: +3-5 BLEU points

**Diminishing returns beyond 1M sentences** (data quality becomes more important than quantity).

---

## Strategy 2: Improve Language Model Quality

### Rationale

Better LM → more fluent translations → higher n-gram matches → higher BLEU

### 2.1 Higher-Order N-grams

#### Experiment 2A: Varying N-gram Order

| LM Order | Perplexity | Expected BLEU | Notes |
|----------|------------|---------------|-------|
| Bigram | High (~500) | 20-25 | Poor fluency |
| Trigram | Medium (~200) | 28-33 | Standard |
| 4-gram | Lower (~150) | 32-36 | Better fluency |
| 5-gram | Lowest (~130) | 34-38 | Best, but larger |

**Trade-off:** Higher order = better fluency, but larger model size and slower decoding

#### Implementation

```bash
# Train different order LMs
for order in 2 3 4 5; do
    lmplz -o $order < hindi.txt > hindi_${order}gram.arpa
    build_binary hindi_${order}gram.arpa hindi_${order}gram.binary
    
    # Update moses.ini and evaluate
    # Compare BLEU scores
done
```

### 2.2 Larger Monolingual Corpus

More monolingual Hindi data → better LM probabilities

**Data Sources:**
- **IndicCorp**: 8.9 billion tokens (Hindi)
- **Wikipedia dumps**: ~200M tokens
- **Common Crawl**: Filtered Hindi text
- **News corpora**: Diverse, formal text

#### Experiment 2B: Scaling LM Training Data

| Monolingual Data | LM Perplexity | Expected BLEU |
|------------------|---------------|---------------|
| 1M sentences | 250 | 25-28 |
| 10M sentences | 180 | 30-33 |
| 50M sentences | 140 | 33-36 |
| 100M sentences | 120 | 35-38 |

**Expected gain:** +5-10 BLEU points when scaling from 1M to 100M sentences

### 2.3 Neural Language Models

Replace n-gram LM with neural LM (LSTM/Transformer)

**Advantages:**
- Better long-range dependencies
- Lower perplexity
- More fluent output

**Implementation:**
```bash
# Train neural LM with KenLM-compatible interface
# Or integrate directly in Moses
```

**Expected gain:** +3-5 BLEU points over 5-gram LM

---

## Strategy 3: Domain-Specific Parallel Corpora

### Rationale

In-domain data provides relevant vocabulary and phrasing → better translations for specific domains

### Domain Mismatch Problem

**Example:** Training on news, testing on medical texts

- Out-of-domain BLEU: 18-22
- In-domain BLEU: 35-40
- **Gain: +15-20 BLEU points**

### Experiment 3: Domain Adaptation

#### Scenario 1: News Domain

**Training Data:**
- General corpus: 100K pairs
- News-specific: 50K pairs (PIB, news archives)

**Expected Results:**
- General test set: BLEU ~30
- News test set: BLEU ~38 (+8 points)

#### Scenario 2: Medical Domain

**Training Data:**
- General corpus: 100K pairs
- Medical corpus: 20K pairs (PubMed, EMEA)

**Expected Results:**
- General test set: BLEU ~28
- Medical test set: BLEU ~42 (+14 points)

### Implementation Strategy

```bash
# Step 1: Identify domain of test set
# (News, Medical, Legal, Technical, etc.)

# Step 2: Collect in-domain parallel data
# - Crawl domain-specific websites
# - Use specialized corpora (EMEA, JRC-Acquis)

# Step 3: Train domain-specific model
# Mix general + domain data (e.g., 70% general + 30% domain)

# Step 4: Evaluate
# Compare general model vs. domain-adapted model on in-domain test
```

### Domain Weighting

Use linear interpolation for LM:

$$
P_{\text{combined}}(w) = \lambda P_{\text{in-domain}}(w) + (1-\lambda) P_{\text{general}}(w)
$$

Tune $\lambda$ on dev set (typically 0.6-0.8 for in-domain).

**Expected gain:** +5-15 BLEU points depending on domain match

---

## Strategy 4: Advanced Preprocessing

### 4.1 Better Tokenization

**Impact of tokenization on BLEU:**

| Tokenization Method | BLEU (Hindi) |
|---------------------|--------------|
| Whitespace only | 28 |
| Moses tokenizer | 32 (+4) |
| Indic NLP Library | 35 (+7) |

**Recommendation:** Use language-specific tokenizers
- English: Moses tokenizer
- Hindi: Indic NLP Library (handles Devanagari properly)

### 4.2 Morphological Analysis

Hindi is morphologically rich → use morphological segmentation

**Example:**
- Before: "लड़कों" (boys) → single token
- After: "लड़क" + "ों" (stem + plural marker)

**Expected gain:** +2-4 BLEU points

### 4.3 Named Entity Preservation

Copy proper nouns from source to target

**Example:**
- Source: "Barack Obama visited New Delhi"
- Without NE: "बराक ओबामा ने नई दिल्ली का दौरा किया" (might mistranslate names)
- With NE: Copy "Barack Obama", "New Delhi" → transliterate correctly

**Expected gain:** +1-3 BLEU points (especially on news/Wikipedia)

---

## Strategy 5: Tuning and Optimization

### 5.1 MERT (Minimum Error Rate Training)

Optimize Moses feature weights to maximize BLEU on dev set

**Features to tune:**
- Translation model weights
- Language model weight
- Reordering weights
- Word penalty
- Phrase penalty

**Expected gain:** +2-5 BLEU points

#### Implementation

```bash
mert-moses.pl \
    dev.en dev.hi \
    moses train/model/moses.ini \
    --mertdir ~/moses/bin/ \
    --working-dir mert-work
```

### 5.2 Alternative Tuning: PRO, KB-MIRA

- **PRO** (Pairwise Ranking Optimization): More stable than MERT
- **KB-MIRA**: Faster convergence

**Expected gain:** Similar to MERT, sometimes +1-2 additional points

### 5.3 Reordering Model

Enable lexicalized reordering (important for English-Hindi due to word order differences)

**Default:** `msd-bidirectional-fe`

**Expected gain:** +3-6 BLEU points (English-Hindi has significant reordering)

---

## Experimental Design

### Controlled Experiment: Measuring BLEU Improvements

#### Baseline System

```
Training Data: 50K sentence pairs (IITB subset)
Language Model: Trigram (10M Hindi sentences)
Preprocessing: Basic tokenization
Tuning: None
Domain: General
```

**Baseline BLEU:** 28.5 (on general test set)

#### Experiment 1: Data Scaling

```bash
# Increase training data to 200K pairs
# Expected BLEU: 34.0 (+5.5)
```

#### Experiment 2: LM Enhancement

```bash
# Upgrade to 5-gram LM trained on 100M sentences
# Expected BLEU: 36.5 (+2.5 from Exp1)
```

#### Experiment 3: Domain Adaptation

```bash
# Add 30K news-specific pairs
# Test on news domain
# Expected BLEU: 42.0 (+5.5 from Exp2 on news test)
```

#### Experiment 4: Preprocessing + Tuning

```bash
# Use Indic NLP tokenizer + MERT
# Expected BLEU: 45.0 (+3.0 from Exp3)
```

### Cumulative Effect

| Experiment | Change | BLEU | Δ BLEU |
|------------|--------|------|--------|
| Baseline | 50K data, 3gram, basic | 28.5 | - |
| Exp 1 | 200K data | 34.0 | +5.5 |
| Exp 2 | + 5-gram, 100M LM | 36.5 | +2.5 |
| Exp 3 | + domain data (news) | 42.0 | +5.5 |
| Exp 4 | + Indic tokenizer + MERT | 45.0 | +3.0 |
| **Total** | - | **45.0** | **+16.5** |

---

## Expected Results

### Summary of Gains

| Strategy | Expected BLEU Gain | Effort | Cost |
|----------|-------------------|--------|------|
| 10K → 100K training data | +10-15 | Medium | Low |
| 3-gram → 5-gram LM | +3-5 | Low | Medium |
| 10M → 100M LM data | +5-8 | Medium | High |
| Domain adaptation | +5-15 | High | Medium |
| Better tokenization | +2-4 | Low | Low |
| MERT tuning | +2-5 | Low | Low |
| Morphological analysis | +2-4 | High | Medium |
| Neural LM | +3-5 | High | High |

### Practical Recommendations (Priority Order)

1. **MERT tuning** (low effort, +2-5 BLEU)
2. **Better tokenization** (low effort, +2-4 BLEU)
3. **Increase training data** (medium effort, +10-15 BLEU)
4. **Upgrade LM order** (low effort, +3-5 BLEU)
5. **Domain adaptation** (high effort, +5-15 BLEU if domain-matched test)

---

## Conclusion

BLEU scores can be systematically improved through a combination of:
1. **More and better data** (both parallel and monolingual)
2. **Enhanced language modeling** (higher order, more data, neural)
3. **Domain matching** (critical for specialized applications)
4. **Proper preprocessing** (tokenization, morphology, NER)
5. **Optimization** (MERT/PRO tuning)

**Key Insight:** No single strategy provides dramatic gains. **Cumulative improvements** from multiple strategies yield the best results (20-30 BLEU point increase achievable).

**Important Note:** BLEU is an imperfect metric. High BLEU doesn't always mean human-quality translation. Always complement with:
- Manual evaluation
- Task-based evaluation
- Other metrics (METEOR, TER, chrF)

---

## References

1. Papineni, K., et al. (2002). BLEU: a method for automatic evaluation of machine translation. *ACL*.

2. Koehn, P. (2009). *Statistical Machine Translation*. Cambridge University Press.

3. Koehn, P., & Knowles, R. (2017). Six challenges for neural machine translation. *WMT*.

4. Post, M. (2018). A call for clarity in reporting BLEU scores. *WMT*.

5. Kunchukuttan, A., et al. (2018). The IIT Bombay English-Hindi parallel corpus. *LREC*.

6. Heafield, K. (2011). KenLM: Faster and smaller language model queries. *WMT*.

---

**Appendix: Conversion to PDF**

```bash
# Using pandoc
pandoc TaskB.md -o TaskB.pdf --pdf-engine=xelatex

# Or with markdown-pdf
npm install -g markdown-pdf
markdown-pdf TaskB.md
```
