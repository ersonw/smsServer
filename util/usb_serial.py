import _thread
import asyncio
import collections
import logging
import socket
import time
import traceback
import serial.tools.list_ports
import serial
import websocket
from _distutils_hack import override
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from websocket import ABNF, WebSocketTimeoutException, WebSocketConnectionClosedException, WebSocketException

from util.Data import Data
from util.http import Http

READ_MAX_LENGHT = 12
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # filename="./log.txt"
)
logger = logging.getLogger(__name__)
list_port = collections.deque()


class USBSerial:
    def __init__(self, port, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=1,
                 xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, ):
        global list_port
        for lp in list_port:
            if lp.port is port:
                return
        list_port.append(self)
        self.read_thread = None
        self.loop = asyncio.new_event_loop()
        self.port = port
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            xonxoff=xonxoff,
            rtscts=rtscts,
            write_timeout=write_timeout,
            dsrdtr=dsrdtr,
            inter_byte_timeout=inter_byte_timeout,
        )
        if not self.ser.isOpen():
            logger.error(f"{port}打开串口失败")
            return
        logger.info(f"{port}串口打开成功")
        self.reconnect = 0

        def on_open(w):
            self.reconnect = 0
            self.ws_send(msg=f'{self.reconnect}')

        config = None
        while config is None:
            try:
                config = Http.auth()
            except Exception as e:
                logger.error(e)
                logger.error("获取主控配置失败，10秒后重新获取.....")
                time.sleep(10)

        token = config["token"]
        logger.info(config)
        if not f'{config["ws"]}'.endswith('/'):
            center_url = f'{config["ws"]}/sms/{token}'
        else:
            center_url = f'{config["ws"]}sms/{token}'
        if center_url is None or token is None:
            logger.error("无法启动节点，缺少服务端配置")
            return
        Http.token = token
        self.ws = websocket.WebSocketApp(
            f"{center_url}",
            on_open=on_open,
            on_data=lambda w, s, t, f: self.on_data(s, t, f),
            # on_error=lambda w, error: on_error(error),
            # on_close=lambda w, close_status_code, close_msg: on_error(f"{close_status_code}-{close_msg}")
        )
        while True:
            try:
                if self.reconnect == 0:
                    logging.info("正在进行首次连接......")
                if not self.ws.keep_running:
                    self.ws.run_forever()
                self.ws.close()
                self.reconnect += 1
                logger.error(f"连接已关闭，10秒后重试第{self.reconnect + 1}次连接")
                time.sleep(10)
            except KeyboardInterrupt:
                print("主动关闭")
                self.ws.close()
                break
            except:
                traceback.print_exc()
                time.sleep(3)
        self.destroy()

    def on_data(self, s, t, f):
        if t == ABNF.OPCODE_BINARY:
            data = Data().from_bytes(s)
            logger.info(data.to_json())

    def ws_send(self, code=0, msg=None, data=None):
        if self.ws.keep_running:
            d = Data(code=code, msg=msg, data=data)
            self.ws.send(d.to_bytes(), opcode=ABNF.OPCODE_BINARY)
            logger.info(f"{d.to_json()} 发送成功!")

    def write_handler(self, msg):
        if not self.ser.isOpen():
            return
        self.ser.write(f"{msg}\r".encode('utf-8'))
        logger.info(f"写入串口[{msg}]")

    def read_handler(self, handler):
        if self.read_thread:
            return
        self.read_thread = _thread.start_new_thread(self.read_always, (handler,))

    def read_msg(self):
        msg = bytearray()
        buff = self.ser.read(READ_MAX_LENGHT)
        while buff:
            msg.extend(bytearray(buff))
            buff = self.ser.read(READ_MAX_LENGHT)
        return msg

    def read_always(self, handler):
        while self.ser.isOpen():
            msg = self.read_msg()
            if msg:
                logger.info(f"msg: {str(msg)}")
                if callable(handler):
                    msg = self.read_msg()
                    handler(msg)
            time.sleep(3)

    def destroy(self):
        self.ser.close()
        self.loop.close()
        self.ws.close()
        global list_port
        list_port.remove(self)
