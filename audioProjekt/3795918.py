#!/usr/bin/env python

import sys
import wave

import pulseaudio as pa
import numpy

(nchannels, sampwidth, sampformat, framerate, length) = (1, 2, pa.SAMPLE_S16LE, 44100, float(sys.argv[1]))

samples = []

with pa.simple.open(
        direction = pa.STREAM_RECORD, format = sampformat, rate = framerate, channels = nchannels) as recorder:

    nframes = int(length * recorder.rate)
    count = 0
    while count < nframes:
        data = recorder.read(min(100,nframes - count))
        count += len(data)
        samples.extend(data)

    trans = numpy.fft.fft(samples)
    trans = trans[:len(trans)/2]

    ans = 0
    for i in range(len(trans)):
        if abs(trans[i]) > abs(trans[ans]):
            ans = i

    print(int(ans / length))
