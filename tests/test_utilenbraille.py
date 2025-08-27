import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PySide6.QtGui import QGuiApplication

def gen_data() -> EnBrailleData:
    app = QGuiApplication([])
    data = EnBrailleData(app)
    return data