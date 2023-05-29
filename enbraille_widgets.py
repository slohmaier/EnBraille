from typing import Optional
from PySide6.QtWidgets import QComboBox, QWidget
from libbrl import libbrlImpl
from enbraille_data import EnBrailleData

class EnBrailleTableComboBox(QComboBox):
    def __init__(self, data: EnBrailleData, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.data = data

        self._libbrl = libbrlImpl()
        self._tables = self._libbrl.listTables()
        
        self.addItem('')
        for table in sorted(self._tables.keys()):
            table_filename = self._tables[table]
            self.addItem(table, table_filename)

        self.table = self.data.textTable
    
    @property
    def table(self) -> Optional[str]:
        if self.currentIndex() >= 0:
            return self.currentText()
        else:
            return None
    
    @table.setter
    def table(self, value: str) -> None:
        if value in self._tables:
            self.setCurrentText(value)
        else:
            self.setCurrentText('')
    
    @property
    def tableFilename(self) -> Optional[str]:
        if self.currentIndex() >= 0:
            return self.itemData(self.currentIndex())
        else:
            return None
