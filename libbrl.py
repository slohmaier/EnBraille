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
import ctypes
import logging
import os
from enum import Enum

class libbrlImpls(Enum):
    LOUIS = 1

class libbrlInterface:
    def listTables(self) -> dict[str, str]:
        raise NotImplementedError()
    
    def translate(self, text: str, table: str) -> str:
        raise NotImplementedError()


def libbrlImpl(impl: libbrlImpls = libbrlImpls.LOUIS) -> libbrlInterface:
    if impl == libbrlImpls.LOUIS:
        return libbrlLouis()
    else:
        raise NotImplemented()

import louis

class libbrlLouis(libbrlInterface):
    def __init__(self) -> None:
        super().__init__()
        self._tables = None
    
    def listTables(self) -> dict[str, str]:
        if self._tables is None:
            louis.liblouis.lou_listTables.restype = ctypes.POINTER(ctypes.c_char_p)
            table_list_ptr = louis.liblouis.lou_listTables()

            self._tables: dict[str, str] = {}

            # Convert the C string array to a Python list of strings
            i = 0
            while table_list_ptr[i] is not None:
                table_item_ptr = table_list_ptr[i]
                list_path = ctypes.string_at(table_item_ptr).decode("utf-8")
                
                table_filename = os.path.basename(list_path)    
                with open(table_item_ptr, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# liblouis: '):
                        table_name = first_line.split(':', 1)[1].strip()
                        self._tables[table_name] = table_filename
                
                i += 1

            #TODO: Free?
        return self._tables

    def translate(self, text: str, table: str) -> str:
        if self._tables is None:
            self._tables = self.listTables()

        table_name = None
        if table in self._tables:
            table_name = self._tables[table]
        else:
            if table in self._tables.values():
                table_name = table
        
        if table_name is None:
            raise ValueError(f'Unknown table {table}')
        
        logging.debug('libbrlLouis.translate: %s with table %s', text, table_name)
        return louis.translateString([table_name], text)
