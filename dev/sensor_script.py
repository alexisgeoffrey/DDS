#!/usr/bin/env python

import pyaudio
import wave
import datetime
import time
import threading
import os
from ftplib import FTP
from pydub import AudioSegment
    
def soundSend(filename, ftp):
    __VOL_THRESHOLD = -3
    sound = AudioSegment.from_file(filename, format="wav")
    #time.sleep(3)
    print(sound.max_dBFS)
    if(sound.max_dBFS > __VOL_THRESHOLD):
        file = open(filename,'rb')
        ftpCommand = "STOR " + filename
        ftp.storbinary(ftpCommand, file)
        file.close()
    os.remove(filename)

test = 0
ftp = FTP('192.168.43.153')
ftp.login("default")
while(test == 0):
    #test = 1
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    RECORD_SECONDS = 3
    #WAVE_OUTPUT_FILENAME = "quiet.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
    WAVE_OUTPUT_FILENAME =  date + '_Sensor1.wav' # name of .wav file

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    newThread = threading.Thread(target=soundSend, args=(WAVE_OUTPUT_FILENAME, ftp,))
    newThread.start()
