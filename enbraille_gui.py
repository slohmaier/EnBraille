#
# Copyright (c) 2024 Stefan Lohmaier.
#
# This file is part of EnBraille 
# (see https://github.com/slohmaier/EnBraille).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import logging
from typing import Optional

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (QButtonGroup, QGridLayout, QLabel, QRadioButton,
                               QWidget, QWizard, QWizardPage, QMessageBox, QVBoxLayout,
                               QHBoxLayout, QPushButton, QCheckBox, QTextEdit, QFrame, 
                               QScrollArea)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_functions.reformat import EnBrailleReformatPage, EnBrailleReformaterWorkPage, EnBrailleReformaterResultPage
from enbraille_functions.text import (EnBrailleSimpleResultPage,
                                      EnBrailleSimpleTextPage,
                                      EnBrailleSimpleTextWorkPage)
from enbraille_functions.document import EnBrailleDocumentPage, EnBrailleDocumentPageOutput, EnBrailleDocumentPageWork

class EnBrailleWelcomePage(QWizardPage):
    """Welcome page with app explanation and settings"""
    
    def __init__(self, data: EnBrailleData):
        super().__init__()
        self.data = data
        
        # Set page properties
        self.setTitle(self.tr('Welcome to EnBraille'))
        self.setSubTitle(self.tr('Your comprehensive braille conversion toolkit'))
        
        # Set accessible properties
        self.setAccessibleName("Welcome Page")
        self.setAccessibleDescription("Introduction to EnBraille application with settings and skip option")
        
        # Create main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create app description
        self.createAppDescription()
        
        # Create feature list
        self.createFeatureList()
        
        # Create footer with settings and skip option
        self.createFooter()
    
    def createAppDescription(self):
        """Create the main app description section"""
        # App logo/title section
        titleLabel = QLabel(self.tr('EnBraille'))
        titleFont = QFont()
        titleFont.setPointSize(18)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setAccessibleName(self.tr('EnBraille Application Title'))
        self.layout.addWidget(titleLabel)
        
        # Version info (you may want to make this dynamic)
        versionLabel = QLabel(self.tr('Version 1.0 - Professional Braille Conversion Tool'))
        versionLabel.setAlignment(Qt.AlignCenter)
        versionLabel.setStyleSheet("color: gray; font-style: italic;")
        versionLabel.setAccessibleName(self.tr('Version Information'))
        self.layout.addWidget(versionLabel)
        
        self.layout.addSpacing(20)
        
        # Main description
        descriptionText = self.tr(
            "EnBraille is a powerful, accessible application designed to help you convert "
            "text and documents into braille format (BRF). Whether you're working with "
            "simple text, complex documents, or need to reformat existing braille files, "
            "EnBraille provides the tools you need."
        )
        
        descriptionLabel = QLabel(descriptionText)
        descriptionLabel.setWordWrap(True)
        descriptionLabel.setAccessibleName(self.tr('Application Description'))
        descriptionLabel.setAccessibleDescription(descriptionText)
        self.layout.addWidget(descriptionLabel)
        
        self.layout.addSpacing(10)
        
        # Add website link
        websiteLabel = QLabel()
        websiteLabel.setText('<a href="https://slohmaier.de/enbraille">Visit EnBraille Website: https://slohmaier.de/enbraille</a>')
        websiteLabel.setTextFormat(Qt.RichText)
        websiteLabel.setOpenExternalLinks(True)
        websiteLabel.setAlignment(Qt.AlignCenter)
        websiteLabel.setAccessibleName(self.tr('EnBraille Website Link'))
        websiteLabel.setAccessibleDescription(self.tr('Link to the official EnBraille website for more information and support'))
        websiteLabel.setStyleSheet("QLabel { color: palette(link); }")
        self.layout.addWidget(websiteLabel)
        
        self.layout.addSpacing(15)
    
    def createFeatureList(self):
        """Create the features list as simple rich text"""
        featuresLabel = QLabel(self.tr('Key Features:'))
        featuresFont = QFont()
        featuresFont.setBold(True)
        featuresLabel.setFont(featuresFont)
        featuresLabel.setAccessibleName(self.tr('Key Features Section'))
        self.layout.addWidget(featuresLabel)
        
        # Create scroll area to contain features text without expanding window
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setMaximumHeight(200)  # Prevent window expansion
        scrollArea.setMinimumHeight(150)  # Ensure minimum readable height
        
        # Create simple text display
        featuresText = QLabel()
        featuresText.setWordWrap(True)
        featuresText.setAccessibleName(self.tr('Features List'))
        featuresText.setAccessibleDescription(self.tr('List of EnBraille key features and capabilities'))
        
        # Build features text content as plain text for better accessibility
        features_text = ""
        features = [
            (self.tr('Text Conversion'), self.tr('Convert plain text to braille format using various braille tables and standards')),
            (self.tr('Document Processing'), self.tr('Handle EPUB and Markdown documents with proper formatting and structure preservation')),
            (self.tr('BRF Reformatting'), self.tr('Adjust line length, page breaks, and formatting of existing braille files')),
            (self.tr('Multiple Braille Tables'), self.tr('Support for various languages and braille standards including Grade 1 and Grade 2')),
            (self.tr('Accessible Interface'), self.tr('Full screen reader support, keyboard navigation, and accessibility features')),
            (self.tr('Customizable Settings'), self.tr('Personalize your conversion preferences and save frequently used configurations'))
        ]
        
        for title, description in features:
            features_text += f"• {title}\n  {description}\n\n"
        
        featuresText.setText(features_text.strip())
        featuresText.setTextFormat(Qt.PlainText)  # Use plain text for VoiceOver compatibility
        
        # Put the text label in the scroll area
        scrollArea.setWidget(featuresText)
        scrollArea.setAccessibleName(self.tr('Features Scroll Area'))
        scrollArea.setAccessibleDescription(self.tr('Scrollable text containing EnBraille features'))
        
        self.layout.addWidget(scrollArea)
        self.layout.addSpacing(15)
    
    def createFooter(self):
        """Create footer with settings button and skip option"""
        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)
        
        self.layout.addSpacing(15)
        
        # Main footer layout - horizontal layout with checkbox on left, button on right
        mainFooterLayout = QHBoxLayout()
        
        # Skip welcome page checkbox (left side)
        self.skipCheckbox = QCheckBox(self.tr('Don\'t show this welcome page again'))
        self.skipCheckbox.setAccessibleName(self.tr('Skip Welcome Page'))
        self.skipCheckbox.setAccessibleDescription(self.tr('Check this box to skip the welcome page on future startups'))
        self.skipCheckbox.setChecked(self.data.skipWelcomePage)
        self.skipCheckbox.stateChanged.connect(self.onSkipCheckboxChanged)
        
        # Make checkbox larger and more prominent
        checkboxFont = self.skipCheckbox.font()
        checkboxFont.setPointSize(11)
        self.skipCheckbox.setFont(checkboxFont)
        self.skipCheckbox.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                min-height: 24px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        mainFooterLayout.addWidget(self.skipCheckbox)
        
        # Add stretch to push settings button to the right
        mainFooterLayout.addStretch()
        
        # Settings button (right side)
        self.settingsButton = QPushButton(self.tr('Settings'))
        self.settingsButton.setAccessibleName(self.tr('Settings Button'))
        self.settingsButton.setAccessibleDescription(self.tr('Open application settings to customize preferences'))
        self.settingsButton.clicked.connect(self.openSettings)
        self.settingsButton.setShortcut("Alt+S")
        
        # Make button larger and more prominent
        buttonFont = self.settingsButton.font()
        buttonFont.setPointSize(11)
        self.settingsButton.setFont(buttonFont)
        self.settingsButton.setMinimumHeight(32)
        self.settingsButton.setMinimumWidth(100)
        # Remove custom styling to use default button appearance
        self.settingsButton.setStyleSheet("")
        
        mainFooterLayout.addWidget(self.settingsButton)
        
        # About button (next to settings)
        self.aboutButton = QPushButton(self.tr('About'))
        self.aboutButton.setAccessibleName(self.tr('About Button'))
        self.aboutButton.setAccessibleDescription(self.tr('Show application information, version, and license details'))
        self.aboutButton.clicked.connect(self.openAbout)
        self.aboutButton.setShortcut("Alt+A")
        
        # Match settings button styling
        buttonFont = self.aboutButton.font()
        buttonFont.setPointSize(11)
        self.aboutButton.setFont(buttonFont)
        self.aboutButton.setMinimumHeight(32)
        self.aboutButton.setMinimumWidth(80)
        self.aboutButton.setStyleSheet("")  # Use default button appearance
        
        mainFooterLayout.addWidget(self.aboutButton)
        
        # Add the main footer layout
        self.layout.addLayout(mainFooterLayout)
        
        self.layout.addSpacing(10)
        
        # Add helpful text below
        helpLabel = QLabel(self.tr('You can always access settings and help from the application menu.'))
        helpLabel.setStyleSheet("color: gray; font-size: 10pt; font-style: italic;")
        helpLabel.setAccessibleName(self.tr('Help Information'))
        helpLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(helpLabel)
    
    @Slot()
    def openSettings(self):
        """Open the settings dialog"""
        # For now, show a message box - you can implement a proper settings dialog later
        QMessageBox.information(
            self, 
            self.tr('Settings'),
            self.tr('Settings dialog will be implemented here.\n\n'
                   'Current settings are automatically saved as you use the application.\n\n'
                   'You can modify braille tables, formatting options, and other preferences '
                   'on each conversion page.')
        )
    
    @Slot()
    def openAbout(self):
        """Open the about dialog with license and version information"""
        about_text = self.tr(
            'EnBraille - Braille Conversion Tool\n\n'
            'A comprehensive tool for converting text and documents to braille format.\n\n'
            'Features:\n'
            '• Text to Braille conversion\n'
            '• EPUB and Markdown document processing\n'
            '• BRF reformatting capabilities\n'
            '• Multiple braille table support\n'
            '• Accessible interface design\n\n'
            'Website: https://slohmaier.de/enbraille\n'
            'Source Code: https://github.com/slohmaier/EnBraille\n\n'
            'Copyright © 2024\n'
            'Licensed under open source terms.\n\n'
            'This application uses:\n'
            '• PySide6/Qt for the user interface\n'
            '• Liblouis for braille translation\n'
            '• Python libraries for document processing\n\n'
            'For support and more information, visit the website above.\n'
            'For source code, issues, and contributions, visit the GitHub repository.'
        )
        
        QMessageBox.about(self, self.tr('About EnBraille'), about_text)
    
    @Slot(int)
    def onSkipCheckboxChanged(self, state):
        """Handle skip checkbox state change"""
        self.data.skipWelcomePage = (state == Qt.Checked)
        logging.debug(f'Skip welcome page setting changed to: {self.data.skipWelcomePage}')
    
    def initializePage(self):
        """Set focus to the skip checkbox when page is shown"""
        super().initializePage()
        
        # Focus the skip checkbox as it's the first interactive element in logical tab order
        QTimer.singleShot(50, lambda: self.skipCheckbox.setFocus(Qt.OtherFocusReason))
        logging.debug('Setting focus to skip checkbox on welcome page')
    
    def isComplete(self):
        """Welcome page is always complete"""
        return True
    
    def nextId(self):
        """Return the ID of the next page (function selection page)"""
        return 1  # Function selection page is at index 1
    
    def isFinalPage(self):
        """Welcome page is never the final page"""
        return False

