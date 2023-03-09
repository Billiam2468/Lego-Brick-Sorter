import tkinter as tk
from functools import partial
from PIL import ImageTk, Image
import os  
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import batchProcessor as batch
import shutil
import tensorflow as tf
from tensorflow import keras

physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

window = tk.Tk()
window.geometry("700x800")

# Make contained (only need to set the models path):
base_path = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)
base_path = base_path.removesuffix(scriptName)

batch_path = base_path + "exampleBatches/"
output_path = base_path + "organizedBatches/"
#ref_path = base_path + "Ref Images/"
ref_path = "/home/billiam/Documents/Lego_Sorter/LEGO_BRICK_LABELS/LEGO_BRICK_LABELS-v39/Labels/Piece Images/"


# This will be a list of the model suggested labels. The index chosen will be returned from choose()
# These will be different pieces since different guesses
suggested = []#["test", "val", "here", "last", "one"]

# Batch of images to be displayed (should be same piee)
imgBatch = []#["3184", "3070b", "3149", "3176"]

# Upon receiving a new batch of images, we will update these buttons (images) and labels (piece name) for the model suggestions
suggestButtons = []
suggestLabels = []

# Stores images displayed in batch
batchImgs = []
predictedImgs = []

batchProcessor = batch.BatchProcessor(batch_path)
model = tf.keras.models.load_model(base_path + "testModel.h5")

file = open(base_path + "pieces.txt")
pieceList = [line.rstrip("\n") for line in file.readlines()]

#DEFINE FUNCTIONS HERE:
def classify(entry):
    global pieceList
    global batchProcessor
    T.delete(0, tk.END)
    if (entry not in pieceList) and (entry != "first"):
        print(entry + " not in list")
        return

    # Move images to correct folder
    if entry != "first":
        prevBatch = batchProcessor.currentBatch
        moveBatch(prevBatch, entry)

    # Grab the batch and add it to the image gallery
    batch = batchProcessor.nextBatch()
    if(len(batch) == 0):
        #If run out of batches, then end the program maybe?
        print("no more batches")
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
    #Delete all of the old images
    for widget in imageFrame.winfo_children():
        widget.destroy()
    global batchImgs
    batchImgs = []
    index = 0
    for img in batch:
        image = Image.open(batch_path + img)
        image.thumbnail((150,150), Image.ANTIALIAS)
        newImg = ImageTk.PhotoImage(image)
        batchImgs.append(newImg)
        imgBox = tk.Button(
            imageFrame,
            image = batchImgs[index])
        imgBox.pack(side=tk.LEFT)
        index += 1


    # First check if val in textbox is valid. IF not, display msg asking to try again somehow?
    # Then move images into folder (or createand move if not exist)
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

    # image1 = Image.open(base_path + "Ref Images/2434.bmp")
    # image1 = image1.resize((100,100), Image.ANTIALIAS)
    # testImg = ImageTk.PhotoImage(image1)

    index = 0
    for prediction in predictions:
        img = Image.open(ref_path + prediction + ".bmp")
        img.thumbnail((150, 150), Image.ANTIALIAS)
        testImg = ImageTk.PhotoImage(img)
        predictedImgs.append(testImg)
        suggestLabels[index]["text"] = prediction
        suggestButtons[index]["image"] = predictedImgs[index]
        suggestButtons[index]["command"] = partial(classify, "classify as" + prediction)
        index += 1

# Takes in batch and returns the top 5 most likely predictions
def modelPredict(batch):
    #Our list of all of the possible pieces
    global pieceList
    global model

    probDict = {}

    # Do not need to pre-process the image to be predicted as it becomes integrated into the model layers
    for img in batch:
        print("reading image", img)
        loaded = tf.keras.utils.load_img(
                batch_path + img, target_size=(224, 224)
        )
        img_array = tf.keras.utils.img_to_array(loaded)
        img_array = tf.expand_dims(img_array, 0)
        predictions = model.predict(img_array)
        prediction_probabilities = tf.math.top_k(predictions, k=4)
        top_5_scores = prediction_probabilities.values.numpy()
        top_5_indices = prediction_probabilities.indices.numpy()
        for index in range(4):
            indexToAdd = top_5_indices[0][index]
            if indexToAdd in probDict:
                probDict[indexToAdd] = probDict[indexToAdd] + top_5_scores[0][index]
            else:
                probDict[indexToAdd] = top_5_scores[0][index]

    sortedDict = sorted(probDict,reverse=True)

    print(sortedDict)
    
    #NOTE: For 3.9.2023:
    # Sorted dict returns the top predicted indices
    # Use these indices in the list of our pieces to get a number to add to our return

    imgBatch = []

    for index in sortedDict:
        imgBatch.append(pieceList[index])

    # # use our model here and predict the top 5 and return an ordered list of the predictions
    # imgBatch = ["3184", "3070b", "3149", "3176", "3185"]
    return imgBatch
    #Takes in imgBatch (next batch of images returned)
    # Creates a prediction on each of the images on the batch and returns the top 5 most likely
    # Puts these top 5 most likely into suggested

def returnListener(self):
    text = T.get()
    classify(text)

def buttonListener():
    text = T.get()
    classify(text)







imageFrame = tk.Frame(master=window, height = 200, width = 500, bg="blue")
textFrame = tk.Frame(master=window, height = 50, width = 500, bg="red")
suggestFrame = tk.Frame(master=window)

imageFrame.pack(fill=tk.X)
textFrame.pack(fill=tk.X)
suggestFrame.pack()

#IMAGE FRAME:
#Centering: https://stackoverflow.com/questions/48930355/center-align-a-group-of-widgets-in-a-frame
# index = 0
# for img in imgBatch:
#     # RIGHT NOW THIS IS REF IMGS BUT CHANGE TO BULK PHOTOS LATER
#     # image = Image.open(base_path + "Ref Images/" + img + ".bmp")
#     # image = image.resize((100,100), Image.ANTIALIAS)
#     # imgs.append(ImageTk.PhotoImage(image))
#     imgBox = tk.Button(
#         imageFrame,
#         image = imgs[index])
#     imgBox.pack(side=tk.LEFT)
#     index += 1


#TEXT ENTRY FRAME
T = tk.Entry(
    textFrame,
    font = ('calibre',30,'normal'))
T.pack()
#T.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
confirm = tk.Button(
    textFrame,
    text="Confirm",
    command=buttonListener
)
confirm.pack(side=tk.RIGHT)
window.bind('<Return>', returnListener)


# image1 = Image.open(base_path + "Ref Images/2434.bmp")
# image1 = image1.resize((100,100), Image.ANTIALIAS)
# testImg = ImageTk.PhotoImage(image1)

#Place our labels
for i in range(5):
    frame = tk.Label(
        master=suggestFrame,
        borderwidth=1
    )
    frame.grid(row=i, column=1)
    suggestLabels.append(frame)

# suggestLabels[0]["text"] = "modify first with?"

#Place our buttons
for i in range(5):
    frame = tk.Button(
        master=suggestFrame,
        borderwidth = 1
        #command=partial(classify, suggested[i])
        #image = testImg
    )
    frame.grid(row=i, column=2)
    suggestButtons.append(frame)

classify("first")

window.mainloop()