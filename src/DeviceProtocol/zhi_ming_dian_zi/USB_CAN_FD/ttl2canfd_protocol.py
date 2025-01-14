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

try:
    from src.struct.can import CAN_FRAME_FLAGS
    from src.struct.can import CAN_FRAME
    from src.struct.can import CAN_BUS_TIMING_PARAMETER
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

        self.rx_thread = threading.Thread(
            target=self.message_receiver_task_controller, args=()
        )
        self.rx_process_thread = threading.Thread(
            target=self.message_receiver_process_task_controller, args=()
        )
        self.tx_thread = threading.Thread(
            target=self.message_sender_task_controller, args=()
        )

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
                self.uart_driver.write_hex_bytes(
                    self.tx_circular_buffer.ring_buf_get(
                        self.tx_circular_buffer.ring_buf_size_get()
                    )
                )
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

    def send_order(self, command: bytes):
        check_values = 0x00
        tx_data_len = 0x00

        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, command, check_values, 0x5A])
        tx_data_len = len(tx_data)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, command, check_values, 0x5A])
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, command, check_values, 0x5A])
        self.uart_driver.write_hex_bytes(tx_data)

    def receive_order(self):
        timer = threading.Timer(3, self.time_out)
        self.is_time_out = False
        timer.start()

        while self.is_time_out is False:
            read_data = self.uart_driver.read()
            read_data = read_data.hex()
            if read_data and len(read_data) and (read_data[-2:] == "5a") > 0:
                break

        timer.cancel()
        time.sleep(0.2)
        return read_data

    def order_check_hardware_is_connect(self):
        check_connect_data = bytes([0x55, 0xAA, 0x07, 0x01, 0x00, 0xF9, 0x5A])
        self.uart_driver.write_hex_bytes(check_connect_data)

        read_data = self.receive_order()

        if bytes.fromhex(read_data) == check_connect_data:
            self.log.info("=> [Success] Hardware is connect.")
            return True
        else:
            self.log.error("=> [Failed] Hardware is not connect.")
            return False

    def order_set_uart_communication_baud_rate(self, baud_rate: int):
        baud_rate_list = [
            2000000,
            1500000,
            1000000,
            921600,
            7500000,
            6000000,
            512000,
            500000,
            460800,
            256000,
            230400,
            128000,
            115200,
            57600,
            56000,
            38400,
            19200,
            14400,
            9600,
            4800,
            2400,
            1200,
            600,
            300,
            110,
        ]
        if baud_rate not in baud_rate_list:
            self.log.error(
                "=> [Failed] Baud rate is vailed, please confirm your baud rate value."
            )
            return False

        check_values = 0x00
        tx_data_len = 0x00
        baud_rate_byte_length = (baud_rate.bit_length() + 7) // 8
        baud_rate_hex_array = baud_rate.to_bytes(
            baud_rate_byte_length, byteorder="little"
        )

        tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x01])
        tx_data_tail = bytes([check_values, 0x5A])

        tx_data = tx_data_header + baud_rate_hex_array + tx_data_tail
        tx_data_len = len(tx_data)
        tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x01])
        tx_data = tx_data_header + baud_rate_hex_array + tx_data_tail
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data_tail = bytes([check_values, 0x5A])
        tx_data = tx_data_header + baud_rate_hex_array + tx_data_tail
        self.uart_driver.write_hex_bytes(tx_data)

        self.log.info(
            "=> [Success] Set uart communication baud rate as [{}]".format(baud_rate)
        )
        return True

    def order_get_uart_communication_baud_rate(self):
        self.send_order(0x02)

        read_data = self.receive_order()

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

    def order_set_can_communication_baud_rate(
        self, can_bus_timing_parameter: CAN_BUS_TIMING_PARAMETER
    ):
        check_values = 0x00
        tx_data_len = 0x00
        aSJW = can_bus_timing_parameter.get_can_timing_parameter_aSJW(0)
        aBS1 = can_bus_timing_parameter.get_can_timing_parameter_aBS1(0)
        aBS2 = can_bus_timing_parameter.get_can_timing_parameter_aBS2(0)
        aBRP = can_bus_timing_parameter.get_can_timing_parameter_aBRP(0)
        dSJW = can_bus_timing_parameter.get_can_timing_parameter_dSJW(0)
        dBS1 = can_bus_timing_parameter.get_can_timing_parameter_dBS1(0)
        dBS2 = can_bus_timing_parameter.get_can_timing_parameter_dBS2(0)
        dBRP = can_bus_timing_parameter.get_can_timing_parameter_dBRP(0)

        aBRP_L = aBRP & 0xFF
        aBRP_H = (aBRP >> 8) & 0xFF

        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x03,
                0x00,
                aSJW,
                aBS1,
                aBS2,
                aBRP,
                aBRP_L,
                aBRP_H,
                dSJW,
                dBS1,
                dBS2,
                dBRP,
                check_values,
                0x5A,
            ]
        )
        tx_data_len = len(tx_data)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x03,
                0x00,
                aSJW,
                aBS1,
                aBS2,
                aBRP,
                aBRP_L,
                aBRP_H,
                dSJW,
                dBS1,
                dBS2,
                dBRP,
                check_values,
                0x5A,
            ]
        )
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x03,
                0x00,
                aSJW,
                aBS1,
                aBS2,
                aBRP,
                aBRP_L,
                aBRP_H,
                dSJW,
                dBS1,
                dBS2,
                dBRP,
                check_values,
                0x5A,
            ]
        )
        # self.uart_driver.write_hex_bytes(tx_data)
        self.log.info(
            "=> [Success] set CAN timing parameter aSJW:[{}], aBS1:[{}], aBS2:[{}], aBRP:[{}], dSJW:[{}], dBS1:[{}], dBS2:[{}], dBRP:[{}]".format(
                aSJW, aBS1, aBS2, aBRP, dSJW, dBS1, dBS2, dBRP
            )
        )

    def order_get_can_communication_baud_rate(self):
        self.send_order(0x04)
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)

        if self.check_xor_is_right_or_not(read_data, len(read_data)) is False:
            self.log.error("=> [Error]: get xor is wrong")
            return None

        aSJW = read_data[6]
        aBS1 = read_data[7]
        aBS2 = read_data[8]
        aBRP_L = read_data[9]
        aBRP_H = read_data[10]
        dSJW = read_data[11]
        dBS1 = read_data[12]
        dBS2 = read_data[13]
        dBRP = read_data[14]
        abRP_1 = read_data[15]
        abRP_2 = read_data[16]
        abRP_3 = read_data[17]
        dbRP_1 = read_data[18]
        dbRP_2 = read_data[19]
        dbRP_3 = read_data[20]

        aBRP = aBRP_H << 8 | aBRP_L
        abRP = abRP_3 << 16 | abRP_2 << 8 | abRP_1
        dbRP = dbRP_3 << 16 | dbRP_2 << 8 | dbRP_1

        self.log.debug(
            "[Debug]: aSJW:[{}], aBS1:[{}], aBS2:[{}], aBRP:[{}], abRP:[{}], dSJW:[{}], dBS1:[{}], dBS2:[{}], dBRP:[{}], dbRP:[{}]".format(
                aSJW, aBS1, aBS2, aBRP, abRP, dSJW, dBS1, dBS2, dBRP, dbRP
            )
        )

    def order_set_work_mode(self, mode: int):
        pass

    def order_get_work_mode(self):
        pass

    def order_reset_hardware_filter(self):
        check_values = 0x00
        tx_data_len = 0x00
        stand_can_mode = 0x00
        extend_can_mode = 0x01
        space_byte = 0x00

        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x07,
                0x00,
                stand_can_mode,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        tx_data_len = len(tx_data)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x07,
                0x00,
                stand_can_mode,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x07,
                0x00,
                stand_can_mode,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        self.uart_driver.write_hex_bytes(tx_data)

        time.sleep(0.2)

        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x07,
                0x00,
                extend_can_mode,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        tx_data_len = len(tx_data)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x07,
                0x00,
                extend_can_mode,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x07,
                0x00,
                extend_can_mode,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        self.uart_driver.write_hex_bytes(tx_data)

    def order_get_hardware_filter(self):
        self.send_order(0x08)
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        self.log.debug("[Debug]: get read data is : [{}]".format(read_data.hex()))

    def order_reset_software_filter(self):
        check_values = 0x00
        tx_data_len = 0x00
        space_byte = 0x00

        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x09,
                0x00,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        tx_data_len = len(tx_data)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x09,
                0x00,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes(
            [
                0x55,
                0xAA,
                tx_data_len,
                0x01,
                0x09,
                0x00,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                space_byte,
                check_values,
                0x5A,
            ]
        )
        self.uart_driver.write_hex_bytes(tx_data)

    def order_get_software_filter(self):
        self.send_order(0x0A)
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        self.log.debug("[Debug]: get read data is : [{}]".format(read_data.hex()))

    def order_set_can_frame_format(self, frame_format: CAN_FRAME):
        can_mode = frame_format.get_can_frame_flags
        if ((can_mode >> 2) & 0x1) is True:
            can_mode = 0x01
            self.log.info("[Success] Set CAN FD Mode")
        else:
            can_mode = 0x00
            self.log.info("[Success] Set CAN 2.0 Mode")

        check_values = 0x00
        tx_data_len = 0x00

        tx_data = bytes(
            [0x55, 0xAA, tx_data_len, 0x01, 0x0B, 0x00, can_mode, check_values, 0x5A]
        )
        tx_data_len = len(tx_data)
        tx_data = bytes(
            [0x55, 0xAA, tx_data_len, 0x01, 0x0B, 0x00, can_mode, check_values, 0x5A]
        )
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes(
            [0x55, 0xAA, tx_data_len, 0x01, 0x0B, 0x00, can_mode, check_values, 0x5A]
        )
        self.uart_driver.write_hex_bytes(tx_data)

    def order_get_can_frame_format(self):
        self.send_order(0x0C)
        read_data = self.receive_order()
        print("read_data123: [{}]".format(read_data))
        
        can_frame_mode = read_data[5]
        if can_frame_mode == 0x00:
            self.log.info("[Success] Get CAN Frame Mode : CAN 2.0 Mode")
        elif can_frame_mode == 0x01:
            self.log.info("[Success] Get CAN Frame Mode : CAN FD Mode")
        else :
            self.log.info("[Error] Get CAN Frame Mode : Unknown")
            return -1
        
        return can_frame_mode

    def order_send_can_frame(self, can_frame: CAN_FRAME):
        check_values = 0x00
        tx_data_len = 0x00
        is_IDE = False
        is_RTR = False
        is_FDF = False
        is_BRS = False
        
        if (can_frame.flags & 0x01) == True:
            is_IDE = True
        elif (can_frame.flags >> 1) & 0x01 == True:
            is_RTR = True
        elif (can_frame.flags >> 2) & 0x01 == True:
            is_FDF = True
        elif (can_frame.flags >> 3) & 0x01 == True:
            is_BRS = True

        CAN_ID = can_frame.get_can_frame_id()
        tx_data_data = can_frame.get_can_frame_data()
        tx_data_data_len = len(tx_data_data)

        if is_IDE != True:
            CAN_ID_L = CAN_ID & 0xFF
            CAN_ID_H = (CAN_ID >> 8) & 0xFF
            if is_RTR != True:
                tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x10, 0x00, is_FDF, is_BRS, is_IDE, is_RTR, CAN_ID_L, CAN_ID_H, tx_data_data_len])
                tx_data_tail = bytes([check_values, 0x5A])
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                tx_data_len = len(tx_data)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                check_values = self.xor_calculate(tx_data, tx_data_len)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
            else:
                tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x10, 0x00, is_FDF, is_BRS, is_IDE, is_RTR, CAN_ID_L, CAN_ID_H, 0x00])
                tx_data_tail = bytes([check_values, 0x5A])
                tx_data_data = bytes([0x00])
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                tx_data_len = len(tx_data)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                check_values = self.xor_calculate(tx_data, tx_data_len)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
        else:
            CAN_ID_1 = CAN_ID & 0xFF
            CAN_ID_2 = (CAN_ID >> 8) & 0xFF
            CAN_ID_3 = (CAN_ID >> 16) & 0xFF
            CAN_ID_4 = (CAN_ID >> 24) & 0xFF
            if is_RTR != True:
                tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x10, 0x00, is_FDF, is_BRS, is_IDE, is_RTR, CAN_ID_1, CAN_ID_2, CAN_ID_3, CAN_ID_4, tx_data_data_len])
                tx_data_tail = bytes([check_values, 0x5A])
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                tx_data_len = len(tx_data)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                check_values = self.xor_calculate(tx_data, tx_data_len)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
            else:
                tx_data_header = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x10, 0x00, is_FDF, is_BRS, is_IDE, is_RTR, CAN_ID_1, CAN_ID_2, CAN_ID_3, CAN_ID_4, 0x00])
                tx_data_tail = bytes([check_values, 0x5A])
                tx_data_data = bytes([0x00])
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                tx_data_len = len(tx_data)
                tx_data = tx_data_header + tx_data_data + tx_data_tail
                check_values = self.xor_calculate(tx_data, tx_data_len)
                tx_data = tx_data_header + tx_data_data + tx_data_tail

        self.uart_driver.write_hex_bytes(tx_data)

    def order_receive_can_frame(self):
        self.send_order(0x12)
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        self.log.debug("[Debug]: get read data is : [{}]".format(read_data.hex()))
        
        if self.check_xor_is_right_or_not(read_data, len(read_data)) is False:
            self.log.error("=> [Error]: get xor is wrong")
            return None

    def order_get_bus_fault_info(self):
        self.send_order(0x13)
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        self.log.debug("[Debug]: get read data is : [{}]".format(read_data.hex()))
        
        send_all_order_cmd_num = (read_data[6] << 24) | (read_data[7] << 16) | (read_data[8] << 8) | read_data[9]
        send_order_successed_num = (read_data[10] << 24) | (read_data[11] << 16) | (read_data[12] << 8) | read_data[13]
        send_order_failed_num = (read_data[14] << 24) | (read_data[15] << 16) | (read_data[16] << 8) | read_data[17]
        receive_order_successed_num = (read_data[18] << 24) | (read_data[19] << 16) | (read_data[20] << 8) | read_data[21]
        send_order_failed = read_data[22]
        receive_order_failed = read_data[23]
        last_error = read_data[24]
        
        self.log.info("[Info]: send_all_order_cmd_num:[{}], send_order_successed_num:[{}], send_order_failed_num:[{}], receive_order_successed_num:[{}], send_order_failed:[{}], receive_order_failed:[{}], last_error:[{}]".format(send_all_order_cmd_num, send_order_successed_num, send_order_failed_num, receive_order_successed_num, send_order_failed, receive_order_failed, last_error))

    def order_set_device_dominant_frequency(self, set_f_clock: int):
        check_values = 0x00
        tx_data_len = 0x00
        write_f_clokc = 0x00
        
        f_clock_1 = set_f_clock & 0xFF
        f_clock_2 = (set_f_clock >> 8) & 0xFF
        f_clock_3 = (set_f_clock >> 16) & 0xFF
        f_clock_4 = (set_f_clock >> 24) & 0xFF
        
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x15, write_f_clokc, f_clock_1, f_clock_2, f_clock_3, f_clock_4, check_values, 0x5A])
        tx_data_len = len(tx_data)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x15, write_f_clokc, f_clock_1, f_clock_2, f_clock_3, f_clock_4, check_values, 0x5A])
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x15, write_f_clokc, f_clock_1, f_clock_2, f_clock_3, f_clock_4, check_values, 0x5A])
        self.uart_driver.write_hex_bytes(tx_data)
        
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        self.log.debug("[Debug]: get read data is : [{}]".format(read_data.hex()))
        f_clock = (read_data[9] << 24) | (read_data[8] << 16) | (read_data[7] << 8) | read_data[6]
        self.log.debug("[Debug]: f_clock is : [{}]".format(f_clock))
        
        if f_clock == set_f_clock:
            return True
        else:
            return False
        
    def order_get_device_dominant_frequency(self):
        check_values = 0x00
        tx_data_len = 0x00
        read_f_clock = 0x01
        
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x15, read_f_clock, 0x00, 0x00, 0x00, 0x00, check_values, 0x5A])
        tx_data_len = len(tx_data)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x15, read_f_clock, 0x00, 0x00, 0x00, 0x00, check_values, 0x5A])
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0x15, read_f_clock, 0x00, 0x00, 0x00, 0x00, check_values, 0x5A])
        self.uart_driver.write_hex_bytes(tx_data)
        
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        self.log.debug("[Debug]: get read data is : [{}]".format(read_data.hex()))
        f_clock = (read_data[9] << 24) | (read_data[8] << 16) | (read_data[7] << 8) | read_data[6]
        self.log.debug("[Debug]: f_clock is : [{}]".format(f_clock))
        return f_clock

    def order_get_device_uuid(self):
        self.send_order(0xF0)
        read_data = self.receive_order()
        read_data = bytes.fromhex(read_data)
        
        uuid = (read_data[16] << 88) | (read_data[15] << 80) | (read_data[14] << 72) | (read_data[13] << 64) | (read_data[12] << 56) | (read_data[11] << 48) | (read_data[10] << 40) | (read_data[9] << 32) | (read_data[8] << 24) | (read_data[7] << 16) | (read_data[6] << 8) | read_data[5]
        
        self.log.info("[Info]: get device uuid is : [{}]".format(uuid))
        return uuid
        
    def order_reset_device(self):
        check_values = 0x00
        tx_data_len = 0x00
        
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0xEE, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, check_values, 0x5A])
        tx_data_len = len(tx_data)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0xEE, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, check_values, 0x5A])
        check_values = self.xor_calculate(tx_data, tx_data_len)
        tx_data = bytes([0x55, 0xAA, tx_data_len, 0x01, 0xEE, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, check_values, 0x5A])
        self.uart_driver.write_hex_bytes(tx_data)
        