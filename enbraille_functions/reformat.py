import logging
import os
import sys

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame, QGridLayout,
                               QLabel, QLineEdit, QProgressBar, QPushButton,
                               QTextEdit, QWizard, QWizardPage, QHBoxLayout,)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_widgets import EnBrailleTableComboBox
from libbrl import libbrlImpl


class EnBrailleReformatPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Reformat BRF'))
        self.setSubTitle(self.tr('Please choose the BRF file you want to reformat:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        hbox = QHBoxLayout()
        self.layout.addLayout(hbox, 0, 0, 1, 5)
        hbox.addWidget(QLabel(self.tr('File:')))
        self.filenameLineEdit = QLineEdit()
        self.filenameLineEdit.setReadOnly(True)
        hbox.addWidget(self.filenameLineEdit)
        self.chooseButton = QPushButton(self.tr('Choose'))
        hbox.addWidget(self.chooseButton)
        self.chooseButton.clicked.connect(self.onChooseButtonClicked)

        #add horizontal line
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.line, 1, 0, 1, 3)
    
    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return os.path.isfile(self.data.reformatFilename)
    
    def onChooseButtonClicked(self) -> None:
        filename = QFileDialog.getOpenFileName(self, self.tr('Choose file to convert'), '', self.tr('Braille files (*.brl)'))[0]
        if filename:
            self.data.reformatFilename = filename
            self.filenameLineEdit.setText(filename)
        self.completeChanged.emit()
        