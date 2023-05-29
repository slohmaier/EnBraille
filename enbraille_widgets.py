from typing import Optional
from PySide6.QtWidgets import QComboBox, QWidget
from libbrl import libbrlImpl

class EnBrailleTableComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._libbrl = libbrlImpl()
        self._tables = self._libbrl.listTables()
        
        for table in sorted(self._tables.keys()):
            table_filename = self._tables[table]
            self.addItem(table, table_filename)
    
    @property
    def table(self) -> Optional[str]:
        if self.currentIndex() >= 0:
            return self.currentText()
        else:
            return None
    
    @table.setter
    def table(self, value: str) -> None:
        self.setCurrentText(value)
    
    @property
    def tableFilename(self) -> Optional[str]:
        if self.currentIndex() >= 0:
            return self.itemData(self.currentIndex())
        else:
            return None
