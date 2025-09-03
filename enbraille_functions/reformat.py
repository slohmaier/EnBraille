#
# Copyright (c) 2024 Stefan Lohmaier.
#
# This file is part of EnBraille 
# (see https://github.com/slohmaier/EnBraille).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import logging
import os
import re
import traceback
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QSpinBox, QFileDialog, QFrame, QGridLayout, QWizard,
                               QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy,
                               QProgressBar, QWizard, QWizardPage, QHBoxLayout, QSpacerItem,
                               QTextEdit, QVBoxLayout, QCheckBox)

from enbraille_data import EnBrailleData, EnBrailleMainFct
from enbraille_widgets import EnBrailleTableComboBox
from enbraille_tools import generateOutput, reformatPragraph
from libbrl import libbrlImpl

class EnBrailleReformater(QObject):
    _pagenoregex = re.compile(r'^\s+\#\w+$')
    _pagenoprefix = '\t'

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
        # If line length is 0, return empty string (no reformatting)
        if data.reformatLineLength == 0:
            return ''
            
        with open(self._filename, 'r') as f:
            paragraphs = self._parseParagraphs(f, data)
            lines = []
            for paragraph in paragraphs:
                if len(paragraph) > 0 and paragraph[0] == self._pagenoprefix:
                    pageStr = paragraph.strip()
                    pageStr = ' '* (data.reformatLineLength - len(pageStr) - 1) + pageStr
                    logging.debug('added page number in output: ' + pageStr)
                    lines.append(pageStr)
                else:
                    lines.extend(reformatPragraph(paragraph, data.reformatLineLength, data.reformatWordSplitter))
            logging.debug('Reformated to {} lines'.format(len(lines)))
            return generateOutput(lines, data.reformatPageLength, data.reformatLineLength)
    
    def _parseParagraphs(self, inputFile, data: EnBrailleData) -> list[str]:
        paragraphs = ['']
        lines = inputFile.readlines()
        logging.debug('parsing lines: {} to paragraphs'.format(len(lines)))
        wordRemainder = ''
        for line in lines:
            #strip trailing ' ', '\n' and '\r'
            line = line.rstrip()

            if self._pagenoregex.match(line):
                if data.reformatKeepPageNo:
                    paragraphs.append(self._pagenoprefix + line)
                    paragraphs.append('')
                else:
                    pass
            else:
                if line.startswith(' ') and paragraphs[-1] != '':
                    paragraphs.append('')

                words = line.split(' ')

                if wordRemainder:
                    words[0] = wordRemainder + words[0]
                    wordRemainder = ''

                if words[-1].endswith(data.reformatWordSplitter) and len(words) > 1:
                    wordRemainder = words[-1][:-1]
                    words = words[:-1]

                for word in words:
                    if word:
                        paragraphs[-1] += word + ' '
                
                if len(line) < data.reformatLineLength-4:
                    paragraphs.append('')
        
        logging.debug('Found {} paragraphs'.format(len(paragraphs)))
        return paragraphs

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
        fileLabel = QLabel(self.tr('File:'))
        hbox.addWidget(fileLabel)
        self.filenameLineEdit = QLineEdit()
        self.filenameLineEdit.setReadOnly(True)
        self.filenameLineEdit.setAccessibleName(self.tr('Selected file'))
        self.filenameLineEdit.setAccessibleDescription(self.tr('Path to the braille file to be reformatted'))
        fileLabel.setBuddy(self.filenameLineEdit)
        hbox.addWidget(self.filenameLineEdit)
        self.chooseButton = QPushButton(self.tr('Choose'))
        self.chooseButton.setAccessibleName(self.tr('Choose file'))
        self.chooseButton.setAccessibleDescription(self.tr('Open file dialog to select a braille file for reformatting'))
        self.chooseButton.setShortcut("Ctrl+O")
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
        lineLengthLabel = QLabel(self.tr('Line length:'))
        self.layout.addWidget(lineLengthLabel, row, 0)
        self.lineLengthSpinBox = QSpinBox()
        self.lineLengthSpinBox.setMinimum(0)
        self.lineLengthSpinBox.setMaximum(1000)
        self.lineLengthSpinBox.setAccessibleName(self.tr('Line length'))
        self.lineLengthSpinBox.setAccessibleDescription(self.tr('Maximum number of characters per line, 0 means no line splitting'))
        lineLengthLabel.setBuddy(self.lineLengthSpinBox)
        self.layout.addWidget(self.lineLengthSpinBox, row, 1)
        self.lineLengthSpinBox.valueChanged.connect(self.onLineLengthSpinBoxValueChanged)
        self.lineLengthWarningLabel = QLabel(self.tr('0 means linues won\'t be split'))
        self.layout.addWidget(self.lineLengthWarningLabel, row, 2)
        self.lineLengthWarningLabel.setVisible(self.data.reformatLineLength == 0)
        row += 1

        pageLengthLabel = QLabel(self.tr('Page length:'))
        self.layout.addWidget(pageLengthLabel, row, 0)
        self.pageLengthSpinBox = QSpinBox()
        self.pageLengthSpinBox.setMinimum(0)
        self.pageLengthSpinBox.setMaximum(1000)
        self.pageLengthSpinBox.setAccessibleName(self.tr('Page length'))
        self.pageLengthSpinBox.setAccessibleDescription(self.tr('Maximum number of lines per page, 0 means no page splitting'))
        pageLengthLabel.setBuddy(self.pageLengthSpinBox)
        self.layout.addWidget(self.pageLengthSpinBox, row, 1)
        self.pageLengthSpinBox.valueChanged.connect(self.onPageLengthSpinBoxValueChanged)
        self.pageLengthWarningLabel = QLabel(self.tr('0 means pages won\'t be split'))
        self.layout.addWidget(self.pageLengthWarningLabel, row, 2)
        row += 1

        wordSplitterLabel = QLabel(self.tr('Word Splitter:'))
        self.layout.addWidget(wordSplitterLabel, row, 0)
        self.wordSplitterLineEdit = QLineEdit()
        self.wordSplitterLineEdit.setAccessibleName(self.tr('Word splitter character'))
        self.wordSplitterLineEdit.setAccessibleDescription(self.tr('Character used to split words across lines, must be exactly one character'))
        self.wordSplitterLineEdit.setMaxLength(1)
        wordSplitterLabel.setBuddy(self.wordSplitterLineEdit)
        self.layout.addWidget(self.wordSplitterLineEdit, row, 1)
        self.wordSplitterLineEdit.textChanged.connect(self.onWordSplitterLineEditTextChanged)
        self.wordSplitterWarningLabel = QLabel(self.tr('WordSplitter must be one character!'))
        self.layout.addWidget(self.wordSplitterWarningLabel, row, 2)
        row += 1

        self._checkboxKeepPageNo = QCheckBox(self.tr('Keep page numbers'))
        self._checkboxKeepPageNo.stateChanged.connect(self.onKeepPageNoCheckBoxStateChanged)
        self._checkboxKeepPageNo.setAccessibleName(self.tr('Keep page numbers'))
        self._checkboxKeepPageNo.setAccessibleDescription(self.tr('Preserve existing page numbers during reformatting'))
        self.layout.addWidget(self._checkboxKeepPageNo, row, 1, 1, 2)

        self.lineLengthSpinBox.setValue(self.data.reformatLineLength)
        self.pageLengthSpinBox.setValue(self.data.reformatPageLength)
        self.wordSplitterLineEdit.setText(self.data.reformatWordSplitter)
        self._checkboxKeepPageNo.setChecked(self.data.reformatKeepPageNo)   
    
    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        super().initializePage()
        logging.debug('child widgets: ' + str(self.layout.count()))
        
        # Focus the choose file button as it's the primary action on this page
        if hasattr(self, 'chooseButton'):
            QTimer.singleShot(50, lambda: self.chooseButton.setFocus(Qt.OtherFocusReason))
            logging.debug('Setting focus to choose file button on reformat page') 
    
    def isComplete(self) -> bool:
        if type(self.data.reformatFilename) == str:
            return os.path.isfile(self.data.reformatFilename) and len(self.data.reformatWordSplitter) == 1
        else:
            return all([os.path.isfile(f) for f in self.data.reformatFilename]) and len(self.data.reformatWordSplitter) == 1
    
    def onChooseButtonClicked(self) -> None:
        filename = QFileDialog.getOpenFileNames(self, self.tr('Choose file to convert'), '', self.tr('Braille files (*.brl)'))[0]
        if filename:
            try:
                if type(filename) == str:
                    self._reformater = EnBrailleReformater(filename)            
                    self.filenameLineEdit.setText(filename)
                    if self._reformater.pageLength > 0:
                        self.readPageLengthLabel.setText(str(self._reformater.pageLength))  
                    else:
                        self.readPageLengthLabel.setText(self.tr('no pages detected'))
                    self.maxLineLengthLabel.setText(str(self._reformater.maxLineLength))
                else:
                    self._reformater = [EnBrailleReformater(f) for f in filename]
                    self.filenameLineEdit.setText(str(len(filename)) + ' ' + self.tr('files') + ': ' + ', '.join(filename))
                    self.readPageLengthLabel.setText(', '.join([str(r.pageLength) for r in self._reformater]))
                    maxlengths = [r.maxLineLength for r in self._reformater]
                    self.maxLineLengthLabel.setText(str(max(maxlengths)))
                self.data.reformatFilename = filename
                
                self.data.reformatFilename = filename
            except Exception as e:
                logging.debug('Error while loading file: ' + str(e) + '\n' + traceback.format_exc())
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
    
    def onKeepPageNoCheckBoxStateChanged(self, state: int) -> None:
        logging.debug('onKeepPageNoCheckBoxStateChanged: ' + str(state == 2))
        self.data.reformatKeepPageNo = state == 2

