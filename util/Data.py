import json
import pickle


class Data:
    def __init__(self,
                 code=0,
                 msg=None,
                 data=None,
                 ):
        self.code = code
        self.msg = msg
        self.data = data

    def __str__(self):
        return json.dumps(self.to_json())

    def to_bytes(self):
        code_bytes = self.code.to_bytes(4, byteorder="big")
        message_bytes = bytearray()
        if self.msg:
            message_bytes = bytearray(bytes(self.msg, encoding="utf8"))
        message_len = len(message_bytes)
        # data_bytes = pickle.dumps(self.message)
        data_bytes = bytearray()
        if self.data:
            data_bytes = bytearray(bytes(self.data, encoding="utf8"))
        data_len = len(data_bytes)

        byte_arr = bytearray(code_bytes)
        byte_arr.extend(message_len.to_bytes(4, byteorder="big"))
        byte_arr.extend(message_bytes)
        byte_arr.extend(data_len.to_bytes(4, byteorder="big"))
        byte_arr.extend(data_bytes)

        return byte_arr

    @staticmethod
    def from_bytes(b):
        offset = 0
        length = 4
        if len(b) < length:
            return None
        code = int.from_bytes(b[offset:length], byteorder="big")
        offset += 4
        length += 4

        if len(b) < length:
            return Data(code=code)
        message_len = int.from_bytes(b[offset:length], byteorder="big")
        offset += 4
        length += message_len
        if len(b) < length:
            return Data(code=code)
        message = str(b[offset:length], encoding="utf8")
        offset += message_len
        length += 4

        if len(b) < length:
            return Data(code=code, msg=message)
        data_len = int.from_bytes(b[offset:length], byteorder="big")
        offset += 4
        length += data_len

        if len(b) < length:
            return Data(code=code, msg=message)
        data = str(b[offset:length], encoding="utf8")

        return Data(code=code, msg=message, data=data)

    def to_json(self):
        dj = json.loads('{}')
        dj['code'] = self.code
        dj['msg'] = self.msg
        dj['data'] = self.data
        return dj

    @staticmethod
    def from_json(dj=None):
        if not dj:
            return None
        code = 0
        msg = None
        data = None
        if 'code' in json.dumps(dj):
            code = dj['code']
        if 'msg' in json.dumps(dj):
            msg = dj['msg']
        if 'data' in json.dumps(dj):
            data = dj['data']
        return Data(code=code, msg=msg, data=data)
