import logging
import os
import re
import sys
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject
from PySide6.QtGui import QClipboard, QGuiApplication
from PySide6.QtWidgets import (QSpinBox, QFileDialog, QFrame, QGridLayout, QWizard,
                               QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy,
                               QProgressBar, QWizard, QWizardPage, QHBoxLayout,)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_widgets import EnBrailleTableComboBox
from libbrl import libbrlImpl

_BREILLENUMS = {
    '0': 'j',
    '1': 'a',
    '2': 'b',
    '3': 'c',
    '4': 'd',
    '5': 'e',
    '6': 'f',
    '7': 'g',
    '8': 'h',
    '9': 'i'
}

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
    
    def reformat(self, progress: Signal, data: EnBrailleData) -> str:
        with open(self._filename, 'r') as f:
            paragraphs = []

            lines = f.readlines()
            lineno = 0
            for line in lines:
                progress.emit(100 * lineno / len(lines), self.tr('Parsing paragraphs line {0} of {1}').format(lineno, len(lines)))

                if self._pagenoregex.match(line):
                    pass
                elif line.startwith('  '):
                    paragraphs.append(line)
                else:
                    line = line.strip()
                    if not line:
                        paragraphs.append(line)
                    elif paragraphs[-1].endswith(data.reformatWordSplitter):
                        paragraphs[-1] = paragraphs[-1][:-1] + line
                    else:
                        paragraphs[-1] += line
                lineno += 1
            
            outputData = ''
            paragraphno = 0
            lineno = 0
            pageno = 1
            for paragraph in paragraphs:
                progress.emit(100 * paragraphno / len(paragraphs), self.tr('Reformatting paragraph {0} of {1}').format(paragraphno, len(paragraphs)))
                paragraphno += 1

                i = 0
                while i < len(paragraph):
                    part = paragraph[i:i + data.reformatLineLength]
                    if i + data.reformatLineLength < len(paragraph):
                        if part[-1] != ' ' and paragraph[i + data.reformatLineLength] != ' ':
                            outputData += part[:-1] + data.reformatWordSplitter
                            i += self.data.reformatLineLength - 1
                        elif part[0] == ' ':
                            outputData += part[1:]
                            i += data.reformatLineLength - 1
                        else:
                            outputData += part
                            i += data.reformatLineLength
                        lineno += 1
                    
                    lineno += 1
                    if lineno % data.reformatPageLength == 0:
                        pageStr = '#{0}\n'.format(pageno)
                        pageStr = pageStr.translate(str.maketrans(_BREILLENUMS))
                        outputData += ' '*(data.reformatLineLength - len(pageStr)) + pageStr
                        pageno += 1
                        lineno += 1
            
            return outputData

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

        row = 0

        hbox = QHBoxLayout()
        self.layout.addLayout(hbox, row, 0, 1, 5)
        row += 1
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
        self.layout.addWidget(self.line, row, 0, 1, 3)
        row += 1

        # add labels for the read pagelength and the maximum line length
        self.layout.addWidget(QLabel(self.tr('File characteristics:')), row, 0, 1, 3)

        self.layout.addWidget(QLabel(self.tr('Read pagelength:')), row, 0)
        self.readPageLengthLabel = QLabel('-')
        self.layout.addWidget(self.readPageLengthLabel, row, 1)
        row += 1

        self.layout.addWidget(QLabel(self.tr('Maximum line length:')), row, 0)
        self.maxLineLengthLabel = QLabel('-')
        self.layout.addWidget(self.maxLineLengthLabel, row, 1)
        row += 1

        #add horizontal line
        self.line2 = QFrame()
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.line2, row, 0, 1, 3)
        row += 1

        # settings for reformatting
        self.layout.addWidget(QLabel(self.tr('Reformat settings:')), row, 0, 1, 3)
        row += 1

        # add reformat settings controls
        self.layout.addWidget(QLabel(self.tr('Line length:')), row, 0)
        self.lineLengthSpinBox = QSpinBox()
        self.lineLengthSpinBox.setMinimum(0)
        self.lineLengthSpinBox.setMaximum(1000)
        self.layout.addWidget(self.lineLengthSpinBox, row, 1)
        self.lineLengthSpinBox.valueChanged.connect(self.onLineLengthSpinBoxValueChanged)
        self.lineLengthWarningLabel = QLabel(self.tr('0 means linues won\'t be split'))
        self.layout.addWidget(self.lineLengthWarningLabel, row, 2)
        self.lineLengthWarningLabel.setVisible(self.data.reformatLineLength == 0)
        row += 1

        self.layout.addWidget(QLabel(self.tr('Page length:')), row, 0)
        self.pageLengthSpinBox = QSpinBox()
        self.pageLengthSpinBox.setMinimum(0)
        self.pageLengthSpinBox.setMaximum(1000)
        self.layout.addWidget(self.pageLengthSpinBox, row, 1)
        self.pageLengthSpinBox.valueChanged.connect(self.onPageLengthSpinBoxValueChanged)
        self.pageLengthWarningLabel = QLabel(self.tr('0 means pages won\'t be split'))
        self.layout.addWidget(self.pageLengthWarningLabel, row, 2)
        row += 1

        self.layout.addWidget(QLabel(self.tr('Word Splitter:')), row, 0)
        self.wordSplitterLineEdit = QLineEdit()
        self.layout.addWidget(self.wordSplitterLineEdit, row, 1)
        self.wordSplitterLineEdit.textChanged.connect(self.onWordSplitterLineEditTextChanged)
        self.wordSplitterWarningLabel = QLabel(self.tr('WordSplitter must be one character!'))
        self.layout.addWidget(self.wordSplitterWarningLabel, row, 2)
        row += 1

        self.lineLengthSpinBox.setValue(self.data.reformatLineLength)
        self.pageLengthSpinBox.setValue(self.data.reformatPageLength)
        self.wordSplitterLineEdit.setText(self.data.reformatWordSplitter)
    
    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return os.path.isfile(self.data.reformatFilename) and len(self.data.reformatWordSplitter) == 1
    
    def onChooseButtonClicked(self) -> None:
        filename = QFileDialog.getOpenFileName(self, self.tr('Choose file to convert'), '', self.tr('Braille files (*.brl)'))[0]
        if filename:
            try:
                self._reformater = EnBrailleReformater(filename)            
                self.data.reformatFilename = filename
                self.filenameLineEdit.setText(filename)
                self.data.reformatFilename = filename
                
                if self._reformater.pageLength > 0:
                    self.readPageLengthLabel.setText(str(self._reformater.pageLength))  
                else:
                    self.readPageLengthLabel.setText('no pages detected')

                self.maxLineLengthLabel.setText(str(self._reformater.maxLineLength))
            except Exception as e:
                QMessageBox.critical(self, self.tr('Error'), self.tr('Error while loading file: ') + str(e))
            
        self.completeChanged.emit()
    
    def onLineLengthSpinBoxValueChanged(self, value: int) -> None:
        self.data.reformatLineLength = value
        self.lineLengthWarningLabel.setVisible(self.data.reformatLineLength == 0)
    
    def onPageLengthSpinBoxValueChanged(self, value: int) -> None:
        self.data.reformatPageLength = value
        self.pageLengthWarningLabel.setVisible(self.data.reformatPageLength == 0)
    
    def onWordSplitterLineEditTextChanged(self, text: str) -> None:
        self.data.reformatWordSplitter = text
        self.wordSplitterWarningLabel.setVisible(len(self.data.reformatWordSplitter) != 1)
        self.completeChanged.emit()

