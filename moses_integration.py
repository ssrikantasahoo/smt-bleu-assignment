"""
Moses SMT Integration Module
=============================
Provides integration with Moses Statistical Machine Translation toolkit.

Moses is a state-of-the-art SMT system. This module provides:
- Detection of Moses installation
- Model path configuration
- Translation via Moses decoder
- Fallback to toy SMT when Moses is unavailable

Moses installation instructions:
https://github.com/moses-smt/mosesdecoder
"""

import subprocess
import os
from typing import Optional, Tuple
import shutil


class MosesTranslator:
    """
    Interface to Moses SMT decoder.

    Supports both Moses installation and fallback to toy SMT.
    """

    def __init__(self,
                 moses_decoder_path: Optional[str] = None,
                 model_dir: Optional[str] = None):
        """
        Initialize Moses translator.

        Args:
            moses_decoder_path: Path to Moses decoder binary
            model_dir: Path to trained Moses model directory
        """
        self.moses_decoder_path = moses_decoder_path
        self.model_dir = model_dir
        self.is_available = self._check_moses_available()

    def _check_moses_available(self) -> bool:
        """
        Check if Moses is available on the system.

        Returns:
            True if Moses is available and configured
        """
        # Check if decoder path is provided and exists
        if self.moses_decoder_path and os.path.exists(self.moses_decoder_path):
            # Check if model directory exists and has required files
            if self.model_dir and os.path.exists(self.model_dir):
                moses_ini = os.path.join(self.model_dir, "moses.ini")
                if os.path.exists(moses_ini):
                    return True

        # Try to find Moses in PATH
        moses_binary = shutil.which("moses")
        if moses_binary:
            self.moses_decoder_path = moses_binary
            # Still need model directory
            return self.model_dir is not None and os.path.exists(self.model_dir)

        return False

    def translate(self, source_text: str) -> str:
        """
        Translate using Moses decoder.

        Args:
            source_text: Source language text

        Returns:
            Translated text

        Raises:
            RuntimeError: If Moses is not available
        """
        if not self.is_available:
            raise RuntimeError(
                "Moses is not available. Please configure Moses or use toy SMT fallback."
            )

        # Prepare Moses command
        moses_ini = os.path.join(self.model_dir, "moses.ini")

        try:
            # Run Moses decoder
            # Format: echo "source text" | moses -f moses.ini
            process = subprocess.Popen(
                [self.moses_decoder_path, "-f", moses_ini],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=source_text + "\n", timeout=30)

            if process.returncode != 0:
                raise RuntimeError(f"Moses decoder failed: {stderr}")

            # Parse output (Moses returns translation on stdout)
            translation = stdout.strip()
            return translation

        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError("Moses decoder timed out")
        except Exception as e:
            raise RuntimeError(f"Moses translation failed: {str(e)}")

    def translate_batch(self, source_texts: list) -> list:
        """
        Translate multiple sentences.

        Args:
            source_texts: List of source sentences

        Returns:
            List of translations
        """
        return [self.translate(text) for text in source_texts]

    def get_configuration_instructions(self) -> str:
        """
        Get instructions for configuring Moses.

        Returns:
            Configuration instructions as string
        """
        instructions = """
Moses Configuration Instructions
================================

1. Install Moses:
   - Download from: https://github.com/moses-smt/mosesdecoder
   - Build instructions: http://www.statmt.org/moses/?n=Development.GetStarted

2. Train a model OR download pre-trained model:
   - Training tutorial: http://www.statmt.org/moses/?n=Moses.Baseline
   - Pre-trained models: http://www.statmt.org/moses/?n=Moses.Models

3. Configure paths in this application:
   - Set MOSES_DECODER_PATH to the moses binary (e.g., /path/to/mosesdecoder/bin/moses)
   - Set MOSES_MODEL_DIR to your model directory (containing moses.ini)

4. Example directory structure:
   model_dir/
   ├── moses.ini          (main configuration file)
   ├── phrase-table.gz    (phrase translation table)
   ├── reordering-table.gz
   └── lm/                (language model files)

5. Environment variables (optional):
   export MOSES_DECODER=/path/to/moses
   export MOSES_MODEL=/path/to/model

For this assignment, you can use the toy SMT fallback if Moses is unavailable.
The toy SMT demonstrates the same principles (phrase table + LM + beam search).
"""
        return instructions


def detect_moses_installation() -> Tuple[Optional[str], bool]:
    """
    Detect Moses installation on the system.

    Returns:
        Tuple of (path_to_moses, is_available)
    """
    # Check environment variable
    moses_path = os.environ.get("MOSES_DECODER")
    if moses_path and os.path.exists(moses_path):
        return moses_path, True

    # Check common installation locations
    common_paths = [
        "/usr/local/bin/moses",
        "/usr/bin/moses",
        os.path.expanduser("~/mosesdecoder/bin/moses"),
        os.path.expanduser("~/moses/bin/moses"),
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path, True

    # Check PATH
    moses_binary = shutil.which("moses")
    if moses_binary:
        return moses_binary, True

    return None, False


def get_model_directory() -> Optional[str]:
    """
    Get Moses model directory from environment or common locations.

    Returns:
        Path to model directory or None
    """
    # Check environment variable
    model_dir = os.environ.get("MOSES_MODEL")
    if model_dir and os.path.exists(model_dir):
        moses_ini = os.path.join(model_dir, "moses.ini")
        if os.path.exists(moses_ini):
            return model_dir

    # Check common locations
    common_dirs = [
        os.path.expanduser("~/moses-models/en-fr"),
        os.path.expanduser("~/moses/models/en-fr"),
        "./moses-model",
        "./model",
    ]

    for model_dir in common_dirs:
        if os.path.exists(model_dir):
            moses_ini = os.path.join(model_dir, "moses.ini")
            if os.path.exists(moses_ini):
                return model_dir

    return None


def create_moses_translator() -> Tuple[Optional[MosesTranslator], str]:
    """
    Create Moses translator with auto-detection.

    Returns:
        Tuple of (translator or None, status_message)
    """
    moses_path, moses_available = detect_moses_installation()

    if not moses_available:
        return None, "Moses decoder not found. Using toy SMT fallback."

    model_dir = get_model_directory()

    if not model_dir:
        return None, f"Moses found at {moses_path}, but no model directory configured. Using toy SMT fallback."

    try:
        translator = MosesTranslator(moses_path, model_dir)
        if translator.is_available:
            return translator, f"Moses configured successfully (model: {model_dir})"
        else:
            return None, "Moses configuration failed. Using toy SMT fallback."
    except Exception as e:
        return None, f"Moses initialization error: {str(e)}. Using toy SMT fallback."


if __name__ == "__main__":
    # Test Moses detection and configuration
    print("Moses Detection Test")
    print("=" * 50)

    moses_path, available = detect_moses_installation()
    print(f"Moses available: {available}")
    if available:
        print(f"Moses path: {moses_path}")

    model_dir = get_model_directory()
    print(f"Model directory: {model_dir if model_dir else 'Not found'}")

    print("\n" + "=" * 50)
    translator, message = create_moses_translator()
    print(message)

    if translator:
        print("\nTesting translation...")
        try:
            translation = translator.translate("hello world")
            print(f"Translation: {translation}")
        except Exception as e:
            print(f"Translation failed: {e}")
    else:
        print("\nMoses not available. Configuration instructions:")
        print(MosesTranslator(None, None).get_configuration_instructions())
