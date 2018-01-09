
import rtmidi
import time

import pyaudio
import numpy as np
import matplotlib.pyplot as plt

import math

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

for a in midiout.get_ports():
    print(a)

midiout.open_port(1)


#exit()

def freqToNote(f):
    # 440 -> 69
    # 880 -> 81
    #1760 -> 93
    return math.floor(69+math.log(f/440,2)*12)

def playNoteOn(n):
    note_on = [0x90, n, 112] # channel 1, middle C, velocity 112
    midiout.send_message(note_on)
    
def playNoteOff(n):
    note_off = [0x80, n, 0]
    midiout.send_message(note_off)
    
def noteOn(n):
    playNoteOn(n)
    #playNoteOn(n+4)
    #playNoteOn(n+7)

def noteOff(n):
    playNoteOff(n)
    #playNoteOff(n+4)
    #playNoteOff(n+7)
    

    
midiout.send_message([0b11000000, 81])

np.set_printoptions(suppress=True) # don't use scientific notation

CHUNK = 4096 # number of data points to read at a time
RATE = 48000 # time resolution of the recording device (Hz)

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK) #uses default input device


lastNote = 0

# create a numpy array holding a single read of audio data
for i in range(10000): #to it a few times just to see
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    data = data * np.hanning(len(data)) # smooth the FFT by windowing data
    fft = abs(np.fft.fft(data).real)
    fft = fft[:int(len(fft)/2)] # keep only first half
    freq = np.fft.fftfreq(CHUNK,1/RATE)
    freq = freq[:int(len(freq)/2)] # keep only first half
    freqPeak = freq[np.where(fft==np.max(fft))[0][0]]+1
    
    note = freqToNote(freqPeak)
    
    #print("peak frequency: %d Hz, %d"%(freqPeak, note))
    aData = np.absolute(data)
    avab = np.mean(aData)
    #print(avab)
    
    if (avab > 600) :
        if (note != lastNote) :
            if (lastNote != 0) :
                noteOff(lastNote)
            noteOn(note)
        lastNote = note
    else:
        if (lastNote != 0) :
            noteOff(lastNote)
        lastNote = 0
    print (note)
    
    

    # uncomment this if you want to see what the freq vs FFT looks like
    #plt.plot(freq,fft)
    #plt.axis([0,4000,None,None])
    #plt.show()
    #plt.close()

# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()
del midiout







