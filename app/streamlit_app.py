"""
Statistical Machine Translation with BLEU Evaluation
Streamlit Web Application

Features:
- Source text input
- Reference selection/upload
- Multiple translation systems (Moses, Toy SMT, Word-by-Word)
- BLEU evaluation with detailed statistics
- Comparative analysis
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
st.title("🌐 Statistical Machine Translation with BLEU Evaluation")
st.markdown("**English → Hindi Translation System**")
st.markdown("---")


@st.cache_resource
def load_translators():
    """Load all translation systems"""
    try:
        toy_smt = ToySMT()
    except Exception as e:
        st.warning(f"Failed to load Toy SMT: {e}")
        toy_smt = None
    
    try:
        word_by_word = WordByWordTranslator()
    except Exception as e:
        st.warning(f"Failed to load Word-by-Word: {e}")
        word_by_word = None
    
    try:
        moses_decoder = create_moses_decoder()
    except Exception as e:
        st.warning(f"Failed to load Moses: {e}")
        moses_decoder = None
    
    return toy_smt, word_by_word, moses_decoder


@st.cache_data
def load_corpus():
    """Load built-in corpus"""
    return load_built_in_corpus()


# Load systems
toy_smt, word_by_word, moses_decoder = load_translators()
corpus = load_corpus()

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# System status
st.sidebar.subheader("System Status")
if moses_decoder and moses_decoder.is_available:
    st.sidebar.success("✅ Moses: Available")
else:
    st.sidebar.warning("⚠️ Moses: Not configured")

if toy_smt:
    st.sidebar.success("✅ Toy SMT: Available")
else:
    st.sidebar.error("❌ Toy SMT: Failed to load")

if word_by_word:
    st.sidebar.success("✅ Word-by-Word: Available")
else:
    st.sidebar.error("❌ Word-by-Word: Failed to load")

st.sidebar.markdown("---")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input")
    
    # Source text input
    source_text = st.text_area(
        "English Source Text:",
        value="Hello, how are you?",
        height=100,
        help="Enter the English sentence to translate"
    )
    
    # Reference selection
    st.subheader("📚 Reference Translation(s)")
    
    reference_mode = st.radio(
        "Reference Mode:",
        ["Built-in Examples", "Upload File", "Manual Input"],
        horizontal=True
    )
    
    references = []
    
    if reference_mode == "Built-in Examples":
        # Show built-in references
        ref_options = {
            f"Ref {ref['id']}: {ref['en'][:50]}...": ref
            for ref in corpus['references']
        }
        
        selected_ref = st.selectbox(
            "Select Reference:",
            options=list(ref_options.keys())
        )
        
        if selected_ref:
            ref_data = ref_options[selected_ref]
            st.info(f"**Source:** {ref_data['en']}")
            
            # Show all reference translations
            references = ref_data['hi']
            for i, ref in enumerate(references, 1):
                st.success(f"**Reference {i}:** {ref}")
    
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
    st.subheader("🔄 Translation & Evaluation")
    
    if st.button("🚀 Translate & Evaluate", type="primary"):
        if not source_text.strip():
            st.error("Please enter source text")
        elif not references:
            st.error("Please provide at least one reference translation")
        else:
            # Container for results
            results_container = st.container()
            
            with results_container:
                # Generate translations from available systems
                translations = {}
                
                # 1. Moses
                if moses_decoder and moses_decoder.is_available:
                    with st.spinner("Running Moses decoder..."):
                        moses_output = moses_decoder.translate(source_text)
                        if moses_output:
                            translations['Moses SMT'] = moses_output
                
                # 2. Toy SMT
                if toy_smt:
                    with st.spinner("Running Toy SMT..."):
                        toy_output = toy_smt.translate(source_text)
                        if toy_output:
                            translations['Toy SMT'] = toy_output
                
                # 3. Word-by-Word
                if word_by_word:
                    with st.spinner("Running Word-by-Word baseline..."):
                        wbw_output = word_by_word.translate(source_text)
                        if wbw_output:
                            translations['Word-by-Word'] = wbw_output
                
                # Allow user to add custom translation
                st.subheader("➕ Add Custom Translation")
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
                    st.subheader("📊 Evaluation Results")
                    
                    # Compute BLEU for all candidates
                    results = {}
                    for system_name, translation in translations.items():
                        bleu_result = compute_bleu(translation, references, max_n=4)
                        results[system_name] = {
                            'translation': translation,
                            'bleu_result': bleu_result
                        }
                    
                    # Comparison table
                    st.subheader("🏆 System Comparison")
                    
                    comparison_data = []
                    for system_name, data in results.items():
                        bleu_res = data['bleu_result']
                        comparison_data.append({
                            'System': system_name,
                            'BLEU': f"{bleu_res['bleu_score']:.4f}",
                            'BLEU-1': f"{bleu_res['bleu_1']:.4f}",
                            'BLEU-2': f"{bleu_res['bleu_2']:.4f}",
                            'BLEU-3': f"{bleu_res['bleu_3']:.4f}",
                            'BLEU-4': f"{bleu_res['bleu_4']:.4f}",
                            'BP': f"{bleu_res['bp']:.4f}",
                            'Length': bleu_res['candidate_length']
                        })
                    
                    df_comparison = pd.DataFrame(comparison_data)
                    
                    # Highlight best BLEU score
                    def highlight_max(s):
                        if s.name == 'BLEU':
                            is_max = s == s.max()
                            return ['background-color: lightgreen' if v else '' for v in is_max]
                        return ['' for _ in s]
                    
                    st.dataframe(
                        df_comparison.style.apply(highlight_max, axis=0),
                        use_container_width=True
                    )
                    
                    # Visualize BLEU scores
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(results.keys()),
                            y=[data['bleu_result']['bleu_score'] for data in results.values()],
                            marker_color='lightblue'
                        )
                    ])
                    fig.update_layout(
                        title="BLEU Score Comparison",
                        xaxis_title="Translation System",
                        yaxis_title="BLEU Score",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed results for each system
                    st.subheader("📋 Detailed Results")
                    
                    for system_name, data in results.items():
                        with st.expander(f"🔍 {system_name} - Detailed Analysis"):
                            translation = data['translation']
                            bleu_res = data['bleu_result']
                            
                            st.markdown(f"**Translation:** {translation}")
                            st.markdown("---")
                            
                            # Metrics in columns
                            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                            
                            with metric_col1:
                                st.metric("BLEU Score", f"{bleu_res['bleu_score']:.4f}")
                            
                            with metric_col2:
                                st.metric("Brevity Penalty", f"{bleu_res['bp']:.4f}")
                            
                            with metric_col3:
                                st.metric("Candidate Length (c)", bleu_res['candidate_length'])
                            
                            with metric_col4:
                                st.metric("Reference Length (r)", bleu_res['reference_length'])
                            
                            # N-gram precision table
                            st.markdown("**N-gram Precision Details:**")
                            ngram_table = create_ngram_precision_table(bleu_res)
                            df_ngram = pd.DataFrame(ngram_table)
                            st.dataframe(df_ngram, use_container_width=True)
                            
                            # Individual BLEU scores
                            st.markdown("**Individual BLEU-n Scores:**")
                            bleu_scores_data = {
                                'Metric': ['BLEU-1', 'BLEU-2', 'BLEU-3', 'BLEU-4'],
                                'Score': [
                                    bleu_res['bleu_1'],
                                    bleu_res['bleu_2'],
                                    bleu_res['bleu_3'],
                                    bleu_res['bleu_4']
                                ]
                            }
                            df_bleu_scores = pd.DataFrame(bleu_scores_data)
                            
                            # Bar chart for individual scores
                            fig_individual = go.Figure(data=[
                                go.Bar(
                                    x=df_bleu_scores['Metric'],
                                    y=df_bleu_scores['Score'],
                                    marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                                )
                            ])
                            fig_individual.update_layout(
                                title=f"{system_name} - Individual BLEU Scores",
                                xaxis_title="BLEU Metric",
                                yaxis_title="Score",
                                height=300
                            )
                            st.plotly_chart(fig_individual, use_container_width=True)
                            
                            # Tokenization info
                            st.markdown("**Tokenization:**")
                            candidate_tokens = tokenize(translation)
                            ref_tokens = [tokenize(ref) for ref in references]
                            
                            st.text(f"Candidate tokens: {candidate_tokens}")
                            for i, ref_tok in enumerate(ref_tokens, 1):
                                st.text(f"Reference {i} tokens: {ref_tok}")

# Footer information
st.markdown("---")
st.markdown("""
### About This System

This application demonstrates Statistical Machine Translation with BLEU evaluation for English→Hindi translation.

**Translation Systems:**
- **Moses SMT**: Industry-standard phrase-based SMT (requires configuration)
- **Toy SMT**: Custom phrase-based SMT with trigram LM and beam search
- **Word-by-Word**: Simple dictionary-based baseline

**BLEU Metric:**
- Bilingual Evaluation Understudy (Papineni et al., 2002)
- Measures n-gram overlap between candidate and reference translations
- Includes modified precision with clipping and brevity penalty
- Reported as BLEU-1, BLEU-2, BLEU-3, BLEU-4, and cumulative BLEU

**Developed for:** Assignment 2 - SMT with BLEU Evaluation
""")
