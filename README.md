# 🧬 Target ID Analyzer: Easy Step-by-Step Guide

Welcome! This tool helps you compare lists of names (like "Target IDs" or Protein names) across many different Excel files. It automatically finds which items are shared between files and creates beautiful, interactive charts to help you see patterns.

---

## 📋 What can I do with this?
- **Compare 60+ files at once**: No more manual copying and pasting.
- **Find "blocks" of files**: See which files share the exact same proteins.
- **Filter results**: Only show IDs that appear in at least X number of files.
- **Save for presentations**: Download your charts as professional PDF or PNG files.

---

## 🛠️ Step 1: Prerequisites
Before you start, make sure you have **Python** installed on your computer. 
- You can download it from [python.org](https://www.python.org/downloads/).
- During installation, make sure to check the box that says **"Add Python to PATH"**.

---

## 🚀 Step 2: Get the Code
1. Open your **Terminal** (on Mac, press `Cmd + Space` and type "Terminal") or **Command Prompt** (on Windows).
2. Type this command and press Enter to download the tool:
   ```bash
   git clone https://github.com/vivekn19/data_plotter.git
   ```
3. Go into the folder:
   ```bash
   cd data_plotter
   ```

---

## 📦 Step 3: Install the "Brains"
This tool needs a few libraries (like Pandas and Streamlit) to work. Run this command in your terminal:
```bash
pip install -r requirements.txt
```
*Note: Depending on your computer, you might need to type `pip3` instead of `pip`.*

---

## 📂 Step 4: Add Your Data
1. Inside the `data_plotter` folder, you will see a folder named `data`.
2. Copy your Excel (`.xlsx`) or CSV (`.csv`) files into this `data` folder.
3. **Important**: Make sure each file has a column header (the top row) that contains your IDs. By default, the tool looks for a column named **"Target ID"**.

---

## 🏁 Step 5: Start the App
Run this command to launch the interface:
```bash
python3 -m streamlit run app.py
```
This will automatically open a new tab in your web browser!

---

## 🖱️ How to use the interface

### 1. Load your Data
In the sidebar on the left, click the **"Load Data"** button. The tool will scan your `data` folder. Once finished, it will say "Processed X files."

### 2. Adjust the Slider
If you have too many Target IDs, the charts might look crowded. Use the **"Minimum Occurrence Threshold"** slider in the sidebar. 
- Setting it to **5** means: "Only show me IDs that appear in 5 or more different files."

### 3. Explore the Charts
- **🔥 Clustered Heatmap**: This groups files that are similar to each other. Darker colors mean the ID is present.
- **📊 UpSet Plot**: This is a powerful way to see how multiple files overlap. It shows the "intersections" of your sets.
- **📄 Raw Data**: View the spreadsheet of which IDs are in which files and download it as a CSV.

### 4. Downloading
Scroll to the bottom of any chart to find the **Download (PDF)** and **Download (PNG)** buttons. These will save the exact view you are looking at right now.

---

## ❓ FAQ & Troubleshooting

**Q: My files use a different column name (like "Protein Name")?**
A: In the sidebar, simply type "Protein Name" into the box labeled **"Target ID Column Name"** and click "Load Data" again.

**Q: The app says "ModuleNotFoundError"?**
A: This means Step 3 didn't finish correctly. Try running `pip install streamlit pandas seaborn openpyxl upsetplot scipy` manually.

**Q: Can I use this for other data?**
A: Yes! As long as you have files with a common column of identifiers, this tool will find the overlaps and cluster them for you.
