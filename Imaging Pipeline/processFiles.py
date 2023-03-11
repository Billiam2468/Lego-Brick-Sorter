import os
import collections


# Make contained (only need to set the models path):
base_path = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)
base_path = base_path.removesuffix(scriptName)

file = open(base_path + "pieces.txt")
pieceList = [line.rstrip("\n") for line in file.readlines()]
# dupes = [item for item, count in collections.Counter(pieceList).items() if count > 1]
# print(len(dupes))

res = []
[res.append(x) for x in pieceList if x not in res]
 
# printing list after removal
print ("The list after removing duplicates in order: "
       + str(res))