import asyncio
import logging

import serial
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE


class USBSerial:
    def __init__(self, port, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None,
                 xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, ):
        self.loop = asyncio.new_event_loop()
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
            logging.error(f"{port}打开串口失败")
            return
        logging.info(f"{port}串口打开成功")
