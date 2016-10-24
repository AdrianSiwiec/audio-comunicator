#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import wave

import pulseaudio as pa
import numpy as np

sample_map = {
    1 : pa.SAMPLE_U8,
    2 : pa.SAMPLE_S16LE,
    4 : pa.SAMPLE_S32LE,
}
sample_type = {
    1 : np.uint8,
    2 : np.int16,
    4 : np.int32,
}

try:
    wav = wave.open(sys.argv[1], 'r')
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams() 
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=sample_map[sampwidth], rate=framerate, channels=nchannels) as player:
        while True:
            frames = wav.readframes(100)
            frames = np.fromstring(frames, dtype=sample_type[sampwidth]).astype(np.float)
            if len(frames) == 0:
                break
            player.write(frames)
        player.drain()
finally:
    wav.close()
