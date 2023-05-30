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

        mainFunctionStr = self._settings.value('mainFunction', str(EnBrailleMainFct.TEXT), type=str)
        self._mainFunction: EnBrailleMainFct = EnBrailleMainFct.fromStr(mainFunctionStr)
        self._textTable: str = self._settings.value('textTable', '', type=str)

        #public members
        self.inputText = ''
        self.outputText = ''
        self.reformatFilename = ''
    
    @property
    def mainFunction(self) -> EnBrailleMainFct:
        return self._mainFunction
    
    @mainFunction.setter
    def mainFunction(self, value: EnBrailleMainFct) -> None:
        if self._mainFunction != value:
            self._mainFunction = value
            
            self._settings.setValue('mainFunction', str(value))
            self._settings.sync()

            self.mainFunctionChanged.emit(value)
        
    @property
    def textTable(self) -> str:
        return self._textTable
    
    @textTable.setter
    def textTable(self, value: str) -> None:    
        if self._textTable != value:
            self._textTable = value

            self._settings.setValue('textTable', value)
            self._settings.sync()

            self.TextTableChanged.emit(value)
