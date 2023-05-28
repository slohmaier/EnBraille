
from typing import Optional
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWizard, QGridLayout, QLabel, QButtonGroup, QWizardPage, QRadioButton, QTextEdit
from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_widgets import EnBrailleTableComboBox

class EnBrailleWindow(QWizard):
    def __init__(self, data: EnBrailleData):
        super().__init__()
        self.setWindowTitle("EnBraille")
        self.setWizardStyle(QWizard.ModernStyle)
        self.addPage(EnBrailleWizardPageStart(data))
        self.addPage(EnBrailleSimpleTextPage(data))

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

class EnBrailleSimpleTextPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Text to BRF'))
        self.setSubTitle(self.tr('Please enter the text you want to convert to BRF:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.textEdit = QTextEdit()
        self.layout.addWidget(self.textEdit, 0, 0)

        self.textEdit.textChanged.connect(self.onTextChanged)

        self.tableComboBox = EnBrailleTableComboBox()
        self.layout.addWidget(self.tableComboBox, 1, 0)
    
    @Slot()
    def onTextChanged(self):
        self.data.inputText = self.textEdit.toPlainText()
