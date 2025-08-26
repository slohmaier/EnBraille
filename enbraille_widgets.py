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
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QWidget
from libbrl import libbrlImpl
from enbraille_data import EnBrailleData

class EnBrailleTableComboBox(QComboBox):
    def __init__(self, data: EnBrailleData, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.data = data

        self._libbrl = libbrlImpl()
        self._tables = self._libbrl.listTables()
        
        # Set accessibility properties
        self.setAccessibleName("Braille Translation Table")
        self.setAccessibleDescription("Select a braille translation table for converting text to braille")
        
        # Add empty item first
        self.addItem('', '')
        self.setItemData(0, "No table selected", Qt.ToolTipRole)
        
        # Add all available tables with descriptions
        for table in sorted(self._tables.keys()):
            table_filename = self._tables[table]
            self.addItem(table, table_filename)
            # Add tooltip for better accessibility
            item_index = self.count() - 1
            self.setItemData(item_index, f"Braille table: {table}", Qt.ToolTipRole)

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
