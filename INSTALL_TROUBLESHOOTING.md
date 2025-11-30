# Installation Troubleshooting Guide

## Issue: Pandas Installation Fails on Server

### Error Message
```
Preparing metadata (pyproject.toml) ... error
exit code: 1
```

### Solutions

#### Solution 1: Install Pre-built Binary Wheels (Recommended)
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies from requirements.txt
pip install -r requirements.txt --prefer-binary
```

#### Solution 2: Install Specific Pandas Version
```bash
# Try an older, stable version
pip install pandas==2.0.3
```

#### Solution 4: Upgrade C++ Compiler (If you need latest pandas)

**Option A: Install Visual Studio 2019 or 2022 Build Tools**
1. Download Build Tools: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
2. Run the installer
3. Select "Desktop development with C++"
4. Make sure these are checked:
   - MSVC v143 - VS 2022 C++ x64/x86 build tools (or latest)
   - Windows 10/11 SDK
   - C++ CMake tools for Windows
5. Install (requires ~6-8 GB)
6. Restart your terminal/PowerShell
7. Try installing pandas again:
   ```bash
   pip install pandas
   ```

**Option B: Install Visual Studio 2022 Community (Full IDE)**
1. Download: https://visualstudio.microsoft.com/vs/community/
2. During installation, select "Desktop development with C++"
3. Install and restart
4. Try installing pandas

**Option C: Update Existing Visual Studio**
1. Open "Visual Studio Installer" (search in Start menu)
2. Click "Modify" on your installed version
3. Select "Desktop development with C++"
4. Click "Modify" to install

**After Installing Compiler:**
```bash
# Verify compiler is available
where cl

# Try installing pandas again
pip install pandas
```

#### Solution 5: Use Conda Instead of Pip (Easiest - No Compiler Needed)
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
