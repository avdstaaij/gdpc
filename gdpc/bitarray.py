#! /usr/bin/python3
"""### Read the bitarray format used by Minecraft."""
__all__ = ['BitArray']
__version__ = 'v5.0'

from math import floor


def inclusiveBetween(start, end, value):
    """**Raise an exception when the value is out of bounds**."""
    if not (start <= value <= end):
        raise ValueError(
            f"The value {value} is not in the inclusive range "
            f"of {start} to {end}")


class BitArray:
    """**Store an array of binary values and its metrics**.

    Minecraft stores block and heightmap data in compacted arrays of longs.
    This class performs index mapping and bit shifting to access the data.
    """

    def __init__(self, bitsPerEntryIn, arraySizeIn, data):
        """**Initialise a BitArray**."""
        inclusiveBetween(1, 32, bitsPerEntryIn)
        self.arraySize = arraySizeIn
        self.bitsPerEntry = bitsPerEntryIn
        self.maxEntryValue = (1 << bitsPerEntryIn) - 1
        self.entriesPerLong = floor(64 / bitsPerEntryIn)
        j = floor((arraySizeIn + self.entriesPerLong - 1)
                  / self.entriesPerLong)
        if data is not None:
            if len(data) != j:
                raise Exception(
                    "Invalid length given for storage, "
                    f"got: {len(data)} but expected: {j}")

            self.longArray = data
        else:
            self.longArray = []  # length j

    # __repr__ displays the class well enough so __str__ is omitted
    def __repr__(self):
        """**Represent the BitArray as a constructor**."""
        return f"BitArray{(self.bitsPerEntry, self.arraySize, self.longArray)}"

    def getPosOfLong(self, index):
        """**Return the position of the long that contains index**."""
        return index // self.entriesPerLong

    def getAt(self, index):
        """**Return the binary value stored at index.**."""
        inclusiveBetween(0, (self.arraySize - 1), index)
        i = self.getPosOfLong(index)
        j = self.longArray[i]
        k = (index - i * self.entriesPerLong) * self.bitsPerEntry
        return j >> k & self.maxEntryValue

    def size(self):
        """**Return self.arraySize**."""
        return self.arraySize
