from bitarray import bitarray


def encodeToBits(source, destination, message):
    msg = bitarray()
    msg.extend(getBitarrayFromInt(destination, 6))
    msg.extend(getBitarrayFromInt(source, 6))
    msg.extend(getBitarrayFromInt(len(message), 2))
    msg.extend(getBitarrayFromString(message))

    return msg


def getBitarrayFromInt(data, length):
    return bitarray(bin(data)[2:].zfill(8 * length))


def getBitarrayFromString(data):
    ret = bitarray()
    for c in data:
        ret.extend(getBitarrayFromInt(ord(c), 1))

    return ret


def encodeToMessage(data):
    msg = bitarray()
    for i in range(7):
        msg.extend(bitarray("10101010"))
    msg.extend(bitarray("10101011"))
    lastbit = True

    for b in data.tobytes():
        (ext, lastbit) = convertByteToBitarray(b, lastbit)
        msg.extend(ext)

    return msg


def convertByteToBitarray(data, lastbit):
    arr = getBitarrayFromInt(data, 1)
    ret = bitarray()

    b1 = arr[0:4]
    b2 = arr[4:8]

    b1 = fourBfiveB[b1.to01()]
    b2 = fourBfiveB[b2.to01()]

    ret.extend(b1)
    ret.extend(b2)

    for i in range(8):
        now = ret[i]
        if (now == lastbit):
            ret[i] = False
        else:
            ret[i] = True
        lastbit = now

    return (ret, lastbit)


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


def encode(source, destination, data):
    return encodeToMessage(encodeToBits(source, destination, data))
