from typing import Optional
import logging
import os
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QPushButton, QGridLayout, QLabel, QRadioButton,
                               QWidget, QWizard, QWizardPage, QLineEdit, QHBoxLayout,
                               QFileDialog, QWizardPage)

from enbraille_data import EnBrailleData

class EnBrailleDocumentPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()

        self._data = data

        self.setTitle(self.tr('Convert Document to BRF'))
        self.setSubTitle(self.tr('Please choose the document you want to reformat:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.documentLayoutWidget = QWidget()
        self.documentLayout = QHBoxLayout(self.documentLayoutWidget)
        self.documentLabel = QLabel(self.tr('Document:'))
        self.documentLayout.addWidget(self.documentLabel)
        self.documentEdit = QLineEdit(tr('Select document ...'))
        self.documentEdit.setReadOnly(True)
        self.documentLayout.addWidget(self.documentEdit)
        self.documentButton = QPushButton(self.tr('Browse ...'))
        self.documentButton.clicked.connect(self.browseDocument)
        self.documentLayout.addWidget(self.documentButton)
        self.layout.addWidget(self.documentLayoutWidget, 0, 0)
    
    def browseDocument(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self.window(),
            self.tr('Select document'),
            os.path.expanduser('~'),
            self.tr('Supported files (*.epub *.md);;EPUB files (*.epub);;Markdown files (*.md);;All files (*.*')
        )
        if filename:
            self.documentEdit.setText(filename)
            self._data.documentFilename = filename

    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return True

    def validatePage(self) -> bool:
        return True

class EnBrailleDocumentPageWork(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()

        self._data = data

    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return True

    def validatePage(self) -> bool:
        return True

class EnBrailleDocumentPageOutput(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()

        self._data = data

    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return True

    def validatePage(self) -> bool:
        return True
    