import io
import zlib

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
        self.auto_de_compress_checkbox = QCheckBox("Auto compress/decompress")
        self.status_bar = QStatusBar()
        self.text = QLabel("No file chosen!")
        self.fname = ""

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.encrypt_button)
        self.layout.addWidget(self.decrypt_button)
        self.layout.addWidget(self.auto_de_compress_checkbox)
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

        input_data = io.BytesIO(bytes(open(self.fname, 'r').read(), 'utf-8'))
        output_data = io.BytesIO()
        if self.auto_de_compress_checkbox.isChecked():
            input_data = io.BytesIO(zlib.compress(input_data.getvalue()))

        output_filename = self.fname.split('.')[0] + '.aes'
        bufferSize = 64 * 1024
        pyAesCrypt.encryptStream(input_data, output_data, password, bufferSize)
        output_file = open(output_filename, 'wb')
        output_file.write(output_data.getvalue())

        self.status_bar.showMessage("Done. output: " + output_filename)

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

        input_data = io.BytesIO(open(self.fname, 'rb').read())
        output_data = io.BytesIO()

        output_filename = self.fname.split('.')[0] + '.txt'
        output_file = open(output_filename, 'w')
        bufferSize = 64 * 1024
        try:
            pyAesCrypt.decryptStream(input_data, output_data, password, bufferSize, len(input_data.getvalue()))
        except ValueError:
            self.status_bar.showMessage("Wrong password")
            return

        if self.auto_de_compress_checkbox.isChecked():
            output_data = io.BytesIO(zlib.decompress(output_data.getvalue()))

        output_file.write(str(output_data.getvalue().decode('utf-8')))
        self.status_bar.showMessage("Done. output: " + output_filename)
