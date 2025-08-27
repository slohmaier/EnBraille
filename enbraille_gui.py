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
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QButtonGroup, QGridLayout, QLabel, QRadioButton,
                               QWidget, QWizard, QWizardPage, QMessageBox)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_functions.reformat import EnBrailleReformatPage, EnBrailleReformaterWorkPage, EnBrailleReformaterResultPage
from enbraille_functions.text import (EnBrailleSimpleResultPage,
                                      EnBrailleSimpleTextPage,
                                      EnBrailleSimpleTextWorkPage)
from enbraille_functions.document import EnBrailleDocumentPage, EnBrailleDocumentPageOutput, EnBrailleDocumentPageWork

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
        # remove all pages except the first one
        for pageId in self.pageIds()[1:]:
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
        
        self.startPage.setFinalPage(False)
        self.updateNextButtonState()

    def updateNextButtonState(self):
        page = self.currentPage()
        self.button(QWizard.NextButton).setEnabled(page.isComplete())
    
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
