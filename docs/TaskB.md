# Task B: Improving BLEU Scores in Statistical Machine Translation

**Assignment-2, Part 1, Task B (2 marks)**

**Topic**: How to Increase BLEU Scores Using Various Approaches

---

## Executive Summary

BLEU scores can be systematically improved through three primary strategies:
1. **Increasing training data quantity and quality**
2. **Enhancing language model sophistication**
3. **Utilizing domain-specific parallel corpora**

This document explains each approach with theoretical justification, practical examples, and expected impact on BLEU scores.

---

## 1. Introduction

### 1.1 Understanding BLEU Limitations

Before discussing improvements, it's essential to understand what BLEU measures:

**BLEU Formula**:
```
BLEU = BP × exp(∑(w_n × log(p_n)))
```

Where:
- **BP** = Brevity Penalty (penalizes short translations)
- **p_n** = Modified n-gram precision for order n
- **w_n** = Weight for n-gram order n (typically uniform: 0.25 each for n=1,2,3,4)

**Key Insight**: BLEU improves when:
1. N-gram precision increases (more matching n-grams)
2. Translation length matches reference length (BP → 1.0)
3. Higher-order n-grams match (fluency improves)

### 1.2 Baseline SMT Pipeline

```
Parallel Corpus → Word Alignment → Phrase Table
                       ↓
Monolingual Data → Language Model
                       ↓
Source Sentence → Decoder → Translation
                       ↓
Reference(s) → BLEU Score
```

Each component can be improved to increase BLEU scores.

---

## 2. Strategy 1: More Training Data

### 2.1 Why More Data Helps

**Theoretical Justification**:
- **Better Coverage**: More phrase pairs in phrase table
- **Better Estimates**: More accurate probability estimates
- **Rare Phenomena**: Captures infrequent constructions
- **Generalization**: Learns diverse translation patterns

**Impact on BLEU Components**:

| Component | Impact | Mechanism |
|-----------|--------|-----------|
| Phrase Table | More entries | Covers more source phrases |
| Translation Probs | More accurate | Better relative probabilities |
| Reordering Model | Better patterns | Learns correct word order |
| N-gram Precision | Increases | More phrase matches → higher p_n |

### 2.2 Types of Data to Add

#### 2.2.1 Parallel Corpora

**High-Quality Sources**:
1. **Professional Translations**:
   - News articles (WMT datasets)
   - Official documents (EU Parliament, UN)
   - Literary works (books, subtitles)

2. **Community Translations**:
   - Wikipedia (aligned articles)
   - TED Talks (multi-lingual subtitles)
   - Software localization (GNOME, KDE)

**Expected BLEU Improvement**:
```
Baseline: 100K sentence pairs → BLEU: 25.3
Add 500K pairs → BLEU: 28.7 (+3.4 points)
Add 2M pairs → BLEU: 31.2 (+5.9 points)
```
*Numbers are illustrative based on typical WMT results*

#### 2.2.2 Data Quality vs. Quantity

**Quality Factors**:
- **Alignment Accuracy**: Sentences truly translations of each other
- **Domain Match**: Similar to test data
- **Translation Quality**: Human vs. machine-translated data
- **Noise Level**: OCR errors, formatting issues

**Practical Example**:
```
Option A: Add 1M sentence pairs (web-scraped, noisy)
  Expected BLEU: +1.5 points

Option B: Add 100K sentence pairs (professional, clean)
  Expected BLEU: +2.0 points

Conclusion: 100K high-quality > 1M low-quality
```

### 2.3 Data Augmentation Techniques

**1. Back-Translation**:
```
Source (EN) → Translate to Target (FR) → Back-translate to EN
Compare: Original EN vs. Back-translated EN
If similar: (EN, FR) is good training pair
```

**Benefits**:
- Leverages monolingual data
- Increases parallel corpus size
- Improves fluency

**2. Paraphrasing**:
```
Original: "the cat is on the mat"
Paraphrase: "a cat sits on the mat"
Both paired with same target translation
```

