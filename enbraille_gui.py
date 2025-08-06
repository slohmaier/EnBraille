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

from PySide6.QtCore import Qt, Slot
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

class EnBrailleWizardPageStart(QWizardPage):
    def __init__(self, data: EnBrailleData):
        super().__init__()

        self.data = data
        self.setTitle(self.tr('What to EnBraille?'))
        self.setSubTitle(self.tr("Please select the function you want to use:"))
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
    
        label = QLabel(description)
        label.setTextFormat(Qt.RichText)
        label.setAccessibleName("")
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        label.setFocusPolicy(Qt.NoFocus)
        return (button, label)