class EnBrailleWindow(QWizard):
    def __init__(self, data: EnBrailleData):
        super().__init__()
        self.data = data

        self.setWindowIcon(QIcon(":/assets/Icon.png"))
        self.setWindowTitle("EnBraille")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Enable keyboard navigation
        self.setOption(QWizard.HaveHelpButton, False)
        self.setOption(QWizard.HaveCustomButton1, False)
        self.setOption(QWizard.HaveCustomButton2, False)
        self.setOption(QWizard.HaveCustomButton3, False)
        
        # Add welcome page
        self.welcomePage = EnBrailleWelcomePage(data)
        self.addPage(self.welcomePage)
        
        self.startPage = EnBrailleWizardPageStart(data)
        self.addPage(self.startPage)

        # add pages for the simple text function
        self.simpleTextPage = EnBrailleSimpleTextPage(data)
        self.simpleTextPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.simpleTextPage)

        self.simpleTextWorkPage = EnBrailleSimpleTextWorkPage(data)
        self.simpleTextWorkPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.simpleTextWorkPage)

        self.simpleTextResultPage = EnBrailleSimpleResultPage(data)
        self.addPage(self.simpleTextResultPage)

        # add pages for the reformat function
        self.reformatPage = EnBrailleReformatPage(data)
        self.reformatPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.reformatPage)

        self.reformatWorkPage = EnBrailleReformaterWorkPage(data)
        self.reformatWorkPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.reformatWorkPage)

        self.reformatResultPage = EnBrailleReformaterResultPage(data)
        self.reformatResultPage.completeChanged.connect(self.updateNextButtonState)   
        self.addPage(self.reformatResultPage)

        # add pages for document function
        self.documentPage = EnBrailleDocumentPage(data)
        self.documentPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.documentPage)

        self.documentWorkPage = EnBrailleDocumentPage(data)
        self.documentWorkPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.documentWorkPage)

        self.documentOutputPage = EnBrailleDocumentPageOutput(data)
        self.documentOutputPage.completeChanged.connect(self.updateNextButtonState)
        self.addPage(self.documentOutputPage)

        # refresh wizard page visibility based on current main function
        data.mainFunctionChanged.connect(self.onMainFunctionChanged)
        self.currentIdChanged.connect(self.onPageChanged)
        
        # Enable better keyboard navigation
        self.setAttribute(Qt.WA_KeyboardFocusChange, True)
        
        # Set accessible properties for the wizard
        self.setAccessibleName("EnBraille Conversion Wizard")
        self.setAccessibleDescription("Step-by-step wizard to convert text, documents, or reformat braille files")
        
        # Add keyboard shortcuts for accessibility
        # Enable help button if needed (commented out as it's not currently used)
        # self.setOption(QWizard.HaveHelpButton, True)
        
    def show(self) -> None:
        # Check if we should skip the welcome page
        if self.data.skipWelcomePage:
            # Start directly on the function selection page
            self.setStartId(1)  # Function selection page is at index 1
            logging.debug('Skipping welcome page based on user preference')
        else:
            # Start with welcome page
            self.setStartId(0)  # Welcome page is at index 0
            logging.debug('Showing welcome page')
        
        res = super().show()
        self.data.mainFunctionChanged.emit(self.data.mainFunction)
        return res
    
    @Slot(int)  
    def onPageChanged(self, newPageId: int):
        for pageId in []:
            page = self.page(pageId)
            logging.debug('EnBrailleWindow: setting visibility for widgets in page ' + str(page.__class__) + ' to ' + str(page.isVisible()))
            for widget in page.findChildren(QWidget):
                widget.setVisible(pageId == newPageId)
        
        # Ensure screen reader focuses the first focusable element on the new page
        self.focusFirstElementOnPage(newPageId)
    
    @Slot(EnBrailleMainFct)
    def onMainFunctionChanged(self, mainFunction: EnBrailleMainFct):
        # Remove all pages except the welcome page (0) and start page (1)
        for pageId in self.pageIds()[2:]:
            self.removePage(pageId)
        
        if mainFunction == EnBrailleMainFct.TEXT:
            self.addPage(self.simpleTextPage)
            self.addPage(self.simpleTextWorkPage)
            self.addPage(self.simpleTextResultPage)
        elif mainFunction == EnBrailleMainFct.REFORMAT:
            self.addPage(self.reformatPage)
            self.addPage(self.reformatWorkPage)
            self.addPage(self.reformatResultPage)
        elif mainFunction == EnBrailleMainFct.DOCUMENT:
            self.addPage(self.documentPage)
            self.addPage(self.documentWorkPage)
            self.addPage(self.documentOutputPage)
        else:
            raise ValueError('Invalid MainFunction: ' + str(mainFunction))

        logging.debug('new main function: ' + str(mainFunction))
        logging.debug('page ids: ' + str(self.pageIds()))
        
        # Update final page status based on whether we have a welcome page
        if not self.data.skipWelcomePage:
            self.startPage.setFinalPage(False)
        else:
            # When welcome page is skipped, start page needs to handle being the first page
            self.startPage.setFinalPage(False)
        
        self.updateNextButtonState()

    def updateNextButtonState(self):
        page = self.currentPage()
        if page:
            self.button(QWizard.NextButton).setEnabled(page.isComplete())
        else:
            self.button(QWizard.NextButton).setEnabled(False)
    
    def focusFirstElementOnPage(self, pageId: int):
        """
        Set focus to the first focusable element on the given page.
        This ensures screen readers announce the page content properly.
        """
        page = self.page(pageId)
        if not page:
            return
            
        # Use a small delay to ensure the page is fully rendered
        QTimer.singleShot(50, lambda: self._setFocusToFirstElement(page))
    
    def _setFocusToFirstElement(self, page: QWizardPage):
        """Helper method to find and focus the first focusable element"""
        # Define priority order for focus (most important elements first)
        priority_widgets = [
            'QRadioButton', 'QLineEdit', 'QTextEdit', 'QComboBox', 
            'QSpinBox', 'QPushButton', 'QCheckBox', 'QListWidget', 
            'QTreeWidget', 'QTableWidget', 'QSlider'
        ]
        
        # First, try to find elements in priority order
        for widget_type in priority_widgets:
            for widget in page.findChildren(QWidget):
                if (widget.__class__.__name__ == widget_type and 
                    widget.isVisible() and 
                    widget.isEnabled() and
                    widget.focusPolicy() != Qt.NoFocus):
                    
                    logging.debug(f'Setting focus to {widget_type}: {widget.objectName() or "unnamed"}')
                    widget.setFocus(Qt.OtherFocusReason)
                    return
        
        # If no priority widget found, focus any focusable widget
        for widget in page.findChildren(QWidget):
            if (widget.isVisible() and 
                widget.isEnabled() and
                widget.focusPolicy() != Qt.NoFocus):
                
                logging.debug(f'Setting focus to fallback widget: {widget.__class__.__name__}')
                widget.setFocus(Qt.OtherFocusReason)
                return
        
        # Last resort: focus the page title or first label
        for widget in page.findChildren(QLabel):
            if widget.isVisible():
                # Make the label focusable temporarily for screen reader announcement
                widget.setFocusPolicy(Qt.StrongFocus)
                widget.setFocus(Qt.OtherFocusReason)
                logging.debug('Setting focus to label for screen reader announcement')
                return
                
        logging.debug('No focusable element found on page')
    
    def next(self):
        """Override next to ensure focus management"""
        result = super().next()
        # Focus will be set by onPageChanged signal
        return result
    
    def back(self):
        """Override back to ensure focus management"""
        result = super().back()
        # Focus will be set by onPageChanged signal
        return result