**Benefits**:
- Increases phrase table coverage
- Handles variation in input
- Improves robustness

### 2.4 Practical Implementation

**Step-by-Step Guide**:

1. **Identify Data Sources**:
   ```bash
   # Download WMT data
   wget http://www.statmt.org/wmt20/translation-task.html
   # Extract parallel sentences
   gunzip news-commentary-v15.en-fr.tsv.gz
   ```

2. **Clean and Filter**:
   ```python
   def filter_parallel_data(src, tgt):
       # Remove if length ratio is extreme
       if len(tgt) / len(src) > 3 or len(src) / len(tgt) > 3:
           return False
       # Remove if too short or too long
       if len(src.split()) < 3 or len(src.split()) > 100:
           return False
       # Remove if likely alignment error
       if src == tgt:  # Same in both languages (suspicious)
           return False
       return True
   ```

3. **Add to Training Pipeline**:
   ```bash
   # Combine with existing data
   cat existing_corpus.en new_data.en > combined.en
   cat existing_corpus.fr new_data.fr > combined.fr

   # Retrain Moses model
   ./train-model.perl --corpus combined --root-dir model_v2
   ```

4. **Measure Improvement**:
   ```bash
   # Evaluate on test set
   ./moses < test.en > output.fr
   ./multi-bleu.perl test.fr < output.fr
   ```

**Expected Results**:
```
Before: BLEU = 24.5
After (+1M sentences): BLEU = 27.8 (+3.3 points)
```

---

## 3. Strategy 2: Better Language Models

### 3.1 Why Language Models Matter

**Role in SMT**:
- **Fluency**: Ensures target language sounds natural
- **Disambiguation**: Chooses between translation options
- **Reordering**: Guides word order decisions

**BLEU Impact**:
- Better LM → More fluent translations
- More fluent → Higher n-gram matches (especially 3-gram, 4-gram)
- Higher n-gram precision → Higher BLEU

### 3.2 LM Improvements

#### 3.2.1 Higher-Order N-grams

**Standard**: Trigram (3-gram) LM
**Improvement**: 5-gram or 6-gram LM

**Example**:
```
Trigram LM: P("est" | "le", "chat")
5-gram LM: P("est" | "il", "dit", "que", "le", "chat")
```

**Benefits**:
- Longer context → Better word choice
- Captures longer-range dependencies
- Improves fluency

**Trade-offs**:
| Aspect | Trigram | 5-gram | 7-gram |
|--------|---------|--------|--------|
| Context | Short | Medium | Long |
| Data Sparsity | Low | Medium | High |
| Model Size | Small | Medium | Large |
| Decoding Speed | Fast | Medium | Slow |
| BLEU Gain | Baseline | +1.5 | +2.0 |

**Practical**: 5-gram is sweet spot for most tasks

#### 3.2.2 Neural Language Models

**Traditional LM**: Count-based n-grams
```
P("chat" | "le") = count("le chat") / count("le")
```

**Neural LM**: LSTM or Transformer
```
P("chat" | "le") = softmax(NN([embed("le")]))
```

**Advantages**:
1. **Continuous Representation**: No hard zeros for unseen n-grams
2. **Longer Context**: Can use entire sentence history
3. **Better Generalization**: Learns semantic patterns

**BLEU Impact**:
```
Count-based 3-gram LM: BLEU = 25.0
Count-based 5-gram LM: BLEU = 26.5 (+1.5)
LSTM LM: BLEU = 28.0 (+3.0)
Transformer LM: BLEU = 29.5 (+4.5)
```

#### 3.2.3 Smoothing Techniques

**Problem**: Unseen n-grams get zero probability → decoder avoids them

**Solutions**:

**1. Kneser-Ney Smoothing** (Standard):
```
P_KN(w_i | w_{i-1}) = max(count(w_{i-1}, w_i) - D, 0) / count(w_{i-1})
                      + λ(w_{i-1}) × P_continuation(w_i)
```

