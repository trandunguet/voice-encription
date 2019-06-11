from PySide2.QtWidgets import *
from PySide2.QtCore import Slot, Qt, QThread, Signal

import speech_recognition as sr


class Recognizer(QThread):
    finished = Signal(str)

    def __init__(self):
        QThread.__init__(self)
        self.recognizer = sr.Recognizer()

    def run(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source, phrase_time_limit=3, timeout=7)
        
        result = ''
        try:
            result = self.recognizer.recognize_google(audio).lower()

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        self.finished.emit(result)
