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

def decodeFromBitarray(data):
    data = reverseNrzi(data, True)

    if (data == None): return None

    return reverse4b5b(data)



def decodeFromBits(message):    #takes decoded bitarray and returns dictionary of source, destination and message

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


