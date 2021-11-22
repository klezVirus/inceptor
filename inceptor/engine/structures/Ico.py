import json
import sys
from struct import pack, unpack

try:
    from engine.structures.Bitmap import BMP
except:
    from Bitmap import BMP


class IconDirectoryEntryFormatException(Exception):
    pass


class IconDirEntry:
    def __init__(self, size):
        square = 2
        while pow(square, 2) < size:
            square = square * 2
            if square > 128:
                square = 128
                break
        self.width = square
        self.height = square
        self.n_colors = 0
        self.reserved = 0
        self.color_planes = 1
        self.bits_per_pixel = 32
        self.size = size
        self.offset = 22

    def from_data(self, data):
        self.width = data[0]
        self.height = data[1]
        self.n_colors = data[2]
        # Reserved, should be 0
        # Although, the .NET icon encoder (System.Drawing.Icon.Save) sets this value to 255
        self.reserved = data[3]
        # ICO: 0 or 1
        # CUR: Horizontal Coordinates
        self.__colorPlanes = data[4:6]
        # ICO: bits per pixel
        # CUR: Vertical Coordinates
        self.__bitsPerPixel = data[6:8]
        self.__size = data[8:12]
        self.__offset = data[12:16]

    @property
    def width(self):
        return unpack("B", self.__width)[0]

    @width.setter
    def width(self, value: int):
        self.__width = pack("B", value)

    @property
    def height(self):
        return unpack("B", self.__height)[0]

    @height.setter
    def height(self, value: int):
        self.__height = pack("B", value)

    @property
    def n_colors(self):
        return unpack("B", self.__nColors)[0]

    @n_colors.setter
    def n_colors(self, value: int):
        self.__nColors = pack("B", value)

    @property
    def reserved(self):
        return unpack("B", self.__reserved)[0]

    @reserved.setter
    def reserved(self, value: int):
        self.__reserved = pack("B", value)

    @property
    def color_planes(self):
        return unpack("H", self.__colorPlanes)[0]

    @color_planes.setter
    def color_planes(self, value: int):
        self.__colorPlanes = pack("H", value)

    @property
    def horizontal_coordinates(self):
        return unpack("H", self.__colorPlanes)[0]

    @horizontal_coordinates.setter
    def horizontal_coordinates(self, value: int):
        self.__colorPlanes = pack("H", value)

    @property
    def bits_per_pixel(self):
        return unpack("H", self.__bitsPerPixel)[0]

    @bits_per_pixel.setter
    def bits_per_pixel(self, value: int):
        self.__bitsPerPixel = pack("H", value)

    @property
    def vertical_coordinates(self):
        return unpack("H", self.__bitsPerPixel)[0]

    @vertical_coordinates.setter
    def vertical_coordinates(self, value: int):
        self.__bitsPerPixel = pack("H", value)

    @property
    def size(self):
        return unpack("<I", self.__size)[0]

    @size.setter
    def size(self, value: int):
        self.__size = pack("<I", value)

    @property
    def offset(self):
        return unpack("<I", self.__offset)[0]

    @offset.setter
    def offset(self, value: int):
        self.__offset = pack("<I", value)

    def to_bytes(self):
        return self.__width + self.__height + self.__nColors + self.__reserved + self.__colorPlanes + self.__bitsPerPixel + self.__size + self.__offset

    def to_dict(self):
        return {
            "Width": self.width,
            "Height": self.height,
            "N Colors": self.n_colors,
            "Reserved": self.reserved,
            "Color Planes": self.color_planes,
            "Bites per Pixel": self.bits_per_pixel,
            "Size": self.size,
            "Offset": self.offset
        }


class ImageDirectoryTable:
    def __init__(self):
        self.image_directory_entries = []

    def append(self, ide: IconDirEntry):
        self.image_directory_entries.append(ide)

    def from_data(self, data):
        if len(data) % 16 != 0:
            raise IconDirectoryEntryFormatException
        for i in range(0, len(data), 16):
            id_entry = IconDirEntry(0)
            id_entry.from_data(data[i:i+16])
            self.image_directory_entries.append(id_entry)

    def to_dict(self):
        d = {}
        for i, entry in enumerate(self.image_directory_entries, start=0):
            d[f"#{i}"] = entry.to_dict()
        return d

    def to_bytes(self):
        return b"".join([ide.to_bytes() for ide in self.image_directory_entries])


