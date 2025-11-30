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

---

## ⚠️ Common Error: Python Architecture Mismatch

### Error Message
```
Need python for x86_64, but found x86
Python dependency not found
```

### Root Cause
You have **32-bit Python** but **64-bit compiler** (or vice versa). They must match.

### Solution: Install 64-bit Python

1. **Check current Python:**
   ```powershell
   python -c "import struct; print(struct.calcsize('P') * 8, 'bit')"
   # If it shows "32 bit", you need 64-bit Python
   ```

2. **Download 64-bit Python:**
   - Go to: https://www.python.org/downloads/
   - Download **"Windows installer (64-bit)"** for Python 3.11 or 3.12
   - **IMPORTANT:** Choose the 64-bit version, NOT 32-bit

3. **During installation:**
   - ✅ Check "Add Python to PATH"
   - Choose "Customize installation"
   - ✅ Check "Install for all users" (optional)
   - Click Install

4. **Verify 64-bit installation:**
   ```powershell
   # Close and reopen terminal
   python -c "import struct; print(struct.calcsize('P') * 8, 'bit')"
   # Should show "64 bit"
   ```

5. **Now install pandas:**
   ```bash
   pip install pandas
   # OR use compatible version:
   pip install -r requirements_compatible.txt
   ```

### Alternative: Use 32-bit Compiler (Not Recommended)
If you must keep 32-bit Python, uninstall 64-bit Build Tools and install 32-bit version (much less common, not recommended).

---

## 🚨 32-bit Python 3.12 - No Pre-built Pandas Wheels

**Problem:** Pandas stopped providing 32-bit wheels for Python 3.12+

**Solutions:**

### Option 1: Downgrade to Python 3.11 (32-bit) - RECOMMENDED
```bash
# Download Python 3.11 32-bit from:
https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe

# After installation:
pip install pandas==2.1.4
pip install requests beautifulsoup4 lxml mysql-connector-python
```

### Option 2: Upgrade to Python 3.12 (64-bit) - BEST LONG-TERM
```bash
# Download 64-bit Python 3.12:
https://www.python.org/downloads/

# Install and then:
pip install -r requirements_compatible.txt
```

### Option 3: Use Conda (Works with 32-bit)
```bash
# Download Miniconda 32-bit:
https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe

# Install and then:
conda create -n commodities python=3.11
conda activate commodities
conda install pandas requests beautifulsoup4 lxml
pip install mysql-connector-python
```

### Why This Happens
- Pandas 2.x stopped building 32-bit wheels for Python 3.12+
- Your pip tries to build from source → hits architecture mismatch
- **You need either:** Python 3.11 (32-bit) OR Python 3.12 (64-bit)