**Benefits**:
- Handles unseen n-grams gracefully
- Considers context diversity
- Industry standard for SMT

**2. Modified Kneser-Ney**:
- Better handling of singletons
- Improved interpolation
- BLEU +0.5 over basic KN

**Example Impact**:
```
No Smoothing: BLEU = 22.0 (decoder gets stuck on unseen phrases)
Add-one Smoothing: BLEU = 23.5
Kneser-Ney: BLEU = 25.8 (+3.8 from no smoothing)
Modified KN: BLEU = 26.3 (+0.5 from KN)
```

### 3.3 Domain-Adapted Language Models

**Approach**: Train separate LMs for different domains

**Example**:
```
General News LM: Trained on newswire (100M words)
Medical LM: Trained on PubMed articles (50M words)

Test: Medical translation task
  Using News LM: BLEU = 28.0
  Using Medical LM: BLEU = 34.5 (+6.5 points!)
```

**Interpolation Strategy**:
```
P_combined = λ × P_domain + (1-λ) × P_general

Tuned λ for dev set:
  λ = 0.7 gives best results
  BLEU = 36.0 (best of both)
```

### 3.4 Practical Implementation

**Building Better LM with KenLM**:

```bash
# Install KenLM
git clone https://github.com/kpu/kenlm.git
cd kenlm
mkdir build && cd build
cmake .. && make -j4

# Build 5-gram LM with modified Kneser-Ney
./lmplz -o 5 --discount_fallback \
  < corpus.fr > corpus.arpa

# Binarize for fast loading
./build_binary corpus.arpa corpus.blm
```

**Using Neural LM (with KenLM fallback)**:

```python
import tensorflow as tf

# Train neural LM
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 256),
    tf.keras.layers.LSTM(512, return_sequences=True),
    tf.keras.layers.Dense(vocab_size, activation='softmax')
])

# In decoder: interpolate neural and count-based LM
score = 0.6 * neural_lm.score(sentence) + \
        0.4 * kenlm.score(sentence)
```

**Expected BLEU Improvement**:
```
Baseline (3-gram, no smoothing): 23.0
+ Modified KN smoothing: 25.8 (+2.8)
+ 5-gram order: 27.3 (+1.5)
+ Neural LM interpolation: 29.8 (+2.5)

Total improvement: +6.8 BLEU points
```

---

## 4. Strategy 3: Domain-Specific Parallel Corpora

### 4.1 Why Domain Matters

**Domain Mismatch Problem**:
```
Training: News articles
Test: Medical reports
Result: Low BLEU (terminology mismatch)
```

**Example**:
```
General corpus translation:
  "The patient has a stroke" → "Le patient a un accident"
  BLEU: 0.45 (vs reference: "Le patient a subi un AVC")

Medical corpus translation:
  "The patient has a stroke" → "Le patient a subi un AVC"
  BLEU: 1.00 (perfect match)
```

### 4.2 Domain Characteristics

**Lexical Differences**:
| Domain | Example Term | General Translation | Domain Translation |
|--------|--------------|---------------------|-------------------|
| Medical | "acute" | "aigu" (sharp) | "aigu" (medical condition) |
| Legal | "consideration" | "considération" (thought) | "contrepartie" (legal term) |
| Technical | "driver" | "conducteur" (person) | "pilote" (software) |

**Syntactic Differences**:
- Legal: Longer sentences, passive voice
- Technical: More noun compounds
- Conversational: Shorter, informal

### 4.3 Domain Adaptation Strategies

#### 4.3.1 In-Domain Data Collection

**Sources by Domain**:

**Medical**:
- PubMed abstracts (aligned English-French)
- WHO reports
- Medical textbooks
- Clinical trial documents

**Legal**:
- Court proceedings
- EU legal documents (EUR-Lex)
- Patent databases (EPO, USPTO)

**Technical**:
- Software documentation (GitHub)
- Technical manuals
- Product specifications

