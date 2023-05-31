import logging
import os
import re
import sys

from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame, QGridLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton,
                               QTextEdit, QWizard, QWizardPage, QHBoxLayout,)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_widgets import EnBrailleTableComboBox
from libbrl import libbrlImpl

class EnBrailleReformater(QObject):
    _pagenoregex = re.compile(r'^\s+\#\w+\s*$')

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._loadFile()
    
    def _loadFile(self) -> str:
        with open(self._filename, 'r') as f:
            data = f.read()

            self._maxLineLength = 0
            self._pageLength = 0
            linecount = 0
            pageLengths = []
            for line in data.splitlines():
                # detect maximum line length
                self._maxLineLength = max(self._maxLineLength, len(line))
            
                # count pagelength
                linecount += 1
                print('"{}"'.format(line))
                if self._pagenoregex.match(line):
                    pageLengths.append(linecount)
                    linecount = 0
            
            # calculate pagelength with most occurences
            self._pageLength = 0
            if pageLengths:
                counts = {}
                for pageLength in pageLengths:
                    counts[pageLength] = counts.get(pageLength, 0) + 1
                pageLength = 0
                maxCount = 0
                for pageLength, count in counts.items():
                    if count > maxCount:
                        maxCount = count
                        self._pageLength = pageLength

    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def maxLineLength(self) -> int:
        return self._maxLineLength
    
    @property
    def pageLength(self) -> int:
        return self._pageLength

    @filename.setter
    def filename(self, value: str) -> None:
        self._filename = value
        self._loadFile()

class EnBrailleReformatPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

        self.setTitle(self.tr('Reformat BRF'))
        self.setSubTitle(self.tr('Please choose the BRF file you want to reformat:'))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self._reformater = None

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

        # add labels for the read pagelength and the maximum line length
        self.layout.addWidget(QLabel(self.tr('Read pagelength:')), 2, 0)
        self.readPageLengthLabel = QLabel()
        self.layout.addWidget(self.readPageLengthLabel, 2, 1)
        self.layout.addWidget(QLabel(self.tr('Maximum line length:')), 2, 2)
        self.maxLineLengthLabel = QLabel()
        self.layout.addWidget(self.maxLineLengthLabel, 2, 3)

    
    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return os.path.isfile(self.data.reformatFilename)
    
    def onChooseButtonClicked(self) -> None:
        filename = QFileDialog.getOpenFileName(self, self.tr('Choose file to convert'), '', self.tr('Braille files (*.brl)'))[0]
        if filename:
            try:
                self._reformater = EnBrailleReformater(filename)            
                self.data.reformatFilename = filename
                self.filenameLineEdit.setText(filename)
                self.data.reformatFilename = filename
            except Exception as e:
                QMessageBox.critical(self, self.tr('Error'), self.tr('Error while loading file: ') + str(e))
            
        self.completeChanged.emit()
        