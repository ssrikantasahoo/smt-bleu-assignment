# Screenshot Documentation Checklist

**Purpose**: This document provides a detailed plan for capturing screenshots demonstrating all features of the SMT+BLEU evaluation system.

---

## Screenshot Requirements

### Minimum Required: 8 screenshots
### Recommended: 12-15 screenshots for complete coverage

---

## 📸 Screenshot Plan

### Screenshot 1: Application Home Page
**Filename**: `01_homepage.png`

**What to Show**:
- Application title and header
- Initial interface layout
- Sidebar with configuration options
- Main input area
- Source text input (empty or with placeholder)
- Reference selection method options

**UI State**:
- Fresh application load
- No translations yet
- All options visible

**Purpose**: Show overall application layout and initial state

---

### Screenshot 2: Sample Reference Selection
**Filename**: `02_sample_selection.png`

**What to Show**:
- "Select from samples" option selected
- Dropdown showing all 8 built-in samples
- Selected sample highlighted
- Sample details displayed (source, description)
- Reference translations shown

**UI State**:
- Sample #1 or #3 selected
- Source text auto-populated
- Reference translations displayed below

**Purpose**: Demonstrate built-in sample functionality

---

### Screenshot 3: Translation Systems Status
**Filename**: `03_systems_status.png`

**What to Show**:
- Sidebar "Translation Systems Status" section
- All three systems listed:
  - Moses SMT (likely unavailable with message)
  - Toy SMT (available, green checkmark)
  - Baseline (available, green checkmark)
- Status messages for each system

**UI State**:
- Typical installation without Moses
- Toy SMT and Baseline available
- Clear status indicators

**Purpose**: Show system availability and fallback behavior

---

### Screenshot 4: BLEU Configuration
**Filename**: `04_bleu_config.png`

**What to Show**:
- Sidebar "BLEU Configuration" section
- Maximum N-gram Order slider (set to 4)
- "Use Custom Weights" checkbox
- If checked, show individual n-gram weight inputs

**UI State**:
- Default configuration (max_n=4)
- Custom weights disabled (or enabled to show feature)

**Purpose**: Demonstrate BLEU customization options

---

### Screenshot 5: Translation Results Overview
**Filename**: `05_translation_results.png`

**What to Show**:
- After clicking "Translate and Evaluate"
- All candidate translations displayed:
  - Toy SMT output
  - Baseline word-by-word output
  - (Optionally) Custom candidate
- Each translation clearly labeled
- Ready to scroll to detailed results

**UI State**:
- Source: "the cat is on the mat"
- Reference: "le chat est sur le tapis"
- Translations displayed
- Before detailed BLEU analysis section

**Purpose**: Show all translation outputs side-by-side

---

### Screenshot 6: BLEU Score Comparison Chart
**Filename**: `06_bleu_comparison.png`

**What to Show**:
- Bar chart comparing BLEU scores across candidates
- Y-axis: BLEU score (0-1)
- X-axis: Translation systems
- Best candidate highlighted in green
- Exact BLEU scores shown on bars

**UI State**:
- Comparison chart fully rendered
- Clear visual distinction of best system
- Interactive Plotly chart

**Purpose**: Demonstrate visual comparison functionality

---

### Screenshot 7: Detailed BLEU Analysis - Best Candidate
**Filename**: `07_bleu_details_best.png`

**What to Show**:
- Detailed BLEU section for best candidate
- Title with "🏆 BEST" indicator
- Four metric cards: BLEU Score, Brevity Penalty, Candidate Length, Reference Length
- N-gram Precision Details table with:
  - N-gram order (1-4)
  - Numerator
  - Denominator
  - Precision (decimal)
  - Precision (percentage)
- All values clearly visible

**UI State**:
- Best candidate (e.g., Toy SMT)
- Green highlight box
- All metrics displayed

**Purpose**: Show detailed BLEU statistics presentation

