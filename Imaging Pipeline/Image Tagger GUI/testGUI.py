
# NOTE: CHANGE THE 4S TO 5S WHEN USING A REAL MODEL. 4 BECAUSE OUR MODEL ONLY RETURNS 4 OUTPUTS

import tkinter as tk
from functools import partial
from PIL import ImageTk, Image
import os  
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import batchProcessor as batch
import shutil
import tensorflow as tf
from tensorflow import keras

window = tk.Tk()
window.geometry("800x800")

print("window width is:", window.winfo_width)

window.mainloop()