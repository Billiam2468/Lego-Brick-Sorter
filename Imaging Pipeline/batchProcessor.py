import uuid
import random

#For each imag with a unique id, want to generate a unique string (this might have to go in the helper.py function and return it)
x= str(uuid.UUID(int=random.getrandbits(128), version=4))

print(x)