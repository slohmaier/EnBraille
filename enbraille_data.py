from enum import Enum
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, Qt

class EnBrailleMainFct(Enum):
    TEXT = 1
    DOCUMENT = 2
    REFORMAT = 3

class EnBrailleData(QObject):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self._mainFunction: EnBrailleMainFct = EnBrailleMainFct.TEXT

        self.mainFunctionChanged = Signal(EnBrailleMainFct)
    
    @property
    def mainFunction(self) -> EnBrailleMainFct:
        return self._mainFunction
    
    @mainFunction.setter
    def mainFunction(self, value: EnBrailleMainFct) -> None:
        if self._mainFunction != value:
            self._mainFunction = value
            self.mainFunctionChanged.emit(value)