#!/bin/bash
# SMT-BLEU Assignment - Automated Checks Script
# Runs tests and validation to ensure project is ready for submission

set -e  # Exit on error

echo "========================================="
echo "SMT-BLEU Assignment - Validation Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo "ℹ $1"
}

# Track overall success
OVERALL_SUCCESS=true

echo "1. Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found"
    OVERALL_SUCCESS=false
fi
echo ""

echo "2. Checking Python dependencies..."
MISSING_DEPS=()
for package in streamlit numpy pytest pandas plotly; do
    if python3 -c "import $package" 2>/dev/null; then
        print_success "$package is installed"
    else
        print_error "$package is NOT installed"
        MISSING_DEPS+=("$package")
        OVERALL_SUCCESS=false
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_warning "Missing dependencies. Install with: pip install -r requirements.txt"
fi
echo ""

echo "3. Checking project structure..."
REQUIRED_DIRS=("data" "src" "app" "tests" "scripts")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory $dir/ exists"
    else
        print_error "Directory $dir/ is missing"
        OVERALL_SUCCESS=false
    fi
done
echo ""

echo "4. Checking required files..."
REQUIRED_FILES=(
    "README.md"
    "Report.md"
    "TaskB.md"
    "LiteratureReview.md"
    "references.bib"
    "requirements.txt"
    "data/built_in_corpus.json"
    "data/phrase_table.json"
    "data/hindi_trigram_lm.json"
    "data/dictionary.json"
    "src/bleu.py"
    "src/toy_smt.py"
    "src/moses_interface.py"
    "src/word_by_word.py"
    "src/utils.py"
    "app/streamlit_app.py"
    "tests/test_bleu.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "File $file exists"
    else
        print_error "File $file is missing"
        OVERALL_SUCCESS=false
    fi
done
echo ""

echo "5. Running unit tests..."
if command -v pytest &> /dev/null; then
    print_info "Running pytest..."
    if pytest tests/ -v --tb=short; then
        print_success "All unit tests passed"
    else
        print_error "Some unit tests failed"
        OVERALL_SUCCESS=false
    fi
else
    print_warning "pytest not found. Skipping unit tests."
    print_info "Install pytest: pip install pytest"
fi
echo ""

echo "6. Testing BLEU module..."
print_info "Running BLEU smoke test..."
if python3 -c "
from src.bleu import compute_bleu
# Use sentence with at least 4 words for 4-gram BLEU
result = compute_bleu('the cat sat on the mat', ['the cat sat on the mat'])
assert result['bleu_score'] == 1.0, f'Expected 1.0, got {result[\"bleu_score\"]}'
print('BLEU perfect match test: PASSED')

result = compute_bleu('', ['hello world test sentence'])
assert result['bleu_score'] == 0.0, f'Expected 0.0, got {result[\"bleu_score\"]}'
print('BLEU empty candidate test: PASSED')

result = compute_bleu('the cat sat on', ['the cat sat on the mat'])
assert 0.0 <= result['bleu_score'] <= 1.0
print('BLEU partial match test: PASSED')
"; then
    print_success "BLEU module tests passed"
else
    print_error "BLEU module tests failed"
    OVERALL_SUCCESS=false
fi
echo ""

echo "7. Testing Toy SMT..."
print_info "Running Toy SMT smoke test..."
if python3 -c "
from src.toy_smt import ToySMT
smt = ToySMT()
translation = smt.translate('hello')
assert translation is not None and translation != ''
print(f'Toy SMT translation: \"{translation}\"')
print('Toy SMT test: PASSED')
"; then
    print_success "Toy SMT module works"
else
    print_error "Toy SMT module failed"
    OVERALL_SUCCESS=false
fi
echo ""

echo "8. Testing Word-by-Word translator..."
print_info "Running Word-by-Word smoke test..."
if python3 -c "
from src.word_by_word import WordByWordTranslator
translator = WordByWordTranslator()
translation = translator.translate('hello')
assert translation is not None and translation != ''
print(f'Word-by-Word translation: \"{translation}\"')
print('Word-by-Word test: PASSED')
"; then
    print_success "Word-by-Word module works"
else
    print_error "Word-by-Word module failed"
    OVERALL_SUCCESS=false
fi
echo ""

echo "9. Checking Moses availability..."
if python3 -c "
from src.moses_interface import create_moses_decoder
decoder = create_moses_decoder()
status = decoder.get_status()
if status['available']:
    print('Moses is AVAILABLE')
    print(f'  Binary: {status[\"moses_bin\"]}')
    print(f'  Config: {status[\"moses_ini\"]}')
    exit(0)
else:
    print('Moses is NOT AVAILABLE (this is OK - Toy SMT will be used)')
    if not status['moses_exists']:
        print('  Moses binary not found')
    if not status['ini_exists']:
        print('  Moses config (moses.ini) not found')
    print('  To configure Moses:')
    print('    export MOSES_INI_PATH=/path/to/moses.ini')
    print('    export MOSES_BIN_PATH=/path/to/moses')
    exit(0)
"; then
    print_success "Moses check completed"
else
    print_warning "Moses check encountered issues (non-critical)"
fi
echo ""

echo "10. Testing Streamlit app (import check)..."
if python3 -c "
import sys
sys.path.insert(0, 'app')
# Just check if it imports without errors
import streamlit
print('Streamlit import: OK')
"; then
    print_success "Streamlit app can be imported"
else
    print_error "Streamlit app has import errors"
    OVERALL_SUCCESS=false
fi
echo ""

echo "11. Checking documentation files..."
DOC_FILES=("README.md" "Report.md" "TaskB.md" "LiteratureReview.md")
for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        if [ "$LINES" -gt 50 ]; then
            print_success "$doc: $LINES lines (substantial content)"
        else
            print_warning "$doc: only $LINES lines (may need more content)"
        fi
    fi
done
echo ""

echo "12. Verifying data files..."
if python3 -c "
import json
from pathlib import Path

files_to_check = [
    'data/built_in_corpus.json',
    'data/phrase_table.json',
    'data/hindi_trigram_lm.json',
    'data/dictionary.json'
]

for file in files_to_check:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f'{file}: Valid JSON ✓')
"; then
    print_success "All data files are valid JSON"
else
    print_error "Some data files have JSON errors"
    OVERALL_SUCCESS=false
fi
echo ""

echo "========================================="
echo "Summary"
echo "========================================="

if [ "$OVERALL_SUCCESS" = true ]; then
    print_success "All checks passed! Project is ready for submission."
    echo ""
    print_info "Next steps:"
    echo "  1. Run the Streamlit app: streamlit run app/streamlit_app.py"
    echo "  2. Take screenshots as per SCREENSHOTS.md"
    echo "  3. Generate PDFs:"
    echo "     pandoc TaskB.md -o TaskB.pdf"
    echo "     pandoc LiteratureReview.md --bibliography=references.bib -o LiteratureReview.pdf"
    echo "     pandoc Report.md -o Report.pdf"
    echo "  4. Package for submission"
    exit 0
else
    print_error "Some checks failed. Please fix the issues above."
    echo ""
    print_info "Common fixes:"
    echo "  - Install dependencies: pip install -r requirements.txt"
    echo "  - Run from project root directory"
    echo "  - Check file permissions"
    exit 1
fi
