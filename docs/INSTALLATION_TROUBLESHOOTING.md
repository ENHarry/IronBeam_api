# Installation Troubleshooting Guide

## Issue: `pip install -e .` Fails with Distutils Error

### Problem Description
When attempting to install the IronBeam SDK in editable mode (`pip install -e .`), you may encounter this error:

```
AssertionError: C:\Program Files\Python\Python311\Lib\distutils\core.py
```

This is a known issue with setuptools and Python 3.11+ on Windows when there are conflicts between the system Python's distutils and the virtual environment's setuptools.

### ✅ Solution: Use Pre-built Wheel

The package has been successfully built and validated. You can install it using the pre-built wheel:

```powershell
# Install from the pre-built wheel (recommended)
pip install dist/ironbeam_sdk-0.1.0-py3-none-any.whl
```

### ✅ Alternative Solutions

#### 1. Force Reinstall from Wheel
```powershell
pip install --force-reinstall dist/ironbeam_sdk-0.1.0-py3-none-any.whl
```

#### 2. Install from Source Archive
```powershell
pip install dist/ironbeam_sdk-0.1.0.tar.gz
```

#### 3. Development Workflow (Alternative to Editable Install)
For development purposes, you can:

1. Install the package normally:
   ```powershell
   pip install dist/ironbeam_sdk-0.1.0-py3-none-any.whl
   ```

2. After making changes to the source code, rebuild and reinstall:
   ```powershell
   # Clean old builds
   Remove-Item -Recurse -Force dist, build, ironbeam_sdk.egg-info -ErrorAction SilentlyContinue
   
   # Rebuild
   python -m build
   
   # Reinstall
   pip install --force-reinstall dist/ironbeam_sdk-0.1.0-py3-none-any.whl
   ```

### ✅ Verification

After installation, verify that everything works correctly:

```powershell
python validate_installation.py
```

You should see:
```
🎉 ALL TESTS PASSED!
✅ IronBeam SDK is properly installed and functional
```

### 🔧 Root Cause

The issue is caused by:
1. Python 3.11+ changes to distutils
2. setuptools trying to override distutils
3. Build isolation creating conflicts between system and virtual environment packages

This is a common issue across many Python packages and doesn't indicate a problem with the IronBeam SDK itself.

### 📞 Support

If you continue to have installation issues:
1. Try the wheel installation method above
2. Ensure you're using Python 3.7+ but consider Python 3.10 if 3.11 continues to cause issues
3. Create a fresh virtual environment if problems persist

The package has been thoroughly tested and validated - the installation method doesn't affect functionality.