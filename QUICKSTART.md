# Quick Start Guide

**Get your SMT+BLEU system running in 5 minutes!**

---

## 🚀 Fastest Path to Running Application

### Step 1: Navigate to Directory
```bash
cd ~/smt-bleu-assignment
```

### Step 2: Install Dependencies
```bash
pip install streamlit pandas plotly
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

### Step 3: Run Application
```bash
streamlit run app.py
```

### Step 4: Open Browser
- Automatically opens at: `http://localhost:8501`
- Or manually navigate to the URL shown in terminal

### Step 5: Try It Out!
1. Click "Select from samples" → Choose Sample 1
2. Click "🚀 Translate and Evaluate"
3. Explore results!

---

## ✅ Verify Installation

### Run Tests (Optional but Recommended)
```bash
python tests/test_bleu.py
```

**Expected Output**:
```
Ran 19 tests in 0.001s
OK
```

### Test Individual Modules (Optional)
```bash
# Test BLEU implementation
python bleu.py

# Test Toy SMT
python smt_toy.py

# Test Baseline Translator
python baseline_translator.py
```

---

## 🎯 Quick Demo Workflow

### Example 1: Simple Translation
1. **Source**: "hello world"
2. **Reference**: Select Sample #2 (built-in)
3. **Translate**: Click button
4. **Result**: See BLEU scores for all systems

### Example 2: Custom Translation
1. **Source**: "the cat is on the mat"
2. **Reference**: Enter "le chat est sur le tapis"
3. **Custom Candidate**: Enter "chat sur tapis"
4. **Translate**: Click button
5. **Result**: Compare your translation to systems

---

## 📊 What You'll See

### Translation Results
- **Toy SMT**: Phrase-based translation
- **Baseline**: Word-by-word translation
- **Best Highlighted**: Green background

### BLEU Analysis
- **Score**: 0-1 (higher is better)
- **N-gram Precision**: 1-4 gram breakdown
- **Brevity Penalty**: Length penalty
- **Charts**: Visual comparison

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution**:
```bash
pip install streamlit pandas plotly
```

### Issue: "FileNotFoundError: data/phrase_table.json"
**Solution**: Generate data files
```bash
python smt_toy.py
python baseline_translator.py
```

### Issue: Port 8501 already in use
**Solution**: Use different port
```bash
streamlit run app.py --server.port 8502
```

### Issue: Moses not found
**Answer**: This is normal! Toy SMT will be used automatically.
Moses is optional. See README.md for installation if desired.

---

## 📚 Next Steps

1. **Explore UI**: Try different samples and input methods
2. **Read Documentation**: See `README.md` for details
3. **Capture Screenshots**: Follow `docs/screenshots_checklist.md`
4. **Generate PDFs**: Convert markdown docs to PDF
5. **Review Code**: Understand BLEU implementation in `bleu.py`

---

## 📖 Full Documentation

- **Setup**: `README.md` (comprehensive)
- **Technical Report**: `docs/Report.md`
- **Task B**: `docs/TaskB.md`
- **Literature Review**: `docs/LiteratureReview.md`
- **Submission Checklist**: `SUBMISSION_CHECKLIST.md`

---

## 💡 Tips

- **Multiple References**: Use the manual entry method to add 2-5 references
- **Custom Weights**: Enable in sidebar to experiment with n-gram weights
- **Moses**: Optional advanced feature, toy SMT works great without it
- **Screenshots**: Capture as you explore for assignment submission

---

## ✅ You're Ready!

The application should now be running and fully functional. Enjoy exploring SMT and BLEU evaluation!

**Need help?** Check `README.md` → Troubleshooting section

---

**Happy Translating! 🌐**
