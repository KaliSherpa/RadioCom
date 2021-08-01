from PyQt5 import QtCore, QtGui, QtWidgets
from string import ascii_letters, digits
from base64 import b64encode, b64decode
from threading import Thread
from scipy.io import wavfile
from time import sleep
import numpy as np
import winsound

text_tones = {l:t*50+300 for t, l in enumerate(ascii_letters + digits + '+/=')}
tone_delay = 0.1

def moveProgressBar(text, delay, progressBar):
    progressBar.setProperty("value", 0)
    text = b64encode(text.encode()).decode()
    current = ''
    for i in range(len(text)):
        progressBar.setProperty("value", 100 / len(text) * (i + 1))
        sleep(delay)

def combine(*arrays):
    out = []
    for array in arrays:
        out += list(array)
    return np.array(out)

def get_sine_wave(frequency, duration=tone_delay, sample_rate=44100, amplitude=4096):
    t = np.linspace(0, duration, int(sample_rate*duration))
    wave = amplitude*np.sin(2*np.pi*frequency*t)
    return wave

def pattern(*args):
    out = []
    for note in args:
        if type(note) == list and len(note) == 2:
            out.append(get_sine_wave(note[0], duration=note[1]))
        else:
            out.append(get_sine_wave(int(note)))
    return combine(*tuple([array for array in out]))

def tone_encode(data):
    tones = []
    data = b64encode(str(data).encode()).decode()
    for char in data:
        tones.append(text_tones[char])
    return pattern(*tuple(tones))

def transmit(text):
    wavfile.write('temp_file.wav', rate=44100, data=tone_encode(text).astype(np.int16))
    Thread(target=winsound.PlaySound, args=('temp_file.wav', winsound.SND_FILENAME)).start()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.send_info = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.send_info.setObjectName("send_info")
        self.gridLayout.addWidget(self.send_info, 3, 0, 1, 2)
        self.send_label = QtWidgets.QLabel(self.centralwidget)
        self.send_label.setAlignment(QtCore.Qt.AlignCenter)
        self.send_label.setObjectName("send_label")
        self.gridLayout.addWidget(self.send_label, 2, 0, 1, 2)
        self.received_info = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.received_info.setObjectName("received_info")
        self.gridLayout.addWidget(self.received_info, 1, 0, 1, 2)
        self.recv_label = QtWidgets.QLabel(self.centralwidget)
        self.recv_label.setAlignment(QtCore.Qt.AlignCenter)
        self.recv_label.setObjectName("recv_label")
        self.gridLayout.addWidget(self.recv_label, 0, 0, 1, 2)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 5, 0, 1, 2)
        self.transmit = QtWidgets.QPushButton(self.centralwidget)
        self.transmit.setObjectName("transmit")
        self.gridLayout.addWidget(self.transmit, 4, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def transmit_function(self):
        text = self.send_info.toPlainText()
        transmit(text)
        moveProgressBar(text, tone_delay, self.progressBar)            

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Tone Encoder"))
        self.send_label.setText(_translate("MainWindow", "Send Information"))
        self.recv_label.setText(_translate("MainWindow", "Received Information"))
        self.transmit.setText(_translate("MainWindow", "Transmit"))
        self.transmit.clicked.connect(self.transmit_function)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
