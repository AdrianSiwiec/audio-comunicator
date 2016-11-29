import binascii
from bitarray import bitarray

#Functions at the top are higher-level and use functions at the bottom


def encode(source, destination, data):
    return encodeToMessage(encodeToBits(source, destination, data))


def encodeToMessage(data):  #Takes bitarray applies 4b5b, NRZI and adds preamble
    msg = bitarray()
    for i in range(7):
        msg.extend(bitarray("10101010"))
    msg.extend(bitarray("10101011"))
    lastbit = True

    data = apply4b5b(data)
    data = applyNRZI(data, lastbit)

    msg.extend(data)
    return msg


def apply4b5b(data):
    msg = bitarray()
    for b in data.tobytes():
        ext = convertByteToBitarray(ord(b))
        msg.extend(ext)

    return msg


def applyNRZI(data, lastbit):
    for i in range(data.length()):
        if (data[i]):
            data[i] = not lastbit
        else:
            data[i] = lastbit
        lastbit = data[i]

    return data


def encodeToBits(source, destination, message):  #Takes args and returns bitarray
    msg = bitarray()
    bDest = getBitarrayFromInt(destination, 6)
    bSrc = getBitarrayFromInt(source, 6)
    bLen = getBitarrayFromInt(len(message), 2)
    bMsg = getBitarrayFromString(message)

    msg.extend(bDest)
    msg.extend(bSrc)
    msg.extend(bLen)
    msg.extend(bMsg)

    msg.extend(getBitarrayFromInt(abs(getCrc(msg.tobytes())), 4))

    return msg


def getBitarrayFromInt(data, length):
    return bitarray(bin(data)[2:].zfill(8 * length))


def getBitarrayFromString(data):
    ret = bitarray()
    for c in data:
        ret.extend(getBitarrayFromInt(ord(c), 1))

    return ret


def convertByteToBitarray(data):
    arr = getBitarrayFromInt(data, 1)
    ret = bitarray()

    b1 = arr[0:4]
    b2 = arr[4:8]

    b1 = fourBfiveB[b1.to01()]
    b2 = fourBfiveB[b2.to01()]

    ret.extend(b1)
    ret.extend(b2)

    return ret


fourBfiveB = {
    '0000': '11110',
    '0001': '01001',
    '0010': '10100',
    '0011': '10101',
    '0100': '01010',
    '0101': '01011',
    '0110': '01110',
    '0111': '01111',
    '1000': '10010',
    '1001': '10011',
    '1010': '10110',
    '1011': '10111',
    '1100': '11010',
    '1101': '11011',
    '1110': '11100',
    '1111': '11101'
}


def getCrc(data):
    return binascii.crc32(data) & 0xffffffff
