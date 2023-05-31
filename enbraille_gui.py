import logging
from typing import Optional

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QButtonGroup, QGridLayout, QLabel, QRadioButton,
                               QWidget, QWizard, QWizardPage)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_functions.reformat import EnBrailleReformatPage, EnBrailleReformaterWorkPage, EnBrailleReformaterResultPage
from enbraille_functions.text import (EnBrailleSimpleResultPage,
                                      EnBrailleSimpleTextPage,
                                      EnBrailleSimpleTextWorkPage)

class EnBrailleWindow(QWizard):
    def __init__(self, data: EnBrailleData):
        super().__init__()
        self.data = data

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

        self.reformatResultPage = EnBrailleSimpleResultPage(data)
        self.reformatResultPage.completeChanged.connect(self.updateNextButtonState)   
        self.addPage(self.reformatResultPage)

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
        elif function == EnBrailleMainFct.DOCUMENT:
            text = textTemplate.format(self.tr('Document'))
            description = descTemplate.format(self.tr('Convert a document to BRF braille documents.'))
        elif function == EnBrailleMainFct.REFORMAT:
            text = textTemplate.format(self.tr('Reformat BRF'))
            description = descTemplate.format(self.tr('Reformat a BRF braille document.'))
        else:
            raise ValueError("Unknown function")        

        button = QRadioButton(text)
        button.setChecked(False)
        button.function = function
    
        label = QLabel(description)
        label.setTextFormat(Qt.RichText)
        return (button, label)
