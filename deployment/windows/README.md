# EnBraille Windows Deployment

This directory contains Windows-specific deployment configuration and documentation for EnBraille's multi-platform deployment system.

## Overview

EnBraille supports three Windows deployment methods:
1. **Portable ZIP** - Standalone executable distribution
2. **MSI Installer** - Windows Package Manager (winget) distribution  
3. **MSIX Package** - Microsoft Store distribution

## Quick Start

```bash
# Build all Windows packages
python scripts/deploy_windows.py --all

# Build specific package type
python scripts/deploy_windows.py --portable
python scripts/deploy_windows.py --msi  
python scripts/deploy_windows.py --msix

# Clean and rebuild everything
python scripts/deploy_windows.py --all --clean --test
```

## Prerequisites

### Required Tools
- **Python 3.8+** with EnBraille dependencies installed
- **PyInstaller** - `pip install pyinstaller`
- **cx_Freeze** - `pip install cx_freeze` (for MSI)
- **Inkscape** - For icon generation from SVG

### Platform-Specific Tools

#### For MSI Installer (winget)
- **WiX Toolset v3** - https://wixtoolset.org/releases/
  - Provides `candle.exe` and `light.exe` for MSI creation

#### For MSIX Package (Microsoft Store)
- **Windows 10 SDK** - https://developer.microsoft.com/windows/downloads/windows-10-sdk/
  - Provides `makeappx.exe` and `signtool.exe`

## Package Details

### 1. Portable Distribution

**Script**: `scripts/build_portable_windows.py`

Creates a self-contained executable with all dependencies bundled:
- **Output**: `dist/EnBraille_Portable_v{version}.zip`
- **Size**: ~50-80 MB
- **Requirements**: None (runs on any Windows 10+)
- **Use Cases**: 
  - Direct distribution
  - USB/removable media
  - Enterprise deployment
  - Air-gapped systems

### 2. MSI Installer (winget)

**Script**: `scripts/build_msi_installer.py`

Creates a Windows Installer package for winget distribution:
- **Output**: `dist/EnBraille_v{version}.msi`
- **Manifest**: `dist/EnBraille_winget_manifest.yaml`
- **Features**:
  - Standard Windows installation
  - Add/Remove Programs entry
  - Desktop shortcuts
  - File associations (.brf, .txt, .epub, .md)
  - Automatic updates via winget

**winget Submission Process**:
1. Upload MSI to GitHub releases
2. Update InstallerUrl in manifest
3. Submit PR to [microsoft/winget-pkgs](https://github.com/Microsoft/winget-pkgs)
4. Wait for validation and merge

### 3. MSIX Package (Microsoft Store)

**Script**: `scripts/build_msix_package.py`

Creates a modern Windows package for Microsoft Store:
- **Output**: `dist/EnBraille_v{version}.msix`
- **Assets**: `dist/EnBraille_Store_Assets/`
- **Features**:
  - Modern Windows 10+ packaging
  - Automatic updates via Store
  - Sandboxed security model
  - Multiple tile sizes
  - File associations

**Microsoft Store Submission Process**:
1. Create Microsoft Partner Center account
2. Sign MSIX with trusted certificate
3. Upload MSIX and store assets
4. Fill store listing information
5. Submit for certification (7-14 days)

## File Structure

```
deployment/windows/
├── README.md                    # This file
scripts/
├── deploy_windows.py           # Master deployment script
├── build_portable_windows.py  # Portable ZIP builder
├── build_msi_installer.py     # MSI installer builder
└── build_msix_package.py      # MSIX package builder

dist/                          # Generated packages
├── EnBraille_Portable_v{version}.zip
├── EnBraille_v{version}.msi
├── EnBraille_v{version}.msix
├── EnBraille_winget_manifest.yaml
├── EnBraille_Store_Assets/
└── DEPLOYMENT_SUMMARY.md
```

## Testing Packages

### Test Portable ZIP
```bash
# Extract and run
unzip dist/EnBraille_Portable_v*.zip
cd EnBraille_Portable
./EnBraille.exe
```

### Test MSI Installer
```bash
# Install silently
msiexec /i "dist/EnBraille_v*.msi" /quiet

# Test installation
EnBraille.exe

# Uninstall
msiexec /x "dist/EnBraille_v*.msi" /quiet
```

### Test MSIX Package
```powershell
# Install (requires Developer Mode or trusted certificate)
Add-AppxPackage -Path "dist/EnBraille_v*.msix"

# Test app
# (Look for EnBraille in Start Menu)

# Uninstall
Remove-AppxPackage -Package "slohmaier.EnBraille_*"
```

## Troubleshooting

### Common Issues

**PyInstaller "module not found" errors**:
- Add missing modules to `--hidden-import` parameters
- Check that all dependencies are installed in current environment

**WiX toolset not found**:
- Download from https://wixtoolset.org/releases/
- Ensure `candle.exe` and `light.exe` are in PATH

**makeappx.exe not found**:
- Install Windows 10 SDK
- Add SDK bin directory to PATH
- Typical location: `C:\Program Files (x86)\Windows Kits\10\bin\{version}\x64\`

**Icon generation fails**:
- Install Inkscape from https://inkscape.org/
- Ensure `inkscape` command is available in PATH

### Debugging

Enable verbose output:
```bash
# See detailed build output
python scripts/deploy_windows.py --all --clean 2>&1 | tee build.log
```

Check generated files:
```bash
# Verify package contents
7z l dist/EnBraille_Portable_v*.zip
msiexec /a dist/EnBraille_v*.msi /qb TARGETDIR=temp_extract
```

## Version Updates

When releasing a new version:

1. **Update version everywhere**:
   ```bash
   python deployment/update_version.py 1.0.1
   ```

2. **Build all packages**:
   ```bash
   python scripts/deploy_windows.py --all --clean --test
   ```

3. **Commit and tag**:
   ```bash
   git commit -am "Update version to 1.0.1"
   git tag v1.0.1
   git push origin v1.0.1
   ```

4. **Upload to GitHub releases**:
   - Upload all files from `dist/`
   - Use `DEPLOYMENT_SUMMARY.md` for release notes

5. **Update package repositories**:
   - Submit winget manifest PR
   - Update Microsoft Store listing

## Distribution Channels

### Direct Distribution
- GitHub releases (all packages)
- Website downloads
- Enterprise deployment

### Package Managers
- **winget**: `winget install slohmaier.EnBraille`
- **Microsoft Store**: Search "EnBraille"
- **Chocolatey**: (future consideration)

### Enterprise
- MSIX for modern deployment
- MSI for traditional deployment
- Portable for specialized environments

## Security Considerations

### Code Signing
- **Recommended** for MSI and MSIX packages
- **Required** for Microsoft Store submission
- Use EV (Extended Validation) certificate for best compatibility
- Sign with timestamping for longevity

### Certificates
```bash
# Sign MSI
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/EnBraille_v*.msi

# Sign MSIX  
signtool sign /f certificate.pfx /p password /fd SHA256 dist/EnBraille_v*.msix
```

## Support Resources

- **winget**: https://docs.microsoft.com/windows/package-manager/
- **Microsoft Store**: https://docs.microsoft.com/windows/uwp/publish/
- **MSIX**: https://docs.microsoft.com/windows/msix/
- **WiX Toolset**: https://wixtoolset.org/documentation/
- **PyInstaller**: https://pyinstaller.readthedocs.io/