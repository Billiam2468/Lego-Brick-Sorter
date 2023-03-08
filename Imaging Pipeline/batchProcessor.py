import uuid
import random
import os

#For each imag with a unique id, want to generate a unique string (this might have to go in the helper.py function and return it)
# x= str(uuid.UUID(int=random.getrandbits(128), version=4))

# print(x)


class BatchProcessor:
    def __init__(self, imgPath):
        self.processed_ids = []
        self.imgPath = imgPath

    def nextBatch(self):
        for image in os.listdir(self.imgPath):
            uniqueId = image.removeprefix(".png")
            uniqueId = uniqueId.partition("_")[0]
            if uniqueId not in self.processed_ids:
                batch = [filename for filename in os.listdir(self.imgPath) if filename.startswith(uniqueId)]
                self.processed_ids.append(uniqueId)
                return batch
        return []
            

#NOTE: USAGE BELOW

# imgPath = "/home/billiam/Documents/Lego_Sorter/Renders/test/6091 (copy)/"

# batchProcessor = BatchProcessor(imgPath)

# while(True):
#     batch = batchProcessor.nextBatch()
#     if(len(batch) == 0):
#         print("no more batches. exiting while loop")
#         break
#     else:
#         print("there was stuff in the batch!")
#         print(batch)
# print("stored in the processor was")
# print(batchProcessor.processed_ids)