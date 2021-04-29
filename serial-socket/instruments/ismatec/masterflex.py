from time import sleep
from serial import Serial
ser = Serial(port="/dev/ttyUSB1", baudrate=4800, bytesize=8, parity="O", stopbits=1, timeout=1)
sleep(1)
ser.write(chr(5).encode("utf8"))
sleep(1)
ser.readline()
sleep(1)
ser.write("{}P01{}".format(chr(2), chr(13)).encode("utf8"))
sleep(1)
ser.write("{}P01S+006.0v100.0G{}".format(chr(2), chr(13)).encode("utf8"))
