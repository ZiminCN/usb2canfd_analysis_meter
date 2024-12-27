import unittest
from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.uart_driver import UartDriver

class TestUartDriver(unittest.TestCase):
    def setUp(self):
        self.uart_driver = UartDriver()
        
    def test_01_run(self):
        self.uart_driver.test()

    def test_02_run(self):
        self.uart_driver.test()

if __name__ == '__main__':
    unittest.main()
