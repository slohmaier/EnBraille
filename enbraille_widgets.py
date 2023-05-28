from typing import Optional
from PySide6.QtWidgets import QComboBox, QWidget
import louis

class EnBrailleTableComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # add all tables from louis to the combobox
        import ctypes

        # Load the LibLouis library
        liblouis = louis.liblouis

        # Declare the return type of louis_listTables as POINTER(c_char_p)
        liblouis.lou_listTables.restype = ctypes.POINTER(ctypes.c_char_p)

        # Call the louis_listTables function
        table_list_ptr = liblouis.lou_listTables()

        # Convert the C string array to a Python list of strings
        table_list = []
        i = 0
        while table_list_ptr[i] is not None:
            table_list.append(ctypes.string_at(table_list_ptr[i]).decode("utf-8"))
            i += 1

        # Free the memory allocated for the C string array
        #TODO: liblouis.lou_freeList(table_list_ptr)

        # Print the list of tables
        print(table_list)

        raise Exception(louis.liblouis.lou_findTables('*'))
        for table in louis.getInstalledTables():
            self.addItem(table)
