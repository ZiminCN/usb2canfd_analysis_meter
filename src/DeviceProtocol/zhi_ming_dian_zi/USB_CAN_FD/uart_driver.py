import os
import glob
import serial
import serial.serialutil
import serial.tools.list_ports
import platform
import threading
import time
try:
    from src.tools.log import Log
except:
    from log import Log
    
class UartDriver:
    
    def __init__(self):
        print("UartDriver init")
        self.baud_rate = 1500000
        self.data_bits = serial.EIGHTBITS
        self.port = None
        self.stop_bits = serial.STOPBITS_ONE
        self.parity = serial.PARITY_NONE
        self.flow_control = None
        self.timeout = 1
        
    def test(self):
        print("test test test test")

        