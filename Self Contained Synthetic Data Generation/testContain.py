import sys, os

scriptPath = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)

print(scriptName)
scriptPath = scriptPath.removesuffix(scriptName)
print("renders would be at: ")
print(scriptPath + "Renders/")