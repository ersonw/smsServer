import _thread
import logging

import serial
import serial.tools.list_ports
import collections
from util.usb_serial import USBSerial

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # filename="./log.txt"
)
logger = logging.getLogger(__name__)


def open_ser(device_name):
    ser = serial.Serial(device_name, 9600)  # 打开COM17，将波特率配置为115200，其余参数使用默认值
    if not ser.isOpen():  # 判断串口是否成功打开
        return
    write_len = ser.write("AT+CNUM\r".encode('utf-8'))
    print("串口发出{}个字节。".format(write_len))
    while True:
        com_input = ser.read(10)
        if com_input:  # 如果读取结果非空，则输出
            print(com_input)
    ser.close()


def get_list():
    ports_list = list(serial.tools.list_ports.comports())
    list_port = collections.deque()
    for comport in ports_list:
        # print(list(comport)[0], list(comport)[1])
        name = f"{list(comport)[1]}".upper()
        if "USB" in name and "SERIAL" in name:
            list_port.append(list(comport)[0])
    return list_port


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    list_port = get_list()
    try:
        while len(list_port) > 0:
            name = list_port.popleft()
            print(f"{name}")
            USBSerial(name)
            # try:
            #     _thread.start_new_thread(USBSerial, (name,))
            # except:
            #     logger.error(f"Error: 无法启动线程: {name}")
    except:
        print("已读取完成!")
