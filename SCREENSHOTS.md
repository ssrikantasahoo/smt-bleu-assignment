# Screenshot Checklist for SMT-BLEU Assignment

This document specifies exactly which screenshots to capture for the assignment submission. Each screenshot should clearly demonstrate a specific feature or functionality.

---

## Screenshot Requirements

**Total Required:** Minimum 8 screenshots  
**Format:** PNG or JPG  
**Resolution:** Minimum 1280x720  
**Naming Convention:** `screenshot_##_description.png`

---

## Screenshot List

### Screenshot 1: Application Homepage with Built-in Example

**Filename:** `screenshot_01_homepage_builtin_example.png`

**What to show:**
- Streamlit app loaded and running
- Source text input area with example: "Hello, how are you?"
- Reference selection mode set to "Built-in Examples"
- Selected reference showing English source and Hindi translation(s)
- System status sidebar showing which systems are available (Moses/Toy SMT/Word-by-Word)

**How to capture:**
1. Run: `streamlit run app/streamlit_app.py`
2. Select "Built-in Examples" in Reference Mode
3. Choose "Ref ref_01: Hello, how are you?"
4. Ensure all three panels visible
5. Take screenshot of entire browser window

---

### Screenshot 2: Translation Results with Comparison Table

**Filename:** `screenshot_02_translation_comparison_table.png`

**What to show:**
- Results after clicking "Translate & Evaluate"
- Comparison table showing all three systems (Moses/Toy SMT/Word-by-Word)
- BLEU scores for each system (BLEU, BLEU-1, BLEU-2, BLEU-3, BLEU-4)
- Brevity Penalty (BP) values
- Candidate lengths
- Highlighted row for best-performing system (green background)

**How to capture:**
1. Enter source text: "I love programming."
2. Select built-in reference: "Ref ref_02: I love programming."
3. Click "Translate & Evaluate"
4. Scroll to "System Comparison" table
5. Ensure table is fully visible
6. Take screenshot

---

### Screenshot 3: BLEU Score Visualization Chart

**Filename:** `screenshot_03_bleu_score_chart.png`

**What to show:**
- Bar chart visualization comparing BLEU scores across systems
- X-axis: Translation systems (Moses, Toy SMT, Word-by-Word, Custom)
- Y-axis: BLEU Score (0.0 to 1.0)
- Chart title: "BLEU Score Comparison"
- Different colored bars for each system

**How to capture:**
1. Same page as Screenshot 2
2. Scroll to "BLEU Score Comparison" chart
3. Ensure full chart visible with legend
4. Take screenshot

---

### Screenshot 4: Detailed N-gram Precision Table (System 1)

**Filename:** `screenshot_04_ngram_precision_table.png`

**What to show:**
- Expanded detailed view for one system (e.g., "Toy SMT - Detailed Analysis")
- Translation output clearly visible
- Metrics displayed: BLEU Score, Brevity Penalty, Candidate Length (c), Reference Length (r)
- N-gram Precision Details table showing:
  - N-gram column (1-gram, 2-gram, 3-gram, 4-gram)
  - Clipped Count (numerator)
  - Total Count (denominator)
  - Precision values
- All four rows visible

**How to capture:**
1. Click on expander: "🔍 Toy SMT - Detailed Analysis"
2. Scroll to "N-gram Precision Details" table
3. Ensure all 4 rows (1-gram to 4-gram) visible
4. Take screenshot showing table and metrics above it

---

### Screenshot 5: Individual BLEU-n Scores Bar Chart

**Filename:** `screenshot_05_individual_bleu_scores.png`

**What to show:**
- Bar chart within expanded system details
- X-axis: BLEU-1, BLEU-2, BLEU-3, BLEU-4
- Y-axis: Score values
- Different colored bars for each metric
- Chart title: "[System Name] - Individual BLEU Scores"

**How to capture:**
1. Within same expanded section as Screenshot 4
2. Scroll to individual BLEU scores chart
3. Ensure full chart visible
4. Take screenshot

---

### Screenshot 6: Multiple References Support

**Filename:** `screenshot_06_multiple_references.png`

**What to show:**
- Reference mode set to "Manual Input"
- Number of References selector set to 2 or 3
- Multiple reference text input boxes filled with different Hindi translations
- Example:
  - Reference 1: "नमस्ते, आप कैसे हैं?"
  - Reference 2: "हैलो, आप कैसे हैं?"
  - Reference 3: "नमस्कार, आप कैसे हैं?"

**How to capture:**
1. Select "Manual Input" for Reference Mode
2. Set "Number of References" to 3
3. Fill in three different reference translations
4. Take screenshot showing all three input boxes
5. Don't click evaluate yet (just show the input)

---

### Screenshot 7: Custom Translation Input and Evaluation

