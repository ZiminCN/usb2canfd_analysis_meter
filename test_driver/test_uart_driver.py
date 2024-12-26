import os
import glob
import serial
import serial.serialutil
import serial.tools.list_ports
import platform
import threading
import time

def test_open_uart_driver():
    print("=> Testing UART driver...")
    print("=> Getting available serial ports...")
    ports = serial.tools.list_ports.comports()
    coms = []
    br = 460800
    systype = platform.system()
    for com in ports:
        if systype == 'Windows': ## Windows
            if com.name.__contains__('COM'):
                coms.append('{}|{}'.format(com.device, com.description.split('(')[0]))
        elif systype == 'Linux': ## Linux
            if com.name.__contains__('ttyUSB') or com.name.__contains__('ttyACM'):
                coms.append('{}|{}'.format(com.device, com.description.split('(')[0]))
        elif systype == 'Darwin': ## MacOS
            if com.name.__contains__('cu'):
                coms.append('{}|{}'.format(com.device, com.description.split('(')[0]))
        print("=> Found port: {}".format(com))
    
    print("=> Try open serial port...")
    try:
        # uart_instance = serial.Serial(port = com, baudrate= br )
        uart_instance = serial.Serial(port = "/dev/tty.usbserial-1140", baudrate= br )
        print("=> [Success] open serial port...")
        return uart_instance
    except serial.serialutil.SerialTimeoutException as e:
        print("=> [Failed] Can not open serial port...")
        return e  

def test_write_uart(uart_instance):
    print("=> Write serial data...")
    try:
        checkValue = 0x00
        # 55 AA nLen nCheck 00 checkValue 5A
        # test_data = bytes([0x55, 0xAA, 0x05, 0x00, 0x20, 0x00, 0x5A])
        # test_data = b'\x55\xaa\x05\x08\x00\x33\x5a'
        test_data2 = b'\x55\xaa\x0c\x01\x15\x00\x00\xb4\xc4\x04\x93\x5a'
        uart_instance.write(test_data2)
        hex_data = ' '.join(format(x, '02X') for x in test_data2)
        print("=> [Success] write serial data as [{}]...".format(hex_data))
    except BaseException as e:
        print("=> [Failed] Can not write serial data...")
        return e

def test_read_uart(uart_instance):
    print("=> Read serial data...")
    read_data = b''
    try:
        print("=> Enter uart read ...")
        while True:
            read_data = uart_instance.read_all()
            if read_data is not None:
                print("=> [Success] Read serial data: {}...".format(read_data))
            time.sleep(0.01)
    except BaseException as e:
        print("=> [Failed] Can not read serial data...")
        return e

if __name__ == '__main__':
    test_uart_instance = test_open_uart_driver()
    thread = threading.Thread(target=test_read_uart, args=(test_uart_instance,))
    thread.start()
    time.sleep(1)
    test_write_uart(test_uart_instance)