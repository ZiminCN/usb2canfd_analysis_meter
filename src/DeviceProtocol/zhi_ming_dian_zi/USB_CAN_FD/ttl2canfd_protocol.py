try:
    from src.tools.ring_buffer import RingBuffer
except:
    print("[Error] Import Log error!")

try:
    from src.tools.log import Log
except:
    print("[Error] Import Log error!")

try:
    from src.DeviceProtocol.zhi_ming_dian_zi.USB_CAN_FD.uart_driver import UartDriver
except:
    print("[Error] Import UartDriver error!")


class TTL2CANFDProtocol:
    def __init__(self, uart_driver: UartDriver):
        self.log = Log("TTL2CANFDProtocol Init.")
        self.uart_driver = uart_driver
        self.tx_circular_buffer = Ring(256)
        self.rx_circular_buffer = Ring(512)

    def message_receiver_task_controller(self):
        pass

    def message_receiver_process_task_controller(self):
        pass

    def message_sender_task_controller(self):
        while True:
            if self.tx_circular_buffer.is_empty() is not True:
                self.uart_driver.write_hex_bytes(self.tx_circular_buffer.get())
            else:
                pass

    def xor_calculate(self, data_queue, data_len):
        xor_value = 0
        for i in range(0, data_len - 2):
            xor_value ^= data_queue[i]
        return xor_value

    def check_xor_is_right_or_not(self, data_queue, data_len):
        xor_value = xor_calculate(data_queue, data_len)
        if xor_value != data_queue[-2]:
            return False
        else:
            return True

    def check_hardware_is_connect(self):
        check_connect_data = bytes([0x55, 0xAA, 0x07, 0x01, 0x00, 0xF9, 0x5A])
        read_back_data = []
        self.uart_driver.write_hex_bytes(check_connect_data)
        while True:
            read_data = self.uart_driver.read()
            read_data = read_data.hex()
            if read_data and len(read_data) > 0:
                break
        if bytes.fromhex(read_data) == check_connect_data:
            self.log.info("=> [Success] Hardware is connect.")
            return True
        else:
            self.log.info("=> [Failed] Hardware is not connect.")
            return False
