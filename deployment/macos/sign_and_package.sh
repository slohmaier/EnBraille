#!/bin/bash
# Sign and package EnBraille for App Store distribution

set -e  # Exit on any error

# Configuration
APP_NAME="EnBraille"
APP_BUNDLE="dist/${APP_NAME}.app"
ENTITLEMENTS="deployment/macos/${APP_NAME}.entitlements"
INSTALLER_PACKAGE="dist/${APP_NAME}_AppStore.pkg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== EnBraille App Store Signing & Packaging ==="
echo

# Check if Developer ID certificates are available
echo "🔍 Checking for certificates..."

# App Store certificates
APP_CERT=$(security find-identity -v -p codesigning | grep "3rd Party Mac Developer Application" | head -1 | cut -d '"' -f 2)
INSTALLER_CERT=$(security find-identity -v -p codesigning | grep "3rd Party Mac Developer Installer" | head -1 | cut -d '"' -f 2)

if [ -z "$APP_CERT" ]; then
    echo -e "${RED}❌ 3rd Party Mac Developer Application certificate not found${NC}"
    echo "Please install App Store certificates from Apple Developer portal"
    echo
    echo "Available certificates:"
    security find-identity -v -p codesigning
    exit 1
else
    echo -e "${GREEN}✅ App certificate: $APP_CERT${NC}"
fi

if [ -z "$INSTALLER_CERT" ]; then
    echo -e "${RED}❌ 3rd Party Mac Developer Installer certificate not found${NC}"
    echo "Please install App Store certificates from Apple Developer portal"
    exit 1
else
    echo -e "${GREEN}✅ Installer certificate: $INSTALLER_CERT${NC}"
fi

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo -e "${RED}❌ App bundle not found: $APP_BUNDLE${NC}"
    echo "Please run build_app.py first to create the app bundle"
    exit 1
fi

echo -e "${GREEN}✅ App bundle found: $APP_BUNDLE${NC}"

# Check entitlements file
if [ ! -f "$ENTITLEMENTS" ]; then
    echo -e "${RED}❌ Entitlements file not found: $ENTITLEMENTS${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Entitlements file found: $ENTITLEMENTS${NC}"
echo

# Step 1: Sign the app bundle
echo "🔑 Signing app bundle..."
codesign --force --deep --sign "$APP_CERT" --entitlements "$ENTITLEMENTS" --options runtime "$APP_BUNDLE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ App bundle signed successfully${NC}"
else
    echo -e "${RED}❌ Failed to sign app bundle${NC}"
    exit 1
fi

# Step 2: Verify the signature
echo "🔍 Verifying signature..."
codesign --verify --verbose=4 "$APP_BUNDLE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Signature verified${NC}"
else
    echo -e "${RED}❌ Signature verification failed${NC}"
    exit 1
fi

# Step 3: Create installer package for App Store
echo "📦 Creating installer package..."
productbuild --component "$APP_BUNDLE" /Applications --sign "$INSTALLER_CERT" "$INSTALLER_PACKAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Installer package created: $INSTALLER_PACKAGE${NC}"
else
    echo -e "${RED}❌ Failed to create installer package${NC}"
    exit 1
fi

# Step 4: Verify installer package
echo "🔍 Verifying installer package..."
pkgutil --check-signature "$INSTALLER_PACKAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Installer package signature verified${NC}"
else
    echo -e "${RED}❌ Installer package signature verification failed${NC}"
    exit 1
fi

echo
echo "🎉 App Store package ready!"
echo -e "${GREEN}📦 Package: $INSTALLER_PACKAGE${NC}"
echo
echo "Next steps:"
echo "1. Test the installer package on a clean system"
echo "2. Upload to App Store Connect using Transporter or Xcode"
echo "3. Submit for App Store review"
echo
echo "Upload command:"
echo -e "${YELLOW}xcrun altool --upload-app --type osx --file \"$INSTALLER_PACKAGE\" --username \"YOUR_APPLE_ID\" --password \"APP_SPECIFIC_PASSWORD\"${NC}"
echo
echo "Or use Transporter app from the Mac App Store"