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
    def __init__(self, id: bytes, dlc: int, flags: int, data: bytes):
        self.is_initialized = False
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

        self.is_initialized = True

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
        self.is_initialized = False
        self.f_clock = f_clock
        self.aSP = aSP / 100
        self.dSP = dSP / 100
        self.abRP = abRP
        self.dbRP = dbRP

        self.aSJW = []
        self.aBS1 = []
        self.aBS2 = []
        self.aBRP = []
        self.dSJW = []
        self.dBS1 = []
        self.dBS2 = []
        self.dBRP = []

        self.calculate_can_timing_parameter()

    def calculate_can_timing_parameter(self):
        BS1_range = range(0, 64)
        BS2_range = range(0, 15)
        BRP_range = range(1, 31)
        SP_range = [750, 800, 850]

        arbitration_matches = []
        for temp_aBS1 in BS1_range:
            for temp_aBS2 in BS2_range:
                for temp_aBRP in BRP_range:
                    temp_abRP = self.f_clock / (
                        (temp_aBRP + 1) * (temp_aBS1 + temp_aBS2 + 1)
                    )
                    if temp_abRP == self.abRP:
                        temp_aSJW = min(temp_aBS1, temp_aBS2)
                        temp_aBRP += 1
                        arbitration_matches.append(
                            [temp_aSJW, temp_aBS1, temp_aBS2, temp_aBRP, temp_abRP]
                        )
                        # self.log.debug(
                        #     "[Debug]: Found arbitration matches: [temp_aSJW: {}, aBS1: {}, aBS2: {}, aBRP: {}, abRP: {}]".format(
                        #         temp_aSJW, temp_aBS1, temp_aBS2, temp_aBRP, temp_abRP
                        #     )
                        # )

        data_matches = []
        for temp_dBS1 in BS1_range:
            for temp_dBS2 in BS2_range:
                for temp_dBRP in BRP_range:
                    temp_dbRP = self.f_clock / (
                        (temp_dBRP + 1) * (temp_dBS1 + temp_dBS2 + 1)
                    )
                    if temp_dbRP == self.dbRP:
                        temp_dSJW = min(temp_dBS1, temp_dBS2)
                        temp_dBRP += 1
                        data_matches.append(
                            [temp_dSJW, temp_dBS1, temp_dBS2, temp_dBRP, temp_dbRP]
                        )
                        # self.log.debug(
                        #     "[Debug]: Found data matches: [temp_dSJW: {}, dBS1: {}, dBS2: {}, dBRP: {}, dbRP: {}]".format(
                        #         temp_dSJW, temp_dBS1, temp_dBS2, temp_dBRP, temp_dbRP
                        #     )
                        # )

        final_matches = []
        cnt = 0

        for arb_param_match in arbitration_matches:
            temp_aSJW, temp_aBS1, temp_aBS2, temp_aBRP, temp_abRP = arb_param_match
            for data_param_match in data_matches:
                temp_dSJW, temp_dBS1, temp_dBS2, temp_dBRP, temp_dbRP = data_param_match

                if temp_aBRP == temp_dBRP:
                    # final_matches.append([temp_aSJW, temp_aBS1, temp_aBS2, temp_aBRP, temp_abRP, temp_dSJW, temp_dBS1, temp_dBS2, temp_dBRP, temp_dbRP])

                    if cnt >= len(self.aSJW):
                        self.aSJW.append(0)
                        self.aBS1.append(0)
                        self.aBS2.append(0)
                        self.aBRP.append(0)
                        self.dSJW.append(0)
                        self.dBS1.append(0)
                        self.dBS2.append(0)
                        self.dBRP.append(0)

                    self.aSJW[cnt] = temp_aSJW
                    self.aBS1[cnt] = temp_aBS1
                    self.aBS2[cnt] = temp_aBS2
                    self.aBRP[cnt] = temp_aBRP
                    self.dSJW[cnt] = temp_dSJW
                    self.dBS1[cnt] = temp_dBS1
                    self.dBS2[cnt] = temp_dBS2
                    self.dBRP[cnt] = temp_dBRP
                    # self.log.debug("[Debug]: Found final matches: [aSJW: {}, aBS1: {}, aBS2: {}, aBRP: {}, abRP: {}, dSJW: {}, dBS1: {}, dBS2: {}, dBRP: {}, dbRP: {}]".format(temp_aSJW, temp_aBS1, temp_aBS2, temp_aBRP, temp_abRP, temp_dSJW, temp_dBS1, temp_dBS2, temp_dBRP, temp_dbRP))
                    cnt += 1

        self.is_initialized = True

    def get_can_timing_parameter_aSJW(self, count: int):
        return self.aSJW[count]

    def get_can_timing_parameter_aBS1(self, count: int):
        return self.aBS1[count]

    def get_can_timing_parameter_aBS2(self, count: int):
        return self.aBS2[count]

    def get_can_timing_parameter_aBRP(self, count: int):
        return self.aBRP[count]

    def get_can_timing_parameter_dSJW(self, count: int):
        return self.dSJW[count]

    def get_can_timing_parameter_dBS1(self, count: int):
        return self.dBS1[count]

    def get_can_timing_parameter_dBS2(self, count: int):
        return self.dBS2[count]

    def get_can_timing_parameter_dBRP(self, count: int):
        return self.dBRP[count]
