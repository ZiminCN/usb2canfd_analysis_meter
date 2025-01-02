import unittest
from src.tools.ring_buffer import RingBuffer

class TestRingBuffer(unittest.TestCase):
    def setUp(self):
        self.ring_buffer = RingBuffer(5)
        
    def test_01_run(self):
        ret = 0
        
        print("==> INIT 01")
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))

        ret = self.ring_buffer.ring_buf_capacity_get()
        print("<ring_buf_capacity_get> => ret is: [{}]".format(ret))

        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))

        print("=====================================")

        print("==> PUT")
        test_input_data = [1, 2]
        ret = self.ring_buffer.ring_buf_put(test_input_data, 2)
        print("<ring_buf_put> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))
        print("=====================================")

        print("==> PEEK")
        peek_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_peek(peek_data, 2)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))
        print("=====================================")
        
        print("==> PUT")
        test_input_data = [3, 4]
        ret = self.ring_buffer.ring_buf_put(test_input_data, 2)
        print("<ring_buf_put> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))
        print("=====================================")
        
        print("==> PEEK")
        peek_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_peek(peek_data, 4)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))
        print("=====================================")
        
        print("==> GET")
        test_output_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_get(test_output_data, 3)
        print("<ring_buf_get> => ret is: [{}]".format(ret))
        print("<ring_buf_get> => test_output_data is: [{}]".format(test_output_data))
        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))
        print("=====================================")
        
        print("==> PEEK")
        peek_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_peek(peek_data, 1)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))
        print("======================================================================")

    def test_02_run(self):
        ret = 0
        
        print("===> Init 02")
        self.ring_buffer.ring_buf_reset()
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))

        ret = self.ring_buffer.ring_buf_capacity_get()
        print("<ring_buf_capacity_get> => ret is: [{}]".format(ret))

        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))
        
        print("=====================================")
        
        print("==> PUT")
        test_input_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        test_input_data = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        ret = self.ring_buffer.ring_buf_put(test_input_data, 10)
        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))
        print("=====================================")
        
        print("==> PEEK")
        peek_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_peek(peek_data, 5)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))
        print("=====================================")

        print("==> GET")
        test_output_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_get(test_output_data, 10)
        print("<ring_buf_get> => ret is: [{}]".format(ret))
        print("<ring_buf_get> => test_output_data is: [{}]".format(test_output_data))
        ret = self.ring_buffer.ring_buf_size_get()
        print("<ring_buf_size_get> => ret is: [{}]".format(ret))
        ret = self.ring_buffer.ring_buf_free_space_get()
        print("<ring_buf_free_space_get> => ret is: [{}]".format(ret))
        print("=====================================")
        
        print("==> PEEK")
        peek_data = [0, 0, 0, 0, 0]
        ret = self.ring_buffer.ring_buf_peek(peek_data, 5)
        print("<ring_buf_peek> => ret is: [{}]".format(ret))
        print("<ring_buf_peek> => peek_data is: [{}]".format(peek_data))
        print("=====================================")

if __name__ == "__main__":
    unittest.main()
        