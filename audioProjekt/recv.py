from encoder import decodeInt, decodeMsg, decodeFromBitarray
import pulseaudio as pa
import numpy

from bitarray import bitarray

_debug = True


def receive(f0, f1, bitsPerSecond):
    if _debug:
        print("Receiving: freq0 = " + str(f0) + ", freq1 = " + str(f1) + ", bitsPerSecond = " + str(bitsPerSecond))
    precision = 6  #should be even, or change isMatch
    noiseRatio = 2
    guesses = [0] * precision
    ratio = [0] * precision

    (nchannels, sampformat, framerate) = (1, pa.SAMPLE_S16LE, 44100)
    samplesPerBit = framerate / bitsPerSecond
    if _debug: print(str(samplesPerBit))

    with pa.simple.open(
            direction = pa.STREAM_RECORD, format = sampformat, rate = framerate, channels = nchannels) as recorder:

        try:
            while (True):
                prevGuesses = list(guesses)
                prevRatio = list(ratio)
                for i in range(precision):
                    (guesses[i], ratio[i]) = sense(samplesPerBit, noiseRatio, recorder, _debug)
                    sense(samplesPerBit / precision, 1, recorder, 0)
                for i in range(precision):
                    if isMatch(guesses[i], ratio[i], prevGuesses[i], prevRatio[i]):
                        raise StopIteration

        except StopIteration:
            pass

        timeWindow = 0
        for i in range(precision):
            if ((guesses[i] == freq0 or guesses[i] == freq1) and ratio[i] > ratio[timeWindow]):
                timeWindow = i

        sense(samplesPerBit / precision * timeWindow, 1, recorder, 0)

        if _debug: print("BRIAN, WE GOT SOMETHING!")

        prevBit = False
        bit = False
        while (True):
            prevBit = bit
            (freq, ratio) = sense(samplesPerBit, 0, recorder, _debug)
            if (freq == freq0):
                bit = False
            elif (freq == freq1):
                bit = True
            else:
                raise Exception
            if (bit and prevBit):
                break

        if _debug: print("I hereby inform you that preamble has finished")

        wholeMessage = bitarray()

        to = listenForBytes(6, samplesPerBit, f0, f1, recorder)
        wholeMessage.extend(to)
        lastbitTo = to[-1]
        to = decodeInt(to, True)
        print("TO: " + str(to))

        frm = listenForBytes(6, samplesPerBit, f0, f1, recorder)
        wholeMessage.extend(frm)
        lastbitFrom = frm[-1]
        frm = decodeInt(frm, lastbitTo)
        print("FROM: " + str(frm))

        ln = listenForBytes(2, samplesPerBit, f0, f1, recorder)
        wholeMessage.extend(ln)
        lastbitLn = ln[-1]
        ln = decodeInt(ln, lastbitFrom)
        print("LEN: " + str(ln))

        msg = listenForBytes(ln, samplesPerBit, f0, f1, recorder)
        wholeMessage.extend(msg)
        lastbitMsg = msg[-1]
        msg = decodeMsg(msg, lastbitLn)
        print("MSG: " + msg)

        crc = listenForBytes(4, samplesPerBit, f0, f1, recorder)
        wholeMessage.extend(crc)

        decodedMessage = decodeFromBitarray(wholeMessage)
        if(decodeMsg == None):
            print("Message Corrupted!")
        else:
            print("CRC OK")


def listenForBytes(ln, samplesPerBit, f0, f1, recorder):
    ans = bitarray()
    for i in range(ln * 8 / 4 * 5):
        (freq, ratio) = sense(samplesPerBit, 0, recorder, _debug)
        if (freq == freq0):
            bit = False
        elif (freq == freq1):
            bit = True
        else:
            raise Exception
        ans.append(bit)

    return ans


def isMatch(g, r, pg, pr):
    return (g == freq1 and pg == freq0) or (g == freq0 and pg == freq1)


def isFreq(freq1, freq2):
    return abs(freq1 - freq2) < 5


def sense(samplesPerBit, noiseRatio, recorder, _debug):
    if (samplesPerBit == 0):
        return (0, 0)
    samples = []

    count = 0
    samples = recorder.read(samplesPerBit)

    trans = numpy.fft.fft(samples)
    trans = trans[:len(trans) / 2]

    goodRange = 5

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

    if _debug: print("Noise Ratio: " + str(max(f0, f1) / fNoise) + " Max: " + str(ans))

    if (max(f0, f1) / fNoise < noiseRatio):
        return (0, 0)

    (stronger, weaker) = (f0, f1) if f0 > f1 else (f1, f0)

    #if _debug: print("Ratio: " + str(stronger / weaker))
    #if _debug: print(str((freq0 if f0 > f1 else freq1, stronger / weaker)))

    return (freq0 if f0 > f1 else freq1, stronger / weaker)


def isInGoodRange(i, goodRange):
    return abs(freq0 - i) <= goodRange or abs(freq1 - i) <= goodRange


def getMaxOverRange(arr, val, rng):
    ret = 0
    for i in range(rng + 1):
        if (val + i < len(arr)):
            ret = max(ret, abs(arr[val + i]))
        if (val - i < len(arr)):
            ret = max(ret, abs(arr[val - i]))
    return ret


import sys
bitsPerSecond = int(sys.argv[1])
freq0 = int(sys.argv[2]) / bitsPerSecond
freq1 = int(sys.argv[3]) / bitsPerSecond
receive(freq0, freq1, bitsPerSecond)
