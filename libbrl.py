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
        louis.liblouis.lou_listTables.restype = ctypes.POINTER(ctypes.c_char_p)
        table_list_ptr = louis.liblouis.lou_listTables()

        # Convert the C string array to a Python list of strings
        i = 0
        while table_list_ptr[i] is not None:
            list_path = ctypes.string_at(table_list_ptr[i]).decode("utf-8")
            table_list_ptr[i].free()
            
            if list_path.find('de') != -1:
                table_filename = os.path.basename(list_path)    
                
                print((table_filename, check_result))
            i += 1

        table_list_ptr.free()
        raise Exception()

    def translate(self, text: str, table: str) -> str:
        pass
