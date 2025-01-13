import unittest
from src.struct.can import CAN_FRAME
from src.struct.can import CAN_FRAME_FLAGS
from src.struct.can import CAN_BUS_TIMING_PARAMETER


class TestCAN(unittest.TestCase):
    def setUp(self):
        self.can_frame = None
        self.can_bus_timing_parameter = None

    def test_01_run(self):
        can_flags = CAN_FRAME_FLAGS.CAN_FRAME_IDE | CAN_FRAME_FLAGS.CAN_FRAME_RTR
        self.can_frame = CAN_FRAME(id=0x123, dlc=8, flags=can_flags, data=[0x00, 0x01])
        if self.can_frame.is_initialized is True:
            id = self.can_frame.get_can_frame_id()
            print("CAN ID: 0x{:X}".format(id))
            dlc = self.can_frame.get_can_frame_dlc()
            print("CAN DLC: 0x{:X}".format(dlc))
            flags = self.can_frame.get_can_frame_flags()
            print("CAN Flags: 0x{:X}".format(flags))
            data = self.can_frame.get_can_frame_data()
            print("CAN Data[0]: 0x{:X}".format(data[0]))
            print("CAN Data[1]: 0x{:X}".format(data[1]))

    def test_02_run(self):
        self.can_bus_timing_parameter = CAN_BUS_TIMING_PARAMETER(
            f_clock=60000000, abRP=1000000, aSP=800, dbRP=5000000, dSP=750
        )


if __name__ == "__main__":
    unittest.main()
