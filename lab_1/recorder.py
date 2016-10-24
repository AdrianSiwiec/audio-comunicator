#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import wave

import pulseaudio as pa

(nchannels, sampwidth, sampformat, framerate, length) = (2, 2, pa.SAMPLE_S16LE, 44100, 5.0)

nframes = int(length * framerate)

wav = wave.open(sys.argv[1], 'w')
try:
    wav.setnchannels(nchannels)
    wav.setsampwidth(sampwidth)
    wav.setframerate(framerate)
    count = 0
    with pa.simple.open(direction=pa.STREAM_RECORD, format=sampformat, rate=framerate, channels=nchannels) as recorder:
        while count < nframes:
            data = recorder.read(min(100,nframes-count))
            count += len(data)
            wav.writeframes(data)
finally:
    wav.close()
