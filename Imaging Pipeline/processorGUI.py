import tkinter as tk
from functools import partial
from PIL import ImageTk, Image
import os

# Make contained (only need to set the models path):
base_path = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)
base_path = base_path.removesuffix(scriptName)

# This will be a list of the model suggested labels. The index chosen will be returned from choose()
# These will be different pieces since different guesses
suggested = ["test", "val", "here", "last", "one"]

# Batch of images to be displayed (should be same piee)
imgBatch = ["3184", "3070b", "3149", "3176"]

# Upon receiving a new batch of images, we will update these buttons (images) and labels (piece name) for the model suggestions
suggestButtons = []
suggestLabels = []

#DEFINE FUNCTIONS HERE:
def classify(entry):
    print("you chose", entry)

    # First check if val in textbox is valid. IF not, display msg asking to try again somehow?
    # Then move images into folder (or createand move if not exist)
    # Then get next batch of images
    #   Next batch entails: Updating suggested (what our model thinks the batch is)
    #                       Updating suggestButtons (image of model idea)
    #                       Updating suggestLabels (text of what model thinks)

def modelPredict():
    #Takes in imgBatch (next batch of images returned)
    # Creates a prediction on each of the images on the batch and returns the top 5 most likely
    # Puts these top 5 most likely into suggested

def nextBatch():
    # Will use our class we have already created and put our next batch of images into imgBatch
    # Will probably call modelPredict(), and update suggested, suggestButtons, suggestLabels

def returnListener(self):
    text = T.get()
    classify(text)







window = tk.Tk()
window.geometry("700x800")

imageFrame = tk.Frame(master=window, height = 200, width = 500, bg="blue")
textFrame = tk.Frame(master=window, height = 50, width = 500, bg="red")
suggestFrame = tk.Frame(master=window)

imageFrame.pack(fill=tk.X)
textFrame.pack(fill=tk.X)
suggestFrame.pack()

#IMAGE FRAME:
#Centering: https://stackoverflow.com/questions/48930355/center-align-a-group-of-widgets-in-a-frame
index = 0
imgs = []
for img in imgBatch:
    # RIGHT NOW THIS IS REF IMGS BUT CHANGE TO BULK PHOTOS LATER
    image = Image.open(base_path + "Ref Images/" + img + ".bmp")
    image = image.resize((100,100), Image.ANTIALIAS)
    imgs.append(ImageTk.PhotoImage(image))
    imgBox = tk.Button(
        imageFrame,
        image = imgs[index])
    imgBox.pack(side=tk.LEFT)
    index += 1


#TEXT ENTRY FRAME
T = tk.Entry(
    textFrame,
    font = ('calibre',30,'normal'))
T.pack()
#T.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
confirm = tk.Button(
    textFrame,
    text="Confirm"
)
confirm.pack(side=tk.RIGHT)
window.bind('<Return>', returnListener)


image1 = Image.open(base_path + "Ref Images/2434.bmp")
image1 = image1.resize((100,100), Image.ANTIALIAS)
testImg = ImageTk.PhotoImage(image1)

#Place our labels
for i in range(5):
    frame = tk.Label(
        master=suggestFrame,
        borderwidth=1,
        text=suggested[i]
    )
    frame.grid(row=i, column=1)
    suggestLabels.append(frame)

# suggestLabels[0]["text"] = "modify first with?"

#Place our buttons
for i in range(5):
    frame = tk.Button(
        master=suggestFrame,
        borderwidth = 1,
        command=partial(classify, suggested[i]),
        image = testImg
    )
    frame.grid(row=i, column=2)
    suggestButtons.append(frame)


window.mainloop()