---

### Screenshot 8: N-gram Precision Breakdown Chart
**Filename**: `08_precision_breakdown.png`

**What to Show**:
- Bar chart showing precision for 1-gram, 2-gram, 3-gram, 4-gram
- Y-axis: Precision (0-1)
- X-axis: N-gram order
- Precision values labeled on bars
- Typical pattern: decreasing precision as n increases

**UI State**:
- Precision breakdown chart for one candidate
- Clear visualization of precision degradation

**Purpose**: Demonstrate n-gram precision visualization

---

### Screenshot 9: Additional Statistics (Expanded)
**Filename**: `09_additional_stats.png`

**What to Show**:
- "📊 Additional Statistics" expander opened
- Geometric mean value
- Weights for each n-gram
- Length ratio
- All formatted clearly

**UI State**:
- Expander section expanded
- All statistics visible
- Clean formatting

**Purpose**: Show expandable additional information

---

### Screenshot 10: Multiple Candidates Comparison
**Filename**: `10_multiple_candidates.png`

**What to Show**:
- At least 3 candidates with different BLEU scores
- Side-by-side detailed analysis
- Clear visual differentiation
- Best candidate highlighted
- Differences in n-gram precisions visible

**UI State**:
- Source: "hello world" or more complex sentence
- Reference provided
- Toy SMT: high BLEU
- Baseline: medium BLEU
- Custom: low BLEU

**Purpose**: Demonstrate multi-candidate evaluation capability

---

### Screenshot 11: Custom Candidate Entry
**Filename**: `11_custom_candidate.png`

**What to Show**:
- "Custom Candidate (Optional)" section
- Text input field with user-entered translation
- Custom candidate included in results
- BLEU score computed for custom entry

**UI State**:
- User has entered a custom translation
- "bonjour monde" for "hello world"
- Custom candidate evaluated alongside others

**Purpose**: Show user-provided candidate evaluation

---

### Screenshot 12: Summary Section
**Filename**: `12_summary.png`

**What to Show**:
- "🎯 Summary" box at bottom
- Best System name
- Best BLEU Score
- Total Candidates Evaluated
- Success message styling

**UI State**:
- All evaluations complete
- Summary clearly displayed
- Professional formatting

**Purpose**: Show final summary presentation

---

## 🎯 Optional Bonus Screenshots

### Screenshot 13: File Upload
**Filename**: `13_file_upload.png`

**What to Show**:
- Reference input method: "Upload file" selected
- File uploader widget
- Sample .txt file uploaded
- References loaded and displayed

**Purpose**: Demonstrate file upload functionality

---

### Screenshot 14: Manual Reference Entry
**Filename**: `14_manual_entry.png`

**What to Show**:
- Reference input method: "Enter manually" selected
- Number of references selector
- Multiple text input fields
- References entered by user

**Purpose**: Show manual entry option

---

### Screenshot 15: About/Information Section
**Filename**: `15_about_section.png`

**What to Show**:
- "ℹ️ About" section
- Expanders for:
  - About BLEU Score
  - About Translation Systems
  - References
- One expander opened showing information

**Purpose**: Demonstrate educational/help content

---

## 📝 Screenshot Capture Instructions

### Setup
1. Start application: `streamlit run app.py`
2. Wait for full load
3. Use browser window at consistent size (1920x1080 recommended)
4. Clear browser cache for clean UI

### Capture Method
**Option 1: Full Page (Recommended)**
- Use browser screenshot tools
- Capture entire visible area
- Maintain aspect ratio

**Option 2: Selective Crop**
- Focus on specific UI section
- Include context (titles, labels)
- Maintain readability

### Quality Requirements
- **Resolution**: Minimum 1200px width
- **Format**: PNG (lossless)
- **Text**: Must be readable when zoomed
- **Colors**: Maintain UI color scheme
- **No Artifacts**: Clear, crisp screenshots

