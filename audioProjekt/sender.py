from encoder import encode
from audioPlayer import playBitarray
import sys

_debug = True


def send(source, destination, freq0, freq1, bitsPerSecond, data):
    msg = encode(source, destination, data)

    bitTime = 1.0 / bitsPerSecond

    playBitarray(msg, freq0, freq1, bitTime)


for line in sys.stdin.readlines():
    line = line[:-1]
    s = line.split(" ", 6)
    send(int(s[3]), int(s[4]), int(s[1]), int(s[2]), float(s[0]), s[5])
