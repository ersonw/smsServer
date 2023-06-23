import uuid
import tempfile


def temp_file(data):
    # print(len(data))
    fp = tempfile.TemporaryFile()
    fp.write(data)
    fp.seek(0)
    # fp.flush()
    print(fp.name)
    return fp


def get_mac_address():
    """
    获取本机物理地址，获取本机mac地址
    :return:
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return "-".join([mac[e:e + 2] for e in range(0, 11, 2)])
