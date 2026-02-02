"""
Statistical Machine Translation with BLEU Evaluation
Streamlit Web Application

Features:
- Source text input
- Reference selection/upload
- Multiple translation systems (Moses, Toy SMT, Word-by-Word)
- BLEU evaluation with detailed statistics
- Comparative analysis with visualizations
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.bleu import compute_bleu, tokenize
from src.toy_smt import ToySMT
from src.moses_interface import create_moses_decoder
from src.word_by_word import WordByWordTranslator
from src.utils import load_built_in_corpus, create_ngram_precision_table


# Page configuration
st.set_page_config(
    page_title="SMT-BLEU Evaluation System",
    page_icon="🌐",
    layout="wide"
)

# Title and description
st.title("Statistical Machine Translation with BLEU Evaluation")
st.markdown("**English → Hindi Translation System**")
st.markdown("---")


@st.cache_resource
def load_translators():
    """Load all translation systems."""
    toy_smt = None
    word_by_word = None
    moses_decoder = None

    try:
        toy_smt = ToySMT()
    except Exception as e:
        pass

    try:
        word_by_word = WordByWordTranslator()
    except Exception as e:
        pass

    try:
        moses_decoder = create_moses_decoder()
    except Exception as e:
        pass

    return toy_smt, word_by_word, moses_decoder


@st.cache_data
def load_corpus():
    """Load built-in corpus."""
    try:
        return load_built_in_corpus()
    except Exception:
        return {"train": [], "dev": [], "test": [], "references": []}


# Load systems
toy_smt, word_by_word, moses_decoder = load_translators()
corpus = load_corpus()

# Sidebar configuration
st.sidebar.header("Configuration")

# System status
st.sidebar.subheader("System Status")
if moses_decoder and moses_decoder.is_available:
    st.sidebar.success("Moses: Available")
else:
    st.sidebar.warning("Moses: Not configured (using Toy SMT)")

if toy_smt:
    st.sidebar.success("Toy SMT: Available")
else:
    st.sidebar.error("Toy SMT: Failed to load")

if word_by_word:
    st.sidebar.success("Word-by-Word: Available")
else:
    st.sidebar.error("Word-by-Word: Failed to load")

st.sidebar.markdown("---")
st.sidebar.subheader("BLEU Configuration")
max_n = st.sidebar.slider("Max N-gram Order", 1, 4, 4)
use_smoothing = st.sidebar.checkbox(
    "Enable sentence-level smoothing",
    value=False,
    help="Avoids all-zero sentence BLEU when high-order n-grams are sparse."
)
smooth_eps = st.sidebar.number_input(
    "Smoothing epsilon",
    min_value=1e-12,
    max_value=1e-2,
    value=1e-9,
    step=1e-9,
    format="%.12f",
    disabled=not use_smoothing
)

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input")

    # Source text input
    source_text = st.text_area(
        "English Source Text:",
        value="Hello, how are you?",
        height=100,
        help="Enter the English sentence to translate"
    )

    # Reference selection
    st.subheader("Reference Translation(s)")

    reference_mode = st.radio(
        "Reference Mode:",
        ["Built-in Examples", "Upload File", "Manual Input"],
        horizontal=True
    )

    references = []

    if reference_mode == "Built-in Examples":
        ref_entries = corpus.get('references', [])
        if ref_entries:
            ref_options = {}
            for ref in ref_entries:
                label = f"Ref {ref['id']}: {ref['en'][:50]}..."
                ref_options[label] = ref

            selected_ref = st.selectbox(
                "Select Reference:",
                options=list(ref_options.keys())
            )

            if selected_ref:
                ref_data = ref_options[selected_ref]
                source_text = ref_data['en']
                st.info(f"**Source:** {ref_data['en']}")

                references = ref_data['hi']
                for i, ref in enumerate(references, 1):
                    st.success(f"**Reference {i}:** {ref}")
        else:
            st.warning("No built-in references found.")

    elif reference_mode == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload Reference File (.txt)",
            type=['txt'],
            help="Each line is treated as a separate reference translation"
        )

        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            references = [line.strip() for line in content.split('\n') if line.strip()]

            st.success(f"Loaded {len(references)} reference(s)")
            for i, ref in enumerate(references, 1):
                st.text(f"Reference {i}: {ref}")

    else:  # Manual Input
        num_refs = st.number_input(
            "Number of References:",
            min_value=1,
            max_value=5,
            value=1
        )

        for i in range(num_refs):
            ref = st.text_input(
                f"Reference {i+1}:",
                value="" if i > 0 else "नमस्ते, आप कैसे हैं?",
                key=f"ref_{i}"
            )
            if ref.strip():
                references.append(ref.strip())

with col2:
    st.subheader("Translation & Evaluation")

    if st.button("Translate & Evaluate", type="primary"):
        if not source_text.strip():
            st.error("Please enter source text")
        elif not references:
            st.error("Please provide at least one reference translation")
        else:
            # Generate translations from available systems
            translations = {}

            # 1. Moses
            if moses_decoder and moses_decoder.is_available:
                with st.spinner("Running Moses decoder..."):
                    try:
                        moses_output = moses_decoder.translate(source_text)
                        if moses_output:
                            translations['Moses SMT'] = moses_output
                    except Exception:
                        pass

            # 2. Toy SMT
            if toy_smt:
                with st.spinner("Running Toy SMT..."):
                    try:
                        toy_output = toy_smt.translate(source_text)
                        if toy_output:
                            translations['Toy SMT'] = toy_output
                    except Exception as e:
                        st.warning(f"Toy SMT error: {e}")

            # 3. Word-by-Word
            if word_by_word:
                with st.spinner("Running Word-by-Word baseline..."):
                    try:
                        wbw_output = word_by_word.translate(source_text)
                        if wbw_output:
                            translations['Word-by-Word'] = wbw_output
                    except Exception as e:
                        st.warning(f"Word-by-Word error: {e}")

            # Allow user to add custom translation
            st.subheader("Add Custom Translation")
            custom_trans = st.text_input(
                "Custom Translation (optional):",
                key="custom_translation"
            )
            if custom_trans.strip():
                translations['Custom'] = custom_trans.strip()

            # Evaluate all translations
            if not translations:
                st.warning("No translations available. Please configure at least one translation system.")
            else:
                st.subheader("Evaluation Results")

                # Compute BLEU for all candidates
                results = {}
                for system_name, translation in translations.items():
                    bleu_result = compute_bleu(
                        translation,
                        references,
                        max_n=max_n,
                        smoothing=use_smoothing,
                        smooth_eps=float(smooth_eps)
                    )
                    results[system_name] = {
                        'translation': translation,
                        'bleu_result': bleu_result
                    }

                # ---- System Comparison Table ----
                st.subheader("System Comparison")

                comparison_data = []
                for system_name, data in results.items():
                    br = data['bleu_result']
                    row = {
                        'System': system_name,
                        'BLEU': f"{br['bleu_score']:.4f}",
                        'BP': f"{br['bp']:.4f}",
                        'Length (c/r)': f"{br['candidate_length']}/{br['reference_length']}",
                    }
                    # Add individual BLEU-n scores
                    for n in range(1, max_n + 1):
                        key = f'bleu_{n}'
                        if key in br:
                            row[f'BLEU-{n}'] = f"{br[key]:.4f}"
                    comparison_data.append(row)

                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)

                # ---- BLEU Score Bar Chart ----
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(results.keys()),
                        y=[data['bleu_result']['bleu_score'] for data in results.values()],
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(results)],
                        text=[f"{data['bleu_result']['bleu_score']:.4f}" for data in results.values()],
                        textposition='auto'
                    )
                ])
                fig.update_layout(
                    title="BLEU Score Comparison Across Systems",
                    xaxis_title="Translation System",
                    yaxis_title="BLEU Score",
                    height=400,
                    yaxis=dict(range=[0, 1])
                )
                st.plotly_chart(fig, use_container_width=True)

                # ---- Detailed Results for Each System ----
                st.subheader("Detailed Results")

                for system_name, data in results.items():
                    with st.expander(f"{system_name} - Detailed Analysis", expanded=True):
                        translation = data['translation']
                        br = data['bleu_result']

                        st.markdown(f"**Translation:** {translation}")
                        st.markdown("---")

                        # Metrics in columns
                        mc1, mc2, mc3, mc4 = st.columns(4)

                        with mc1:
                            st.metric("BLEU Score", f"{br['bleu_score']:.4f}")
                        with mc2:
                            st.metric("Brevity Penalty", f"{br['bp']:.4f}")
                        with mc3:
                            st.metric("Candidate Length (c)", br['candidate_length'])
                        with mc4:
                            st.metric("Reference Length (r)", br['reference_length'])

                        # N-gram precision table
                        st.markdown("**N-gram Precision Table:**")
                        ngram_table = create_ngram_precision_table(br)
                        df_ngram = pd.DataFrame(ngram_table)
                        st.dataframe(df_ngram, use_container_width=True)

                        # Individual BLEU-n bar chart
                        bleu_n_labels = []
                        bleu_n_values = []
                        for n in range(1, max_n + 1):
                            key = f'bleu_{n}'
                            if key in br:
                                bleu_n_labels.append(f"BLEU-{n}")
                                bleu_n_values.append(br[key])

                        fig_ind = go.Figure(data=[
                            go.Bar(
                                x=bleu_n_labels,
                                y=bleu_n_values,
                                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(bleu_n_labels)],
                                text=[f"{v:.4f}" for v in bleu_n_values],
                                textposition='auto'
                            )
                        ])
                        fig_ind.update_layout(
                            title=f"{system_name} - Individual BLEU-n Scores",
                            xaxis_title="Metric",
                            yaxis_title="Score",
                            height=300,
                            yaxis=dict(range=[0, 1])
                        )
                        st.plotly_chart(fig_ind, use_container_width=True)

                        # Tokenization info
                        st.markdown("**Tokenization Details:**")
                        candidate_tokens = tokenize(translation)
                        st.text(f"Candidate tokens ({len(candidate_tokens)}): {candidate_tokens}")
                        for i, ref in enumerate(references, 1):
                            ref_tok = tokenize(ref)
                            st.text(f"Reference {i} tokens ({len(ref_tok)}): {ref_tok}")

# Footer
st.markdown("---")
st.markdown(
    f"**Current BLEU mode:** {'Smoothed sentence BLEU' if use_smoothing else 'Strict unsmoothed BLEU'}"
)
st.markdown("""
### About This System

This application demonstrates Statistical Machine Translation with BLEU evaluation
for English to Hindi translation.

**Translation Systems:**
- **Moses SMT**: Industry-standard phrase-based SMT (requires separate configuration)
- **Toy SMT**: Custom phrase-based SMT with trigram LM and greedy decoding
- **Word-by-Word**: Simple dictionary-based baseline

**BLEU Metric** (Papineni et al., 2002):
- Measures n-gram overlap between candidate and reference translations
- Includes modified precision with clipping and brevity penalty
- Reports BLEU-1 through BLEU-4 and cumulative BLEU score

**Developed for:** Assignment 2 - SMT with BLEU Evaluation
""")
