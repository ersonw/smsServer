import _thread
import logging
import time
import traceback

import serial

import collections

from serial import SerialException

from util.Data import Data
from util.usb_serial import USBSerial, WSSerial


def get_list():
    ports_list = list(serial.tools.list_ports.comports())
    ports = []
    for comport in ports_list:
        # print(list(comport)[0], list(comport)[1])
        name = f"{list(comport)[1]}".upper()
        if "USB" in name and "SERIAL" in name:
            ports.append(list(comport)[0])
    return ports


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    WSSerial()
    coms = []
    ports = get_list()
    try:
        while True:
            for port in ports:
                _thread.start_new_thread(USBSerial, (port,))
            time.sleep(30)
    except SerialException as e:
        print(e)
    except:
        traceback.print_exc()
