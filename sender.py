import sys
from encoder import encode
from audioPlayer import playBitarray

#Functions at the top are higher-level and use functions at the bottom
#with exception to main function call which is at the bottom


def send(source, destination, freq0, freq1, bitsPerSecond, data):
    msg = encode(source, destination, data)

    bitTime = 1.0 / bitsPerSecond

    playBitarray(msg, freq0, freq1, bitTime)


msg = ""
for i in range(len(sys.argv)):
    if (i > 6): msg += " "
    if (i >= 6): msg += sys.argv[i]

send(int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[1]), msg)
