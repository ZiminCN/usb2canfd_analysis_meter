from collections import deque
import threading
try:
    from src.tools.log import Log
except:
    print("[Error] Import Log error!")
import numpy as np

class RingBuffer:
    def __init__(self, size):
        self.log = Log("RingBuffer")
        self.buffer = [None] * size
        self.size = size
        self.put_head = 0
        self.put_tail = 0
        self.put_base = 0
        self.get_head = 0
        self.get_tail = 0
        self.get_base = 0
        self.lock = threading.Lock()
        
    def ring_buf_reset(self):
        self.put_head = 0
        self.put_tail = 0
        self.put_base = 0
        self.get_head = 0
        self.get_tail = 0
        self.get_base = 0
        for cnt in range(self.size):
            self.buffer[cnt] = None
    
    def ring_buf_is_empty(self):
        return self.put_head == self.get_tail
    
    def ring_buf_free_space_get(self):
        return self.size - (self.put_head - self.get_tail)
    
    def ring_buf_caoacity_get(self):
        return self.size
    
    def ring_buf_size_get(self):
        return self.put_tail - self.get_head
    
    ##
    # This routine writes data to a ring buffer
    # #
    def ring_buf_put(self, input_data: bytes, size):
        cnt = 0
        with self.lock:
            while True:
                if self.ring_buf_free_space_get() <= 0:
                    self.log.error("ring_buf_put: no free space")
                    return False
                
                if cnt == size:
                    return True
                
                self.buffer[self.put_tail] = input_data[cnt]
                cnt += 1
                if self.put_tail == (self.size - 1):
                    self.put_base += self.size
                    self.put_tail = 0
                else:
                    self.put_tail += 1
                
                
                
                
                
                
                
        
    ##
    # This routine reads data to a ring buffer with removal.
    # #
    def ring_buf_get(self, output_data: bytes, size):
        with self.lock:
            pass
    
    
    ##
    # This routine reads data from a ring buffer @param bupeek_dataf without removal.
    # #
    def ring_buf_peek(self, peek_data: bytes, size):
    
            
    
    
        
        