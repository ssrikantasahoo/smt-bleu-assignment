"""
Statistical Machine Translation with BLEU Evaluation
====================================================
Interactive web application for SMT and BLEU score evaluation.

Features:
- Multiple translation systems (Moses SMT, Toy SMT, Word-by-word baseline)
- BLEU score computation with detailed statistics
- N-gram precision tables
- Brevity penalty visualization
- Multi-candidate comparison
- Built-in sample references

Author: Assignment Implementation
Course: NLP - Statistical Machine Translation
"""

import streamlit as st
import json
import os
import sys
from typing import List, Dict, Tuple
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Import custom modules
from bleu import BLEUScorer
from smt_toy import ToySMT
from moses_integration import create_moses_translator, MosesTranslator
from baseline_translator import BaselineTranslator

# Page configuration
st.set_page_config(
    page_title="SMT + BLEU Evaluator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .best-candidate {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_sample_references():
    """Load built-in sample references."""
    samples_path = "data/sample_references.json"
    if os.path.exists(samples_path):
        with open(samples_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['samples']
    return []


@st.cache_resource
def initialize_translators():
    """Initialize all translation systems."""
    systems = {}

    # Initialize Moses translator (if available)
    moses_translator, moses_status = create_moses_translator()
    systems['moses'] = {
        'translator': moses_translator,
        'status': moses_status,
        'available': moses_translator is not None
    }

    # Initialize Toy SMT
    try:
        toy_smt = ToySMT(
            phrase_table_path="data/phrase_table.json",
            lm_path="data/lm_trigrams.json",
            beam_size=10,
            lm_weight=0.5
        )
        systems['toy_smt'] = {
            'translator': toy_smt,
            'status': "Toy SMT initialized successfully",
            'available': True
        }
    except Exception as e:
        systems['toy_smt'] = {
            'translator': None,
            'status': f"Toy SMT initialization failed: {str(e)}",
            'available': False
        }

    # Initialize baseline translator
    try:
        baseline = BaselineTranslator(dictionary_path="data/bilingual_dict.json")
        systems['baseline'] = {
            'translator': baseline,
            'status': "Baseline translator initialized successfully",
            'available': True
        }
    except Exception as e:
        systems['baseline'] = {
            'translator': None,
            'status': f"Baseline initialization failed: {str(e)}",
            'available': False
        }

    return systems


def create_precision_table(bleu_result: Dict) -> pd.DataFrame:
    """Create n-gram precision table."""
    data = []
    for n in range(1, len(bleu_result['precisions']) + 1):
        num, denom, prec = bleu_result['precision_details'][n-1]
        data.append({
            'N-gram': f'{n}-gram',
            'Numerator': num,
            'Denominator': denom,
            'Precision': f'{prec:.4f}',
            'Precision %': f'{prec*100:.2f}%'
        })

    return pd.DataFrame(data)


def plot_precision_breakdown(bleu_result: Dict):
    """Create bar chart of n-gram precisions."""
    precisions = bleu_result['precisions']
    ngrams = [f'{i+1}-gram' for i in range(len(precisions))]

    fig = go.Figure(data=[
        go.Bar(
            x=ngrams,
            y=precisions,
            text=[f'{p:.4f}' for p in precisions],
            textposition='auto',
            marker_color='lightblue'
        )
    ])

    fig.update_layout(
        title='N-gram Precision Breakdown',
        xaxis_title='N-gram Order',
        yaxis_title='Precision',
        yaxis_range=[0, 1],
        height=400
    )

    return fig


def plot_candidate_comparison(candidates_results: List[Tuple[str, Dict]]):
    """Create comparison chart of BLEU scores."""
    names = [name for name, _ in candidates_results]
    scores = [result['bleu'] for _, result in candidates_results]

    # Color the best candidate
    colors = ['#28a745' if s == max(scores) else '#1f77b4' for s in scores]

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=scores,
            text=[f'{s:.4f}' for s in scores],
            textposition='auto',
            marker_color=colors
        )
    ])

    fig.update_layout(
        title='BLEU Score Comparison Across Candidates',
        xaxis_title='Translation System',
        yaxis_title='BLEU Score',
        yaxis_range=[0, 1],
        height=400
    )

    return fig


def display_bleu_details(candidate_name: str, bleu_result: Dict, is_best: bool = False, key_suffix: str = ""):
    """Display detailed BLEU statistics for a candidate."""
    container_class = "best-candidate" if is_best else "metric-box"

    st.markdown(f"### {candidate_name}" + (" 🏆 **BEST**" if is_best else ""))

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("BLEU Score", f"{bleu_result['bleu']:.4f}")
    with col2:
        st.metric("Brevity Penalty", f"{bleu_result['brevity_penalty']:.4f}")
    with col3:
        st.metric("Candidate Length", bleu_result['candidate_length'])
    with col4:
        st.metric("Reference Length", bleu_result['reference_length'])

    # Precision table
    st.markdown("#### N-gram Precision Details")
    precision_df = create_precision_table(bleu_result)
    st.dataframe(precision_df, use_container_width=True, hide_index=True)

    # Precision breakdown chart
    fig = plot_precision_breakdown(bleu_result)
    st.plotly_chart(fig, use_container_width=True, key=f"plotly_{candidate_name}_{key_suffix}")

    # Additional statistics
    with st.expander("📊 Additional Statistics"):
        st.markdown(f"""
        - **Geometric Mean**: {bleu_result['geometric_mean']:.4f}
        - **Weights**: {', '.join([f'{w:.2f}' for w in bleu_result['weights']])}
        - **Length Ratio**: {bleu_result['candidate_length'] / max(bleu_result['reference_length'], 1):.2f}
        """)


