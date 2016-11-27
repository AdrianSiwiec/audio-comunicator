import binascii
from bitarray import bitarray


def encodeToBits(source, destination, message):
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

def decodeInt(data, lastbit):
    data = reverseNrzi(data, lastbit)
    if (data == None): return None
    data = reverse4b5b(data)
    if (data == None): return None

    return int(data.to01(), 2)


def decodeMsg(data, lastbit):
    data = reverseNrzi(data, lastbit)
    if (data == None): return None
    data = reverse4b5b(data)
    if (data == None): return None

    return data.tobytes().decode()

def decodeFromBitarray(data):
    data = reverseNrzi(data, True)

    if (data == None): return None

    return reverse4b5b(data)



def decodeFromBits(message):

    if (len(message) < 16 * 8):
        return None

    sDest = message[:6 * 8]
    sSrc = message[6 * 8:12 * 8]
    sLen = message[12 * 8:14 * 8]
    sMsg = message[14 * 8:-4 * 8]
    sCrc = message[-4 * 8:]

    sContent = sDest + sSrc + sLen + sMsg
    content = bitarray()
    for c in sContent:
        if (c == '0'):
            content.append(False)
        else:
            content.append(True)

    contentCrc = getCrc(content.tobytes())
    messageCrc = int(sCrc, 2)

    if (contentCrc != messageCrc):
        #        print("crc dont match")
        return None

    dest = int(sDest, 2)
    src = int(sSrc, 2)
    length = int(sLen, 2)

    if (length * 8 != len(sMsg)):
        print("length is incorrect")
        return None

    bMsg = bitarray()
    for c in sMsg:
        if (c == '0'):
            bMsg.append(False)
        else:
            bMsg.append(True)

    msg = bMsg.tobytes().decode()

    return ({"dest": dest, "src": src, "msg": msg})


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

    data = apply4b5b(data)

    data = nrzi(data, lastbit)

    msg.extend(data)

    return msg


def decodeFromMessage(data):
    if (data < 65):
        return None
    data = data[64:]

    msg = bitarray()
    for i in data:
        msg.append(i == '1')

    data = msg

    data = reverseNrzi(data, True)

    data = reverse4b5b(data)

    return data



def apply4b5b(data):
    msg = bitarray()
    for b in data.tobytes():
        ext = convertByteToBitarray(ord(b))
        msg.extend(ext)

    return msg


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


def nrzi(data, lastbit):
    for i in range(data.length()):
        if (data[i]):
            data[i] = not lastbit
        else:
            data[i] = lastbit
        lastbit = data[i]

    return data


def reverseNrzi(data, lastbit):
    for i in range(data.length()):
        nju = data[i]
        data[i] = not (data[i] == lastbit)
        lastbit = nju

    return data


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


def getCrc(data):
    return binascii.crc32(data) & 0xffffffff


def encode(source, destination, data):
    return encodeToMessage(encodeToBits(source, destination, data))


def decode(data):
    data = decodeFromMessage(data)
    if (data == None): return None
    return decodeFromBits(data.to01())


def decodeInt(data, lastbit):
    data = reverseNrzi(data, lastbit)
    if (data == None): return None
    data = reverse4b5b(data)
    if (data == None): return None

    return int(data.to01(), 2)


def decodeMsg(data, lastbit):
    data = reverseNrzi(data, lastbit)
    if (data == None): return None
    data = reverse4b5b(data)
    if (data == None): return None

    return data.tobytes().decode()


def getPreamble():
    msg = bitarray()
    for i in range(7):
        msg.extend(bitarray("10101010"))
    msg.extend(bitarray("10101011"))
    return msg


def encodeWithoutPreamble(source, destination, data):
    return encode(source, destination, data)[64:]
