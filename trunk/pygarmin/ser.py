import serial

ser = serial.Serial("/dev/tty.usbserial0")
ser.close()

