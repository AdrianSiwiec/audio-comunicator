import binascii
from bitarray import bitarray

#Functions at the top are higher-level and use functions at the bottom


def decodeInt(data, lastbit):
    data = reverseNrzi(data, lastbit)
    if (data == None): return None
    data = reverse4b5b(data)
    if (data == None): return None

    return int(data.to01(), 2)


def decodeString(data, lastbit):
    data = reverseNrzi(data, lastbit)
    if (data == None): return None
    data = reverse4b5b(data)
    if (data == None): return None

    return data.tobytes().decode()


#Takes fully encoded bitarray and reverses NRZI and 4b5b, used for the purpose of easy crc checking
def decodeFromBitarray(data):
    data = reverseNrzi(data, True)
    if (data == None): return None
    return reverse4b5b(data)


def reverse4b5b(data):
    msg = bitarray()
    data = data.to01()
    for s in [data[i:i + 5] for i in range(0, len(data), 5)]:
        ext = rev4B5B.get(s)
        if (ext != None):
            msg.extend(rev4B5B.get(s))
        else:
            return None

    return msg


def reverseNrzi(data, lastbit):
    for i in range(data.length()):
        nju = data[i]
        data[i] = not (data[i] == lastbit)
        lastbit = nju

    return data


rev4B5B = {
    '11110': '0000',
    '01001': '0001',
    '10100': '0010',
    '10101': '0011',
    '01010': '0100',
    '01011': '0101',
    '01110': '0110',
    '01111': '0111',
    '10010': '1000',
    '10011': '1001',
    '10110': '1010',
    '10111': '1011',
    '11010': '1100',
    '11011': '1101',
    '11100': '1110',
    '11101': '1111'
}
