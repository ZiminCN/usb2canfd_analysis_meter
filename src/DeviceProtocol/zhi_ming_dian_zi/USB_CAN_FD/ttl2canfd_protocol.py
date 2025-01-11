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

try:
    from src.struct.can import CAN_FRAME
except:
    print("[Error] Import CAN Struct Define error!")
    
import threading
import time

class TTL2CANFDProtocol:
    def __init__(self, uart_driver: UartDriver):
        self.log = Log("TTL2CANFDProtocol Init.")
        self.uart_driver = uart_driver
        self.tx_circular_buffer = RingBuffer(256)
        self.rx_circular_buffer = RingBuffer(512)
        self.rx_thread = None
        self.rx_process_thread = None
        self.tx_thread = None
        self.is_thread_running = False
        self.is_time_out = False

    def start_all_thread(self):
        if self.is_thread_running == True:
            return
        
        self.rx_thread = threading.Thread(target=self.message_receiver_task_controller, args=())
        self.rx_process_thread = threading.Thread(target=self.message_receiver_process_task_controller, args=())
        self.tx_thread = threading.Thread(target=self.message_sender_task_controller, args=())
        
        self.rx_thread.start()
        self.rx_process_thread.start()
        self.tx_thread.start()
        
        self.log.info("All thread start.")
        self.is_thread_running = True
    
    def finish_all_thread(self):
        if self.is_thread_running == False:
            return
        
        self.tx_thread.join()
        self.rx_thread.join()
        self.rx_process_thread.join()
        
        self.log.info("All thread finish.")
        self.is_thread_running = False

    def message_receiver_task_controller(self):
        while True:
            read_data = self.uart_driver.read()
            read_data_len = len(read_data)
            self.rx_circular_buffer.ring_buf_put(read_data, read_data_len)

    def message_receiver_process_task_controller(self):
        pass

    def message_sender_task_controller(self):
        while True:
            if self.tx_circular_buffer.ring_buf_is_empty() is not True:
                self.uart_driver.write_hex_bytes(self.tx_circular_buffer.ring_buf_get(self.tx_circular_buffer.ring_buf_size_get()))
            else:
                pass

    def xor_calculate(self, data_queue: bytes, data_len):
        xor_value = data_queue[0]
        
        for i in range(1, (data_len - 2)):
            xor_value ^= data_queue[i]
        return xor_value

    def check_xor_is_right_or_not(self, data_queue, data_len):
        xor_value = self.xor_calculate(data_queue, data_len)
        if xor_value != data_queue[-2]:
            return False
        else:
            return True

    def time_out(self):
        print("time out!")
        self.is_time_out = True

    def order_check_hardware_is_connect(self):
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
            self.log.error("=> [Failed] Hardware is not connect.")
            return False

    def order_set_uart_communication_baud_rate(self, baud_rate: int):
        baud_rate_list = [2000000, 1500000, 1000000, 921600, 7500000, 6000000, 512000, 500000, 460800, 256000, 230400, 128000, 115200, 57600, 56000, 38400, 19200, 14400, 9600, 4800, 2400, 1200, 600, 300, 110]
        if baud_rate not in baud_rate_list:
            self.log.error("=> [Failed] Baud rate is vailed, please confirm your baud rate value.")
            return False
        
        check_values = 0x00
        tx_data_len = 0x00
        baud_rate_byte_length = (baud_rate.bit_length() + 7) // 8
        baud_rate_hex_array = baud_rate.to_bytes(baud_rate_byte_length, byteorder='little')
        
        tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x01])
        tx_data_tail = bytes([check_values, 0x5A])
        
        tx_data = tx_data_header + baud_rate_hex_array + tx_data_tail
        tx_data_len = len(tx_data)
        tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x01])
        tx_data = tx_data_header + baud_rate_hex_array + tx_data_tail
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data_tail = bytes([check_values, 0x5A])
        tx_data = tx_data_header + baud_rate_hex_array + tx_data_tail
        self.log.info("=> [Success] Set uart communication baud rate as [{}]".format(baud_rate))
        return True
    
    def order_get_uart_communication_baud_rate(self):
        check_values = 0x00
        tx_data_len = 0x00
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x02, check_values, 0x5A])
        tx_data_len = len(tx_data)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x02, check_values, 0x5A])
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x02, check_values, 0x5A])
        self.uart_driver.write_hex_bytes(tx_data)
        
        timer = threading.Timer(3, self.time_out)
        self.is_time_out = False
        timer.start()
        
        while self.is_time_out is False:
            read_data = self.uart_driver.read()
            read_data = read_data.hex()
            if read_data and len(read_data) > 0:
                break    
        
        read_data = bytes.fromhex(read_data)
        if self.check_xor_is_right_or_not(read_data, len(read_data)) is False:
            self.log.error("=> [Error]: get xor is wrong")
            return None
        
        uart_baud_rate = (read_data[7] << 16) | (read_data[6] << 8) | read_data[5]
        print("=> [Read]: uart baud rate is [{}]".format(uart_baud_rate))
        return uart_baud_rate
    
    ##
    # * +---------+----------+------------+------------+
    # * |sync_seg | prop_seg | phase_seg1 | phase_seg2 |
    # * +---------+----------+------------+------------+
    #
    # Calculate timing parameters from bitrate and sample point.
    # Calculate the timing parameters from a given bitrate in bits/s and the sampling 
    # point in permill (1/1000) of the entire bit time. The bitrate must always match perfectly. 
    # If the sample point is set to 0, this function defaults to a sample point of 75.0% for bitrates 
    # over 800 kbit/s, 80.0% for bitrates over 500 kbit/s, and 87.5% for all other bitrates.
    #
    # br = (core_clock / prescaler) / (1 + prop_seg + phase_seg1 + phase_seg2)
    # 
    # @param aSJW: 仲裁段同步跳转宽度
    # @param aBS1: 仲裁段相位1段
    # @param aBS2: 仲裁段相位2段
    # @param aBRP: 仲裁段预分频系数
    # @param dSJW: 数据段同步跳转宽度
    # @param dBS1: 数据段相位1段    
    # @param dBS2: 数据段相位2段
    # @param dBRP: 数据段预分频系数
    # #
    
    def order_set_can_communication_baud_rate(self, aSJW: int, aBS1: int, aBS2: int, aBRP: bytes, dSJW: int, dBS1: int, dBS2: int, dBRP: bytes):
        pass
    
    def order_get_can_communication_baud_rate(self):
        pass
    
    def order_set_work_mode(self, mode: int):
        pass
    
    def order_get_work_mode(self):
        pass
    
    def order_set_hardware_filter(self, filter_mode: bool, filter_id_1: bytes, filter_id_2: bytes):
        pass
    
    def order_get_hardware_filter(self):
        pass
    
    def order_set_software_filter(self, filter_id: bytes, filter_mask: bytes):
        pass
    
    def order_get_software_filter(self):
        pass
    
    def order_set_can_frame_format(self, frame_format: bytes):
        pass
    
    def order_get_can_frame_format(self):
        pass
    
    def order_send_can_frame(self, is_can_fd: bool, is_can_fd_brs: bool, can_frame_format: bool):
        pass
    
    def order_receive_can_frame(self):
        pass
    
    def order_get_bus_fault_info(self):
        pass
    
    def order_set_device_dominant_frequency(self):
        pass
    
    def order_get_device_dominant_frequency(self):
        pass
    
    def order_get_device_uuid(self):
        pass
    
    def order_reset_device(self):
        pass
    