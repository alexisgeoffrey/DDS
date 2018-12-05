from tkinter import *
from functools import partial
import os
import glob
from win32 import win32file
from win32 import win32event
import win32con
import pyaudio
import wave
import sys
import threading
import queue

root = Tk()
root.geometry("1050x670")
root.title("Distress Monitor")

def fileListener():
    filepath = os.path.abspath("C:\DDSFTP")
    #filepath = os.path.abspath(".")
    changehandle = win32file.FindFirstChangeNotification(filepath, 0, win32con.FILE_NOTIFY_CHANGE_FILE_NAME)
    try:
        while 1:
            result = win32event.WaitForSingleObject(changehandle, 500)
            if result == win32con.WAIT_OBJECT_0:
                files = glob.glob("C:\DDSFTP\*.wav")
                files.sort(key=os.path.getmtime, reverse = True)
                print(files[0])
                sentpath = files[0]
                newbox = AlertBox(sentpath)
                newbox.alertBox()

                win32file.FindNextChangeNotification (changehandle)
    finally:
        win32file.FindCloseChangeNotification(changehandle)
    
def hello():
    print('hello')

def disable_event():
    pass

class AlertBox():
    def __init__(self, filepath):
        self.filepath = filepath
        self.q = queue.Queue()
        self.playing = False
        #self.audioThread = None
        
    def alertBox(self):
        #playAudio_witharg = partial(playAudio, filepath, q)
        #audioThread = threading.Thread(target=self.playAudio)
        
        alertSound = threading.Thread(target=self.alertSound)
        alertSound.start()
        alertbox = Toplevel()
        alertbox.protocol("WM_DELETE_WINDOW", disable_event)
        alertbox.title = "Alert! Distress Signal Detected"
        message = "ALERT! Distress Signal Detected"
        Label(alertbox, text=message, font="Times 24").grid(row=0, column=0)
        Button(alertbox, text="Play", font="Times 16", command=self.startThread).grid(row=1, column=0)
        Button(alertbox, text="Stop", font="Times 16", command=self.stopAudio).grid(row=2, column=0)
        Button(alertbox, text="Positive", font="Times 16", command=alertbox.destroy).grid(row=1, column=1)
        Button(alertbox, text="Unsure", font="Times 16", command=alertbox.destroy).grid(row=2, column=1)
        Button(alertbox, text="False Positive", font="Times 16", command=alertbox.destroy).grid(row=3, column=1)
        #alertbox.grab_set()
        x = root.winfo_width() / 2 - 150
        y = root.winfo_height() / 2 - 150
        w = 800
        h = 200
        alertbox.geometry("%dx%d+%d+%d" % (w, h, x, y))
        alertbox.configure(bg="Red")

    def alertSound(self):
        wf = wave.open("./airhorn.wav", 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(1024)        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def startThread(self):
        if(self.playing == False):
            self.audioThread = threading.Thread(target=self.playAudio)
            self.audioThread.start()
            self.playing = True
        

    def playAudio(self):
        wf = wave.open(self.filepath, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(1024)
            #print(self.q.get(False))
            try:
                if (self.q.get(False) == 'stop'):
                    break
            except queue.Empty:
                pass
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stopAudio(self):
        if(self.playing == True):
            self.q.put('stop')
            self.playing = False
            self.audioThread.join()

    
Label(root, text="Reports:", font="Times 28").grid(row=1, column=1)
Label(root, text="Generate:", font="Times 22").grid(row=2, column=2)
buttons=[]
for loop in range(4,7):
    buttons.append(Button(root, text="Option "+str(loop-3), font="Times 16", command=hello))
    buttons[-1].grid(row=loop, column=3, padx=10, pady=10)    
Label(root, text="View Previous Reports:", font="Times 22").grid(row=7, column=2)
for loop in range(8,11):
    buttons.append(Button(root, text="Report "+str(loop-7), font="Times 16", command=hello))
    buttons[-1].grid(row=loop, column=3, padx=10, pady=10)    

Label(root, text="Alerts:", font="Times 28").grid(row=1, column=5)

#distressroot = Frame(root, bg = 'yellow')
#distressroot.grid(row=3, column=5, rowspan=3, columnspan=3)
#Label(distressroot, text="Distress Call Detected:", font="Times 28", bg = 'yellow').grid(row=2, column=1, columnspan=3)
#buttons.append(Button(distressroot, text="Show", font="Times 16", command=alertBox))
#buttons.append(Button(distressroot, text="Listen", font="Times 16", command=hello))
#buttons[-1].grid(row=3, column=2, padx=10, pady=10)    
#buttext=['Real','Unsure','False Alarm']
##for loop in range(1,2):
##    buttons.append(Button(distressroot, text="Show", font="Times 16", command=hello))
##    buttons[-1].grid(row=4, column=2, padx=10, pady=10)
listenThread = threading.Thread(target=fileListener)
listenThread.start()
root.mainloop()