**Example Collection**:
```bash
# Download medical parallel corpus
wget http://opus.nlpl.eu/EMEA-v3.php
# Extract English-French pairs
tar xzf EMEA.en-fr.txt.tar.gz

# Result: 1.1M medical sentence pairs
```

#### 4.3.2 Domain-Specific Training

**Approach 1: Train from Scratch**
```
Use ONLY domain data
Pros: Pure domain adaptation
Cons: May lose general knowledge
```

**Approach 2: Fine-tuning**
```
1. Train on general corpus (10M pairs)
2. Continue training on domain corpus (100K pairs)
Pros: Retains general knowledge + domain adaptation
Cons: Risk of overfitting
```

**Approach 3: Mixture**
```
Combine general + domain data
Oversample domain data (repeat 5x)
Pros: Balanced approach
Cons: Tuning mixture ratio tricky
```

**BLEU Results** (Medical domain test):
```
General corpus only: 28.0
Domain corpus only: 33.5 (+5.5)
Fine-tuning: 36.0 (+8.0)
Mixture (optimal ratio): 37.2 (+9.2) ← BEST
```

#### 4.3.3 Domain-Specific Phrase Tables

**Standard Phrase Table** (from news):
```
"patient" → "patient" (0.7), "malade" (0.2), "client" (0.1)
```

**Medical Phrase Table**:
```
"patient" → "patient" (0.95), "malade" (0.05)
"stroke" → "AVC" (0.8), "accident vasculaire cérébral" (0.2)
"acute myocardial infarction" → "infarctus du myocarde aigu" (0.9)
```

**Impact**:
- Correct medical terminology
- Multi-word medical expressions
- Higher precision n-grams

### 4.4 Practical Domain Adaptation Guide

**Step 1: Identify Target Domain**
```python
# Analyze test set
def identify_domain(test_sentences):
    domain_keywords = {
        'medical': ['patient', 'disease', 'treatment', 'diagnosis'],
        'legal': ['contract', 'agreement', 'liability', 'court'],
        'technical': ['software', 'hardware', 'configuration', 'module']
    }
    scores = {domain: 0 for domain in domain_keywords}
    for sent in test_sentences:
        for domain, keywords in domain_keywords.items():
            scores[domain] += sum(1 for kw in keywords if kw in sent.lower())
    return max(scores, key=scores.get)
```

**Step 2: Collect Domain Corpus**
```bash
# For medical domain
wget http://opus.nlpl.eu/EMEA.php  # EMEA corpus
wget http://opus.nlpl.eu/ECB.php    # If financial domain
```

**Step 3: Train Domain-Adapted Model**
```bash
# Option A: Fine-tuning
# First train general model, then continue with domain data
./train-model.perl --corpus general_corpus --root-dir model_general
./train-model.perl --corpus domain_corpus --root-dir model_domain \
  --reuse-model model_general

# Option B: Mixture
# Oversample domain data
cat general_corpus.en domain_corpus.en domain_corpus.en domain_corpus.en \
  > mixed.en
# Train on mixture
./train-model.perl --corpus mixed --root-dir model_mixed
```

**Step 4: Evaluate Domain Fit**
```bash
# Test on domain-specific test set
./moses < test_domain.en > output.fr
./multi-bleu.perl test_domain.fr < output.fr

# Compare to general model
# Domain model should give higher BLEU
```

**Expected Results** (Medical domain example):
```
General model: BLEU = 28.5
Domain-adapted model: BLEU = 36.8 (+8.3 points)
```

---

## 5. Combined Strategy: Synergistic Effects

### 5.1 Combining All Three Approaches

**Individual Impacts**:
1. More data: +5 BLEU
2. Better LM: +3 BLEU
3. Domain corpus: +8 BLEU

**Naive Sum**: +16 BLEU
**Actual Combined**: +12 BLEU

**Why Not Additive?**
- Overlapping benefits
- Diminishing returns
- Ceiling effects

### 5.2 Optimal Combination Recipe

**Best Practice Pipeline**:

