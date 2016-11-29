import sys
import pulseaudio as pa
import numpy
from bitarray import bitarray

from decoder import decodeInt, decodeString, decodeFromBitarray
from encoder import getCrc

_debug = False

#Functions at the top are higher-level and use functions at the bottom
#with exception to main function call which is at the bottom


def receive(f0, f1, bitsPerSecond):
    if _debug:
        print("Receiving: freq0 = " + str(f0) + ", freq1 = " + str(f1) + ", bitsPerSecond = " + str(bitsPerSecond))

    precision = 6  #should be even, or change isMatch #will try to match frame in 6 places
    noiseRatio = 2  #expected frequency to noise strength ratio, used by function sense

    guesses = [0] * precision
    ratio = [0] * precision

    (nchannels, sampformat, framerate) = (1, pa.SAMPLE_S16LE, 44100)
    samplesPerBit = framerate / bitsPerSecond

    if _debug: print(str(samplesPerBit))

    with pa.simple.open(
            direction = pa.STREAM_RECORD, format = sampformat, rate = framerate, channels = nchannels) as recorder:
        try:
            while (True):  #tries to match the frame within one of 6 positions, exits when isMatch() returns true
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

        if _debug: print("BRIAN, WE GOT SOMETHING!")

        timeFrame = 0
        for i in range(precision):  #chooses best time frame based on ratio[]
            if ((guesses[i] == freq0 or guesses[i] == freq1) and ratio[i] > ratio[timeFrame]):
                timeFrame = i

        sense(samplesPerBit / precision * timeFrame, 1, recorder, 0)  #listens for enough time to match with time Frame

        prevBit = False
        bit = False
        while (True):  #waits for end of preamble, recognized by double one bit
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
        print("TO: " + str(to))  #prints data right after it comes for cool effect

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
        msg = decodeString(msg, lastbitLn)
        print("MSG: " + msg)

        crc = listenForBytes(4, samplesPerBit, f0, f1, recorder)
        crc = decodeInt(crc, lastbitMsg)

        decodedMessage = decodeFromBitarray(wholeMessage)
        if (decodedMessage == None or crc != getCrc(decodedMessage)):
            print("Message Corrupted!")
        else:
            print("CRC OK")


#listens for ln bits and returns bitarray containing those, or throws Exception if there is corruption
def listenForBytes(ln, samplesPerBit, f0, f1, recorder):
    ans = bitarray()
    for i in range(ln * 8 / 4 * 5):

        #required noise ratio for sense is 0, because we hope to get expected sound
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


#listens for one bit and returns if it was freq0 or freq1 and ratio of stronger of these two to weaker
def sense(samplesPerBit, noiseRatio, recorder, _debug):
    if (samplesPerBit == 0):
        return (0, 0)
    samples = []

    count = 0
    samples = recorder.read(samplesPerBit)

    trans = numpy.fft.fft(samples)
    trans = trans[:len(trans) / 2]

    goodRange = 5  #frequencies within this range of frequency we expect are considered to be the same

    f0 = getMaxOverRange(trans, freq0, goodRange)  #f0 means "stregth" of bit 0
    f1 = getMaxOverRange(trans, freq1, goodRange)

    fNoise = 0  # "strength" of noise

    for i in range(len(trans)):
        if (not isInGoodRange(i, goodRange)):
            fNoise = max(fNoise, abs(trans[i]))

    maxi = 0  # the stronges sound
    for i in range(len(trans)):
        if abs(trans[i]) > abs(trans[maxi]):
            maxi = i

    if _debug: print("Noise Ratio: " + str(max(f0, f1) / fNoise) + " Max: " + str(maxi))

    if (max(f0, f1) / fNoise < noiseRatio):  #if ratio of expected sound to noise is too big we treat this bit as noise
        return (0, 0)

    (stronger, weaker) = (f0, f1) if f0 > f1 else (f1, f0)

    return (freq0 if f0 > f1 else freq1, stronger / weaker)  #returns stronger frequency and its ratio to weaker


def isInGoodRange(i, goodRange):  #checks if i is within goodRange of either freq0 or freq1
    return abs(freq0 - i) <= goodRange or abs(freq1 - i) <= goodRange


def getMaxOverRange(arr, val, rng):  #get max strength over range of radius rng and center in val
    ret = 0
    for i in range(rng + 1):
        if (val + i < len(arr)):
            ret = max(ret, abs(arr[val + i]))
        if (val - i < len(arr)):
            ret = max(ret, abs(arr[val - i]))
    return ret


bitsPerSecond = int(sys.argv[1])
freq0 = int(sys.argv[2]) / bitsPerSecond
freq1 = int(sys.argv[3]) / bitsPerSecond
try :
    receive(freq0, freq1, bitsPerSecond)
except Exception:
    print("Message Corrupted")
