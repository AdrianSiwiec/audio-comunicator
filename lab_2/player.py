#!/usr/bin/env python

import sys
import pulseaudio as pa
from decimal import Decimal
import math
import numpy as np

freq = sys.argv[1]
time = int(sys.argv[2])

sampleFormat = 3
scale = 25000
framerate = 44100
channels = 1
batchSize = 100

sinusLength = float(framerate) / float(freq)

samples = [None] * batchSize

with pa.simple.open(
        direction = pa.STREAM_PLAYBACK, format = sampleFormat, rate = framerate, channels = channels) as player:
    for i in range(time * framerate):
        samples[i % batchSize] = int(math.sin(i / sinusLength * 2 * math.pi) * scale)
        if ((i + 1) % batchSize == 0):
            player.write(samples)
    player.drain()
