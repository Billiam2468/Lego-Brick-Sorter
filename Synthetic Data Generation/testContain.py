# import sys, os

# scriptPath = os.path.realpath(__file__)
# scriptName = os.path.basename(__file__)

# print(scriptName)
# scriptPath = scriptPath.removesuffix(scriptName)
# print("renders would be at: ")
# print(scriptPath + "Renders/")

# with open(scriptPath + "blacklist.txt") as f:
#     if "u9577" in f.read():
#         print("test")
#     print("end of with statement")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

table = pd.read_html("https://library.ldraw.org/tracker/search?s=%22moved+to%22&scope=header")

print("total tables", len(table))

df = table[1]
print(df.head())

for name in df['Part']:
    name = name.removeprefix("parts/")
    name = name.removeprefix("s/")
    name = name.removesuffix(".dat")
    print(name)