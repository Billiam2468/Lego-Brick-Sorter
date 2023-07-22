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

from ttkthemes import ThemedTk

# NOTE: UNCOMMENT THIS ON LINUX#
# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
# config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

#window = tk.Tk()
window = ThemedTk(theme="clam")
numTop = 5
window.geometry("700x800")

# Make contained (only need to set the models path):
base_path = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)
base_path = base_path.removesuffix(scriptName)

# Swap batch path to exampleBatches when debugging with premade batches
#batch_path = base_path + "exampleBatches/"
batch_path = "/home/billiam/Documents/Lego_Sorter/CREATED BATCHES/"
output_path = base_path + "organizedBatches/"
ref_path = base_path + "Ref Images/"

# Upon receiving a new batch of images, we will update these buttons (images) and labels (piece name) for the model suggestions
suggestButtons = []
suggestLabels = []
batchButtons = []
currBatch = []

# Stores images displayed in batch
batchImgs = []
predictedImgs = []

batchProcessor = batch.BatchProcessor(batch_path)
model = tf.keras.models.load_model(base_path + "syntheticTrainedModel1593Classes.h5")
#model.summary()

file = open(base_path + "finalPieceList.txt")
pieceList = [line.rstrip("\n") for line in file.readlines()]

#DEFINE FUNCTIONS HERE:

# This function is called after you either click on one of the suggested labels or type and enter a valid piece number
# Moves the current batch of images to a corresponding folder, clears the text box, and brings in new batch images and adds the predictions
def classify(entry):
    global pieceList
    global batchProcessor
    global currBatch
    T.delete(0, tk.END)
    if (entry not in pieceList) and (entry != "first") and (entry != "junk"):
        print(entry + " not in list")
        return

    # Move images to correct folder
    if entry != "first":
        prevBatch = currBatch
        moveBatch(prevBatch, entry)

    # Grab the batch and add it to the image gallery
    batch = batchProcessor.nextBatch()
    currBatch = batch
    if(len(batch) == 0):
        #If run out of batches, then end the program maybe?
        print("no more batches")

        # Delete all of the old images
        for widget in imageFrame.winfo_children():
            widget.destroy()
        return
    addBatch(batch)
    addPredictions(batch)

# Moves the images to the folder in which it was classified
def moveBatch(batch, pieceName):
    if not os.path.exists(output_path + pieceName):
        os.makedirs(output_path + pieceName)
    for img in batch:
        shutil.move(batch_path+img, output_path + pieceName + "/" +img)

# Takes a list of images (batch), removes the current displayed batch, and displays the new batch
def addBatch(batch):
    global batchButtons
    global batchImgs
    batchButtons = []
    batchImgs = []

    # Delete all of the old images
    for widget in canvas.winfo_children():
        widget.destroy()

    each_width = 150

    # Create a frame inside the canvas to hold the images
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    index = 0
    for img in batch:
        image = Image.open(batch_path + img)
        image.thumbnail((each_width, each_width), Image.Resampling.LANCZOS)
        newImg = ImageTk.PhotoImage(image)
        batchImgs.append(newImg)
        imgBox = tk.Button(
            frame,  # Add the buttons to the frame instead of directly to the canvas
            image=batchImgs[index],
            command=partial(removeBatch, index)
        )
        imgBox.grid(row=0, column=index)
        batchButtons.append(imgBox)
        index += 1

    # Update the scrollable region to fit all images
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# This functions removes the clicked batch image from the batch
def removeBatch(index):
    global currBatch
    global batchButtons
    global batchImgs
    
    #print("currBatch is ", currBatch)
    #print("removing img at index:", index)
    thisBatch = currBatch[index]
    del currBatch[index]
    # When we delete our piece it would be nice if we could move it to a junk folder
    #print("currBatch after deletion is:", currBatch)

    shutil.move(batch_path+thisBatch, output_path + "junk/" + thisBatch)


    if len(currBatch) == 0:
        batch = batchProcessor.nextBatch()
        currBatch = batch
        addBatch(currBatch)
        addPredictions(currBatch)
    else:
        addBatch(currBatch)
    # Only have to update currBatch and then re-call addBatch()




# First check if val in textbox is valid. IF not, display msg asking to try again somehow?
# Then move images into folder (or create and move if not exist)
# Then get next batch of images
#   Next batch entails: Updating suggested (what our model thinks the batch is)
#                       Updating suggestButtons (image of model idea)
#                       Updating suggestLabels (text of what model thinks)

# Gets predictions from the model and formats the recommendation panel accordingly
def addPredictions(batch):
    global suggestLabels
    global suggestButtons
    global predictedImgs
    predictedImgs = []
    predictions = modelPredict(batch)

    index = 0
    for prediction in predictions:
        img = Image.open(ref_path + prediction + ".bmp")
        img.thumbnail((150, 150), Image.Resampling.LANCZOS)
        testImg = ImageTk.PhotoImage(img)
        predictedImgs.append(testImg)
        suggestLabels[index]["text"] = prediction
        suggestButtons[index]["image"] = predictedImgs[index]
        suggestButtons[index]["command"] = partial(classify, prediction)
        index += 1

