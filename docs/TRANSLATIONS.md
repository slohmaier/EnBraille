# EnBraille Translations

This directory contains translations for the EnBraille application.

## Available Languages

- **English (en)** - Default language
- **German (de)** - Complete translation (Deutsch)

## Using German Translation

### Command Line
To start EnBraille in German:
```bash
python enbraille_main.py --language de
```

### Automatic Detection
The application automatically detects your system language. If your system is set to German, EnBraille will start in German automatically.

## Translation Files

- `enbraille_de.py` - German translations dictionary
- `enbraille_de.ts` - Qt translation source file (for reference)

## German Translation Coverage

The German translation includes **130+ translated strings** covering:

### Main Interface
- ✅ Welcome page and descriptions
- ✅ Main navigation and buttons
- ✅ Menu items and dialogs
- ✅ Settings and about dialogs

### Text Conversion
- ✅ Text input prompts
- ✅ Conversion progress messages
- ✅ Results and copy functionality

### Document Processing
- ✅ File selection dialogs
- ✅ Document conversion options
- ✅ Format settings

### BRF Reformatting
- ✅ File characteristics display
- ✅ Reformat settings and options
- ✅ Progress and completion messages

### Error Messages
- ✅ All error dialogs
- ✅ File operation errors
- ✅ Validation messages

## Key German Translations

| English | German |
|---------|---------|
| Welcome to EnBraille | Willkommen zu EnBraille |
| Text to BRF | Text zu BRF |
| Settings | Einstellungen |
| About | Über |
| Choose file | Datei auswählen |
| Save file | Datei speichern |
| Error | Fehler |
| Done | Fertig |
| Braille table | Braille-Tabelle |
| Document | Dokument |

## Adding New Languages

To add support for a new language:

1. Create `enbraille_[language_code].py` in this directory
2. Copy the structure from `enbraille_de.py`
3. Translate all strings in the `TRANSLATIONS` dictionary
4. Test with: `python enbraille_main.py --language [language_code]`

## Implementation Details

The translation system uses a Python-based approach that:
- Loads translation dictionaries at runtime
- Patches Qt's `tr()` method to use our translations
- Falls back to English for untranslated strings
- Automatically detects system language

This approach avoids the need for Qt's `lrelease` tool and works across all platforms.

## Testing Translations

Run the test scripts:
```bash
# Test translation loading
python test_translations.py

# Demo German interface
python demo_german.py
```

## Quality Assurance

The German translations have been:
- ✅ Reviewed for accuracy and context
- ✅ Tested in the actual GUI
- ✅ Verified for proper encoding (UTF-8)
- ✅ Checked for UI layout compatibility
- ✅ Tested with screen readers for accessibility