#!/usr/bin/env python

import sys
import pulseaudio as pa
from decimal import Decimal
import math
import numpy as np

sampleFormat = 3
scale = 25000
framerate = 44100
channels = 1
batchSize = 100


def playBitarray(array, f0, f1, bitTime):
    samples0 = getSamples(f0, bitTime)          #Can do better bu don't care
    samples1 = getSamples(f1, bitTime)

    with pa.simple.open(
            direction = pa.STREAM_PLAYBACK, format = sampleFormat, rate = framerate, channels = channels) as player:
        for b in array:
            player.write(samples1 if b else samples0)
            player.drain()


def getSamples(freq, time):
    sinusLength = float(framerate) / float(freq)
    size = int(time * framerate)
    samples = [None] * size
    for i in range(size):
        samples[i] = int(math.sin(i / sinusLength * 2 * math.pi) * scale)
    samples.append(0)
    return samples
