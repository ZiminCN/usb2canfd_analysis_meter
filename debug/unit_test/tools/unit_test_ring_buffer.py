import unittest
from src.tools.ring_buffer import RingBuffer

class TestRingBuffer(unittest.TestCase):
    def setUp(self):
        self.ring_buffer = RingBuffer(5)
        
    def test_01_run(self):
        ret = 0
        ret = self.ring_buffer.ring_buf_is_empty()
        print("<ring_buf_is_empty> => ret is: [{}]".format(ret))
        
        ret = self.ring_buffer.ring_buf_is_full()
        print("<ring_buf_is_full> => ret is: [{}]".format(ret))
        
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))

        ret = self.ring_buffer.ring_buf_capacity_get()
        print("<ring_buf_capacity_get> => ret is: [{}]".format(ret))

        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))

        test_input_data = [1, 2, 3, 4, 5]
        ret = self.ring_buffer.ring_buf_put(test_input_data, 5)
        print("<ring_buf_put> => ret is: [{}]".format(ret))
        
        peek_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_peek(peek_data, 5)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))
        
        test_output_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_get(test_output_data, 5)
        print("<ring_buf_get> => ret is: [{}]".format(ret))
        print("<ring_buf_get> => test_output_data is: [{}]".format(test_output_data))
        
        ret = self.ring_buffer.ring_buf_get(test_output_data, 5)
        print("<ring_buf_get> => ret is: [{}]".format(ret))
        print("<ring_buf_get> => test_output_data is: [{}]".format(test_output_data))
        
        ret = self.ring_buffer.ring_buf_peek(peek_data, 5)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))

if __name__ == "__main__":
    unittest.main()
        