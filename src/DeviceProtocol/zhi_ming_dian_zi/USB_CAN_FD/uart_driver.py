import serial
import serial.serialutil
import serial.tools.list_ports
import platform

try:
    from src.tools.log import Log
except:
    print("[Error] Import Log error!")


class UartDriver:

    def __init__(self):
        self.uart_instance = None
        self.log = Log("UartDriver Init.")
        self.port = None
        self.baud_rate = 1500000
        self.byte_size = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stop_bits = serial.STOPBITS_ONE
        self.timeout = 1
        self.xonxoff = False
        self.rtscts = False
        self.write_timeout = 5
        self.dsrdtr = False
        self.inter_byte_timeout = None
        self.exclusive = None

    def test(self):
        print("test test test test")

    def get_ports(self):
        try:
            coms = []
            ports = serial.tools.list_ports.comports()
            systype = platform.system()
            for com in ports:
                if systype == "Windows":  ## Windows
                    if com.name.__contains__("COM"):
                        coms.append(
                            "{}|{}".format(com.device, com.description.split("(")[0])
                        )
                elif systype == "Linux":  ## Linux
                    if com.name.__contains__("ttyUSB") or com.name.__contains__(
                        "ttyACM"
                    ):
                        coms.append(
                            "{}|{}".format(com.device, com.description.split("(")[0])
                        )
                elif systype == "Darwin":  ## MacOS
                    if com.name.__contains__("cu"):
                        coms.append(
                            "{}|{}".format(com.device, com.description.split("(")[0])
                        )
                self.log.info("=> Found port: {}".format(com))
            return coms
        except Exception as e:
            self.log.error("=> Failed to get ports: {}".format(e))

    def select_ports(self, port_name):
        try:
            self.port = port_name
        except Exception as e:
            self.log.error("=> Failed to select port: {}".format(e))

    def check_status(self):
        if self.uart_instance is None:
            return False
        else:
            return self.uart_instance.is_open

    def open_uart(self):
        try:
            # self.uart_instance = serial.Serial(port= self.port, baudrate= self.baud_rate, bytesize= self.byte_size, parity= self.parity, stopbits= self.stop_bits, timeout= self.timeout, xonxoff= self.xonxoff, rtscts= self.rtscts, write_timeout= self.write_timeout, dsrdtr= self.dsrdtr, inter_byte_timeout= self.inter_byte_timeout, exclusive= self.exclusive)
            self.uart_instance = serial.Serial(
                port="/dev/tty.usbserial-1130", baudrate=self.baud_rate
            )
        except Exception as e:
            self.log.error("=> Failed to open uart: {}".format(e))

    def close_uart(self):
        try:
            self.uart_instance.close()
        except Exception as e:
            self.log.error("=> Failed to close uart: {}".format(e))

    def get_instance(self):
        return self.uart_instance

    def read(self):
        read_data = b""
        try:
            read_data = self.uart_instance.read_all()
        except Exception as e:
            self.log.error("=> Failed to read uart: [{}]".format(e))
            self.close_uart()
        return read_data

    def write_hex_bytes(self, bArray: bytes):
        try:
            self.uart_instance.write(bArray)
        except Exception as e:
            self.log.error("=> Failed to write uart: [{}]".format(e))
