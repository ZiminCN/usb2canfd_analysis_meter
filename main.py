import src.tools.log as Log
import src.DeviceProtocol.serial as SerialControler

def test_func():
        print("test_func")
        serial_controller = SerialControler.SerialControler()
        # SerialControler.open('tty.usbserial-1140', 115200)
        serial_controller.test()
        
if __name__ == '__main__':
        test_func()