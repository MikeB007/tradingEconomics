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

#### Solution 3: Install Build Tools (if needed)
If building from source is required, install Microsoft C++ Build Tools:
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++"

#### Solution 4: Use Conda Instead of Pip
```bash
# Install Miniconda from https://docs.conda.io/en/latest/miniconda.html
conda create -n commodities python=3.11
conda activate commodities
conda install pandas beautifulsoup4 requests lxml mysql-connector-python
```

#### Solution 5: Install Dependencies One by One
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
