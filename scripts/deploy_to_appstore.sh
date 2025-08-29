#!/bin/bash
# Complete workflow for deploying EnBraille to the App Store

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 EnBraille App Store Deployment Workflow${NC}"
echo "==========================================="
echo

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check if we're on macOS
if [[ $(uname) != "Darwin" ]]; then
    echo -e "${RED}❌ This script must be run on macOS${NC}"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required${NC}"
    exit 1
fi

# Check for required certificates
APP_CERT=$(security find-identity -v -p codesigning | grep "3rd Party Mac Developer Application" | head -1 | cut -d '"' -f 2)
if [ -z "$APP_CERT" ]; then
    echo -e "${YELLOW}⚠️  App Store certificates not found${NC}"
    echo "   You'll need to install them before running the signing step"
else
    echo -e "${GREEN}✅ App Store certificates available${NC}"
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"
echo

# Step 2: Install build dependencies
echo -e "${BLUE}Step 2: Installing build dependencies...${NC}"

pip3 install -r deployment/requirements-build.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install build dependencies${NC}"
    exit 1
fi
echo

# Step 3: Build the app bundle
echo -e "${BLUE}Step 3: Building app bundle...${NC}"

python3 deployment/macos/build_app.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ App bundle built successfully${NC}"
else
    echo -e "${RED}❌ App bundle build failed${NC}"
    exit 1
fi
echo

# Step 4: Validate the bundle
echo -e "${BLUE}Step 4: Validating app bundle...${NC}"

python3 deployment/macos/validate_bundle.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bundle validation passed${NC}"
else
    echo -e "${RED}❌ Bundle validation failed${NC}"
    echo "Please fix validation issues before proceeding"
    exit 1
fi
echo

# Step 5: Sign and package (if certificates are available)
if [ ! -z "$APP_CERT" ]; then
    echo -e "${BLUE}Step 5: Signing and packaging for App Store...${NC}"
    
    deployment/macos/sign_and_package.sh
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ App signed and packaged successfully${NC}"
        echo -e "${GREEN}📦 Ready for App Store submission!${NC}"
        echo
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. Test the installer package: dist/EnBraille_AppStore.pkg"
        echo "2. Upload using Transporter or xcrun altool"
        echo "3. Submit for review in App Store Connect"
        echo
        echo -e "${BLUE}Upload command example:${NC}"
        echo 'xcrun altool --upload-app --type osx --file "dist/EnBraille_AppStore.pkg" --username "YOUR_APPLE_ID" --password "APP_SPECIFIC_PASSWORD"'
    else
        echo -e "${RED}❌ Signing and packaging failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Step 5: Skipped signing (certificates not available)${NC}"
    echo
    echo -e "${YELLOW}Manual signing required:${NC}"
    echo "1. Install App Store certificates from Apple Developer portal"
    echo "2. Run: deployment/macos/sign_and_package.sh"
fi

echo
echo -e "${GREEN}🎉 Deployment workflow completed!${NC}"

# Show final file locations
echo
echo -e "${BLUE}Generated files:${NC}"
if [ -d "dist/EnBraille.app" ]; then
    echo -e "${GREEN}📦 App bundle: dist/EnBraille.app${NC}"
fi

if [ -f "dist/EnBraille_AppStore.pkg" ]; then
    echo -e "${GREEN}📦 App Store package: dist/EnBraille_AppStore.pkg${NC}"
    
    # Show package size
    PKG_SIZE=$(ls -lh "dist/EnBraille_AppStore.pkg" | awk '{print $5}')
    echo -e "${BLUE}📏 Package size: ${PKG_SIZE}${NC}"
fi

echo
echo -e "${BLUE}Bundle identifier: com.slohmaier.enbraille${NC}"
echo -e "${BLUE}Ready for App Store submission! 🚀${NC}"