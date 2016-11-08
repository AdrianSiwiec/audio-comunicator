from bitarray import bitarray
import binascii


def getBitarrayFromInt(data, length):
    return bitarray(bin(data)[2:].zfill(8 * length))
