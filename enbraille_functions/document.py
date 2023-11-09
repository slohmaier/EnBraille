from typing import Optional
import logging
import os
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QButtonGroup, QGridLayout, QLabel, QRadioButton,
                               QWidget, QWizard, QWizardPage)

from enbraille_data import EnBrailleData

class EnBrailleDocumentPage(QWizardPage):
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
    