# Takes in batch and returns the top 5 most likely predictions
# Takes in imgBatch (next batch of images returned)
# Creates a prediction on each of the images on the batch and returns the top 5 most likely
# Puts these top 5 most likely into suggested
def modelPredict(batch):
    #Our list of all of the possible pieces
    global pieceList
    global model

    probDict = {}

    # For each img in the batch, we are going to grab the top 5 predictions for the image by the model, and then add it to a dictionary that adds up the percentages
    # Do not need to pre-process the image to be predicted as it becomes integrated into the model layers
    for img in batch:
        #print("reading image", img)
        loaded = tf.keras.utils.load_img(
                batch_path + img, target_size=(224, 224)
        )
        img_array = tf.keras.utils.img_to_array(loaded)
        img_array = tf.expand_dims(img_array, 0)
        predictions = model.predict(img_array)
        prediction_probabilities = tf.math.top_k(predictions, k=numTop)

        # The model will predict the top 5 possible pieces that it thinks it could be
        # top_5_scores will return the probabilities of the top 5 scores
        # top_5_indices will return the matching index of the type of piece that it predicts
        top_5_scores = prediction_probabilities.values.numpy()
        top_5_indices = prediction_probabilities.indices.numpy()

        top5 = []
        for rank in top_5_indices[0]:
            pieceName = pieceList[rank]
            top5.append(pieceName)
        #print("top 5 pieces are" , top5)
        #print("top 5 scores are ", top_5_scores)
        #print("\n")
        # Iterate through each of the top 5 scores and add them to a dictionary that keeps track of our probabilities
        for index in range(numTop):
            indexToAdd = top_5_indices[0][index]
            if indexToAdd in probDict:
                probDict[indexToAdd] = probDict[indexToAdd] + top_5_scores[0][index]
            else:
                probDict[indexToAdd] = top_5_scores[0][index]

    # Sort the dict (in form: indexOfPiece : sumOfProbabilities)
    sortedDict = {k: v for k, v in sorted(probDict.items(), reverse=True, key=lambda item: item[1])}

    imgBatch = []
    index = 0
    for k, v in sortedDict.items():
        if index < numTop:
            imgBatch.append(pieceList[k])
            index += 1
        else:
            break
    return imgBatch


# Listener that calls classify on the batch using the text in the text box when enter key pressed
def returnListener(self):
    print("pressed enter")
    text = T.get()
    classify(text)
    # Update the scrollable region after classifying
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Listener that calls classify on the batch using the text in the text box when button is pressed
def buttonListener():
    text = T.get()
    classify(text)



#Creating all of the frames and windows here


#imageFrame = tk.Frame(master=window, height = 200, width = 500, bg="blue")
# Creating a canvas widget with a horizontal scrollbar
canvas = tk.Canvas(window, height=200, width=500, bg="blue")
scrollbar = tk.Scrollbar(window, orient="horizontal", command=canvas.xview)
canvas.config(xscrollcommand=scrollbar.set)

canvas.pack(side=tk.TOP, fill=tk.X)
scrollbar.pack(side=tk.TOP, fill=tk.X)
# canvas.place(x=0, y=0, relwidth=1, height=200)
# scrollbar.place(x=0, y=200, relwidth=1, height=20)

textFrame = tk.Frame(master=window, height = 50, width = 500, bg="red")
suggestFrame = tk.Frame(master=window)

# THESE CHANGE DEPENDING ON WHETHER YOU ARE LINUX OR MAC/WINDOWS

# MAC/WINDOWS:
# def on_mousewheel(event):
#     # Determine the scrolling direction and amount
#     print("scrolling here")
#     if event.delta > 0:
#         direction = -1  # Scrolling to the left
#     else:
#         direction = 1   # Scrolling to the right

#     # Update the horizontal scrollbar's position based on the scrolling direction
#     canvas.xview_scroll(direction, "units")

# # Bind the mouse wheel event to the canvas
# canvas.bind("<MouseWheel>", on_mousewheel)

# LINUX:
def on_mousewheel_up(event):
    # Determine the scrolling direction and amount
    canvas.xview_scroll(-1, "units")
def on_mousewheel_down(event):
    # Determine the scrolling direction and amount
    canvas.xview_scroll(1, "units")

# Bind the mouse wheel event to the canvas
canvas.bind("<Button-4>", on_mousewheel_up)
canvas.bind("<Button-5>", on_mousewheel_down)



textFrame.pack(fill=tk.X)
suggestFrame.pack()

#TEXT ENTRY FRAME
T = tk.Entry(
    textFrame,
    font = ('calibre',30,'normal'))
T.pack()

#BUTTON FRAME
confirm = tk.Button(
    textFrame,
    text="Confirm",
    command=buttonListener
)
confirm.pack(side=tk.RIGHT)
window.bind('<Return>', returnListener)

#Place our labels
for i in range(5):
    frame = tk.Label(
        master=suggestFrame,
        borderwidth=1
    )
    frame.grid(row=i, column=1)
    suggestLabels.append(frame)

#Place our buttons
for i in range(5):
    frame = tk.Button(
        master=suggestFrame,
        borderwidth = 1
    )
    frame.grid(row=i, column=2)
    suggestButtons.append(frame)


window.update_idletasks()
classify("first")

window.mainloop()