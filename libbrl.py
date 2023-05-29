import ctypes
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
                with open(table_item_ptr, 'r') as f:
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
        if not table in self._tables:
            table_name = table
        else:
            for name, filename in self._tables.items():
                if filename == table:
                    table_name = name
                    break
        if table_name is None:
            raise ValueError(f'Unknown table {table}')
        
        return louis.translateString([table_name], text)
