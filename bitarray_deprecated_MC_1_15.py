from math import ceil

def inclusiveBetween(start, end, value):
   if value < start or value > end:
      raise ValueError("The value %i is not in the specified inclusive range of %i to %i" % (value, start, end))

class BitArray:
#    long[] longArray
#    bitsPerEntry
#    maxEntryValue
#    arraySize

#    public BitArray(bitsPerEntryIn, arraySizeIn):
#       this(bitsPerEntryIn, arraySizeIn, new long[MathHelper.roundUp(arraySizeIn * bitsPerEntryIn, 64) / 64])

   def __init__(self, bitsPerEntryIn, arraySizeIn, data):
      if bitsPerEntryIn < 1 or bitsPerEntryIn > 32:
          raise ValueError("bitsPerEntryIn must be between 1 and 32 (inclusive)")
      self.arraySize = arraySizeIn
      self.bitsPerEntry = bitsPerEntryIn
      self.longArray = [num % (1<<64) for num in data] # convert negative 'longs' to positive python ints
      self.maxEntryValue = (1 << bitsPerEntryIn) - 1
      
    #   i = roundUp(arraySizeIn * bitsPerEntryIn, 64) / 64
      i = ((arraySizeIn * bitsPerEntryIn - 1) >> 6) + 1
      if (len(data) != i):
         raise Exception("Invalid length given for storage, got: %i but expected: %i" % (len(data), i))


   def swapAt(self, index, value):
      inclusiveBetween(0, (self.arraySize - 1), index)
      inclusiveBetween(0, self.maxEntryValue, value)
      i = index * self.bitsPerEntry
      j = i >> 6
      k = (index + 1) * self.bitsPerEntry - 1 >> 6
      l = i ^ j << 6
      i1 = 0
      i1 = i1 | (self.longArray[j] >> l & self.maxEntryValue)
      self.longArray[j] = self.longArray[j] & ~(self.maxEntryValue << l) | (value & self.maxEntryValue) << l
      if (j != k):
         j1 = 64 - l
         k1 = self.bitsPerEntry - j1
         i1 |= (self.longArray[k] << j1 & self.maxEntryValue)
         self.longArray[k] = self.longArray[k] >> k1 << k1 | (value & self.maxEntryValue) >> j1

      return i1

   '''
    * Sets the entry at the given location to the given value
   '''
   def setAt(self, index, value):
      inclusiveBetween(0, (self.arraySize - 1), index)
      inclusiveBetween(0, self.maxEntryValue, value)
      i = index * self.bitsPerEntry
      j = i >> 6
      k = (index + 1) * self.bitsPerEntry - 1 >> 6
      l = i ^ j << 6
      self.longArray[j] = self.longArray[j] & ~(self.maxEntryValue << l) | (value & self.maxEntryValue) << l
      if (j != k):
         i1 = 64 - l
         j1 = self.bitsPerEntry - i1
         self.longArray[k] = self.longArray[k] >> j1 << j1 | (value & self.maxEntryValue) >> i1


   '''
    * Gets the entry at the given index
   '''
   def getAt(self, index):
      inclusiveBetween(0, (self.arraySize - 1), index)
      i = index * self.bitsPerEntry
      j = i >> 6
      k = (index + 1) * self.bitsPerEntry - 1 >> 6
      l = i ^ j << 6
      if (j == k):
         return (self.longArray[j] >> l & self.maxEntryValue)
      else:
         i1 = 64 - l
         return ((self.longArray[j] >> l | self.longArray[k] << i1) & self.maxEntryValue)

   '''
    * Gets the array that is used to store the data in this BitArray. This is useful for sending packet data.
   '''
   def getBackingLongArray(self):
      return self.longArray

   def size(self):
      return self.arraySize

   def getBitsPerEntry(self):
      return self.bitsPerEntry

   def getAll(self, consumer):
      i = len(self.longArray)
      if (i != 0):
         j = 0
         k = self.longArray[0]
         l = self.longArray[1] if i > 1 else 0

         for i1 in range(self.arraySize):
            j1 = i1 * self.bitsPerEntry
            k1 = j1 >> 6
            l1 = (i1 + 1) * self.bitsPerEntry - 1 >> 6
            i2 = j1 ^ k1 << 6
            if (k1 != j):
               k = l
               l = self.longArray[k1 + 1] if k1 + 1 < i else 0
               j = k1

            if (k1 == l1):
               consumer((k >> i2 & self.maxEntryValue)) # keep an eye on that first shift?
            else:
               j2 = 64 - i2
               consumer(((k >> i2 | l << j2) & self.maxEntryValue)) # keep an eye on that first shift?

