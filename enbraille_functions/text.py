import os
import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QTextEdit, QWizardPage
from enbraille_widgets import EnBrailleTableComboBox
from enbraille_data import EnBrailleData, EnBrailleMainFct

class EnBrailleSimpleTextPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Text to BRF'))
        self.setSubTitle(self.tr('Please enter the text you want to convert to BRF:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.tableComboBox = EnBrailleTableComboBox()
        self.layout.addWidget(QLabel(self.tr('Braille table:')), 0, 0)      
        self.layout.addWidget(self.tableComboBox, 0, 1)

        self.textEdit = QTextEdit()
        self.layout.addWidget(QLabel(self.tr('Text:')), 1, 0, 1, 2)
        self.layout.addWidget(self.textEdit, 2, 0, 1, 2)

        self.textEdit.textChanged.connect(self.onTextChanged)
    
    @Slot()
    def onTextChanged(self):
        self.data.inputText = self.textEdit.toPlainText()

    @Slot()
    def onmainFunctionChanged(self):
        self.setVisible(self.data.mainFunction == EnBrailleMainFct.TEXT)