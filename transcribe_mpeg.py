#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess

SetLogLevel(0)

if not os.path.exists("model"):
    print ("Please download the model from https://github.com/alphacep/vosk-api/blob/master/doc/models.md and unpack as 'model' in the current folder.")
    exit (1)

sample_rate=8000
model = Model("model")
rec = KaldiRecognizer(model, sample_rate)

process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                            sys.argv[1],
                            '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                            stdout=subprocess.PIPE)

name = os.path.basename(sys.argv[1])
fileName = name + '.json'
file = open(f'newTranscribRes/{fileName}', "w")

file.write("[")

time = 0
while True:
    data = process.stdout.read(8000)
    time += 0.5 #4000/(8000)
    print ("processed time = " +  str(time/60) + " minutes")
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        #print(rec.Result())
        file.write(rec.Result())
        file.write(",")
    else:
        rec.PartialResult()

file.write(rec.FinalResult())
file.write("]")
file.close()
#print(rec.FinalResult())