### Annotation (Optional)
- Red boxes around key features
- Arrows pointing to important elements
- Brief labels for clarity
- Use image editor (Photoshop, GIMP, etc.)

---

## 🎬 Screenshot Sequence Workflow

### Recommended Capture Sequence

1. **Start Fresh**
   ```bash
   streamlit run app.py
   ```

2. **Screenshot 1** (Homepage)
   - Capture initial state
   - No interaction yet

3. **Screenshot 3** (Systems Status)
   - Focus on sidebar
   - Show status messages

4. **Screenshot 4** (BLEU Config)
   - Show configuration options
   - Set n=4 (default)

5. **Screenshot 2** (Sample Selection)
   - Select Sample #1: "the cat is on the mat"
   - Show references loaded

6. **Screenshot 5** (Translate - Click button)
   - Click "🚀 Translate and Evaluate"
   - Wait for results
   - Capture translation outputs

7. **Screenshot 6** (Comparison Chart)
   - Scroll to comparison section
   - Capture bar chart

8. **Screenshot 7** (Best Candidate Details)
   - Scroll to best candidate section
   - Capture with green highlight

9. **Screenshot 8** (Precision Chart)
   - Capture n-gram breakdown for one candidate

10. **Screenshot 9** (Additional Stats)
    - Click to expand "Additional Statistics"
    - Capture expanded view

11. **Screenshot 12** (Summary)
    - Scroll to bottom
    - Capture summary box

12. **Screenshot 11** (Custom Candidate) - New Session
    - Refresh page
    - Enter custom translation
    - Evaluate
    - Capture results

13. **Screenshot 10** (Multiple Candidates)
    - Use sentence with varied quality
    - Capture all three candidates side-by-side

14. **Screenshots 13-15** (Optional)
    - Demonstrate remaining features

---

## ✅ Verification Checklist

Before submitting screenshots, verify:

- [ ] All screenshots are PNG format
- [ ] Filenames match the plan (01_homepage.png, etc.)
- [ ] Text is readable in all screenshots
- [ ] No personal information visible
- [ ] UI elements are complete (no cut-off buttons)
- [ ] Color scheme is consistent
- [ ] All key features are demonstrated
- [ ] Screenshots are organized in logical order
- [ ] Minimum 8 screenshots captured
- [ ] Screenshot descriptions written for each

---

## 📦 Delivery Format

### Directory Structure
```
screenshots/
├── 01_homepage.png
├── 02_sample_selection.png
├── 03_systems_status.png
├── 04_bleu_config.png
├── 05_translation_results.png
├── 06_bleu_comparison.png
├── 07_bleu_details_best.png
├── 08_precision_breakdown.png
├── 09_additional_stats.png
├── 10_multiple_candidates.png
├── 11_custom_candidate.png
├── 12_summary.png
├── (optional) 13_file_upload.png
├── (optional) 14_manual_entry.png
├── (optional) 15_about_section.png
└── README.md (this file with descriptions)
```

### README.md for screenshots/
```markdown
# Screenshot Documentation

This directory contains screenshots demonstrating all features of the SMT+BLEU evaluation system.

## Screenshot Descriptions

1. **01_homepage.png**: Application home page and initial layout
2. **02_sample_selection.png**: Built-in sample reference selection
3. **03_systems_status.png**: Translation systems availability status
... (continue for all screenshots)

## Usage
These screenshots demonstrate the complete workflow from input to BLEU evaluation results.
```

---

## 🎓 Educational Use

Screenshots should demonstrate:

1. **Ease of Use**: Intuitive interface
2. **Completeness**: All features covered
3. **Professional Quality**: Clean, polished UI
4. **Functionality**: Working translation and evaluation
5. **Transparency**: Detailed BLEU statistics visible

---

**Status**: Screenshot plan complete, ready for capture
**Last Updated**: January 2026
**Total Screenshots**: 12-15 (8 minimum required)
