# **AceChecker-sigil**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/jun-hyung-joon/EpubChecker-sigil)
[![Sigil](https://img.shields.io/badge/Sigil-1.0%2B-blue)](https://sigil-ebook.com/)

A Sigil plugin that validates EPUB files using Ace by DAISY, providing detailed accessibility reports and warnings directly within the Sigil editor. The plugin automatically detects and uses the installed version of Ace by DAISY, checks for updates, and ensures you're always aware of the latest accessibility standards.

## **Installation**

### **1. Install Ace by DAISY**

**Option A: Package Manager (Recommended)**

```bash
# Install Node.js first (if not already installed)
# Windows (Chocolatey)
choco install nodejs

# macOS (Homebrew)
brew install node

# Linux (varies by distribution)
sudo apt install nodejs npm  # Ubuntu/Debian

# Then install Ace by DAISY globally
npm install -g @daisy/ace
```

**Option B: Manual Installation**
1. Install Node.js from [nodejs.org](https://nodejs.org/)
2. Open terminal/command prompt
3. Run: `npm install -g @daisy/ace`

### **2. Install the Sigil Plugin**
1. Download the latest `AceChecker.zip` from releases
2. In Sigil, go to **Plugins** → **Manage Plugins**
3. Click **Add Plugin** and select the downloaded file

## **Usage**
1. Open your EPUB project in Sigil
2. Go to **Plugins** → **AceChecker**
3. The plugin will:
   * Check for Ace by DAISY installation
   * Check for available updates
   * Generate a temporary EPUB file
   * Run accessibility validation using Ace by DAISY.
   * Display detailed accessibility results

**Note**: The plugin will notify you when newer versions of Ace by DAISY are available and provide update instructions.

## **Sample Output**

```
🔍 Ace by DAISY accessibility check started
============================================================
🔧 Checking Ace by DAISY installation...
✅ Ace by DAISY found: 1.3.7
🔧 Checking for Ace by DAISY updates...
✅ You have the latest version of Ace by DAISY
📖 Preparing current EPUB file...
📦 EPUB created successfully (size: 1,234,567 bytes)
🔍 Running Ace by DAISY accessibility check...
📄 Ace by DAISY processing completed

📊 Accessibility Check Results
============================================================
Total check items: 15
Passed items: 12 ✅
Failed items: 3 ❌

Check target: My Accessible Book
EPUB version: 3.0
Check time: 2025-08-21T10:30:00.000Z

❌ Accessibility issues found (3 items):
------------------------------------------------------------
1. Images must have alternate text
   Severity: 🔴 serious
   Issue: Element has no alt attribute
   Description: Ensures <img> elements have alternate text
   📁 File: chapter01.xhtml
   📍 Location: img
   💻 HTML: <img src="../Images/cover.jpg">
   📖 Solution: https://dequeuniversity.com/rules/axe/4.4/image-alt
   📋 WCAG standards: wcag2a, wcag111, section508

✅ Files that passed (8 items):
   • chapter01.xhtml
   • chapter02.xhtml
   • toc.xhtml
   • nav.xhtml

📋 Missing accessibility metadata (2 items):
   • schema:accessibilityFeature
   • schema:accessibilitySummary
```

## **Supported Environments**

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 11 | ✅ | Supports npm and manual installation |
| macOS | ✅ | Intel and Apple Silicon, Homebrew support |
| Linux | ✅ | Most distributions with Node.js support |

## **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## **Acknowledgments**
* **[Ace by DAISY](https://github.com/daisy/ace)** - The accessibility checker for EPUB by DAISY Consortium. This plugin is a wrapper that integrates Ace by DAISY into Sigil.
* [Sigil](https://sigil-ebook.com/) - The amazing EPUB editor

## **Dependencies**
This plugin requires and integrates with:
* **[Ace by DAISY](https://github.com/daisy/ace)** - Official EPUB accessibility checker
* **Node.js** - Required to run Ace by DAISY

## **Legal Notice**
This plugin is a third-party integration tool and is not affiliated with or endorsed by the DAISY Consortium or the [Ace by DAISY](https://github.com/daisy/ace) project. Ace by DAISY is developed and maintained by the DAISY Consortium.