```
1. Collect large general corpus (5-10M pairs)
2. Train baseline with 5-gram modified KN LM
   → BLEU: ~28

3. Add domain-specific corpus (100K-1M pairs)
4. Train domain-adapted model with mixture approach
   → BLEU: ~36 (+8)

5. Use neural LM interpolation
   → BLEU: ~38 (+2)

6. Add back-translated data (1M pairs)
   → BLEU: ~40 (+2)

Total: 28 → 40 (+12 BLEU points)
```

### 5.3 Practical Example: Medical Translation System

**Starting Point**:
```
Data: WMT News corpus (2M pairs)
LM: 3-gram, count-based
Domain: General news
Test: Medical reports
BLEU: 23.5 (baseline)
```

**Step 1: Add General Data** (+500K sentences from Europarl)
```
BLEU: 25.0 (+1.5)
```

**Step 2: Upgrade LM** (5-gram modified KN)
```
BLEU: 26.8 (+1.8)
```

**Step 3: Add Domain Data** (EMEA medical corpus, 1M pairs)
```
BLEU: 33.5 (+6.7)
```

**Step 4: Fine-tune with Neural LM**
```
BLEU: 35.8 (+2.3)
```

**Final Result**:
```
Improvement: 23.5 → 35.8 (+12.3 BLEU points)
Achieved through combined strategies!
```

---

## 6. Limitations and Considerations

### 6.1 Diminishing Returns

**Law of Diminishing Returns**:
```
First 100K sentences: +5 BLEU
Next 1M sentences: +4 BLEU
Next 10M sentences: +2 BLEU
```

**Practical Limit**: Beyond ~40 BLEU for SMT, gains become very difficult

### 6.2 Data Quality vs. Quantity

**Always prefer**:
- Clean, aligned data over noisy web-scraped data
- In-domain data over out-of-domain data
- Human translations over machine translations

### 6.3 Computational Costs

**Trade-offs**:
| Improvement | Training Time | Memory | Decoding Speed |
|-------------|---------------|---------|----------------|
| 10x more data | 10x slower | 5x more | Same |
| 5-gram LM | 2x slower | 3x more | 1.5x slower |
| Neural LM | 20x slower | 10x more | 3x slower |

**Practical**: Balance quality and resources

---

## 7. Conclusion

### 7.1 Summary of Strategies

| Strategy | BLEU Gain | Difficulty | Cost | Recommendation |
|----------|-----------|------------|------|----------------|
| More general data | +3-5 | Medium | Medium | Do it |
| Better LM | +2-3 | Low | Low | Always do |
| Domain-specific data | +5-10 | High | High | If domain-critical |
| Combined approach | +10-15 | High | High | For production |

### 7.2 Key Takeaways

1. **BLEU can be significantly improved** through systematic approaches
2. **Domain adaptation has highest impact** for specialized tasks
3. **Better LMs are low-hanging fruit** - always improve
4. **More data helps, but quality matters** more than quantity
5. **Combined strategies have synergistic effects** but not fully additive

### 7.3 Recommendations

**For Academic Projects**:
- Focus on better LMs (easy to implement, good results)
- Use domain adaptation if test set is specialized
- Document improvements with ablation studies

**For Production Systems**:
- Invest in domain-specific parallel corpora
- Use neural LMs with count-based fallback
- Continuously add more training data
- A/B test improvements with human evaluation

---

## References

1. Koehn, P. (2009). *Statistical machine translation*. Cambridge University Press.
2. Chen, S. F., & Goodman, J. (1999). *An empirical study of smoothing techniques for language modeling*. Computer Speech & Language, 13(4), 359-394.
3. Sennrich, R., Haddow, B., & Birch, A. (2016). *Improving neural machine translation models with monolingual data*. ACL 2016.
4. Koehn, P., & Knowles, R. (2017). *Six challenges for neural machine translation*. ACL Workshop on NMT.

---

**Document Status**: Ready for Submission
**Estimated Page Count**: 10-12 pages (PDF)
**Last Updated**: January 2026
