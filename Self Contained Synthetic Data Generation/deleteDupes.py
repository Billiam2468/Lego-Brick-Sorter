from collections import OrderedDict
import os

# Make contained (only need to set the models path):
base_path = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)
#base_path = base_path.removesuffix(scriptName)
base_path = base_path[:-14]
input_file = base_path + "dupes.txt"

with open(input_file, "r") as fp:
    lines = fp.readlines()
    new_lines = []
    dupes = []
    for line in lines:
        #- Strip white spaces
        line = line.strip()
        if line not in new_lines:
            new_lines.append(line)
        else:
            dupes.append(line)

print(dupes)
print("length is")
print(len(dupes))

# items = ['Mango', 'Orange', 'Apple', 'Lemon']
# file = open('items.txt','w')
# for the item in items:
# 	file.write(item+"\n")
# file.close()

file = open(base_path + "newPieces.txt", 'w')
for line in new_lines:
    file.write(line+"\n")
file.close()