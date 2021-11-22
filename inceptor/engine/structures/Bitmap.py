from binascii import hexlify
from struct import pack, unpack


class BitmapFileHeader:
    def __init__(self, size: int, offset: int):
        self.header_field = pack("BB", 0x42, 0x4d)
        self.size = pack("<I", size)
        self.reserved1 = pack("H", 0)
        self.reserved2 = pack("H", 0)
        self.offset = pack("<I", offset)

    def from_data(self, data):
        self.header_field = data[:2]
        self.size = data[2:6]
        self.reserved1 = data[6:8]
        self.reserved2 = data[8:10]
        self.offset = data[10:14]

    def to_bytes(self):
        return self.header_field + self.size + self.reserved1 + self.reserved2 + self.offset

    def to_dict(self):
        return {
            "Header Field": self.header_field,
            "R1": unpack("<I", self.reserved1)[0],
            "R2": unpack("<I", self.reserved2)[0],
            "Size": unpack("<I", self.size)[0],
            "Offset": unpack("<I", self.offset)[0],
        }


class DibHeader:
    def __init__(self, size):
        # We want to have a square
        square = 2
        while pow(square, 2) < size:
            square = square * 2
        self.header_size = pack("<I", 40)
        self.width = pack("<I", square)
        self.height = pack("<I", square)
        self.color_planes = pack("H", 0x1)
        self.bites_per_pixel = pack("H", 32)
        self.compression = pack("<I", 0)
        self.size = pack("<I", size)
        self.horizontal_resolution = pack("<I", 4 * pow(10, 4))
        self.vertical_resolution = pack("<I", 4 * pow(10, 4))
        self.number_of_colors = pack("<I", 0)
        self.number_of_important_colors = pack("<I", 0)

    def from_data(self, data):
        self.header_size = data[:4]
        self.width = data[4:8]
        self.height = data[8:12]
        self.color_planes = data[12:14]
        self.bites_per_pixel = data[14:16]
        self.compression = data[16:20]
        self.size = data[20:24]
        self.horizontal_resolution = data[24:28]
        self.vertical_resolution = data[28:32]
        self.number_of_colors = data[32:36]
        self.number_of_important_colors = data[36:40]

    def to_bytes(self):
        return self.header_size + self.width + self.height + self.color_planes + self.bites_per_pixel + \
               self.compression + self.size + self.horizontal_resolution + self.vertical_resolution + \
               self.number_of_colors + self.number_of_important_colors

    def to_dict(self):
        return {
            "Header Size": unpack("<I", self.header_size)[0],
            "Width": unpack("<I", self.width)[0],
            "Height": unpack("<I", self.height)[0],
            "Color Planes": unpack("H", self.color_planes)[0],
            "Bits per Pixel": unpack("H", self.bites_per_pixel)[0],
            "Compression": unpack("<I", self.compression)[0],
            "Size": unpack("<I", self.size)[0],
            "H-Res": unpack("<I", self.horizontal_resolution)[0],
            "V-Res": unpack("<I", self.vertical_resolution)[0],
            "Number of Colors": unpack("<I", self.number_of_colors)[0],
            "Number of Important Colors": unpack("<I", self.number_of_important_colors)[0]
        }


class BMP:
    def __init__(self, pixels: bytes, bfh_size=0, bfh_offset=0, bfh=False):
        self.bfh = bfh
        self.__bitmapFileHeader = None
        if bfh:
            self.__bitmapFileHeader = BitmapFileHeader(bfh_size, bfh_offset)
        self.__dib_header = DibHeader(size=len(pixels))
        self.__opt_extrabit_mask = None
        self.__color_table = None
        self.__gap1 = None
        self.__pixel_array = pixels
        self.__gap2 = b"\x90" * (4 - len(pixels) % 4)
        self.__icc_color_profile = None

    def to_bytes(self):
        return self.__dib_header.to_bytes() + self.__pixel_array + self.__gap2

    def from_data(self, data, bfh=False):
        offset = 0
        if bfh:
            self.__bitmapFileHeader.from_data(data)
            offset = 14
        self.__dib_header.from_data(data[offset:])
        offset += unpack("<I", self.__dib_header.header_size)[0]
        # Might land to an error here
        # But implementing the parsing logic here is a pain
        gap2_length = 4 - (len(data[offset:]) % 4)
        self.__pixel_array = data[offset:-gap2_length]
        self.__gap2 = self.__pixel_array[-gap2_length:]

    def to_dict(self):
        return {
            "Bitmap File Header": self.__bitmapFileHeader if self.bfh else "None",
            "DIB Header": self.__dib_header.to_dict(),
            "Extrabit Mask": self.__opt_extrabit_mask if self.__opt_extrabit_mask else "None",
            "Color table": self.__color_table if self.__color_table else "None",
            "Gap1": hexlify(self.__gap1).decode() if self.__gap1 else "None",
            "Pixel Array": hexlify(self.__pixel_array[:10]).decode() if self.__pixel_array else "None",
            "Gap2": hexlify(self.__gap2).decode() if self.__gap2 else "None",
            "ICC Color profile": self.__icc_color_profile if self.__icc_color_profile else "None"
        }


