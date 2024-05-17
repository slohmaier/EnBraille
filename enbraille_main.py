import logging
import sys
from argparse import ArgumentParser
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from enbraille_gui import EnBrailleWindow
from enbraille_data import EnBrailleData

if __name__ == "__main__":
    logLevel = logging.INFO

    parser = ArgumentParser()

    parser.add_argument("-d", '--debug', action='store_true', help='activate debug logging')
    parser.add_argument('-r', '--reset', action='store_true', help='reset settings to default values')

    args = parser.parse_args()

    if args.debug:
        logLevel = logging.DEBUG

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)

    import enbraille_resources as _

    app = QApplication(sys.argv)
    app.setApplicationName("EnBraille")
    app.setOrganizationName("slohmaier")
    app.setOrganizationDomain("slohmaier.de")
    app.setApplicationVersion("0.1.0")

    # activate dark-mode on windows
    if sys.platform == 'win32':
        import qdarktheme
        qdarktheme.setup_theme()
    
    embrailledata = EnBrailleData(app)
    if args.reset:
        embrailledata.resetSettings()   
    enrailleWindow = EnBrailleWindow(data=embrailledata)
    enrailleWindow.show()

    sys.exit(app.exec())