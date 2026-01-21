"""
Hindi Tokenizer for Devanagari Script
Simple rule-based tokenization for Hindi text
"""

import re
import unicodedata


class HindiTokenizer:
    """
    Simple rule-based tokenizer for Hindi (Devanagari script)
    
    Handles:
    - Unicode normalization (NFC)
    - Punctuation separation
    - Number handling
    - Basic word segmentation
    """
    
    def __init__(self):
        # Devanagari range: U+0900 to U+097F
        self.devanagari_range = range(0x0900, 0x0980)
        
        # Common Hindi punctuation
        self.punctuation = set('।॥,.:;!?()[]{}"\'-')
    
    def normalize(self, text: str) -> str:
        """
        Normalize Unicode text to NFC form
        (Canonical composition for Devanagari)
        """
        return unicodedata.normalize('NFC', text)
    
    def is_devanagari(self, char: str) -> bool:
        """Check if character is in Devanagari range"""
        return ord(char) in self.devanagari_range
    
    def tokenize(self, text: str) -> list:
        """
        Tokenize Hindi text into words
        
        Args:
            text: Hindi text string
            
        Returns:
            List of tokens
        """
        # Normalize first
        text = self.normalize(text)
        
        # Add spaces around punctuation
        for punct in self.punctuation:
            text = text.replace(punct, f' {punct} ')
        
        # Split on whitespace
        tokens = text.split()
        
        # Remove empty tokens
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def detokenize(self, tokens: list) -> str:
        """
        Reconstruct text from tokens
        
        Args:
            tokens: List of word tokens
            
        Returns:
            Reconstructed text
        """
        text = ' '.join(tokens)
        
        # Remove spaces before certain punctuation
        text = re.sub(r'\s+([।॥,.:;!?])', r'\1', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


def tokenize_file(input_path: str, output_path: str):
    """
    Tokenize a Hindi text file
    
    Args:
        input_path: Input file path
        output_path: Output file path
    """
    tokenizer = HindiTokenizer()
    
    with open(input_path, 'r', encoding='utf-8') as f_in:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                tokens = tokenizer.tokenize(line.strip())
                f_out.write(' '.join(tokens) + '\n')


def demo():
    """Demonstrate Hindi tokenizer"""
    tokenizer = HindiTokenizer()
    
    test_sentences = [
        "नमस्ते, आप कैसे हैं?",
        "मुझे प्रोग्रामिंग पसंद है।",
        "आज मौसम अच्छा है।",
        "यह एक पेन है।"
    ]
    
    print("Hindi Tokenizer Demo\n")
    for sent in test_sentences:
        tokens = tokenizer.tokenize(sent)
        detok = tokenizer.detokenize(tokens)
        
        print(f"Original:     {sent}")
        print(f"Tokens:       {tokens}")
        print(f"Detokenized:  {detok}")
        print(f"Match:        {sent == detok}")
        print()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 3:
        # File mode
        tokenize_file(sys.argv[1], sys.argv[2])
        print(f"Tokenized {sys.argv[1]} -> {sys.argv[2]}")
    else:
        # Demo mode
        demo()