class ReformatWorker(QThread):
    finished = Signal()
    progress = Signal(int, str)

    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

    def run(self) -> None:
        try:
            reformater = EnBrailleReformater(self.data.reformatFilename)
            self.data.outputData = reformater.reformat(self.progress, self.data)
        except Exception as e:
            logging.debug('Error while reformatting: ' + str(e) + '\n' + traceback.format_exc())
            self.progress.emit(-1, self.tr('Error while reformatting: ') + str(e))

        self.progress.emit(100, self.tr('Done.'))
        self.finished.emit()
        

class EnBrailleReformaterWorkPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__(None)
        self.data = data

        self.setTitle(self.tr('Reformatting'))
        self.setSubTitle(self.tr('Reformatting the file...'))

        self.layout = QGridLayout
        self.setLayout(self.layout)

        row = 0

        # add vertical spacer
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0, 1, 3)
        row += 1

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.layout.addWidget(self.progressBar, row, 0, 1, 3)
        row += 1
        
        self.progressLabel = QLabel(self.tr('Starting...'))
        self.progressLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progressLabel, row, 0, 1, 3)

        # add vertical spacer
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0, 1, 3)
        row += 1

        self.worker = EnBrailleReformaterWorker(self.data)
        self.worker.finished.connect(self.onWorkerFinished)     
        self.worker.progress.connect(self.onWorkerProgress)
    
    def cleanupPage(self) -> None:
        pass

    def initializePage(self) -> None:
        self.worker = ReformatWorker(self.data)
        self.worker.finished.connect(self.onWorkerFinished)
        self.worker.progress.connect(self.onWorkerProgress)
        self.worker.start()

        #disable back button
        self.wizard().button(QWizard.BackButton).setEnabled(False)
        self.wizard().button(QWizard.NextButton).setEnabled(False)
        self.wizard().button(QWizard.FinishButton).setEnabled(False)
    
    def isComplete(self) -> bool:
        return self.worker.isFinished()
    
    def onWorkerFinished(self) -> None:
        self.wizard().button(QWizard.BackButton).setEnabled(True)
        self.wizard().button(QWizard.NextButton).setEnabled(True)
        self.wizard().button(QWizard.FinishButton).setEnabled(True)
        self.completeChanged.emit()
    
    def onWorkerProgress(self, progress: int, message: str) -> None:
        if progress == -1:
            QMessageBox.critical(self, self.tr('Error'), message)   
            self.wizard().back()
        else:
            self.progressBar.setValue(progress)
            self.progressLabel.setText(message)

class EnBrailleReformaterResultPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__(None)
        self.data = data

        self.setTitle(self.tr('Reformatting done'))
        self.setSubTitle(self.tr('Reformatting the file is done.'))

        self.layout = QGridLayout
        self.setLayout(self.layout)
        row = 0
        