import logging
import os
import sys
from PySide6.QtCore import Qt, Slot, QThread, Signal
from PySide6.QtGui import QGuiApplication, QClipboard
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QTextEdit, QWizardPage, QWizard, QPushButton, QProgressBar
from enbraille_widgets import EnBrailleTableComboBox
from enbraille_data import EnBrailleData, EnBrailleMainFct
from libbrl import libbrlImpl

class EnBrailleSimpleTextPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Text to BRF'))
        self.setSubTitle(self.tr('Please enter the text you want to convert to BRF:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.tableComboBox = EnBrailleTableComboBox(data)
        self.tableComboBox.currentTextChanged.connect(self.onTableChanged)
        self.layout.addWidget(QLabel(self.tr('Braille table:')), 0, 0)      
        self.layout.addWidget(self.tableComboBox, 0, 1)

        self.textEdit = QTextEdit()
        self.layout.addWidget(QLabel(self.tr('Text:')), 1, 0, 1, 2)
        self.layout.addWidget(self.textEdit, 2, 0, 1, 2)

        self.textEdit.textChanged.connect(self.onTextChanged)
    
    def isComplete(self) -> bool:
        return self.data.inputText != '' and self.tableComboBox.currentText() != ''
    
    @Slot(str)
    def onTableChanged(self, value: str):
        self.data.textTable = value
        logging.debug('SimpleTextPage: textTable changed to ' + value)
        self.completeChanged.emit()

    @Slot()
    def onTextChanged(self):
        self.data.inputText = self.textEdit.toPlainText()
        logging.debug('SimpleTextPage: inputText changed to ' + self.data.inputText)
        self.completeChanged.emit()

    @Slot()
    def onTaskFinished(self, outputText: str):
        self.data.outputText = outputText
        self.completeChanged.emit()

class EnBrailleSimpleWorker(QThread):
    finished = Signal(str)

    def __init__(self, data: EnBrailleData):
        super().__init__()
        self.data = data

    def run(self):
        brl = libbrlImpl()
        outputText = brl.translate(self.data.inputText, self.data.textTable)
        logging.debug('EnBrailleSimpleWorker: finished translation: %s', outputText)
        self.finished.emit(outputText)
    
    @Slot(EnBrailleMainFct)
    def onmainFunctionChanged(self, value: EnBrailleMainFct):
        self.setVisible(value == EnBrailleMainFct.TEXT)

class EnBrailleSimpleTextWorkPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Text to BRF'))
        self.setSubTitle(self.tr('Please wait while your text is converted to BRF:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.layout.addWidget(self.label)

        self.worker = EnBrailleSimpleWorker(self.data)
        self.worker.finished.connect(self.onTaskFinished)
    
    @Slot()
    def onTaskFinished(self, outputText: str):
        self.data.outputText = outputText
        self.completeChanged.emit()
        self.wizard().button(QWizard.NextButton).click()
    
    def initializePage(self):
        self.worker.start()

    def isComplete(self) -> bool:
        return self.worker.isFinished()

class EnBrailleSimpleResultPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Text to BRF'))
        self.setSubTitle(self.tr('Here is your text in BRF:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel(self.tr('Text:')), 0, 0)   

        self.copyToClipboardButton = QPushButton(self.tr('&Copy to Clipboard'))
        self.copyToClipboardButton.clicked.connect(self.onCopyToClipboard)
        self.layout.addWidget(self.copyToClipboardButton, 1, 0)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(self.data.outputText)
        self.layout.addWidget(self.textEdit, 2, 0)
    
    def initializePage(self):
        self.textEdit.setText(self.data.outputText)
    
    def onCopyToClipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.data.outputText)
