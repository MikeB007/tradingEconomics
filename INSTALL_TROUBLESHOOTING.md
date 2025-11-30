# Installation Troubleshooting Guide

## Issue: Pandas Installation Fails on Server

### Error Message
```
Preparing metadata (pyproject.toml) ... error
exit code: 1
ERROR: None of values ['c11'] are supported by the C compiler
```

### Root Cause
Server has old C compiler (VS 15.9.17 / Visual Studio 2017) that doesn't support C11 standard required by pandas 2.3.3.

---

## 🚀 FASTEST SOLUTION (No Compiler Upgrade)

### Use Compatible Requirements File
```bash
pip install -r requirements_compatible.txt
```

This installs pandas 2.0.3 which works with older compilers.

---

## 💻 How to Upgrade Compiler (For Latest Pandas)

### Option 1: Install Visual Studio 2022 Build Tools (Recommended)

**Step 1: Download**
- URL: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
- Click "Download Build Tools for Visual Studio 2022"

**Step 2: Install**
1. Run the downloaded installer (`vs_BuildTools.exe`)
2. In the Workloads tab, select **"Desktop development with C++"**
3. In the Installation details panel (right side), ensure these are checked:
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools (Latest)
   - ✅ Windows 11 SDK (or Windows 10 SDK)
   - ✅ C++ CMake tools for Windows
   - ✅ Testing tools core features - Build Tools
4. Click **"Install"** (requires ~6-8 GB disk space)
5. Wait for installation to complete (10-20 minutes)

**Step 3: Verify Installation**
```powershell
# Open NEW PowerShell/CMD window (important!)
where cl

# Should show path like:
# C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.xx.xxxxx\bin\Hostx64\x64\cl.exe
```

**Step 4: Install Pandas**
```bash
pip install pandas
```

### Option 2: Install Visual Studio 2022 Community (Full IDE)

1. Download: https://visualstudio.microsoft.com/vs/community/
2. Run installer
3. Select **"Desktop development with C++"** workload
4. Click Install
5. Restart and try: `pip install pandas`

### Option 3: Update Existing Visual Studio

1. Open **"Visual Studio Installer"** (search in Start menu)
2. Find your installed version
3. Click **"Modify"**
4. Select **"Desktop development with C++"**
5. Click **"Modify"** to install
6. Restart terminal and try: `pip install pandas`

---

## 🐍 Alternative: Use Conda (No Compiler Needed)
```bash
# Install Miniconda from https://docs.conda.io/en/latest/miniconda.html
conda create -n commodities python=3.11
conda activate commodities
conda install pandas beautifulsoup4 requests lxml mysql-connector-python
```

#### Solution 6: Install Dependencies One by One
```bash
pip install --upgrade pip setuptools wheel
pip install numpy
pip install pandas
pip install requests
pip install beautifulsoup4
pip install lxml
pip install mysql-connector-python
```

### Recommended Installation Order

1. **Update pip and tools**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install from requirements with binary preference**
   ```bash
   pip install -r requirements.txt --prefer-binary --no-cache-dir
   ```

3. **Verify installation**
   ```bash
   python -c "import pandas; print(pandas.__version__)"
   python -c "import mysql.connector; print('MySQL connector OK')"
   ```

### Check Python Version
Ensure Python 3.8+ is installed:
```bash
python --version
```

If using older Python (< 3.8), upgrade to Python 3.10 or 3.11.
