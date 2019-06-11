import sys
from PySide2.QtWidgets import *

from main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(500, 300)
    widget.show()

    sys.exit(app.exec_())
