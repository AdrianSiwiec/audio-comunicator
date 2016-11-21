from encoder import encode
from audioPlayer import playBitarray
import sys

_debug = True


def send(source, destination, freq0, freq1, bitsPerSecond, data):
    msg = encode(source, destination, data)

    bitTime = 1.0 / bitsPerSecond

    playBitarray(msg, freq0, freq1, bitTime)

msg = ""
for i in range(len(sys.argv)):
    if(i > 6): msg+=" "
    if(i >= 6): msg += sys.argv[i]

print(msg)
    
send(int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[1]), msg)

#for line in sys.stdin.readlines():
#    line = line[:-1]
#    s = line.split(" ", 6)
#    send(int(s[3]), int(s[4]), int(s[1]), int(s[2]), float(s[0]), s[5])
