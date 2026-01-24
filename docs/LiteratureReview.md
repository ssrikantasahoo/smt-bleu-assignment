# Literature Review: Automatic Evaluation Metrics for Statistical Machine Translation

**Assignment-2, Part 2: Literature Survey (5 marks)**

**Topic**: Automatic Evaluation Metrics for Machine Translation Quality

---

## Abstract

This literature review surveys the landscape of automatic evaluation metrics for machine translation (MT), with focus on their development, methodology, strengths, weaknesses, and correlation with human judgments. We comprehensively examine BLEU, METEOR, TER, chrF, BEER, COMET, and BLEURT, along with recent neural-based approaches. The review includes comparative analysis, discussion of why BLEU remains dominant despite known limitations, and future directions for MT evaluation research.

**Keywords**: Machine Translation, Evaluation Metrics, BLEU, METEOR, TER, Neural Metrics, Quality Estimation

---

## 1. Introduction

### 1.1 The Evaluation Problem

Machine translation evaluation is fundamental to MT research and development. Manual evaluation by human annotators is:
- **Expensive**: Requires expert bilingual speakers
- **Time-consuming**: Slow turnaround for iterative development
- **Inconsistent**: Inter-annotator agreement issues
- **Not Scalable**: Cannot evaluate millions of translations

Automatic metrics address these limitations by providing:
- **Fast**: Instant evaluation of translations
- **Cheap**: No human cost
- **Reproducible**: Same score for same input
- **Scalable**: Can evaluate unlimited translations

However, automatic metrics must correlate with human judgments to be useful. This tension between efficiency and accuracy drives metric development.

### 1.2 Evaluation Criteria for Metrics

Good MT evaluation metrics should satisfy:

1. **Validity**: Correlates with human quality judgments
2. **Reliability**: Consistent scores across repeated evaluations
3. **Sensitivity**: Distinguishes between quality levels
4. **Simplicity**: Easy to understand and implement
5. **Efficiency**: Fast computation
6. **Language Independence**: Applicable to any language pair

No single metric perfectly satisfies all criteria, leading to metric diversity.

### 1.3 Scope and Organization

This review covers:
- **Section 2**: Classical reference-based metrics (BLEU, METEOR, TER)
- **Section 3**: Character-based and hybrid metrics (chrF, BEER)
- **Section 4**: Neural and learned metrics (COMET, BLEURT, BERTScore)
- **Section 5**: Comparative analysis and correlation studies
- **Section 6**: BLEU's continued dominance and known limitations
- **Section 7**: Future directions and emerging trends

---

## 2. Classical Reference-Based Metrics

### 2.1 BLEU (Bilingual Evaluation Understudy)

#### 2.1.1 Methodology

Introduced by Papineni et al. (2002), BLEU revolutionized MT evaluation by providing the first widely-adopted automatic metric.

**Core Components**:

1. **Modified N-gram Precision** with clipping:
   ```
   p_n = Σ_candidate Σ_ngram min(Count(ngram), Max_Ref_Count(ngram))
         ──────────────────────────────────────────────────────────
                     Σ_candidate Σ_ngram Count(ngram)
   ```

2. **Brevity Penalty** (BP):
   ```
   BP = 1                if c > r
   BP = exp(1 - r/c)     if c ≤ r
   ```
   where c = candidate length, r = reference length

3. **Geometric Mean** of precisions:
   ```
   BLEU = BP × exp(Σ(w_n × log p_n))
   ```

**Key Innovation**: Clipping prevents gaming the metric through repetition.

**Example**:
```
Candidate: "the the the"
Reference: "the cat sat"

Without clipping: precision = 3/3 = 1.0 (incorrect!)
With clipping: precision = 1/3 = 0.33 (correct)
```

#### 2.1.2 Strengths

