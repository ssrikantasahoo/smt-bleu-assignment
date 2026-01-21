"""
Utility functions for SMT-BLEU assignment
"""

import json
import os
from typing import List, Dict


def load_built_in_corpus(data_dir: str = None) -> Dict:
    """
    Load built-in English-Hindi corpus.
    
    Args:
        data_dir: Directory containing built_in_corpus.json
        
    Returns:
        Dictionary with train, dev, test, and references
    """
    if data_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, '..', 'data')
    
    corpus_path = os.path.join(data_dir, 'built_in_corpus.json')
    
    with open(corpus_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    return corpus


def format_bleu_result(result: Dict) -> str:
    """
    Format BLEU result for display.
    
    Args:
        result: BLEU result dictionary from compute_bleu()
        
    Returns:
        Formatted string
    """
    lines = []
    lines.append(f"BLEU Score: {result['bleu_score']:.4f}")
    lines.append(f"Brevity Penalty: {result['bp']:.4f}")
    lines.append(f"Candidate Length: {result['candidate_length']}")
    lines.append(f"Reference Length: {result['reference_length']}")
    lines.append(f"Length Ratio (c/r): {result['length_ratio']:.4f}")
    lines.append("")
    lines.append("N-gram Precisions:")
    
    for stat in result['ngram_stats']:
        n = stat['n']
        precision = stat['precision']
        clipped = stat['clipped_count']
        total = stat['total_count']
        lines.append(f"  BLEU-{n}: {precision:.4f} ({clipped}/{total})")
    
    return '\n'.join(lines)


def create_ngram_precision_table(result: Dict) -> List[Dict]:
    """
    Create n-gram precision table for display.
    
    Args:
        result: BLEU result dictionary
        
    Returns:
        List of dictionaries for table display
    """
    table = []
    for stat in result['ngram_stats']:
        table.append({
            'N-gram': f"{stat['n']}-gram",
            'Clipped Count': stat['clipped_count'],
            'Total Count': stat['total_count'],
            'Precision': f"{stat['precision']:.4f}"
        })
    
    return table


def normalize_text(text: str) -> str:
    """
    Normalize text for consistent processing.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    # Basic normalization
    text = text.strip()
    
    # Unicode normalization for Hindi text
    import unicodedata
    text = unicodedata.normalize('NFC', text)
    
    return text


def save_results_to_file(results: Dict, output_path: str):
    """
    Save evaluation results to JSON file.
    
    Args:
        results: Results dictionary
        output_path: Output file path
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def load_reference_file(file_path: str) -> List[str]:
    """
    Load reference translations from a text file.
    Each line is treated as a separate reference.
    
    Args:
        file_path: Path to reference file
        
    Returns:
        List of reference translations
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        references = [line.strip() for line in f if line.strip()]
    
    return references
