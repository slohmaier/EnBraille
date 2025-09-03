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
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QComboBox, QWidget
from libbrl import libbrlImpl
from enbraille_data import EnBrailleData
from braille_table_translations import BrailleTableTranslations

class EnBrailleTableComboBox(QComboBox):
    def __init__(self, data: EnBrailleData, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.data = data

        self._libbrl = libbrlImpl()
        self._tables = self._libbrl.listTables()
        
        # Set accessibility properties
        self.setAccessibleName(QCoreApplication.translate("EnBrailleTableComboBox", "Braille Translation Table"))
        self.setAccessibleDescription(QCoreApplication.translate("EnBrailleTableComboBox", "Select a braille translation table for converting text to braille"))
        
        # Add empty item first
        empty_text = QCoreApplication.translate("EnBrailleTableComboBox", "No table selected")
        self.addItem(empty_text, '')
        self.setItemData(0, empty_text, Qt.ToolTipRole)
        
        # Add all available tables with descriptions
        for table in sorted(self._tables.keys()):
            table_filename = self._tables[table]
            translated_name = self._translateTableName(table)
            self.addItem(translated_name, table_filename)
            # Add tooltip for better accessibility
            item_index = self.count() - 1
            tooltip = QCoreApplication.translate("EnBrailleTableComboBox", "Braille table: {0}").format(translated_name)
            self.setItemData(item_index, tooltip, Qt.ToolTipRole)
            # Store original table name for internal use
            self.setItemData(item_index, table, Qt.UserRole)

        self.table = self.data.textTable
    
    def _translateTableName(self, table_name: str) -> str:
        """Translate braille table names to German"""
        # Use the generated translations with fallback to original
        return BrailleTableTranslations.get_translated_name(table_name)
    
    @property
    def table(self) -> Optional[str]:
        if self.currentIndex() >= 0:
            # Return the original table name stored in UserRole
            return self.itemData(self.currentIndex(), Qt.UserRole)
        else:
            return None
    
    @table.setter
    def table(self, value: str) -> None:
        if value in self._tables:
            # Find item by original table name (stored in UserRole)
            for i in range(self.count()):
                if self.itemData(i, Qt.UserRole) == value:
                    self.setCurrentIndex(i)
                    break
        else:
            self.setCurrentIndex(0)  # Select empty item
    
    @property
    def tableFilename(self) -> Optional[str]:
        if self.currentIndex() >= 0:
            return self.itemData(self.currentIndex())
        else:
            return None
