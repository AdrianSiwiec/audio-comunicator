from encoder import decodeInt, decodeMsg
import pulseaudio as pa
import numpy

from bitarray import bitarray

_debug = True


def receive(f0, f1, bitTime):
    if _debug: print("Receiving: freq0 = " + str(f0) + ", freq1 = " + str(f1) + ", bitTime = " + str(bitTime))
    precision = 5
    noiseRatio = 8
    guesses = [0] * precision
    ratio = [0] * precision

    (nchannels, sampformat, framerate) = (1, pa.SAMPLE_S16LE, 44100)

    with pa.simple.open(
            direction = pa.STREAM_RECORD, format = sampformat, rate = framerate, channels = nchannels) as recorder:

        try:
            while (True):
                prevGuesses = list(guesses)
                prevRatio = list(ratio)
                for i in range(precision):
                    (guesses[i], ratio[i]) = sense(bitTime, noiseRatio, recorder, _debug)
                    sense(bitTime / float(precision), noiseRatio, recorder, False)
                for i in range(precision):
                    if isMatch(guesses[i], ratio[i], prevGuesses[i], prevRatio[i]):
                        raise StopIteration

        except StopIteration:
            pass

        timeWindow = 0
        for i in range(precision):
            if ((guesses[i] == freq0 or guesses[i] == freq1) and ratio[i] > ratio[timeWindow]):
                timeWindow = i

        if _debug: print("BRIAN, WE GOT SOMETHING!")

        prevBit = False
        bit = False
        while (True):
            prevBit = bit
            (freq, ratio) = sense(bitTime, 0, recorder, _debug)
            if (freq == freq0): bit = False
            elif (freq == freq1): bit = True
            else: raise Exception
            if (bit and prevBit):
                break

        if _debug: print("I hereby inform you that preamble has finished")

        to = listenForBytes(6, bitTime, f0, f1, recorder)
        lastbitTo = to[-1]
        to = decodeInt(to, True)
        if _debug: print("TO: " + str(to))

        frm = listenForBytes(6, bitTime, f0, f1, recorder)
        lastbitFrom = frm[-1]
        frm = decodeInt(frm, lastbitTo)
        if _debug: print("FROM: " + str(frm))

        ln = listenForBytes(2, bitTime, f0, f1, recorder)
        lastbitLn = ln[-1]
        ln = decodeInt(ln, lastbitFrom)
        if _debug: print("LEN: " + str(ln))

        msg = listenForBytes(ln, bitTime, f0, f1, recorder)
        lastbitMsg = msg[-1]
        msg = decodeMsg(msg, lastbitLn)
        if _debug: print("MSG: " + msg)

        crc = listenForBytes(3, bitTime, f0, f1, recorder)
        crc = decodeInt(crc, lastbitMsg)
        #checkCrc()


def listenForBytes(ln, bitTime, f0, f1, recorder):
    ans = bitarray()
    for i in range(ln * 8 / 4 * 5):
        (freq, ratio) = sense(bitTime, 0, recorder, _debug)
        if (freq == freq0): bit = False
        elif (freq == freq1): bit = True
        else: raise Exception
        ans.append(bit)

    return ans


def isMatch(g, r, pg, pr):
    return g == freq0 or g == freq1


def isFreq(freq1, freq2):
    return abs(freq1 - freq2) < 5


def sense(time, noiseRatio, recorder, _debug):
    samples = []

    nframes = int(time * recorder.rate)
    count = 0
#    samples = recorder.read(nframes)
    while count < nframes:
        data = recorder.read(10)
        count += len(data)
        samples.extend(data)

    #if _debug: print( str(nframes) + ":" + str(len(samples)))

    trans = numpy.fft.fft(samples)
    trans = trans[:len(trans) / 2]

    goodRange = 3

    f0 = getMaxOverRange(trans, freq0, goodRange)
    f1 = getMaxOverRange(trans, freq1, goodRange)

    fNoise = 0

    for i in range(len(trans)):
        if (not isInGoodRange(i, goodRange)):
            fNoise = max(fNoise, abs(trans[i]))

    ans = 0
    for i in range(len(trans)):
        if abs(trans[i]) > abs(trans[ans]):
            ans = i
            
    #if _debug: print("Noise Ratio: " + str(max(f0, f1) / fNoise) + " Max: " + str(ans))

    if (max(f0, f1) / fNoise < noiseRatio):
        return (0, 0)

    (stronger, weaker) = (f0, f1) if f0 > f1 else (f1, f0)

    #if _debug: print("Ratio: " + str(stronger / weaker))

    return (freq0 if f0 > f1 else freq1, stronger / weaker)


def isInGoodRange(i, goodRange):
    return abs(freq0 - i) <= goodRange or abs(freq1 - i) <= goodRange


def getMaxOverRange(arr, val, rng):
    ret = abs(arr[val])
    for i in range(rng + 1):
        ret = max(ret, abs(arr[val + i]))
        ret = max(ret, abs(arr[val - i]))
    return ret


import sys
freq0 = int(sys.argv[2])
freq1 = int(sys.argv[3])
freq0/=5
freq1/=5
bitsPerSecond = float(sys.argv[1])
receive(freq0, freq1, 1.0 / bitsPerSecond)

#(nchannels, sampwidth, sampformat, framerate) = (1, 2, pa.SAMPLE_S16LE, 44100)
#with pa.simple.open(
#        direction = pa.STREAM_RECORD, format = sampformat, rate = framerate, channels = nchannels) as recorder:
#    sense(1, 1, recorder)
