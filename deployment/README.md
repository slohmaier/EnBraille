# EnBraille App Store Deployment

This directory contains all the necessary files and scripts for deploying EnBraille to the macOS App Store.

## Files Overview

### Configuration Files
- **`macos/Info.plist`** - Complete app bundle configuration with App Store requirements
- **`macos/EnBraille.entitlements`** - Sandboxing and security entitlements for App Store
- **`macos/build_app.py`** - Python script to build the macOS app bundle using py2app
- **`macos/sign_and_package.sh`** - Shell script to sign and package for App Store submission

## Bundle Identifier
✅ **com.slohmaier.enbraille** - Configured throughout all deployment files

## Prerequisites

### 1. Apple Developer Account
- Active Apple Developer Program membership ($99/year)
- App Store Connect access

### 2. Certificates (from Apple Developer Portal)
- **3rd Party Mac Developer Application** - For code signing the app
- **3rd Party Mac Developer Installer** - For signing the installer package

### 3. Development Tools
- Xcode (for codesign and other tools)
- Python 3.8+ with required dependencies
- py2app package (`pip install py2app`)

## Build Process

### Step 1: Build the App Bundle
```bash
cd /path/to/EnBraille
python deployment/macos/build_app.py
```

This will:
- Create a universal binary (Intel + Apple Silicon)
- Bundle all dependencies (PySide6, liblouis, etc.)
- Include assets and resources
- Generate `dist/EnBraille.app`

### Step 2: Sign and Package for App Store
```bash
deployment/macos/sign_and_package.sh
```

This will:
- Sign the app bundle with App Store certificates
- Verify the code signature
- Create an installer package for App Store submission
- Generate `dist/EnBraille_AppStore.pkg`

### Step 3: Upload to App Store Connect

**Option A: Using Transporter**
1. Download Transporter from the Mac App Store
2. Open the generated `.pkg` file in Transporter
3. Click "Deliver" to upload

**Option B: Using Command Line**
```bash
xcrun altool --upload-app --type osx --file "dist/EnBraille_AppStore.pkg" \
  --username "your_apple_id@example.com" \
  --password "app-specific-password"
```

## App Store Configuration

### App Information
- **Bundle ID**: com.slohmaier.enbraille
- **Category**: Utilities
- **Minimum macOS**: 10.14 (Mojave)
- **Architecture**: Universal (Intel + Apple Silicon)

### Key Features Highlighted
- ✅ **Accessibility**: Full VoiceOver and screen reader support
- ✅ **Sandboxed**: Secure app sandbox with minimal permissions
- ✅ **Document Types**: Supports BRF, EPUB, Markdown, and plain text
- ✅ **Privacy Compliant**: No data collection, local processing only
- ✅ **Universal Binary**: Optimized for all Mac hardware

### Permissions Required
- **File Access**: User-selected files for conversion
- **Network**: Access to website and GitHub (for About dialog links)

### App Store Listing Suggestions

**Title**: EnBraille - Braille Conversion

**Subtitle**: Convert text and documents to braille format

**Description**:
```
EnBraille is a powerful, accessible tool for converting text and documents into braille format. Perfect for educators, students, and accessibility professionals.

KEY FEATURES:
• Convert plain text to braille (BRF format)
• Process EPUB and Markdown documents
• Reformat existing braille files
• Support for multiple braille tables and languages
• Grade 1 and Grade 2 braille translation
• Fully accessible interface with VoiceOver support
• Clean, intuitive design

SUPPORTED FORMATS:
• Input: Plain text, EPUB, Markdown, existing BRF files
• Output: Braille Ready Format (BRF)
• Multiple braille translation tables

ACCESSIBILITY FIRST:
EnBraille is designed with accessibility in mind, featuring complete screen reader support, keyboard navigation, and clear visual design that works in both light and dark modes.

Perfect for creating accessible educational materials, personal documents, or professional braille publications.
```

**Keywords**: braille, accessibility, text conversion, education, screen reader, BRF, EPUB, markdown

**Screenshots Needed**:
1. Main welcome screen
2. Text conversion interface
3. Document processing view
4. Settings/preferences
5. About dialog (showing accessibility features)

## Testing Before Submission

### Local Testing
1. Test the built app on multiple macOS versions (10.14+)
2. Verify all features work in sandboxed environment
3. Test accessibility with VoiceOver enabled
4. Test file open/save dialogs work properly
5. Verify network access (website links) work

### App Store Requirements Checklist
- ✅ Uses only approved APIs
- ✅ Properly sandboxed
- ✅ No private framework usage
- ✅ Accessibility compliant
- ✅ Privacy policy compliance (no data collection)
- ✅ Human interface guidelines compliance
- ✅ Signed with valid certificates

## Troubleshooting

### Common Issues
1. **Certificate problems**: Ensure certificates are properly installed from Developer Portal
2. **Entitlements errors**: Verify entitlements match your app's actual needs
3. **Bundle ID mismatch**: Ensure bundle ID matches your App Store Connect app
4. **Rejection for API usage**: EnBraille uses only standard Qt/PySide6 APIs

### Support Resources
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [macOS App Store Submission](https://developer.apple.com/macos/submit/)
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)

## Version Updates

For future updates:
1. Update version numbers in `Info.plist`
2. Update `setup.py` version
3. Rebuild, sign, and resubmit following the same process
4. Update App Store Connect with new version information