class ImageTable:
    def __init__(self):
        self.image_entries = []

    def append(self, bmp: BMP):
        self.image_entries.append(bmp)

    def to_dict(self):
        d = {}
        for i, entry in enumerate(self.image_entries, start=0):
            d[f"#{i}"] = entry.to_dict()
        return d

    def to_bytes(self):
        return b"".join([ide.to_bytes() for ide in self.image_entries])

    def from_data(self, data, offsets: list):
        offsets.append(sys.maxsize)
        for i in range(len(offsets) - 1):
            bmp = BMP(pixels=b"")
            print(data[:50])
            bmp.from_data(data[offsets[i]:offsets[i+1]])
            print(bmp.to_dict())
            input()
            self.image_entries.append(bmp)



class ICO:
    def __init__(self, payload: bytes):
        # Reserved: Must be 0
        self.__reserved = pack("H", 0)
        # 1: ICO, 2: CUR
        self.__imageType = pack("H", 1)
        # Number of images in the ICO
        # We have just 1, our payload
        self.__nImages = pack("H", 1)

        # In order to "work" the image should be of a certain size
        payload += b"\x90"*(pow(2, 17)-len(payload))

        # IMAGE DIRECTORY
        self.__imageDirEntries = ImageDirectoryTable()
        self.__imageDirEntries.append(
            IconDirEntry(size=len(payload))
        )
        self.__imageEntries = ImageTable()
        self.__imageEntries.append(BMP(pixels=payload))

    def from_data(self, data):
        self.__reserved = data[0:2]
        self.__imageType = data[2:4]
        self.__nImages = data[4:6]
        self.__imageDirEntries = ImageDirectoryTable()
        self.__imageDirEntries.from_data(data=data[6:6+(16*self.n_images)])
        offsets = [ide.offset for ide in self.__imageDirEntries.image_directory_entries]
        self.__imageEntries = ImageTable()
        offset = 6+(16*self.n_images)
        print(f"Images Offset: {offset}")
        self.__imageEntries.from_data(data=data, offsets=offsets)

    @property
    def reserved(self):
        return unpack("H", self.__reserved)[0]

    @property
    def image_type(self):
        return unpack("H", self.__imageType)[0]

    @property
    def n_images(self):
        return unpack("H", self.__nImages)[0]

    def to_bytes(self):
        return self.__reserved + self.__imageType + self.__nImages + self.__imageDirEntries.to_bytes() + self.__imageEntries.to_bytes()

    def to_dict(self):
        return {
            "Reserved": self.reserved,
            "Image Type": self.image_type,
            "Number of Images": self.n_images,
            "Image Directory": self.__imageDirEntries.to_dict(),
            "Images": self.__imageEntries.to_dict(),
        }

    def save(self, filename):
        with open(filename, "wb") as saving:
            saving.write(self.to_bytes())


if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser(description="Test ICO parser")
    parser.add_argument("-i", "--infile", type=str, help="ICO File to parse")
    parser.add_argument("-p", "--payload", type=str, help="Payload File to embed in the ICO")
    parser.add_argument("-s", "--size", type=int, help="Add padding to the Payload till this size")
    parser.add_argument("-o", "--outfile", type=str, help="Output ICO File")
    args = parser.parse_args()

    if all([args.infile is None, args.outfile is None, args.payload is None]):
        parser.print_help()
        exit(1)

    if args.infile and os.path.isfile(args.infile):
        with open(args.infile, "rb") as infile:
            content = infile.read()
            ico = ICO(payload=b"")
            ico.from_data(content)
            print(json.dumps(ico.to_dict(), indent=2))

    if args.payload and os.path.isfile(args.payload):
        with open(args.payload, "rb") as infile:
            payload = infile.read()

            if args.size and args.size > len(payload):
                payload += b"\x90"*(args.size - len(payload))
            icon = ICO(payload=payload)
            print(icon.to_dict())
            print(json.dumps(icon.to_dict(), indent=2))
        if args.outfile:
            icon.save(args.outfile)
        with open(args.outfile, "rb") as infile:
            test = infile.read()
            if payload not in test:
                print("AAAAAAAAAAAAAAAAAARRGHH!?")