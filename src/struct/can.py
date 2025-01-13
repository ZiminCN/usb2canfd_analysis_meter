from enum import Enum
import struct

try:
    from src.tools.log import Log
except:
    print("[Error] Import Log error")


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
            self.data = data[: self.dlc]
        else:
            self.dlc = max(0, min(dlc, 8))
            self.data = data[: self.dlc]

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
        self.log = Log("CAN_BUS_TIMING_PARAMETER Init.")
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
        self.log.info("BitTime: [{}]".format(self.BitTime))

        self.Tseg = self.BitTime * self.aSP
        self.log.info("Tseg: [{}]".format(self.Tseg))

        BS1_range = range(0, 31)
        BS2_range = range(0, 15)
        BRP_range = range(1, 31)
        SP_range = [750, 800, 850]

        arbitration_matches = []
        for temp_aBS1 in BS1_range:
            for temp_aBS2 in BS2_range:
                for temp_aBRP in BRP_range:
                    temp_abRP = self.f_clock / (
                        (temp_aBRP + 1) * (temp_aBS1 + temp_aBS2 + 3)
                    )
                    if temp_abRP == self.abRP:
                        arbitration_matches.append(
                            [temp_aBRP, temp_aBS1, temp_aBS2, temp_abRP]
                        )
                        self.log.debug(
                            "[Debug]: Found arbitration matches: [aBRP: {}, aBS1: {}, aBS2: {}, abRP: {}]".format(
                                temp_aBRP, temp_aBS1, temp_aBS2, temp_abRP
                            )
                        )

        data_matches = []
        for temp_dBS1 in BS1_range:
            for temp_dBS2 in BS2_range:
                for temp_dBRP in BRP_range:
                    temp_dbRP = self.f_clock / (
                        (temp_dBRP + 1) * (temp_dBS1 + temp_dBS2 + 3)
                    )
                    if temp_dbRP == self.dbRP:
                        data_matches.append(
                            [temp_dBRP, temp_dBS1, temp_dBS2, temp_dbRP]
                        )
                        self.log.debug(
                            "[Debug]: Found data matches: [dBRP: {}, dBS1: {}, dBS2: {}, dbRP: {}]".format(
                                temp_dBRP, temp_dBS1, temp_dBS2, temp_dbRP
                            )
                        )

        # arbitration_rst = []
        # for temp_abRP in arbitration_matches:
        #         temp_aBS1 = temp_abRP[1]
        #         temp_aBS2 = temp_abRP[2]
        #         temp_aSP = (temp_dBS1 + 2) / (temp_dBS2 + 3) * 100
        #         if temp_aSP in SP_range:
        #                 arbitration_rst.append([temp_abRP, temp_aSP])

        # data_rst = []
        # for temp_dbRP in data_matches:
        #         temp_dBS1 = temp_dbRP[1]
        #         temp_dBS2 = temp_dbRP[2]
        #         temp_dSP = (temp_dBS1 + 2) / (temp_dBS2 + 3) * 100
        #         if temp_dSP in SP_range:
        #                 data_rst.append([temp_dbRP, temp_dSP])

        self.log.debug("[Debug]: arbitration result: ")

        self.log.debug("[Debug]: data result: ")

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
