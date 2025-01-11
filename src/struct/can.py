from enum import Enum
import struct

class CAN_FRAME_FLAGS:
        # Frame uses extended (29-bit) CAN ID
        CAN_FRAME_IDE = 1 << 0
        # Frame is a Remote Transmission Request (RTR)
        CAN_FRAME_RTR = 1 << 1
        # Frame uses CAN-FD format (FDF)
        CAN_FRAME_FDF = 1 << 2
        # Frame uses CAN-FD Baud Rate Switch (BRS). Only valid in combination with ``CAN_FRAME_FDF``.
        CAN_FRAME_BRS = 1 << 3
        
class CAN_FRAME:
        def __init__(self, id: bytes, dlc: int, flags: bytes, data: bytes):
                if id is None:
                        raise ValueError("id is required")
                if dlc is None:
                        raise ValueError("dlc is required")
                if flags is None:
                        raise ValueError("flags is required")
                
                self.id = id & 0x1FFFFFFF
                self.flags = flags

                if (self.flags >> 2) & 0x1:
                        self.dlc = max(0, min(dlc, 64))
                        self.data = data[:self.dlc]
                else:
                        self.dlc = max(0, min(dlc, 8))
                        self.data = data[:self.dlc]
        
        def get_can_frame_id(self):
                return self.id
        
        def get_can_frame_dlc(self):
                return self.dlc
        
        def get_can_frame_flags(self):
                return self.flags
        
        def get_can_frame_data(self):
                return self.data
        
##
# @param f_clock: Frequency of the clock in MHz
# @param aBRP: Arbitration Bit Rate Per-second in bps
# @param aSP: Arbitration Sampling Point * 1000 (aSP=800 means real sampling point is 0.80)
# @param dBRP: Data Bit Rate Per-second in bps
# @param dSP: Data Sampling Point * 1000 (dSP=750 means real sampling point is 0.75)
#
# #        

class CAN_BUS_TIMING_PARAMETER:
        def __init__(self, f_clock: int, abRP: int, aSP: int, dbRP: int, dSP: int):
                self.f_clock = f_clock
                self.aSP = aSP / 100
                self.dSP = dSP / 100
                self.abRP = abRP
                self.dbRP = dbRP
                
                self.aSJW = None
                self.aBS1 = None
                self.aBS2 = None
                self.aBRP = None
                self.dSJW = None
                self.dBS1 = None
                self.dBS2 = None
                self.dBRP = None
                
                self.Tq = None
                self.BitTime = None
                self.Tseg = None
        def calculate_can_timing_parameter(self):
                self.BitTime = self.f_clock / self.aBRP
                print("BitTime: [{}]".format(self.BitTime))
                
                self.Tseg =self.BitTime * self.aSP
                print("Tseg: [{}]".format(self.Tseg))
                
                self.Tq = 
                
                pass
                
        def get_can_timing_parameter_aSJW(self):
                return self.aSJW

        def get_can_timing_parameter_aBS1(self):
                return self.aBS1
        
        def get_can_timing_parameter_aBS2(self):
                return self.aBS2
        
        def get_can_timing_parameter_aBRP(self):
                return self.aBRP
        
        def get_can_timing_parameter_dSJW(self):
                return self.dSJW

        def get_can_timing_parameter_dBS1(self):
                return self.dBS1

        def get_can_timing_parameter_dBS2(self):
                return self.dBS2

        def get_can_timing_parameter_dBRP(self):
                return self.dBRP