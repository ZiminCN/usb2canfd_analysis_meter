from collections import deque
import threading

try:
    from src.tools.log import Log
except:
    print("[Error] Import Log error!")
import numpy as np


class RingBuffer:
    def __init__(self, element_cnt):
        self.log = Log("RingBuffer")
        self.size = element_cnt  # 缓冲区的大小
        self.buffer = [None] * element_cnt  # 初始化缓冲区
        self.head = 0  # 头部索引
        self.tail = 0  # 尾部索引
        self.count = 0  # 当前元素计数
        self.lock = threading.Lock()
        self.ring_buf_reset()

    def ring_buf_reset(self):
        with self.lock:
            self.head = 0
            self.tail = 0
            self.count = 0
            self.buffer = [None] * self.size

    def ring_buf_is_full(self):
        return self.count == self.size

    def ring_buf_is_empty(self):
        return self.count == 0

    def ring_buf_free_space_get(self):
        return self.size - self.count

    def ring_buf_capacity_get(self):
        return self.size

    def ring_buf_size_get(self):
        return self.count

    ##
    # This routine writes data to a ring buffer
    # #
    def ring_buf_single_put(self, input_data: bytes):
        """写入数据到缓冲区"""
        if self.ring_buf_is_full():
            self.log.info("Buffer full, cannot write data.")
            return False

        self.buffer[self.tail] = input_data  # 写入数据
        self.tail = (self.tail + 1) % self.size  # 更新尾部索引
        self.count += 1  # 增加元素计数
        return True

    ##
    # This routine reads data to a ring buffer with removal.
    # #
    def ring_buf_single_get(self):
        """从缓冲区读取数据"""
        if self.ring_buf_is_empty():
            self.log.info("Buffer empty, cannot read data.")
            return None

        data = self.buffer[self.head]  # 读取数据
        self.buffer[self.head] = None  # 清空该位置
        self.head = (self.head + 1) % self.size  # 更新头部索引
        self.count -= 1  # 减少元素计数
        return data

    ##
    # This routine reads data from a ring buffer @param bupeek_dataf without removal.
    # #
    def ring_buf_peek_single(self, cnt):
        """查看缓冲区头部的数据，不移除它"""
        if self.ring_buf_is_empty():
            self.log.info("Buffer empty, nothing to peek.")
            return None
        return self.buffer[self.head + cnt]

    def ring_buf_put(self, input_data: bytes, size):
        with self.lock:
            cnt = 0
            for cnt in range(size):
                if self.ring_buf_single_put(input_data[cnt]) is False:
                    self.log.error("ring_buf_put failed")
                    return False
            return True

    def ring_buf_get(self, output_data, size):
        with self.lock:
            cnt = 0
            for cnt in range(size):
                temp_data = self.ring_buf_single_get()
                if temp_data is None:
                    self.log.error("ring_buf_get failed")
                    return False

                output_data[cnt] = temp_data
            return True

    def ring_buf_peek(self, output_data, size):
        cnt = 0
        if self.ring_buf_size_get() < size:
            self.log.info("The amount of data that can be read is exceeded.")
            return None

        for cnt in range(size):
            output_data[cnt] = self.ring_buf_peek_single(cnt)

        return output_data