1. **Simple to Understand**: Clear mathematical formulation
2. **Fast Computation**: O(n) time complexity
3. **Language Independent**: Works for any language pair
4. **Corpus-level Correlation**: Good correlation with human judgments at corpus level (Pearson's r ≈ 0.7-0.9)
5. **Reproducible**: Identical implementations give same scores
6. **Widely Adopted**: De facto standard in MT research

#### 2.1.3 Weaknesses

1. **No Semantic Understanding**: "bank" (financial) vs "bank" (river) treated identically
2. **No Synonym Recognition**: "happy" and "joyful" get no credit
3. **Word Order Insensitivity**: Only partially captured through n-grams
4. **Reference Dependency**: Requires high-quality reference translations
5. **Sentence-level Weakness**: Poor correlation at sentence level (r ≈ 0.2-0.4)
6. **Gaming Potential**: Can be optimized without improving translation quality

**Critical Analysis** (Callison-Burch et al., 2006):
- BLEU improvements don't always mean better translations
- Can favor shorter, conservative translations
- Misses paraphrases and legitimate variations

### 2.2 METEOR (Metric for Evaluation of Translation with Explicit ORdering)

#### 2.2.1 Methodology

Banerjee and Lavie (2005) developed METEOR to address BLEU's limitations, particularly synonym and paraphrase handling.

**Alignment Process**:
1. **Exact Match**: Identical words
2. **Stem Match**: Stemmed forms (e.g., "running" → "run")
3. **Synonym Match**: WordNet synonyms (e.g., "happy" → "joyful")
4. **Paraphrase Match**: Paraphrase tables

**Scoring Formula**:
```
Fmean = (Precision × Recall) / (α × Precision + (1-α) × Recall)

Penalty = γ × (chunks / matches)^β

METEOR = Fmean × (1 - Penalty)
```

where:
- **chunks** = number of contiguous matched segments (word order)
- **α, β, γ** = tuned parameters (typically α=0.9, β=3, γ=0.5)

**Example**:
```
Candidate: "the happy cat sat on the mat"
Reference: "the joyful cat was on the mat"

Exact matches: "the" (×2), "cat", "on", "mat" = 5/7 words
Synonym match: "happy" → "joyful" = 1 additional
Total alignment: 6/7 = 0.857

Chunks: ["the", "happy→joyful cat", "sat→was?", "on the mat"]
  = 4 chunks (penalized for fragmentation)

METEOR ≈ 0.82 (after penalty)
BLEU ≈ 0.65 (misses synonym, no "was")
```

#### 2.2.2 Strengths

1. **Semantic Awareness**: Recognizes synonyms and stems
2. **Recall Consideration**: Balances precision and recall
3. **Word Order Penalty**: Explicit handling via chunks
4. **Better Sentence-level Correlation**: r ≈ 0.4-0.6 (vs BLEU's 0.2-0.4)
5. **Tunable Parameters**: Can optimize for specific languages/domains

**Improvements** (Denkowski & Lavie, 2014):
- METEOR Universal for any target language
- Paraphrase tables from parallel corpora
- Better parameter tuning

#### 2.2.3 Weaknesses

1. **Language Dependent**: Requires WordNet, stemmers (not available for all languages)
2. **Slower**: Alignment computation expensive
3. **Parameter Tuning**: Optimal α, β, γ vary by task
4. **Less Intuitive**: More complex than BLEU
5. **Resource Requirements**: Needs external linguistic resources

### 2.3 TER (Translation Edit Rate)

#### 2.3.1 Methodology

Snover et al. (2006) introduced TER as an error-focused metric based on edit distance.

**Edit Operations** (cost = 1 each):
1. **Insertion**: Add a word
2. **Deletion**: Remove a word
3. **Substitution**: Replace a word
4. **Shift**: Move a word/phrase

**Formula**:
```
TER = (# edits needed to match reference) / (# words in reference)
```

**Example**:
```
Reference: "the cat is on the mat"
Candidate: "the mat is on the cat"

Edits needed:
  1. Shift "mat" from position 6 to position 2
  2. Shift "cat" from position 2 to position 6
  Total: 2 shifts

TER = 2/6 = 0.333
```

**Lower TER is better** (0 = perfect match, higher = more errors)

#### 2.3.2 Strengths

1. **Interpretable**: Direct measure of editing effort
2. **Error-focused**: Natural for post-editing estimation
3. **Shift-aware**: Handles word reordering explicitly
4. **Corpus Correlation**: Good at corpus level (r ≈ 0.7-0.8)

**Variants**:
- **HTER**: Human-targeted TER (post-editor creates reference)
- **TERp**: Parameterized TER with stem/synonym matching
- **CharacTER**: Character-level TER

#### 2.3.3 Weaknesses

1. **No Partial Credit**: "happy" vs "joyful" costs same as "happy" vs "sad"
2. **Reference Bias**: Assumes reference is perfect
3. **Edit Path Dependency**: Multiple edit sequences possible
4. **Ignores Semantic Similarity**: Pure surface-level matching
5. **Not Normalized**: Different ranges for different sentence lengths

---

## 3. Character-Based and Hybrid Metrics

### 3.1 chrF (Character n-gram F-score)

#### 3.1.1 Methodology

Popović (2015) proposed chrF to address morphologically-rich languages where word-level metrics struggle.

**Algorithm**:
1. Extract character n-grams (typically 1-6)
2. Compute precision and recall
3. Combine using F-score

**Formula**:
```
chrF_β = (1 + β²) × (chrP × chrR) / (β² × chrP + chrR)
```

where:
- **chrP** = character n-gram precision
- **chrR** = character n-gram recall
- **β** = weight parameter (β=1 for F1, β=2 for F2)

**Example**:
```
Reference: "unbelievable"
Candidate: "believable"

Character 3-grams:
  Reference: "unb", "nbe", "bel", "eli", "lie", "iev", "eva", "vab", "abl", "ble"
  Candidate: "bel", "eli", "lie", "iev", "eva", "vab", "abl", "ble"

Overlap: 8/8 candidate 3-grams match reference
Precision: 8/8 = 1.0
Recall: 8/10 = 0.8
chrF1: 2 × (1.0 × 0.8) / (1.0 + 0.8) = 0.889
```

#### 3.1.2 Strengths

1. **Language Independent**: No linguistic resources needed
2. **Morphology-aware**: Captures sub-word similarities
3. **Robust to Spelling**: Partial credit for near-misses
4. **Prefix/Suffix Handling**: Naturally handles affixes
5. **Better for Agglutinative Languages**: Turkish, Finnish, Hungarian

**WMT Results**: chrF often correlates better than BLEU for non-English targets

#### 3.1.3 Weaknesses

1. **Less Interpretable**: Character n-grams not intuitive units
2. **Over-rewards Partial Matches**: "unbelievable" vs "believable" gets high score
3. **Language Sensitivity**: Optimal n-gram order varies by language
4. **No Semantic Understanding**: Still surface-level

### 3.2 BEER (BEtter Evaluation as Ranking)

#### 3.2.1 Methodology

Stanojević and Sima'an (2014) developed BEER as a trainable metric combining multiple features.

**Feature Types**:
1. **Character n-grams**: Similar to chrF
2. **Word n-grams**: BLEU-like features
3. **Permutation Trees**: Word reordering features
4. **Function Words**: Special handling of grammatical words

**Learning**:
- Train on human judgments (WMT datasets)
- Learn feature weights using ranking loss
- Optimize for ranking correlation (Kendall's τ)

**Scoring**:
```
BEER = Σ(w_i × feature_i(candidate, reference))
```

#### 3.2.2 Strengths

1. **Trainable**: Adapts to human preferences
2. **Multi-faceted**: Combines complementary features
3. **Reordering-aware**: Permutation trees capture word movement
4. **Strong Correlation**: Often top performer in WMT metrics tasks

#### 3.2.3 Weaknesses

1. **Requires Training Data**: Needs human judgments
2. **Less Interpretable**: Black-box feature combination
3. **Language-specific Training**: Different weights per language pair
4. **Computational Cost**: More complex than simple metrics

---

## 4. Neural and Learned Metrics

### 4.1 COMET (Crosslingual Optimized Metric for Evaluation of Translation)

#### 4.1.1 Methodology

Rei et al. (2020) introduced COMET, leveraging pretrained multilingual encoders.

**Architecture**:
```
Input: (source, candidate, reference)
         ↓
    XLM-RoBERTa Encoder
         ↓
    Pooling Layer
         ↓
    Feed-forward Network
         ↓
    Quality Score (0-1)
```

**Training**:
- **Data**: WMT Direct Assessment (DA) human scores
- **Loss**: Regression loss predicting DA scores
- **Model**: Fine-tune XLM-RoBERTa on DA data

**Variants**:
- **COMET-DA**: Trained on Direct Assessment
- **COMET-MQM**: Trained on Multidimensional Quality Metrics
- **COMET-QE**: Quality Estimation (no reference needed)

#### 4.1.2 Strengths

1. **State-of-the-art Correlation**: Segment-level r > 0.5 (vs BLEU's ~0.3)
2. **Semantic Understanding**: Contextual embeddings capture meaning
3. **Cross-lingual**: Leverages multilingual pretraining
4. **Paraphrase-aware**: Understands semantic equivalence
5. **Source-aware**: Uses source for better judgment

**WMT 2020 Results**: COMET ranked #1 in metrics shared task

#### 4.1.3 Weaknesses

1. **Computationally Expensive**: Requires GPU for practical use
2. **Black Box**: Hard to interpret why score is X
3. **Training Data Dependency**: Performance tied to training data quality
4. **Reference Dependency**: (For COMET-DA; QE variant exists)
5. **Reproducibility**: Model version and checkpoint matter

### 4.2 BLEURT (Bilingual Evaluation Understudy with Representations from Transformers)

#### 4.2.1 Methodology

Sellam et al. (2020) developed BLEURT to combine robustness of learned metrics with BLEU's simplicity.

**Two-stage Training**:

**Stage 1: Pretraining** on synthetic data
- Generate millions of (reference, candidate) pairs with varying quality
- Augmentation: back-translation, word dropping, masking
- Learn to distinguish quality levels

**Stage 2: Fine-tuning** on human ratings
- Fine-tune on WMT DA scores
- Learn to match human judgments

**Architecture**:
```
(Reference, Candidate)
         ↓
    BERT Encoder
         ↓
    [CLS] Representation
         ↓
    Regression Head
         ↓
    Quality Score
```

#### 4.2.2 Strengths

1. **Robust**: Pretraining reduces sensitivity to small changes
2. **High Correlation**: r ≈ 0.5-0.6 at segment level
3. **Reproducible**: Fixed checkpoint, deterministic scores
4. **Less Training Data**: Pretraining reduces fine-tuning needs
5. **Semantic Similarity**: Captures paraphrases

#### 4.2.3 Weaknesses

1. **Slow**: Transformer inference expensive
2. **Model Size**: Several GB, not lightweight
3. **Still Reference-dependent**: Requires gold reference
4. **Monolingual**: Doesn't use source (unlike COMET)
5. **English-centric**: Primarily developed for English

### 4.3 BERTScore

#### 4.3.1 Methodology

Zhang et al. (2020) proposed BERTScore for comparing embeddings.

**Algorithm**:
1. Encode candidate and reference with BERT
2. Compute cosine similarity for each token pair
3. Greedy matching: align each token to most similar token
4. Aggregate using F-score

**Formula**:
```
Precision: (1/|C|) × Σ_{c∈C} max_{r∈R} cos(c, r)
Recall: (1/|R|) × Σ_{r∈R} max_{c∈C} cos(c, r)
F1: 2 × (P × R) / (P + R)
```

**Innovation**: Soft matching via embeddings vs hard matching (BLEU)

#### 4.3.2 Strengths

1. **Semantic Matching**: "happy" and "joyful" have high similarity
2. **Contextual**: Word meaning depends on context
3. **No Training on MT Data**: Uses pretrained BERT only
4. **Multilingual**: Works with multilingual BERT

#### 4.3.3 Weaknesses

1. **Computational Cost**: Embedding all tokens expensive
2. **Threshold Sensitivity**: Alignment quality depends on similarity threshold
3. **Granularity**: Token-level may be too fine-grained
4. **Not Optimized for MT**: Designed for general text generation

---

## 5. Comparative Analysis

### 5.1 Correlation with Human Judgments

**Segment-level Correlation** (WMT 2020, EN-DE):

| Metric | Kendall's τ | Pearson's r | Rank |
|--------|-------------|-------------|------|
| COMET | 0.403 | 0.616 | 1 |
| BLEURT | 0.385 | 0.589 | 2 |
| BERTScore | 0.325 | 0.512 | 3 |
| METEOR | 0.245 | 0.421 | 5 |
| chrF | 0.238 | 0.398 | 6 |
| BLEU | 0.185 | 0.312 | 12 |

**Key Finding**: Neural metrics significantly outperform classical metrics at segment level.

**System-level Correlation** (WMT 2020, EN-DE):

| Metric | Kendall's τ | Pearson's r | Rank |
|--------|-------------|-------------|------|
| COMET | 0.633 | 0.882 | 1 |
| BLEU | 0.600 | 0.851 | 4 |
| METEOR | 0.583 | 0.829 | 6 |
| chrF | 0.617 | 0.865 | 3 |
| BLEURT | 0.650 | 0.895 | 1 (tied) |

**Key Finding**: Gap narrows at system level; BLEU remains competitive.

### 5.2 Metric Comparison Table

| Metric | Type | Speed | Interpretability | Correlation (Seg) | Correlation (Sys) | Resources Needed |
|--------|------|-------|------------------|-------------------|-------------------|------------------|
| BLEU | N-gram | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | None |
| METEOR | N-gram + | ⚡⚡⚡ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | WordNet, Stemmer |
| TER | Edit dist | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | None |
| chrF | Char n-gram | ⚡⚡⚡⚡ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | None |
| BEER | Trainable | ⚡⚡⚡ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Training data |
| COMET | Neural | ⚡ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | GPU, Pretrained |
| BLEURT | Neural | ⚡ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | GPU, Pretrained |

⚡ = Fast, ⭐ = Good

### 5.3 Use Case Recommendations

**Research & Development**:
- Primary: COMET or BLEURT (best correlation)
- Secondary: BLEU (for comparability with literature)
- Tertiary: chrF or METEOR (linguistic insight)

**Production Monitoring**:
- Primary: BLEU (speed, simplicity)
- Secondary: chrF (language robustness)
- With references: COMET (quality critical)

**Low-resource Languages**:
- Primary: chrF (no external resources)
- Secondary: BLEU (universal)
- Avoid: METEOR (resource-dependent)

**Evaluation Campaigns** (e.g., WMT):
- Report multiple: BLEU, chrF, COMET
- Primary ranking: COMET or BLEURT
- Backwards compatibility: BLEU

---

## 6. Why BLEU Still Dominates

### 6.1 Historical Momentum

**Published Papers Using BLEU** (ACL Anthology):
- 2002-2010: ~1,500 papers
- 2011-2015: ~3,200 papers
- 2016-2020: ~4,800 papers
- 2021-2025: ~5,500 papers (projected)

**Total**: ~15,000+ papers cite BLEU

**Network Effect**: Everyone uses BLEU → must report BLEU for comparison

### 6.2 Practical Advantages

**1. Simplicity**:
```python
# BLEU in 20 lines (simplified)
def bleu(candidate, reference):
    # Clear, understandable algorithm
    # Can be implemented from scratch
    ...
```

**2. Speed**:
- BLEU: 0.001 seconds/sentence
- COMET: 0.5 seconds/sentence (500x slower)
- For 1M sentences: BLEU = 16 minutes, COMET = 5.7 days

**3. Reproducibility**:
- BLEU: Identical scores across implementations (if tokenization matches)
- Neural: Model version, random seeds, hardware affect scores

**4. Interpretability**:
- BLEU: Can examine n-gram matches, BP penalty
- Neural: Black box score, no clear explanation

### 6.3 Sufficient for Most Purposes

**System-level Ranking**:
- BLEU: Kendall's τ = 0.60
- COMET: Kendall's τ = 0.63
- Difference: 0.03 (often not significant)

**Practical Impact**:
```
Top 5 MT systems (BLEU ranking):
  1. System A: 32.5 BLEU
  2. System B: 32.1 BLEU
  3. System C: 31.8 BLEU
  4. System D: 31.5 BLEU
  5. System E: 31.2 BLEU

Top 5 MT systems (COMET ranking):
  1. System A: 0.645
  2. System C: 0.641
  3. System B: 0.638
  4. System D: 0.632
  5. System E: 0.628

Conclusion: Top systems largely agree
```

### 6.4 Known Limitations (and Mitigations)

**Limitation 1: Poor Segment-level Correlation**
- **Mitigation**: Use system-level or corpus-level evaluation
- **Alternative**: Use COMET for segment-level feedback

**Limitation 2: No Semantic Understanding**
- **Mitigation**: Use multiple references
- **Alternative**: Combine with METEOR or BLEURT

**Limitation 3: Reference Dependency**
- **Mitigation**: Use high-quality, diverse references
- **Alternative**: Quality Estimation metrics (COMET-QE)

**Limitation 4: Gaming Potential**
- **Mitigation**: Human evaluation for final decisions
- **Alternative**: Use ensemble of metrics

**Best Practice** (Post, 2018):
```
# Report BLEU with configuration
BLEU = 32.5 [tokenization: 13a, case: mixed,
              references: 1, smoothing: exp]
```

---

## 7. Future Directions

### 7.1 Emerging Trends

**1. Reference-free Evaluation**:
- Quality Estimation without references
- COMET-QE, Unsupervised MT metrics
- Useful for low-resource languages

**2. Explainable Neural Metrics**:
- Attention visualization
- Error type classification
- Rationale generation

**3. Multilingual Metrics**:
- Single metric for all language pairs
- Cross-lingual embeddings
- Reduce language pair bias

**4. Beyond Correlation**:
- Interpretability
- Actionable feedback
- Error analysis integration

### 7.2 Open Research Questions

1. **What should metrics optimize for?**
   - Adequacy vs fluency
   - Literal vs free translation
   - Domain-specific quality

2. **How to evaluate rare phenomena?**
   - Named entities
   - Idiomatic expressions
   - Cultural references

3. **Can metrics guide MT training?**
   - Trainable metrics as reward signals
   - Differentiable BLEU variants
   - Metric-augmented training

4. **How to handle multiple valid translations?**
   - Paraphrases
   - Style variation
   - Cultural adaptation

### 7.3 Recommendations for Practitioners

**For Researchers**:
1. Report BLEU for comparability
2. Add neural metric (COMET/BLEURT) for quality
3. Include human evaluation for key claims
4. Document metric configurations

**For Practitioners**:
1. Use BLEU for monitoring
2. Periodically validate with human evaluation
3. Consider neural metrics for critical applications
4. Don't over-optimize for single metric

---

## 8. Conclusion

Automatic MT evaluation has evolved significantly from BLEU's introduction in 2002 to modern neural metrics like COMET. Key takeaways:

1. **BLEU remains dominant** due to simplicity, speed, and sufficient accuracy for system-level comparison
2. **Neural metrics outperform** classical metrics in segment-level correlation but at computational cost
3. **No perfect metric exists** – each has trade-offs between accuracy, speed, interpretability, and resource requirements
4. **Multi-metric evaluation** is best practice, combining complementary strengths
5. **Human evaluation** remains gold standard for critical decisions

**Future**: Metrics will become more semantic, multilingual, and actionable, but BLEU's role as a simple, fast, reproducible baseline will likely persist.

---

## References

See `references.bib` for complete BibTeX entries.

**Key Citations**:
1. Papineni et al. (2002): BLEU
2. Banerjee & Lavie (2005): METEOR
3. Snover et al. (2006): TER
4. Popović (2015): chrF
5. Stanojević & Sima'an (2014): BEER
6. Rei et al. (2020): COMET
7. Sellam et al. (2020): BLEURT
8. Zhang et al. (2020): BERTScore
9. Callison-Burch et al. (2006): BLEU limitations
10. Ma et al. (2019): WMT metrics results
11. Mathur et al. (2020): Metric meta-evaluation
12. Post (2018): BLEU reporting standards