**Filename:** `screenshot_07_custom_translation.png`

**What to show:**
- "Add Custom Translation" section
- Custom translation input box filled with user-provided translation
- Results table showing 4 systems: Moses, Toy SMT, Word-by-Word, AND Custom
- Custom translation's BLEU score displayed
- Comparison showing how custom performs vs. automatic systems

**How to capture:**
1. After evaluating with built-in systems
2. Enter custom translation in "Custom Translation (optional)" field
3. Results should update to include Custom in comparison
4. Take screenshot showing custom input and updated comparison table

---

### Screenshot 8: File Upload for References

**Filename:** `screenshot_08_reference_upload.png`

**What to show:**
- Reference mode set to "Upload File"
- File uploader widget showing ".txt" file selected or uploaded
- Success message: "Loaded X reference(s)"
- List of loaded references displayed below
- Each reference numbered and shown

**How to capture:**
1. Select "Upload File" for Reference Mode
2. Create a sample .txt file with 2-3 Hindi references (one per line)
3. Upload the file using the file uploader
4. Take screenshot showing:
   - File uploader widget
   - Success message
   - List of loaded references

---

## Bonus Screenshots (Optional - for extra credit)

### Screenshot 9: Moses Configuration Status

**Filename:** `screenshot_09_moses_status.png`

**What to show:**
- Sidebar "System Status" section
- Moses status indicator (Available ✅ or Not configured ⚠️)
- Toy SMT: Available ✅
- Word-by-Word: Available ✅

---

### Screenshot 10: Tokenization Details

**Filename:** `screenshot_10_tokenization_details.png`

**What to show:**
- Tokenization section in expanded system details
- "Candidate tokens:" list
- "Reference 1 tokens:" list
- Showing both English and Hindi tokenization

---

### Screenshot 11: Edge Case - Zero BLEU Score

**Filename:** `screenshot_11_zero_bleu_score.png`

**What to show:**
- Source text with no matches to reference
- Example: Source: "xyz abc def", Reference: "hello world"
- BLEU Score: 0.0000
- All n-gram precisions showing 0.0000
- Demonstrating proper handling of no-match case

---

### Screenshot 12: Unit Test Results

**Filename:** `screenshot_12_unit_test_results.png`

**What to show:**
- Terminal/command prompt showing `pytest tests/ -v` output
- All tests passing with green checkmarks
- Test summary: "X passed in Y seconds"
- List of individual test functions that passed

**How to capture:**
1. Open terminal
2. Run: `pytest tests/test_bleu.py -v`
3. Wait for completion
4. Take screenshot of terminal output
5. Ensure all test names and results visible

---

## Screenshot Submission Checklist

Before submission, verify:

- [ ] All 8 required screenshots captured
- [ ] Screenshots are clear and readable (minimum 1280x720)
- [ ] File names follow naming convention
- [ ] Screenshots show different features (no duplicates)
- [ ] UI elements are fully visible (not cut off)
- [ ] Text is legible (zoom in if needed for small text)
- [ ] Screenshots are saved in PNG or JPG format
- [ ] Create a `screenshots/` folder with all images
- [ ] Optional: Create a `screenshots/README.md` with descriptions

---

## Tips for Good Screenshots

1. **Use full-screen browser** for Streamlit app screenshots
2. **Zoom appropriately** (Ctrl/Cmd + +/-) so text is readable
3. **Hide browser bookmarks bar** for cleaner screenshots
4. **Close unnecessary tabs** to reduce clutter
5. **Use consistent browser** (same browser for all screenshots)
6. **Capture on high-resolution display** if possible
7. **Include browser window frame** to show it's a web app
8. **Take screenshots in light mode** (better for printing/viewing)

---

## Screenshot Annotation (Optional)

For clarity, you can add annotations to screenshots:

1. **Red boxes** around key features
2. **Arrows** pointing to important elements
3. **Text labels** explaining what's shown
4. **Numbered callouts** for multi-part screenshots

**Tools for annotation:**
- macOS: Preview (markup tools)
- Windows: Snip & Sketch
- Linux: GIMP, Krita
- Online: Photopea, Canva

---

## Verification

After capturing all screenshots, run this check:

```bash
# Verify all screenshots exist
ls -1 screenshot_*.png

# Should show:
# screenshot_01_homepage_builtin_example.png
# screenshot_02_translation_comparison_table.png
# screenshot_03_bleu_score_chart.png
# screenshot_04_ngram_precision_table.png
# screenshot_05_individual_bleu_scores.png
# screenshot_06_multiple_references.png
# screenshot_07_custom_translation.png
# screenshot_08_reference_upload.png
```

---

**Prepared by:** SMT-BLEU Assignment Team  
**Last Updated:** January 2026  
**Minimum Screenshots Required:** 8  
**Recommended Screenshots:** 12
