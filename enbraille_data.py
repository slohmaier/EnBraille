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
from enum import Enum
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, Qt, QSettings
from PySide6.QtWidgets import QApplication

_EMBRAILLEMAINFCT_STRMAP = {
        1: 'TEXT',
        2: 'DOCUMENT',
        3: 'REFORMAT'
    }

class EnBrailleMainFct(Enum):
    TEXT = 1
    DOCUMENT = 2
    REFORMAT = 3

    def __str__(self) -> str:
        return _EMBRAILLEMAINFCT_STRMAP[self.value]
    
    @staticmethod
    def fromStr(value: str) -> Optional['EnBrailleMainFct']:
        for key, val in _EMBRAILLEMAINFCT_STRMAP.items():
            if val == value:
                return EnBrailleMainFct(key)
        return None

class EnBrailleData(QObject):
    mainFunctionChanged = Signal(EnBrailleMainFct)
    TextTableChanged = Signal(str)
    DocumentTextTableChanged = Signal(str)

    def __init__(self, app: QApplication) -> None:
        super().__init__(None)

        self._settings = QSettings(app.organizationName(), app.applicationName())

        #public members
        self.inputText = ''
        self.outputText = ''
        self.reformatFilename = ''
        self.documentFilename = ''

    def resetSettings(self) -> None:
        self._settings.clear()
        self._settings.sync()
    
    @property
    def mainFunction(self) -> EnBrailleMainFct:
        s = self._settings.value('mainFunction', str(EnBrailleMainFct.TEXT), type=str)
        return EnBrailleMainFct.fromStr(s)
    
    @mainFunction.setter
    def mainFunction(self, value: EnBrailleMainFct) -> None:
        if self.mainFunction != value:
            self._settings.setValue('mainFunction', str(value))
            self._settings.sync()

            self.mainFunctionChanged.emit(value)
        
    @property
    def textTable(self) -> str:
        return self._settings.value('textTable', '', type=str)
    
    @textTable.setter
    def textTable(self, value: str) -> None:    
        if self.textTable != value:
            logging.debug('EnBrailleData: setting textTable to ' + str(value))
            self._settings.setValue('textTable', value)
            self._settings.sync()

            self.TextTableChanged.emit(value)
    
    @property
    def reformatLineLength(self) -> int:
        return self._settings.value('reformatLineLength', 40, type=int)
    
    @reformatLineLength.setter
    def reformatLineLength(self, value: int) -> None:
        if self.reformatLineLength != value:
            logging.debug('EnBrailleData: setting reformatLineLength to ' + str(value))
            self._settings.setValue('reformatLineLength', value)
            self._settings.sync()
    
    @property
    def reformatPageLength(self) -> int:
        return self._settings.value('reformatPageLength', 0, type=int)
    
    @reformatPageLength.setter
    def reformatPageLength(self, value: int) -> None:
        if self.reformatPageLength != value:
            logging.debug('EnBrailleData: setting reformatPageLength to ' + str(value)) 
            self._settings.setValue('reformatPageLength', value)
            self._settings.sync()
    
    @property
    def reformatWordSplitter(self) -> str:
        return self._settings.value('reformatWordSplitter', '-', type=str)
    
    @reformatWordSplitter.setter
    def reformatWordSplitter(self, value: str) -> None:
        if self.reformatWordSplitter != value:
            logging.debug('EnBrailleData: setting reformatWordSplitter to ' + str(value))
            self._settings.setValue('reformatWordSplitter', value)
            self._settings.sync()
    
    @property
    def reformatKeepPageNo(self) -> bool:
        return self._settings.value('reformatKeepPageNo', False, type=bool)
    
    @reformatKeepPageNo.setter
    def reformatKeepPageNo(self, value: bool) -> None:
        if self.reformatPageLength != value:
            logging.debug('EnBrailleData: setting reformatKeepPageNo to ' + str(value))
            self._settings.setValue('reformatKeepPageNo', value)
            self._settings.sync()
    
    @property
    def documentTextTable(self) -> str:
        return self._settings.value('documenttextTable', '', type=str)
    
    @textTable.setter
    def documentTextTable(self, value: str) -> None:    
        if self.documentTextTable != value:
            logging.debug('EnBrailleData: setting documenttextTable to ' + str(value))
            self._settings.setValue('documenttextTable', value)
            self._settings.sync()

            self.DocumentTextTableChanged.emit(value)

    @property
    def documentLineLength(self) -> int:
        return self._settings.value('documentLineLength', 40, type=int)
    
    @documentLineLength.setter
    def documentLineLength(self, value: int) -> None:
        if self.documentLineLength != value:
            logging.debug('EnBrailleData: setting documentLineLength to ' + str(value))
            self._settings.setValue('documentLineLength', value)
            self._settings.sync()
    
    @property
    def documentPageLength(self) -> int:
        return self._settings.value('documentPageLength', 0, type=int)
    
    @documentPageLength.setter
    def documentPageLength(self, value: int) -> None:
        if self.documentPageLength != value:
            logging.debug('EnBrailleData: setting documentPageLength to ' + str(value)) 
            self._settings.setValue('documentPageLength', value)
            self._settings.sync()
    
    @property
    def documentWordSplitter(self) -> str:
        return self._settings.value('documentWordSplitter', '-', type=str)
    
    @documentWordSplitter.setter
    def documentWordSplitter(self, value: str) -> None:
        if self.documentWordSplitter != value:
            logging.debug('EnBrailleData: setting documentWordSplitter to ' + str(value))
            self._settings.setValue('documentWordSplitter', value)
            self._settings.sync()   
        
    @property
    def documentH1Char(self) -> str:
        return self._settings.value('document/H1Char', '#', type=str)

    @documentH1Char.setter
    def documentH1Char(self, value: str) -> None:
        if self.documentH1Char != value:
            logging.debug('EnBrailleData: setting documentH1Char to ' + str(value))
            self._settings.setValue('document/H1Char', value)
            self._settings.sync()
    
    @property
    def documentH2Char(self) -> str:
        return self._settings.value('document/H2Char', '=', type=str)
    
    @documentH2Char.setter
    def documentH2Char(self, value: str) -> None:
        if self.documentH2Char != value:
            logging.debug('EnBrailleData: setting documentH2Char to ' + str(value))
            self._settings.setValue('document/H2Char', value)
            self._settings.sync()

    @property
    def documentH3Char(self) -> str:
        return self._settings.value('document/H3Char', '-', type=str)
    
    @documentH3Char.setter
    def documentH3Char(self, value: str) -> None:
        if self.documentH3Char != value:
            logging.debug('EnBrailleData: setting documentH3Char to ' + str(value))
            self._settings.setValue('document/H3Char', value)
            self._settings.sync()

    @property
    def documentH4Char(self) -> str:
        return self._settings.value('document/H4Char', '.', type=str)
    
    @documentH4Char.setter
    def documentH4Char(self, value: str) -> None:
        if self.documentH4Char != value:
            logging.debug('EnBrailleData: setting documentH4Char to ' + str(value))
            self._settings.setValue('document/H4Char', value)
            self._settings.sync()

    @property
    def documentH5Char(self) -> str:
        return self._settings.value('document/H5Char', ',', type=str)
    
    @documentH5Char.setter
    def documentH5Char(self, value: str) -> None:
        if self.documentH5Char != value:
            logging.debug('EnBrailleData: setting documentH5Char to ' + str(value))
            self._settings.setValue('document/H5Char', value)
            self._settings.sync()
    
    @property
    def documentH6Char(self) -> str:
        return self._settings.value('document/H6Char', ';', type=str)
    
    @documentH6Char.setter
    def documentH6Char(self, value: str) -> None:
        if self.documentH6Char != value:
            logging.debug('EnBrailleData: setting documentH6Char to ' + str(value))
            self._settings.setValue('document/H6Char', value)
            self._settings.sync()
    
    @property
    def documentBulletL1Char(self) -> str:
        return self._settings.value('document/BulletL1Char', '*', type=str)
    
    @documentBulletL1Char.setter
    def documentBulletL1Char(self, value: str) -> None:
        if self.documentBulletL1Char != value:
            logging.debug('EnBrailleData: setting documentBulletL1Char to ' + str(value))
            self._settings.setValue('document/BulletL1Char', value)
            self._settings.sync()
    
    @property
    def documentBulletL2Char(self) -> str:
        return self._settings.value('document/BulletL2Char', '+', type=str)

    @documentBulletL2Char.setter
    def documentBulletL2Char(self, value: str) -> None:
        if self.documentBulletL2Char != value:
            logging.debug('EnBrailleData: setting documentBulletL2Char to ' + str(value))
            self._settings.setValue('document/BulletL2Char', value)
            self._settings.sync()
    
    @property
    def documentBulletL3Char(self) -> str:
        return self._settings.value('document/BulletL3Char', '-', type=str)
    
    @documentBulletL3Char.setter
    def documentBulletL3Char(self, value: str) -> None:
        if self.documentBulletL3Char != value:
            logging.debug('EnBrailleData: setting documentBulletL3Char to ' + str(value))
            self._settings.setValue('document/BulletL3Char', value)
            self._settings.sync()
    
    @property
    def documentBulletL4Char(self) -> str:
        return self._settings.value('document/BulletL4Char', '.', type=str)
    
    @documentBulletL4Char.setter
    def documentBulletL4Char(self, value: str) -> None:
        if self.documentBulletL4Char != value:
            logging.debug('EnBrailleData: setting documentBulletL4Char to ' + str(value))
            self._settings.setValue('document/BulletL4Char', value)
            self._settings.sync()
    
    @property
    def documentBulletL5Char(self) -> str:
        return self._settings.value('document/BulletL5Char', ',', type=str)

    @documentBulletL5Char.setter
    def documentBulletL5Char(self, value: str) -> None:
        if self.documentBulletL5Char != value:
            logging.debug('EnBrailleData: setting documentBulletL5Char to ' + str(value))
            self._settings.setValue('document/BulletL5Char', value)
            self._settings.sync()
    
    @property
    def documentBulletL6Char(self) -> str:
        return self._settings.value('document/BulletL6Char', ';', type=str)
    
    @documentBulletL6Char.setter
    def documentBulletL6Char(self, value: str) -> None:
        if self.documentBulletL6Char != value:
            logging.debug('EnBrailleData: setting documentBulletL6Char to ' + str(value))
            self._settings.setValue('document/BulletL6Char', value)
            self._settings.sync()
