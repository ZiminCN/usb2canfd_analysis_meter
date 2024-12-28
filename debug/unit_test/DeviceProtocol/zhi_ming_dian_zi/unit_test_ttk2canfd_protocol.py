import unittest
import threading
from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.uart_driver import UartDriver
from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.ttl2canfd_protocol import (
    TTL2CANFDProtocol,
)


class TestTTL2CANFDProtocol(unittest.TestCase):
    def setUp(self):
        self.uart_driver = UartDriver()

    def test_01_run(self):
        self.uart_driver.select_ports("/dev/tty.usbserial-1130")
        self.uart_driver.open_uart()
        if self.uart_driver.check_status():
            print("串口已打开")
        else:
            print("串口未打开")
            return
        self.protocol = TTL2CANFDProtocol(self.uart_driver)
        self.protocol.check_hardware_is_connect()


if __name__ == "__main__":
    unittest.main()
