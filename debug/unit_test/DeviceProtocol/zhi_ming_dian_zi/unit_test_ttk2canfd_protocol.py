import unittest
import threading
from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.uart_driver import UartDriver
from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.ttl2canfd_protocol import (
    TTL2CANFDProtocol,
)

try:
    from src.struct.can import CAN_FRAME_FLAGS
    from src.struct.can import CAN_FRAME
    from src.struct.can import CAN_BUS_TIMING_PARAMETER
except:
    print("[Error] Import CAN Struct Define error!")


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

        if self.protocol.order_check_hardware_is_connect() is True:
            # self.protocol.order_get_uart_communication_baud_rate()
            # self.protocol.order_get_can_communication_baud_rate()
            self.protocol.order_reset_hardware_filter()
            self.protocol.order_reset_software_filter()

            self.protocol.order_get_hardware_filter()
            self.protocol.order_get_software_filter()
            self.protocol.order_get_can_frame_format()


if __name__ == "__main__":
    unittest.main()
