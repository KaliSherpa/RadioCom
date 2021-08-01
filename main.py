from string import ascii_letters, digits
from base64 import b64encode, b64decode
from threading import Thread
from scipy.io import wavfile
from time import sleep
import numpy as np
import winsound

text_tones = {l:t*50+300 for t, l in enumerate(ascii_letters + digits + '+/=')}
tone_delay = 0.1

def message(text, delay):
    text = b64encode(text.encode()).decode()
    current = ''
    for char in text:
        current += char
        try:
            print('\r' + b64decode(current.encode()).decode(), end='', flush=True)
        except:
            print('█', end='', flush=True)
        sleep(delay)
    print()

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

while True:
    text = input('> ')
    wavfile.write('temp_file.wav', rate=44100, data=tone_encode(text).astype(np.int16))
    Thread(target=winsound.PlaySound, args=('temp_file.wav', winsound.SND_FILENAME)).start()
    sleep(0.3)
    message(text, tone_delay)