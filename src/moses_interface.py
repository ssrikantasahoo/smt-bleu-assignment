"""
Moses Decoder Interface
Provides Python wrapper for Moses SMT decoder
"""

import subprocess
import os
import shlex
from typing import Optional, List


class MosesDecoder:
    """Interface to Moses decoder"""
    
    def __init__(self, moses_ini_path: Optional[str] = None, 
                 moses_bin_path: Optional[str] = None):
        """
        Initialize Moses decoder interface.
        
        Args:
            moses_ini_path: Path to moses.ini configuration file
            moses_bin_path: Path to moses binary (default: search in PATH)
        """
        self.moses_ini_path = moses_ini_path
        
        # Try to find Moses binary
        if moses_bin_path is None:
            # Try common locations
            possible_paths = [
                'moses',  # In PATH
                '/usr/local/bin/moses',
                os.path.expanduser('~/mosesdecoder/bin/moses'),
                './moses/mosesdecoder/bin/moses'
            ]
            
            self.moses_bin_path = None
            for path in possible_paths:
                if self._check_moses_exists(path):
                    self.moses_bin_path = path
                    break
        else:
            self.moses_bin_path = moses_bin_path
        
        self.is_available = (
            self.moses_bin_path is not None and 
            self.moses_ini_path is not None and
            os.path.exists(self.moses_ini_path)
        )
    
    def _check_moses_exists(self, path: str) -> bool:
        """Check if Moses binary exists at given path"""
        try:
            # Try to run moses --version or moses -h
            result = subprocess.run(
                [path, '--version'],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0 or 'Moses' in result.stderr
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def translate(self, source_sentence: str) -> Optional[str]:
        """
        Translate a single sentence using Moses.
        
        Args:
            source_sentence: English input sentence
            
        Returns:
            Hindi translation, or None if Moses is not available
        """
        if not self.is_available:
            return None
        
        try:
            # Run Moses decoder
            cmd = [
                self.moses_bin_path,
                '-f', self.moses_ini_path
            ]
            
            result = subprocess.run(
                cmd,
                input=source_sentence,
                capture_output=True,
                timeout=30,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                translation = result.stdout.strip()
                return translation
            else:
                print(f"Moses error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("Moses translation timed out")
            return None
        except Exception as e:
            print(f"Error running Moses: {e}")
            return None
    
    def translate_batch(self, source_sentences: List[str]) -> List[Optional[str]]:
        """
        Translate multiple sentences.
        
        Args:
            source_sentences: List of English sentences
            
        Returns:
            List of Hindi translations
        """
        if not self.is_available:
            return [None] * len(source_sentences)
        
        # For simplicity, translate one by one
        # In production, would use batch mode
        translations = []
        for sent in source_sentences:
            translations.append(self.translate(sent))
        
        return translations
    
    def get_status(self) -> dict:
        """
        Get status information about Moses availability.
        
        Returns:
            Dictionary with status information
        """
        return {
            'available': self.is_available,
            'moses_bin': self.moses_bin_path,
            'moses_ini': self.moses_ini_path,
            'moses_exists': self.moses_bin_path is not None and 
                           os.path.exists(self.moses_bin_path) if self.moses_bin_path else False,
            'ini_exists': self.moses_ini_path is not None and 
                         os.path.exists(self.moses_ini_path) if self.moses_ini_path else False
        }


# Configuration helper
def get_default_moses_config() -> dict:
    """
    Get default Moses configuration.
    User should edit this to point to their trained model.
    
    Returns:
        Dictionary with Moses paths
    """
    return {
        'moses_ini_path': os.path.expanduser('~/moses_model/model/moses.ini'),
        'moses_bin_path': 'moses'  # Assumes moses is in PATH
    }


def create_moses_decoder() -> MosesDecoder:
    """
    Create Moses decoder with default or environment-configured paths.
    
    Environment variables:
    - MOSES_INI_PATH: Path to moses.ini
    - MOSES_BIN_PATH: Path to moses binary
    
    Returns:
        MosesDecoder instance
    """
    config = get_default_moses_config()
    
    # Check environment variables
    moses_ini = os.environ.get('MOSES_INI_PATH', config['moses_ini_path'])
    moses_bin = os.environ.get('MOSES_BIN_PATH', config['moses_bin_path'])
    
    return MosesDecoder(moses_ini_path=moses_ini, moses_bin_path=moses_bin)


# Demo
def demo():
    """Demonstrate Moses interface"""
    decoder = create_moses_decoder()
    status = decoder.get_status()
    
    print("Moses Decoder Status:")
    print(f"  Available: {status['available']}")
    print(f"  Binary: {status['moses_bin']}")
    print(f"  Config: {status['moses_ini']}")
    print(f"  Binary exists: {status['moses_exists']}")
    print(f"  Config exists: {status['ini_exists']}")
    
    if decoder.is_available:
        print("\nTesting translation:")
        test_sent = "Hello, how are you?"
        translation = decoder.translate(test_sent)
        print(f"  Source: {test_sent}")
        print(f"  Translation: {translation}")
    else:
        print("\nMoses is not available. Please configure paths.")


if __name__ == '__main__':
    demo()
