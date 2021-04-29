from time import sleep
from serial import Serial
ser = Serial(port="/dev/ttyUSB0", baudrate=9600, bytesize=8, parity="N", stopbits=1, timeout=1)
sleep(0.2)
ser.write("@3{}".format(chr(13)).encode('ascii'))
sleep(0.2)
print(ser.readline())
ser.write("3M{}".format(chr(13)).encode('ascii'))
sleep(0.2)
print(ser.readline())
