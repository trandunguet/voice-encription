from PySide2.QtWidgets import *
from PySide2.QtCore import Slot, Qt
import pyAesCrypt

from recognizer import Recognizer

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        
        self.browse_button = QPushButton("Choose file")
        self.encrypt_button = QPushButton("Encrypt")
        self.decrypt_button = QPushButton("Decrypt")
        self.status_bar = QStatusBar()
        self.text = QLabel("No file chosen!")
        self.fname = ""

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.encrypt_button)
        self.layout.addWidget(self.decrypt_button)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.status_bar)
        self.setLayout(self.layout)

        # Connecting the signal
        self.browse_button.clicked.connect(self.browse)
        self.encrypt_button.clicked.connect(self.encrypt)
        self.decrypt_button.clicked.connect(self.decrypt)

    @Slot()
    def browse(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file')[0]
        if self.fname:
            self.text.setText(self.fname)

    @Slot()
    def encrypt(self):
        if not self.fname:
            return

        self.recognizer_thread = Recognizer()
        self.recognizer_thread.finished.connect(self.repeat)
        self.status_bar.showMessage("Say the password")
        self.recognizer_thread.start()

    @Slot()
    def repeat(self, password):
        if not password:
            self.status_bar.showMessage("Error: empty password")
            return
        self.password = password
        self.recognizer_thread = Recognizer()
        self.recognizer_thread.finished.connect(self.do_encrypt)
        self.status_bar.showMessage("Your password is '" + password + "'. Repeat to confirm.")
        self.recognizer_thread.start()

    @Slot()
    def do_encrypt(self, password):
        if not password:
            self.status_bar.showMessage("Error: empty password")
            return

        if self.password != password:
            self.status_bar.showMessage("Error: confirm failed")
            return

        output = self.fname.split('.')[0] + '.aes'
        bufferSize = 64 * 1024
        pyAesCrypt.encryptFile(self.fname, output, password, bufferSize)
        self.status_bar.showMessage("Done. output: " + output)

    @Slot()
    def decrypt(self):
        if not self.fname:
            return

        self.recognizer_thread = Recognizer()
        self.recognizer_thread.finished.connect(self.do_decrypt)
        self.status_bar.showMessage("Say the password")
        self.recognizer_thread.start()

    @Slot()
    def do_decrypt(self, password):
        if not password:
            self.status_bar.showMessage("Error: empty password")
            return

        output = self.fname.split('.')[0] + '.txt'
        bufferSize = 64 * 1024
        try:
            pyAesCrypt.decryptFile(self.fname, output, password, bufferSize)
            self.status_bar.showMessage("Done. output: " + output)
        except ValueError:
            self.status_bar.showMessage("Wrong password")
