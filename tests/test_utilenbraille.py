from enbraille_data import EnBrailleData
from PySide6.QtGui import QGuiApplication

def gen_data() -> EnBrailleData:
    app = QGuiApplication([])
    data = EnBrailleData(app)
    return data