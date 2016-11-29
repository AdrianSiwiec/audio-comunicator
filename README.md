It's a simple sender-receiver tool, which transmits text messages via sound. It uses NRZI and 4B5B coding with crc32 error checking.
It's written in python2

Usage:

Sender receives 7 arguments: number of bits per second of transmission, frequency to represent 0, frequency to represent 1, recipient's id, sender's id and message. Message can contain spaces.

Example: "python2 sender.py 5 440 880 1 2 abc def" sends message from 2 to 1, 5 bits per second. The message is "abc def"
  
Receiver takes 3 arguments: number of bits per second of transmission, frequency to represent 0 and frequency to represent 1.

When there is unexpected end of message or message is corrupted it prints "Message Corrupted"

Example: "python2 recv.py 5 440 880". It writes to output recipient's and sender's id and message and whether crc32 check was positive.

To write debug messages (mostly information about samples being listened) change _debug variable to True in 7th line of recv.py
