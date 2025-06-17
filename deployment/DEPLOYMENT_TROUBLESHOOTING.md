# 🔧 Deployment Troubleshooting Guide

## Issue: Requirements Installation Error

### Problem
Streamlit Cloud shows "Error installing requirements" with dependency conflicts.

### Root Cause
The original `requirements.txt` contained 130+ packages with version conflicts and unnecessary dependencies.

### Solution Applied ✅

1. **Simplified Requirements**: Reduced from 130+ packages to only 4 essential ones
2. **Version Compatibility**: Used broader version ranges instead of exact pins
3. **Removed Conflicts**: Eliminated packages causing dependency hell

### New Clean Requirements
```
streamlit>=1.28.0
pandas>=2.0.0  
numpy>=1.24.0
plotly>=5.15.0
```

## Deployment Steps (Updated)

### Option 1: Streamlit Community Cloud (Recommended)

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub
3. **Click "New app"**
4. **Repository**: `aimed-lab/mondrian-map`
5. **Branch**: `main`
6. **Main file path**: `app.py`
7. **Advanced settings** (if needed):
   - Python version: 3.9
   - Requirements file: `requirements.txt` (default)
8. **Deploy**

### Option 2: Alternative - Use Minimal Requirements

If still having issues, try these steps:

1. **In Streamlit Cloud dashboard**:
   - Go to "Manage app"
   - Click "Reboot app"
   - Or try "Delete app" and redeploy

2. **Check the logs**:
   - Click "Manage app" → View logs
   - Look for specific error messages

## Common Issues & Fixes

### Issue: "Package not found"
**Fix**: Ensure all packages in requirements.txt are available on PyPI

### Issue: "Memory limit exceeded"  
**Fix**: The minimal requirements should resolve this

### Issue: "Build timeout"
**Fix**: Simplified requirements should build much faster

### Issue: "Import errors"
**Fix**: All imports in app.py should work with the 4 core packages

## Files Created for Deployment

- ✅ `requirements.txt` - Minimal, clean dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `requirements_original_backup.txt` - Backup of original
- ✅ `requirements_streamlit_cloud.txt` - Alternative version

## Verification Steps

After deployment:

1. **Check app loads**: Should show the Mondrian Map interface
2. **Test dataset selection**: Try different datasets
3. **Test canvas grid**: Should show multiple maps
4. **Test interactivity**: Click on tiles, toggle options

## Alternative Deployment (If Streamlit Cloud Fails)

### Railway (Backup Option)
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy automatically
4. Uses the same clean requirements.txt

### Render (Backup Option)
1. Go to [render.com](https://render.com)  
2. Create new Web Service
3. Connect GitHub repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

## Success Indicators

✅ **Build completes** without errors  
✅ **App starts** and shows interface  
✅ **Data loads** correctly  
✅ **Visualizations render** properly  
✅ **Interactive features** work  

## Need Help?

If you're still having issues:

1. **Check the specific error** in deployment logs
2. **Try the alternative platforms** (Railway, Render)
3. **Use the backup requirements** files if needed
4. **Verify all data files** are in the repository

The simplified approach should resolve the dependency conflicts you were experiencing! 