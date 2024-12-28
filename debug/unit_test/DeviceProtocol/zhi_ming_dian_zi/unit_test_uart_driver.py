import unittest
import threading
from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.uart_driver import UartDriver


class TestUartDriver(unittest.TestCase):
    def setUp(self):
        self.uart_driver = UartDriver()

    def test_01_run(self):
        self.uart_driver.test()

    def test_02_run(self):
        self.uart_driver.get_ports()

    def test_03_run(self):
        self.uart_driver.select_ports("/dev/tty.usbserial-1130")

    def test_04_run(self):
        self.uart_driver.open_uart()
        if self.uart_driver.check_status():
            print("串口已打开")
        else:
            print("串口未打开")
            return
        read_id_data = bytes(
            [
                0x55,
                0xAA,
                0x13,
                0x01,
                0xF0,
                0x3E,
                0x02,
                0x3F,
                0x0C,
                0x22,
                0x6E,
                0x7D,
                0x8C,
                0x7F,
                0x8B,
                0xA0,
                0xA4,
                0x5F,
                0x5A,
            ]
        )
        self.uart_driver.write_hex_bytes(read_id_data)
        read_data = b""
        while True:
            read_data = self.uart_driver.read()
            read_data = read_data.hex()
            if read_data and len(read_data) > 0:
                print("=> [Success] Read serial data: [{}] ...".format(read_data))
                break


if __name__ == "__main__":
    unittest.main()
