'''

'''

import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from enbraille import EnBrailleWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("EnBraille")
    app.setOrganizationName("slohmaier")
    app.setOrganizationDomain("slohmaier.de")
    app.setApplicationVersion("0.1.0")
    
    enrailleWindow = EnBrailleWindow()
    enrailleWindow.show()

    sys.exit(app.exec())