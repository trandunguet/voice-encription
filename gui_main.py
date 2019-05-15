import sys
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QFileDialog,
                               QStatusBar)
from PySide2.QtCore import Slot, Qt

import speech_recognition as sr
import pyAesCrypt

class MyWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        
        self.recognizer = sr.Recognizer()

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

        self.status_bar.showMessage("Say the password")

        with sr.Microphone() as source:
            audio = self.recognizer.listen(source, phrase_time_limit=3, timeout=7)
        
        self.status_bar.showMessage("Recognizing voice ...")
        password = ""
        try:
            password = self.recognizer.recognize_google(audio).lower()
            self.status_bar.showMessage(password)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        if not password:
            self.status_bar.showMessage("Error: empty password")
            return

        self.status_bar.showMessage("Encrypting ...")
        output = self.fname.split('.')[0] + '.aes'
        bufferSize = 64 * 1024
        pyAesCrypt.encryptFile(self.fname, output, password, bufferSize)
        self.status_bar.showMessage("Done. output: " + output)

    @Slot()
    def decrypt(self):
        if not self.fname:
            return

        self.status_bar.showMessage("Say the password")

        with sr.Microphone() as source:
            audio = self.recognizer.listen(source, phrase_time_limit=3, timeout=7)
        
        self.status_bar.showMessage("Recognizing voice ...")
        password = ""
        try:
            password = self.recognizer.recognize_google(audio).lower()
            self.status_bar.showMessage(password)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        if not password:
            self.status_bar.showMessage("Error: empty password")
            return

        self.status_bar.showMessage("Decrypting ...")
        output = self.fname.split('.')[0] + '.txt'
        bufferSize = 64 * 1024
        try:
            pyAesCrypt.decryptFile(self.fname, output, password, bufferSize)
            self.status_bar.showMessage("Done. output: " + output)
        except ValueError:
            self.status_bar.showMessage("Wrong password")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(500, 300)
    widget.show()

    sys.exit(app.exec_())
