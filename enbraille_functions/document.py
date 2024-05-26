from typing import Optional
import logging
import os
from PySide6.QtWidgets import (QPushButton, QGridLayout, QLabel, QRadioButton,
                               QWidget, QFrame, QWizardPage, QLineEdit, QHBoxLayout,
                               QFileDialog, QWizardPage, QSpinBox)
from PySide6.QtCore import QObject
import markdown.treeprocessors
from enbraille_data import EnBrailleData
from enbraille_widgets import EnBrailleTableComboBox
from util_epib import epub2md
from PySide6.QtCore import Signal
import markdown

class EnBrailleMd2BRF(markdown.treeprocessors.Treeprocessor):
    def run(self, doc: markdown.util.etree.Element) -> None:
        return self.convert_elemnents(doc)

    def convert_elemnents(self, elements: markdown.util.etree.Element) -> None:
        brf = ''
        for element in elements:
            if element.tag == 'p':
                brf += self.convert_paragraph(element)
            elif element.tag == 'h1':
                brf += self.convert_heading(element, 1)
            elif element.tag == 'h2':
                brf += self.convert_heading(element, 2)
            elif element.tag == 'h3':
                brf += self.convert_heading(element, 3)
            elif element.tag == 'h4':
                brf += self.convert_heading(element, 4)
            elif element.tag == 'h5':
                brf += self.convert_heading(element, 5)
            elif element.tag == 'h6':
                brf += self.convert_heading(element, 6)
            elif element.tag == 'ul':
                brf += self.convert_unordered_list(element)
            elif element.tag == 'ol':
                brf += self.convert_ordered_list(element)
            elif element.tag == 'blockquote':
                brf += self.convert_blockquote(element)
            elif element.tag == 'pre':
                brf += self.convert_preformatted(element)
            elif element.tag == 'code':
                brf += self.convert_code(element)
            elif element.tag == 'img':
                brf += self.convert_image(element)
            elif element.tag == 'a':
                brf += self.convert_link(element)
            elif element.tag == 'hr':
                brf += self.convert_horizontal_rule(element)
            elif element.tag == 'br':
                brf += self.convert_line_break(element)
            elif element.tag == 'table':
                brf += self.convert_table(element)
            elif element.tag == 'tr':
                brf += self.convert_table_row(element)
            elif element.tag == 'td':
                brf += self.convert_table_data(element)
            elif element.tag == 'th':
                brf += self.convert_table_header(element)
            else:
                brf += self.convert_elemnents(element)

class EnBrailleDocumentConverter(QObject):
    progress = Signal(int, str)

    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()

        self.data = data

    def convert(self, proggressCallback: callable) -> None:
        mdContent : str  = None
        if self.data.documentFilename.endswith('.epub'):
            mdContent = epub2md(self.data.documentFilename, self.data.documentFilename + '.md')
        elif self.data.documentFilename.endswith('.md'):
            with open(self.data.documentFilename, 'r') as f:
                mdContent = f.read()
        else:
            raise ValueError('Unsupported file format')
    
        # parse amrkdown
        doc = markdown.markdown(mdContent)

        doc.

        proggressCallback(100)

class EnBrailleDocumentPage(QWizardPage):
    def __init__(self, data: EnBrailleData) -> None:
        super().__init__()

        self.data = data

        self.setTitle(self.tr('Convert Document to BRF'))
        self.setSubTitle(self.tr('Please choose the document you want to reformat:'))

        self.layout = QGridLayout()
        row = 0
        self.setLayout(self.layout)

        self.documentLayoutWidget = QWidget()
        self.documentLayout = QHBoxLayout(self.documentLayoutWidget)
        self.documentLabel = QLabel(self.tr('Document:'))
        self.documentLayout.addWidget(self.documentLabel)
        self.documentEdit = QLineEdit(self.tr('Select document ...'))
        self.documentEdit.setReadOnly(True)
        self.documentLayout.addWidget(self.documentEdit)
        self.documentButton = QPushButton(self.tr('Browse ...'))
        self.documentButton.clicked.connect(self.browseDocument)
        self.documentLayout.addWidget(self.documentButton)
        self.layout.addWidget(self.documentLayoutWidget, row, 0, 1, 3)
        row += 1

        self.tableComboBox = EnBrailleTableComboBox(data)
        self.tableComboBox.currentTextChanged.connect(self.onTableChanged)
        self.layout.addWidget(QLabel(self.tr('Braille table:')), row, 0)      
        self.layout.addWidget(self.tableComboBox, row, 1, 1, 3)
        row += 1

        #add horizontal line
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.line, row, 0, 1, 3)
        row += 1

        #add page settings
        self.layout.addWidget(QLabel(self.tr('Page settings:')), row, 0, 1, 3)
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
    
    def onTableChanged(self, text: str) -> None:
        self.data.documentTable = text
    
    def onLineLengthSpinBoxValueChanged(self, value: int) -> None:
        self.data.documentLineLength = value
        self.lineLengthWarningLabel.setVisible(value == 0)
    
    def onPageLengthSpinBoxValueChanged(self, value: int) -> None:
        self.data.documentPageLength = value
        self.pageLengthWarningLabel.setVisible(value == 0)
    
    def onWordSplitterLineEditTextChanged(self, text: str) -> None:
        self.data.documentWordSplitter = text
        self.wordSplitterWarningLabel.setVisible(len(text) != 1)
    
    def browseDocument(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self.window(),
            self.tr('Select document'),
            os.path.expanduser('~'),
            self.tr('Supported files (*.epub *.md);;EPUB files (*.epub);;Markdown files (*.md);;All files (*.*')
        )
        if filename:
            self.documentEdit.setText(filename)
            self.data.documentFilename = filename

    def cleanupPage(self) -> None:
        pass
    
    def initializePage(self) -> None:
        logging.debug('child widgets: ' + str(self.layout.count())) 
    
    def isComplete(self) -> bool:
        return os.path.exists(self.data.documentFilename) and self.data.documentTable != ''

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
    