class EnBrailleReformaterWorker(QThread):
    finished = Signal()
    progress = Signal(int, str)

    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()
        self.data = data

    def run(self) -> None:
        try:
            if type(self.data.reformatFilename) == str:
                logging.debug('Reformating file: ' + self.data.reformatFilename)
                reformater = EnBrailleReformater(self.data.reformatFilename)
                self.data.outputData = reformater.reformat(self.progress, self.data)
                logging.debug('Reformated to {} lines'.format(len(self.data.outputData.splitlines())))
            else:
                self.data.outputData = []
                for filename in self.data.reformatFilename:
                    reformater = EnBrailleReformater(filename)
                    logging.debug('Reformating file: ' + filename)
                    self.data.outputData.append(reformater.reformat(self.progress, self.data))
                    logging.debug('Reformated to {} lines'.format(len(self.data.outputData[-1].splitlines())))
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

        self.layout = QGridLayout()
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
        self.wizard().next()
    
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

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        row = 0

        self.layout.addWidget(QLabel(self.tr('Reformatted file:')), row, 0)
        row += 1

        # add a frame to hold the text edit
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.frame.setLineWidth(1)
        self.frame.setMidLineWidth(0)
        self.layout.addWidget(self.frame, row, 0, 1, 3)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setFont(QFont('Courier New', 10))
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().addWidget(self.textEdit)
        row += 1

        self.saveButton = QPushButton(self.tr('&Save'))
        self.saveButton.clicked.connect(self.onSaveButtonClicked)
        self.layout.addWidget(self.saveButton, row, 0)
        row += 1

    def cleanupPage(self) -> None:
        pass

    def initializePage(self) -> None:
        if type(self.data.outputData) == str:
            self.textEdit.setText(self.data.outputData)
        else:
            self.textEdit.setText('\n#-#-#-#-#-#-#-#-#-#-#-#-#\n'.join(self.data.outputData))
    
    def onSaveButtonClicked(self) -> None:
        if type(self.data.outputData) == str:
            filename = QFileDialog.getSaveFileName(self, self.tr('Save file'), '', self.tr('Braille files (*.brl)'))[0]
            if filename:
                try:
                    with open(filename, 'w') as f:
                        f.write(self.data.outputData)
                except Exception as e:
                    QMessageBox.critical(self, self.tr('Error'), self.tr('Error while saving file: ') + str(e))
        else:
            folder = QFileDialog.getExistingDirectory(self, self.tr('Save files to folder'), '')
            if folder:
                for i, outputData in enumerate(self.data.outputData):
                    filename = os.path.join(folder, os.path.basename(self.data.reformatFilename[i]))
                    # add _EnBraille to filename before .
                    filename = filename[:filename.rfind('.')] + '_EnBraille' + filename[filename.rfind('.'):]
                    try:
                        with open(filename, 'w') as f:
                            f.write(outputData)
                    except Exception as e:
                        QMessageBox.critical(self, self.tr('Error'), self.tr('Error while saving file: ') + str(e))
        