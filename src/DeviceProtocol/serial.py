import serial
import time
try:
        from src.tools.log import Log
except:
        from tools.log import Log
from typing import Callable
import platform


class SerialControler:
        def __init__(self):
                super(SerialControler, self).__init__()
                self.interConnStatus = False
                self.log = Log('Log')
                self.instance = None
                self.connStatusCallback = None
        
        def __notifyConnStatus(self, status: bool):
                if self.connStatusCallback is not None:
                        try:
                                self.connStatusCallback(status)
                        except Exception as e:
                                print(f"回调函数执行失败：{e}")
        
        def registerConnCallback(self, callback: Callable[[bool], None]):
                self.connStatusCallback = callback
                
        def open(self, portName, br):
                try:
                        self.instance = serial.Serial(port = portName, baudrate = br)
                        self.__notifyConnStatus(True)
                        self.log.debug('successed to connect', portName)
                        return True
                except serial.serialutil.SerialException as e:
                        self.log.error('failed to connect', portName, e)
                        return e
        
        def getInstance(self):
                return self.instance
        
        def close(self):
                if self.checkStatus() == True:
                        self.instance.close()
                        self.log.debug('com is closed')
                self.__notifyConnStatus(False)
                
        def checkStatus(self):
                if self.instance == None:
                        return False
                else:
                        return self.instance.is_open
        
        def getCOMS(self):
                ports = serial.tools.list_ports.comports()
                coms = []
                systype = platform.system()
                for com in ports:
                        if systype == 'Linux':
                                if com.name.__contains__('ttyUSB') or com.name.__contains__('ttyACM'):
                                        coms.append('{}|{}'.format(com.device, com.description.split('(')[0]))
                        elif systype == 'Windows':
                                if com.name.__contains__('COM'):
                                        coms.append('{}|{}'.format(com.device, com.description.split('(')[0]))
                        elif systype == 'Darwin':
                                if coms.name.__contains__('cu'):
                                        coms.append('{}|{}'.format(com.device, com.description.split('(')[0]))
                return coms
        
        def read(self):
                data = b''
                try:
                        data = self.instance.read_all()
                except BaseException as e:
                        self.log.error(e)
                        self.close()
                return data
        
        def writeString(self, text:str):
                try:
                        self.instance.write(text.encode())
                except BaseException as e:
                        self.log.error(e)
                        self.close()
                        
        def writeBytes(self, bArray:bytes):
                try:
                        self.instance.write(bArray)
                except BaseException as e:
                        self.log.error(e)
                        self.close()
        
        def test(self):
                print('test!')                 
                                