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

    def __init__(self, app: QApplication) -> None:
        super().__init__(None)

        self._settings = QSettings(app.organizationName(), app.applicationName())
    

        #public members
        self.inputText = ''
        self.outputText = ''
        self.reformatFilename = ''

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
        
