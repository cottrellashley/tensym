


class Buffer:
    def __init__(self, size: int):
        self.size = size
        self.data = bytearray(size)
        self.position = 0

    def write(self, bytes_data: bytes):
        length = len(bytes_data)
        if self.position + length > self.size:
            raise BufferError("Buffer overflow")
        self.data[self.position:self.position + length] = bytes_data
        self.position += length

    def read(self, length: int) -> bytes:
        if self.position + length > self.size:
            raise BufferError("Buffer underflow")
        bytes_data = self.data[self.position:self.position + length]
        self.position += length
        return bytes(bytes_data)

    def seek(self, position: int):
        if position < 0 or position > self.size:
            raise ValueError("Invalid buffer position")
        self.position = position

    def tell(self) -> int:
        return self.position

    def clear(self):
        self.data = bytearray(self.size)
        self.position = 0