def main():
    """Main application."""

    # Header
    st.markdown('<div class="main-header">🌐 Statistical Machine Translation with BLEU Evaluation</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Compare multiple translation systems and evaluate with BLEU metric</div>',
                unsafe_allow_html=True)

    # Initialize
    sample_references = load_sample_references()
    translation_systems = initialize_translators()

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    # Show system status
    st.sidebar.markdown("### Translation Systems Status")
    for system_name, system_info in translation_systems.items():
        status_icon = "✅" if system_info['available'] else "❌"
        st.sidebar.markdown(f"{status_icon} **{system_name.upper()}**: {system_info['status']}")

    st.sidebar.markdown("---")

    # BLEU configuration
    st.sidebar.markdown("### BLEU Configuration")
    max_n = st.sidebar.slider("Maximum N-gram Order", 1, 6, 4)
    use_custom_weights = st.sidebar.checkbox("Use Custom Weights", False)

    if use_custom_weights:
        st.sidebar.markdown("#### N-gram Weights")
        weights = []
        for i in range(max_n):
            weight = st.sidebar.number_input(
                f"{i+1}-gram weight",
                min_value=0.0,
                max_value=1.0,
                value=1.0/max_n,
                step=0.05,
                key=f"weight_{i}"
            )
            weights.append(weight)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        st.sidebar.info(f"Normalized weights: {[f'{w:.3f}' for w in weights]}")
    else:
        weights = None

    # Initialize BLEU scorer
    bleu_scorer = BLEUScorer(max_n=max_n, weights=weights)

    # Main content
    st.markdown("---")

    # Input section
    st.header("📝 Input")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Source Text (English)")
        source_text = st.text_area(
            "Enter source text to translate:",
            value="the cat is on the mat",
            height=100,
            key="source_input"
        )

    with col2:
        st.subheader("Reference Translation(s) (Hindi)")

        # Reference input method
        ref_method = st.radio(
            "Reference input method:",
            ["Select from samples", "Upload file", "Enter manually"],
            horizontal=True
        )

        references = []

        if ref_method == "Select from samples":
            if sample_references:
                sample_options = [
                    f"Sample {s['id']}: {s['source'][:40]}..." for s in sample_references
                ]
                selected_idx = st.selectbox("Select a sample:", range(len(sample_options)),
                                             format_func=lambda i: sample_options[i])

                selected_sample = sample_references[selected_idx]
                st.info(f"**Source**: {selected_sample['source']}")
                st.info(f"**Description**: {selected_sample['description']}")

                # Update source text
                source_text = selected_sample['source']

                # Show references
                references = selected_sample['references']
                st.success(f"**{len(references)} reference(s) loaded:**")
                for i, ref in enumerate(references, 1):
                    st.markdown(f"{i}. {ref}")
            else:
                st.warning("No sample references found. Please check data/sample_references.json")

        elif ref_method == "Upload file":
            uploaded_file = st.file_uploader("Upload reference file (.txt)", type=['txt'])
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                references = [line.strip() for line in content.split('\n') if line.strip()]
                st.success(f"Loaded {len(references)} reference(s)")
                for i, ref in enumerate(references, 1):
                    st.markdown(f"{i}. {ref}")

        else:  # Enter manually
            ref_count = st.number_input("Number of references:", min_value=1, max_value=5, value=1)
            for i in range(ref_count):
                ref = st.text_input(f"Reference {i+1}:", key=f"ref_{i}")
                if ref:
                    references.append(ref)

    # Translation and Evaluation section
    st.markdown("---")
    st.header("🔄 Translation & Evaluation")

    if st.button("🚀 Translate and Evaluate", type="primary", use_container_width=True):
        if not source_text.strip():
            st.error("Please enter source text.")
        elif not references:
            st.error("Please provide at least one reference translation.")
        else:
            with st.spinner("Translating and computing BLEU scores..."):

                candidates_results = []

                # Candidate 1: SMT (Moses or Toy)
                st.subheader("1️⃣ SMT Translation")

                if translation_systems['moses']['available']:
                    try:
                        smt_translation = translation_systems['moses']['translator'].translate(source_text)
                        st.info(f"**Moses SMT**: {smt_translation}")
                        bleu_result = bleu_scorer.compute_bleu(smt_translation, references)
                        candidates_results.append(("Moses SMT", smt_translation, bleu_result))
                    except Exception as e:
                        st.error(f"Moses translation failed: {str(e)}")

                if translation_systems['toy_smt']['available']:
                    try:
                        toy_translation = translation_systems['toy_smt']['translator'].translate(source_text)
                        st.info(f"**Toy SMT**: {toy_translation}")
                        bleu_result = bleu_scorer.compute_bleu(toy_translation, references)
                        candidates_results.append(("Toy SMT", toy_translation, bleu_result))
                    except Exception as e:
                        st.error(f"Toy SMT translation failed: {str(e)}")

                # Candidate 2: Baseline word-by-word
                st.subheader("2️⃣ Baseline Word-by-Word Translation")

                if translation_systems['baseline']['available']:
                    try:
                        baseline_translation = translation_systems['baseline']['translator'].translate(source_text)
                        st.info(f"**Baseline**: {baseline_translation}")
                        bleu_result = bleu_scorer.compute_bleu(baseline_translation, references)
                        candidates_results.append(("Baseline (Word-by-Word)", baseline_translation, bleu_result))
                    except Exception as e:
                        st.error(f"Baseline translation failed: {str(e)}")

                # Candidate 3: User-provided
                st.subheader("3️⃣ Custom Candidate (Optional)")

                user_candidate = st.text_input(
                    "Enter your own translation to evaluate:",
                    key="user_candidate"
                )

                if user_candidate.strip():
                    bleu_result = bleu_scorer.compute_bleu(user_candidate, references)
                    candidates_results.append(("User Candidate", user_candidate, bleu_result))

                # Results section
                if candidates_results:
                    st.markdown("---")
                    st.header("📊 Results")

                    # Comparison chart
                    st.subheader("BLEU Score Comparison")
                    comparison_data = [(name, result) for name, _, result in candidates_results]
                    fig_comparison = plot_candidate_comparison(comparison_data)
                    st.plotly_chart(fig_comparison, use_container_width=True)

                    # Find best candidate
                    best_idx = max(range(len(candidates_results)),
                                   key=lambda i: candidates_results[i][2]['bleu'])

                    # Detailed results for each candidate
                    st.markdown("---")
                    st.subheader("Detailed BLEU Analysis")

                    for idx, (name, translation, bleu_result) in enumerate(candidates_results):
                        with st.container():
                            st.markdown(f"**Translation**: _{translation}_")
                            display_bleu_details(name, bleu_result, is_best=(idx == best_idx), key_suffix=str(idx))
                            st.markdown("---")

                    # Summary
                    st.success(f"""
                    ### 🎯 Summary
                    - **Best System**: {candidates_results[best_idx][0]}
                    - **Best BLEU Score**: {candidates_results[best_idx][2]['bleu']:.4f}
                    - **Total Candidates Evaluated**: {len(candidates_results)}
                    """)

    # Information section
    st.markdown("---")
    st.header("ℹ️ About")

    with st.expander("📖 About BLEU Score"):
        st.markdown("""
        **BLEU (Bilingual Evaluation Understudy)** is an automatic metric for evaluating machine translation quality.

        **Key Components:**
        1. **Modified N-gram Precision**: Measures how many n-grams in the candidate appear in the references (with clipping)
        2. **Brevity Penalty (BP)**: Penalizes candidates shorter than references
        3. **Geometric Mean**: Combines precisions from different n-gram orders

        **Formula:**
        ```
        BLEU = BP × exp(Σ(w_n × log(p_n)))
        ```

        where:
        - `BP = 1` if `c > r`, else `exp(1 - r/c)`
        - `c` = candidate length
        - `r` = closest reference length
        - `p_n` = n-gram precision
        - `w_n` = weight for n-gram order n

        **Range**: 0 (worst) to 1 (perfect match)

        **Reference**: Papineni et al. (2002), "BLEU: a Method for Automatic Evaluation of Machine Translation"
        """)

    with st.expander("🔧 About Translation Systems"):
        st.markdown("""
        ### Moses SMT
        State-of-the-art statistical machine translation toolkit. Requires separate installation and trained models.

        ### Toy SMT
        Simplified phrase-based SMT implementation demonstrating core SMT principles:
        - Phrase table with translation probabilities
        - N-gram language model
        - Beam search decoding
        - Log-linear model combination

        ### Baseline (Word-by-Word)
        Naive translation using bilingual dictionary without reordering or phrase translation.
        Demonstrates why SMT is necessary.

        ### Custom Candidate
        Enter your own translation to evaluate against the reference(s).
        """)

    with st.expander("📚 References"):
        st.markdown("""
        - Papineni, K., Roukos, S., Ward, T., & Zhu, W. J. (2002). BLEU: a method for automatic evaluation of machine translation. *ACL*.
        - Koehn, P., et al. (2007). Moses: Open source toolkit for statistical machine translation. *ACL*.
        - Och, F. J., & Ney, H. (2003). A systematic comparison of various statistical alignment models. *Computational linguistics*.
        """)


if __name__ == "__main__":
    main()
