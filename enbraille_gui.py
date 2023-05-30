import logging
from typing import Optional
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWizard, QGridLayout, QLabel, QButtonGroup, QWizardPage, QRadioButton, QTextEdit
from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_widgets import EnBrailleTableComboBox
from enbraille_functions.text import EnBrailleSimpleTextPage, EnBrailleSimpleTextWorkPage, EnBrailleSimpleResultPage
from enbraille_functions.reformat import EnBrailleReformatPage

class EnBrailleWindow(QWizard):
    def __init__(self, data: EnBrailleData):
        super().__init__()
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

        # refresh wizard page visibility based on current main function
        logging.debug('EnBrailleWindow: mainFunction = %s', data.mainFunction)
        self.onMainFunctionChanged(data.mainFunction)
    
    @Slot(EnBrailleMainFct)
    def onMainFunctionChanged(self, mainFunction: EnBrailleMainFct):
        # hide all pages
        for pageId in self.pageIds():
            self.page(pageId).setVisible(False)

        self.startPage.setVisible(True)
        # show the pages for the current main function
        if mainFunction == EnBrailleMainFct.TEXT:
            self.simpleTextPage.setVisible(True)
            self.simpleTextWorkPage.setVisible(True)
            self.simpleTextResultPage.setVisible(True)
        elif mainFunction == EnBrailleMainFct.REFORMAT:
            self.reformatPage.setVisible(True)

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
