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
import logging
import sys
import os
from argparse import ArgumentParser
from PySide6.QtCore import Qt, QTranslator, QLocale
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from enbraille_gui import EnBrailleWindow
from enbraille_data import EnBrailleData
import tools.translation_helper as translation_helper

if __name__ == "__main__":
    logLevel = logging.INFO

    parser = ArgumentParser()

    parser.add_argument("-d", '--debug', action='store_true', help='activate debug logging')
    parser.add_argument('-r', '--reset', action='store_true', help='reset settings to default values')
    parser.add_argument('-l', '--language', help='set application language (e.g., de, en)')

    args = parser.parse_args()

    if args.debug:
        logLevel = logging.DEBUG

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)

    import resources.enbraille_resources as _

    app = QApplication(sys.argv)
    app.setApplicationName("EnBraille")
    app.setOrganizationName("slohmaier")
    app.setOrganizationDomain("slohmaier.de")
    app.setApplicationVersion("0.1.0")
    
    # Setup translations using our Python-based system
    # Determine language
    if args.language:
        locale = args.language
    else:
        # Use system locale
        locale = translation_helper.get_system_language()
    
    # Load translations
    if translation_helper.load_translations(locale):
        logging.info(f"Loaded translations for language: {locale}")
        # Patch Qt's tr() method to use our translation system
        if translation_helper.patch_qt_tr():
            logging.info("Successfully patched Qt translation system")
        else:
            logging.warning("Failed to patch Qt translation system")
    else:
        logging.info(f"No translations found for language: {locale}, using English")
    
    embrailledata = EnBrailleData(app)
    if args.reset:
        embrailledata.resetSettings()   
    enrailleWindow = EnBrailleWindow(data=embrailledata)
    enrailleWindow.show()

    sys.exit(app.exec())