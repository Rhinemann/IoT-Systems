import os

SUDO = os.environ.get("SUDO", None) or "sudo"

class UARTReader:
    def __init__(self, port = None):
        if port == None:
            # testing mode
            pass
        else:
            # configure TTY
            os.system(f"{SUDO} stty -F {port} 1:0:8bf:0:3:1c:7f:15:4:5:1:0:11:13:1a:0:12:f:17:16:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0")
            self.port = open(port, "rb")

            self.i = 0
            self.d = 0
            self.state = 0
            self.data = bytearray(6)

    def close(self):
        self.port.close()

    def __to_int(self, x):
        if x >= 0x8000:
            return x - 0x10000
        else:
            return x

    def __frame_seek(self, byte):
        if byte == 0xFF:
            self.i += 1

        if self.i >= 10 and byte != 0xFF:
            self.i = 0

            self.data[self.d] = byte
            self.d = 1

            self.state = 1

    def __data_read(self, byte):
        self.data[self.d] = byte

        self.d += 1

        if self.d >= 6:
            self.d = 0
            self.state = 2

    def read_next(self):
        while True:
            b = self.port.read(1)

            if not b:
                self.close()
                return None

            if self.state == 0:
                self.__frame_seek(b[0])
            elif self.state == 1:
                self.__data_read(b[0])

            if self.state == 2:
                self.state = 0

                return (self.__to_int(self.data[0] + (self.data[1] << 8)),
                        self.__to_int(self.data[2] + (self.data[3] << 8)),
                        self.__to_int(self.data[4] + (self.data[5] << 8)))
