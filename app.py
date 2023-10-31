import speech_recognition as sr
from gtts import gTTS
import winsound
from pydub import AudioSegment
import pyautogui
import webbrowser
import pyttsx3
import os, sys
from PyQt5.QtWidgets import QLabel, QPushButton, QTextEdit, QStatusBar
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PIL import Image

os.environ["FFMPEG_PATH"] = "avconv"

# initialize speech engine
engine = pyttsx3.init()


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.img = None
        uic.loadUi("va.ui", self)

        self.label = self.findChild(QLabel, "label")
        self.textEdit = self.findChild(QTextEdit, "textEdit")
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.statusbar = self.findChild(QStatusBar, "statusbar")

        self.pushButton.clicked.connect(self.answer)

        self.show()
        self.tasks = []
        self.listeningToTask = False

    def answer(self):
        global tasks
        global listeningToTask

        self.speak('hello, I am listening for your command')

        while True:
            command = self.listen_for_command()

            if command:
                if self.listeningToTask:
                    self.tasks.append(command)
                    self.listeningToTask = False
                    self.respond("Adding " + command + " to your task list. You have " + str(
                        len(self.tasks)) + " currently in your list.")
                elif "add a task" in command:
                    listeningToTask = True
                    self.respond("Sure, what is the task?")
                elif "list tasks" in command:
                    self.respond("Sure. Your tasks are:")
                    for task in self.tasks:
                        self.respond(task)
                elif "take a screenshot" in command:
                    pyautogui.screenshot("screenshot.png")
                    self.respond("I took a screenshot for you.")
                    self.img = Image.open("screenshot.png")
                    self.img.show()
                elif "open chrome" in command:
                    self.respond("Opening Chrome.")
                    webbrowser.open("https://www.google.com")
                elif "exit" in command:
                    self.respond("Goodbye!")
                    break
                else:
                    self.respond("Sorry, I'm not sure how to handle that command.")

    def speak(self, word):
        engine.setProperty('rate', 135)
        engine.setProperty('volume', 0.8)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)

        engine.say(str(word))
        engine.runAndWait()
        engine.stop()

    def listen_for_command(self):
        recognizer = sr.Recognizer()
        self.statusbar.showMessage("listening...")
        print("listening...")

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            self.statusbar.showMessage("waiting...")
            print("waiting...")
            self.speak('I am computing an answer for your request. i will be done soon')

        try:
            command = recognizer.recognize_google(audio)
            self.textEdit.append("You said: " + command)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            self.textEdit.append("Could not understand audio. Please try again.")
            self.statusbar.showMessage("error...")
            print("Could not understand audio. Please try again.")
            return None
        except sr.RequestError:
            self.textEdit.append("Unable to access the Google Speech Recognition API.")
            self.statusbar.showMessage("error...")
            print("Unable to access the Google Speech Recognition API.")
            return None

    def respond(self, response_text):
        self.textEdit.append(response_text)
        print(response_text)
        tts = gTTS(text=response_text, lang='en')
        tts.save("response.mp3")
        sound = AudioSegment.from_mp3("response.mp3")
        sound.export("response.wav", format="wav")
        winsound.PlaySound("response.wav", winsound.SND_FILENAME)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())