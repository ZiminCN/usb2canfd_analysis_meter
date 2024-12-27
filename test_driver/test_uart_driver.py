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
    br = 1500000
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
        uart_instance = serial.Serial(port = "/dev/tty.usbserial-1130", baudrate= br )
        print("=> [Success] open serial port...")
        return uart_instance
    except serial.serialutil.SerialTimeoutException as e:
        print("=> [Failed] Can not open serial port...")
        return e  

def test_write_uart(uart_instance, data: str):
    print("=> Write serial data...")
    data = data.replace(" ", "")
    data = bytes.fromhex(data)
    
    try:
        checkValue = 0x00
        # 55 AA nLen nCheck 00 checkValue 5A
        uart_instance.write(data)
        hex_data = ' '.join(format(x, '02X') for x in data)
        print("=> [Success] write serial data as [{}]...".format(hex_data))
        time.sleep(0.5)
        
    except BaseException as e:
        print("=> [Failed] Can not write serial data...")
        return e

def test_read_uart(uart_instance):
    print("=> Read serial data...")
    read_data = b''
    print("=> Enter uart read ...")
    while True:
        try:
            # read_data = uart_instance.read_all()
            read_data = uart_instance.read(1)
            read_data = read_data.hex()
            if read_data and len(read_data) > 0:
                print("=> [Success] Read serial data: [{}] ...".format(read_data))
        except BaseException as e:
            print("=> [Failed] Can not read serial data...")
            return e

def xor_calculate(data_queue, data_len):
    xor_value = 0
    # data_queue = data_queue.replace(" ", "")
    # data_queue = bytes.fromhex(data_queue)
    for i in range(0, data_len - 2):
        xor_value ^= data_queue[i]
    return xor_value

def check_xor_is_right_or_not(data_queue, data_len):
    xor_value = xor_calculate(data_queue, data_len)
    print("=> data_queue[-2]: [{}]".format(hex(data_queue[-2])))
    if xor_value != data_queue[-2]:
        return False
    else:
        return True

if __name__ == '__main__':
    test_uart_instance = test_open_uart_driver()
    thread = threading.Thread(target=test_read_uart, args=(test_uart_instance,))
    thread.start()
    time.sleep(1)
    test_write_uart(test_uart_instance, "55 AA 07 00 F0 00 5A")
    
    id_data = bytes([0x55, 0xaa, 0x13, 0x01, 0xf0, 0x3e, 0x02, 0x3f, 0x0c, 0x22, 0x6e, 0x7d, 0x8c, 0x7f, 0x8b, 0xa0, 0xa4, 0x5f, 0x5a])
    xor_value = xor_calculate(id_data, 0x13)
    
    print("=> XOR value is [{}]...".format(hex(xor_value)))
    
    if check_xor_is_right_or_not(id_data, 0x13):
        print("=> [Success] XOR is right...")
    else:
        print("=> [Failed] XOR is wrong...")

    