class EnBrailleWizardPageStart(QWizardPage):
    def __init__(self, data: EnBrailleData):
        super().__init__()

        self.data = data
        self.setTitle(self.tr('What to EnBraille?'))
        self.setSubTitle(self.tr("Please select the function you want to use:"))
        
        # Set accessible properties for the page
        self.setAccessibleName("Function Selection Page")
        self.setAccessibleDescription("Choose between text conversion, document conversion, or BRF reformatting")
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonClicked.connect(self.onButtonClicked)

        row = 0
        for fct in EnBrailleMainFct:
            button, label = self.createRadioButton(fct)

            self.layout.addWidget(button, row, 0)
            row += 1

            self.layout.addWidget(label, row, 0)
            label.setMinimumHeight(50)
            row += 1

            self.buttonGroup.addButton(button)   

            if self.data.mainFunction == fct:
                button.setChecked(True)
    
    def onButtonClicked(self, button):
        self.data.mainFunction = button.function
    
    @Slot(EnBrailleMainFct)
    def onMainFunctionChanged(self, value: EnBrailleMainFct):
        for button in self.buttonGroup.buttons():
            if button.function == value:
                button.setChecked(True)
                break
    
    # function that creates a new radio button and a descriptive label for a EnBrailleMainFct
    def createRadioButton(self, function: EnBrailleMainFct):
        textTemplate = '{}'
        descTemplate = '<i>        {}</i>'
        if function == EnBrailleMainFct.TEXT:
            text = textTemplate.format(self.tr('Text'))
            description = descTemplate.format(self.tr('Convert simple and plain text to BRF braille format.'))
            accessibleDescription = self.tr('Convert simple and plain text to BRF braille format.')
        elif function == EnBrailleMainFct.DOCUMENT:
            text = textTemplate.format(self.tr('Document'))
            description = descTemplate.format(self.tr('Convert a document to BRF braille documents.'))
            accessibleDescription = self.tr('Convert a document to BRF braille documents.')
        elif function == EnBrailleMainFct.REFORMAT:
            text = textTemplate.format(self.tr('Reformat BRF'))
            description = descTemplate.format(self.tr('Reformat a BRF braille document.'))
            accessibleDescription = self.tr('Reformat a BRF braille document.')
        else:
            raise ValueError("Unknown function")        

        button = QRadioButton(text)
        button.setChecked(False)
        button.function = function
        button.setAccessibleDescription(accessibleDescription)
        button.setAccessibleName(text)
        
        # Add keyboard shortcuts for quick access
        if function == EnBrailleMainFct.TEXT:
            button.setShortcut("Alt+T")
        elif function == EnBrailleMainFct.DOCUMENT:
            button.setShortcut("Alt+D")
        elif function == EnBrailleMainFct.REFORMAT:
            button.setShortcut("Alt+R")
    
        label = QLabel(description)
        label.setTextFormat(Qt.RichText)
        label.setAccessibleName("")
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        label.setFocusPolicy(Qt.NoFocus)
        label.setBuddy(button)  # Associate label with button for screen readers
        return (button, label)
    
    def initializePage(self):
        """Set focus to the first radio button when page is shown"""
        super().initializePage()
        
        # Find the first visible radio button and set focus
        for button in self.buttonGroup.buttons():
            if button.isVisible() and button.isEnabled():
                QTimer.singleShot(50, lambda: button.setFocus(Qt.OtherFocusReason))
                logging.debug('Setting focus to first radio button on start page')
                break
