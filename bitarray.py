# Important!!!!!
# This code is just ported and adapted from the decompiled minecraft source
# This means it has questionable copyright
# Maybe a re-write is in order?

from math import floor

def inclusiveBetween(start, end, value):
   if value < start or value > end:
      raise ValueError("The value %i is not in the specified inclusive range of %i to %i" % (value, start, end))

weirdArray = [-1, -1, 0, -2147483648, 0, 0, 1431655765, 1431655765, 0, -2147483648, 0, 1, 858993459, 858993459, 0, 715827882, 715827882, 0, 613566756, 613566756, 0, -2147483648, 0, 2, 477218588, 477218588, 0, 429496729, 429496729, 0, 390451572, 390451572, 0, 357913941, 357913941, 0, 330382099, 330382099, 0, 306783378, 306783378, 0, 286331153, 286331153, 0, -2147483648, 0, 3, 252645135, 252645135, 0, 238609294, 238609294, 0, 226050910, 226050910, 0, 214748364, 214748364, 0, 204522252, 204522252, 0, 195225786, 195225786, 0, 186737708, 186737708, 0, 178956970, 178956970, 0, 171798691, 171798691, 0, 165191049, 165191049, 0, 159072862, 159072862, 0, 153391689, 153391689, 0, 148102320, 148102320, 0, 143165576, 143165576, 0, 138547332, 138547332, 0, -2147483648, 0, 4, 130150524, 130150524, 0, 126322567, 126322567, 0, 122713351, 122713351, 0, 119304647, 119304647, 0, 116080197, 116080197, 0, 113025455, 113025455, 0, 110127366, 110127366, 0, 107374182, 107374182, 0, 104755299, 104755299, 0, 102261126, 102261126, 0, 99882960, 99882960, 0, 97612893, 97612893, 0, 95443717, 95443717, 0, 93368854, 93368854, 0, 91382282, 91382282, 0, 89478485, 89478485, 0, 87652393, 87652393, 0, 85899345, 85899345, 0, 84215045, 84215045, 0, 82595524, 82595524, 0, 81037118, 81037118, 0, 79536431, 79536431, 0, 78090314, 78090314, 0, 76695844, 76695844, 0, 75350303, 75350303, 0, 74051160, 74051160, 0, 72796055, 72796055, 0, 71582788, 71582788, 0, 70409299, 70409299, 0, 69273666, 69273666, 0, 68174084, 68174084, 0, -2147483648, 0, 5]

'''
This class was ported from the Minecraft source. Minecraft stores block and heightmap data in compacted arrays of longs. This class does the proper index mapping and bit shifting to get to the actual data.
'''
class BitArray:
   def __init__(self, bitsPerEntryIn, arraySizeIn, data):
      inclusiveBetween(1, 32, bitsPerEntryIn)
      self.arraySize = arraySizeIn
      self.bitsPerEntry = bitsPerEntryIn
      self.maxEntryValue = (1 << bitsPerEntryIn) - 1
    #   self.field_232982_f_ = (char)(64 / bitsPerEntryIn)
      self.entriesPerLong = floor(64 / bitsPerEntryIn)
      i = 3 * (self.entriesPerLong - 1)
      self.someKindaInterval = weirdArray[i + 0]
      self.lengthyBits = weirdArray[i + 1]
      self.lengthyBitOffset = weirdArray[i + 2]
      j = floor((arraySizeIn + self.entriesPerLong - 1) / self.entriesPerLong)
      if (data != None):
         if (len(data) != j):
            raise Exception("Invalid length given for storage, got: %s but expected: %s" % (len(data), j))

         self.longArray = data
      else:
         self.longArray = [] #new long[j]
      

   

   def getPosOfLong(self, index):
    #   i = Integer.toUnsignedong(self.field_232983_g_)
      i = self.someKindaInterval % (1<<64)
    #   j = Integer.toUnsignedong(self.field_232984_h_)
      j = self.lengthyBits % (1<<64)
      return index * i + j >> 32 >> self.lengthyBitOffset
   

   def swapAt(self, index, value):
      inclusiveBetween(0, (self.arraySize - 1), index)
      inclusiveBetween(0, self.maxEntryValue, value)
      i = self.getPosOfLong(index)
      j = self.longArray[i]
      k = (index - i * self.entriesPerLong) * self.bitsPerEntry
      l = (j >> k & self.maxEntryValue)
      self.longArray[i] = j & ~(self.maxEntryValue << k) | (value & self.maxEntryValue) << k
      return l
   

   '''
    * Sets the entry at the given location to the given value
   '''
   def setAt(self, index, value):
      inclusiveBetween(0, (self.arraySize - 1), index)
      inclusiveBetween(0, self.maxEntryValue, value)
      i = self.getPosOfLong(index)
      j = self.longArray[i]
      k = (index - i * self.entriesPerLong) * self.bitsPerEntry
      self.longArray[i] = j & ~(self.maxEntryValue << k) | (value & self.maxEntryValue) << k
   

   '''
    * Gets the entry at the given index
   '''
   def getAt(self, index):
      inclusiveBetween(0, (self.arraySize - 1), index)
      i = self.getPosOfLong(index)
      j = self.longArray[i]
      k = (index - i * self.entriesPerLong) * self.bitsPerEntry
      return (j >> k & self.maxEntryValue)
   

   '''
    * Gets the array that is used to store the data in this BitArray. This is useful for sending packet data.
   '''
   def getBackingongArray(self):
      return self.longArray
   

   def size(self):
      return self.arraySize
   

   def getAll(self, consumer):
      i = 0

      for j in self.longArray:
         for k in range(self.entriesPerLong):
            consumer(j & self.maxEntryValue)
            j >>= self.bitsPerEntry
            i += 1
            if (i >= self.arraySize):
               return
