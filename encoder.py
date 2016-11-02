from bitarray import bitarray
import binascii


def encodeToBits(source, destination, message):
    #    print("from: " + str(source) + ", to: " + str(destination) + ":" + message + ";")
    msg = bitarray()
    bDest = getBitarrayFromInt(destination, 6)
    bSrc = getBitarrayFromInt(source, 6)
    bLen = getBitarrayFromInt(len(message), 2)
    bMsg = getBitarrayFromString(message)

    #    print("from: " + str(bSrc))
    #    print("to: " + str(bDest))
    #    print("len: " + str(bLen))
    #    print("msg: " + str(bMsg))

    msg.extend(bDest)
    msg.extend(bSrc)
    msg.extend(bLen)
    msg.extend(bMsg)

    msg.extend(getBitarrayFromInt(binascii.crc32(msg.tobytes()), 4))

    return msg


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

    contentCrc = binascii.crc32(content.tobytes())
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


import sys

for line in sys.stdin:
    line = line[:-1]
    s = line.split(" ", 3)
    if (s[0] == "E"):
        print(encodeToBits(int(s[1]), int(s[2]), s[3]).to01())
    else:
        decoded = decodeFromBits(s[1])
        if(decoded != None) :
            print(str(decoded["src"]) +" " + str(decoded["dest"])+" "+decoded["msg"])
