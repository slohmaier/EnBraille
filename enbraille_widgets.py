from typing import Optional
from PySide6.QtWidgets import QComboBox, QWidget
from libbrl import libbrlImpl

class EnBrailleTableComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._libbrl = libbrlImpl()
        print(self._libbrl.listTables())
        
