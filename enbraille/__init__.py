from PySide6.QtWidgets import QMainWindow, QGridLayout, QLabel

class EnBrailleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EmBraille")
        self.resize(800, 600)

        # set qgridlayout as main layout
        self._gridLayout = QGridLayout()
        self.setLayout(self._gridLayout)
        self._gridLayout.addWidget(QLabel("Hello World!"), 0, 0)
