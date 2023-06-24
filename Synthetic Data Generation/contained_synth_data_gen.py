# RUNNING THIS SCRIPT (Make sure in Blender folder)
# ./blender -b --python /home/billiam/Documents/Lego_Sorter/synthetic_data_gen.py -- pieceToRender.dat

# THE BLENDER DEBUGGING TOOL:
# raise KeyboardInterrupt()

#Adding module path:


import bpy
import os
import sys

#Adding module filepath
#sys.path.append("C:\\users\\seung\\appdata\\roaming\\python\\python310\\site-packages\\")

import random
from random import uniform
import math
from math import inf
from mathutils.geometry import intersect_line_plane as ilp
from mathutils import Vector
import matplotlib.path as mplPath
import numpy as np
import time
import sys
from pandas import *
import colorsys
import os.path
from PIL import ImageColor
from tqdm import tqdm

sys.stdout = sys.stderr #For print statements only

#Discord Bot!
from tqdm.contrib.discord import tqdm, trange

#Firebase Database
import firebase_admin
from firebase_admin import db

# Global Variables
cam = None
light = None
currentModel = None
num_generate = 1000 #Number of images to generate
renderResolution = 600
cameraAngleOfView = 64.8 #Degrees from vertical of the top plane of the cameras view
dropHeight = 4 #Height (m) in which to drop the Lego piece
frameStart = 1
frameEnd = 25 #Frame on which the drop simulation ends
padding = 0.01
# For plane of cam
plane_co = (0, 0, 0)
plane_no = (0, 0, 1)
context = bpy.context
scene = context.scene
colorLibrary = []

scene.cycles.device = "GPU"
#scene.cycles.use_denoising = False
scene.cycles.adaptive_threshold = 0.1 # Increasing noise threshold
scene.cycles.samples = 500 # Decreasing number of samples from 4096 to increase render times
scene.gravity[2] = -75

# Make contained (only need to set the models path):
base_path = os.path.realpath(__file__)
scriptName = os.path.basename(__file__)
base_path = base_path.removesuffix(scriptName)

#Import Textures and Model References (Mac or Linux)
material_path = base_path + "paper_texture.blend"
models_path = "/home/billiam/Documents/Lego_Sorter/LDraw Files/complete/ldraw/parts/"
render_path = base_path + "Renders/"

with bpy.data.libraries.load(material_path) as (data_from, data_to):
    data_to.materials = data_from.materials
paper_texture = data_to.materials[0]

#Database Access:
cred_obj = firebase_admin.credentials.Certificate(base_path + "firebaseKey.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    "databaseURL":"https://lego-brick-sorter-default-rtdb.firebaseio.com/"
})
ref = db.reference("/")


# Execute
def execute():
    startTime = time.perf_counter()
    
    
    global currentModel
    global colorLibrary

    # Objects to render
    file = open(base_path + "pieces.txt")
    pieceList = [line.rstrip("\n") for line in file.readlines()]

    for model in tqdm(pieceList,
                      token ='MTA4MjIxMjY4NDc0Njk5MzY4NQ.Gp8hFW.L67JvpL3hFSmZmF3xY8QhX8e5dGWy96vVCOU5M',
                      channel_id='1082212254688235612',
                      miniters=50):
        #Models to test:
        # u9132c05.dat (1: EMPTY, 2: EMPTY WITH MESHES INSIDE, MESH, MESH)
        # 73587po4.dat (1: EMPTY, 2: MESH, MESH)
        # 54696p01c01.dat (1: EMPTY, 2: MESH, MESH WITH MESHES INSIDE, MESH WITH MESHES INSIDE)
        
        #model = "u9328.dat"
        
        #Check if model not in database and not in blacklist
        model = model + ".dat"
        if(model not in os.listdir(models_path)):
            continue

        pieceName = model[:-4]
        pieces = ref.order_by_key().get()
        
        with open(base_path + "blacklist.txt") as f:
            if (pieceName not in pieces) and (pieceName not in f.read()):
                ref.update({
                    pieceName:False
                })

                currentModel = importModel(model) 

                if(currentModel.type == "EMPTY" and (len(currentModel.children) == 0)):
                    #print("skipping")
                    continue
                #joinMeshes(currentModel)

                # Save state of the model
                ogPos = currentModel.location
                ogRotation = currentModel.rotation_euler

                if not os.path.exists(render_path + model[:-4]):
                    os.makedirs(render_path + model[:-4])
                for iteration in range(num_generate):
                    random.seed()
                    random.shuffle(colorLibrary)
                    frame = getCamView()
                    placePiece(frame)
                    
                    renderPiece(render_path + model[:-4], iteration)
                removeModel()
                ref.update({
                    pieceName:False
                })

    endTime = time.perf_counter()
    print(f"Finished render in {endTime - startTime:0.4f} seconds")

# Render Scene
def renderPiece(final_path, num):
    global currentModel
    nameCut = currentModel.name[6:].removesuffix('.dat')
    bpy.context.scene.render.filepath = os.path.join(final_path, nameCut + "_" + str(num)) #to get unique file names will have to fix this one

    # Object square bounding box to render piece
    x, y, width, height = camera_view_bounds_2d(scene, cam, currentModel)
    if width > height:
        height = width
    else:
        width = height
    bpy.context.scene.render.use_border = True
    bpy.context.scene.render.use_crop_to_border = True

    # Borders are a percentage of the resolution
    scene.render.border_max_y = (1 - ((y + height)/renderResolution)) + (height/renderResolution) + (padding)
    scene.render.border_min_y = 1 - ((y + height)/renderResolution) - (padding)
    scene.render.border_max_x = ((x + width)/renderResolution) + (padding)
    scene.render.border_min_x = (x/renderResolution) - (padding)
    bpy.ops.render.render(write_still = True)

# 2D Bounding box of piece for border rendering
def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def camera_view_bounds_2d(scene, cam_ob, me_ob):
    """
    Returns camera space bounding box of mesh object.

    Negative 'z' value means the point is behind the camera.

    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.

    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg me: Untransformed Mesh.
    :type me: :class:`bpy.types.Mesh´
    :return: a Box object (call its to_tuple() method to get x, y, width and height)
    :rtype: :class:`Box`
    """
    
    me_ob = getMeshes(me_ob)[0]

    # NOTE: OLD
    # # First join the meshes
    # bpy.ops.object.select_all(action='DESELECT')
    # first = True
    # if(me_ob.type == "EMPTY"):
    #     for children in me_ob.children:
    #         if(first):
    #             bpy.context.view_layer.objects.active = children
    #             first = False
    #         children.select_set(True)
    # bpy.ops.object.join()

    # me_ob = bpy.context.view_layer.objects.active


    mat = cam_ob.matrix_world.normalized().inverted()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh_eval = me_ob.evaluated_get(depsgraph)
    me = mesh_eval.to_mesh()
    me.transform(me_ob.matrix_world)
    me.transform(mat)

    camera = cam_ob.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    camera_persp = camera.type != 'ORTHO'

    lx = []
    ly = []

    for v in me.vertices:
        co_local = v.co
        z = -co_local.z

        if camera_persp:
            if z == 0.0:
                lx.append(0.5)
                ly.append(0.5)
            else:
                frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    min_x = clamp(min(lx), 0.0, 1.0)
    max_x = clamp(max(lx), 0.0, 1.0)
    min_y = clamp(min(ly), 0.0, 1.0)
    max_y = clamp(max(ly), 0.0, 1.0)

    mesh_eval.to_mesh_clear()

    r = scene.render
    fac = r.resolution_percentage * 0.01
    dim_x = r.resolution_x * fac
    dim_y = r.resolution_y * fac

    # # Separate the meshes:
    # bpy.ops.object.select_all(action='DESELECT')
    # me_ob.select_set(True)
    # bpy.ops.mesh.separate(type='MATERIAL')
    
    # Sanity check
    if round((max_x - min_x) * dim_x) == 0 or round((max_y - min_y) * dim_y) == 0:
        return (0, 0, 0, 0)

    return (
        round(min_x * dim_x),            # X
        round(dim_y - max_y * dim_y),    # Y
        round((max_x - min_x) * dim_x),  # Width
        round((max_y - min_y) * dim_y)   # Height
    )

# Join all the meshes in a multipart object and returns main mesh:
def joinMeshes(model):
    global currentModel
    allMeshes = getMeshes(model)
    bpy.ops.object.select_all(action='DESELECT')
    for mesh in allMeshes:
        mesh.select_set(True)
    bpy.context.view_layer.objects.active = allMeshes[0]
    bpy.ops.object.join()

    # Attempting to remove all parents of mesh
    trueName = model.name
    bpy.ops.object.select_all(action='DESELECT')
    allMeshes[0].select_set(True)
    bpy.ops.object.parent_clear(type='CLEAR')
    
    #raise KeyboardInterrupt()

    if not (allMeshes[0].name == trueName):
        modelSkeleton = selectMeshes(model)
        bpy.ops.object.select_all(action='DESELECT')
        for mod in modelSkeleton:
            mod.select_set(True)
        bpy.ops.object.delete()


    allMeshes[0].name = trueName
    currentModel = allMeshes[0]

    return(allMeshes[0])

# Get all meshes that have information:
# Will use recursion here to obtain all of the different mesh objects and put them into one list that other functions can use
def getMeshes(model):
    allMeshObjects = []
    if(model.type == "MESH"):
        allMeshObjects.append(model)
    for children in model.children:
        allMeshObjects += getMeshes(children)
    return allMeshObjects
        
#Select all meshes including those empty NONE meshes:
def selectMeshes(model):
    allMeshObjects = []
    allMeshObjects.append(model)
    for children in model.children:
        allMeshObjects += selectMeshes(children)
    return allMeshObjects


# Randomize light placement and power
def randomLight(minY, maxY):
    global light
    light.data.energy = uniform(500, 1000)
    yLoc = uniform(minY, maxY)
    light.location.y = yLoc

# Randomize the color of the piece and paper plane
# NOTE: Something up with the randomization of the colors. All of them are pink/pastel and don't get any dark colors.
# Tried using color library but was still all the same types of colors. Will have to look into making random really random
def randomColor(model):
    trueModels = getMeshes(model)
    for meshObject in trueModels:
        bpy.ops.object.select_all(action='DESELECT')
        meshObject.select_set(True)
        for key,val in meshObject.data.materials.items():
            random.seed()
            color = (random.random(), random.random(), random.random(), 1)
            bpy.data.materials[str(key)].node_tree.nodes["Group"].inputs[0].default_value = color

    #NOTE: OLD    
    # trueModels = []
    # if(model.type == "EMPTY"):
    #     for children in model.children:
    #         trueModels.append(children)
    # else:
    #     trueModels.append(model)

    # for meshObject in trueModels:
    #     bpy.ops.object.select_all(action='DESELECT')
    #     meshObject.select_set(True)
    #     color = (random.random(), random.random(), random.random(), 1)
    #     bpy.data.materials["Material_4_c"].node_tree.nodes["Group"].inputs[0].default_value = color



    random.seed()
    bpy.ops.object.select_all(action='DESELECT')
    plane = bpy.context.scene.objects.get("paper")
    plane.select_set(True)
    color1 = (random.random(), random.random(), random.random(), 1)
    random.seed()
    color2 = (random.random(), random.random(), random.random(), 1)
    bpy.data.materials["paper_texture"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].color = color1
    bpy.data.materials["paper_texture"].node_tree.nodes["ColorRamp"].color_ramp.elements[1].color = color2

# Drop Piece
# NOTE: might have to vary the height in which its dropped as pieces like 3004 will almost always land on their side at this height
def dropPiece(model, startLocationX, startLocationY):
    scene.rigidbody_world.enabled = True
    scene.frame_set(1)
    bpy.ops.ptcache.free_bake_all()
    model.rotation_euler = (uniform(0, 2 * math.pi), uniform(0, 2 * math.pi), uniform(0, 2 * math.pi))
    bpy.context.view_layer.update()

    height = getHighestPoint(model) - model.matrix_world.translation.z

    model.location = (startLocationX, startLocationY, height * 2)

    rbw = scene.rigidbody_world
    pc = rbw.point_cache
    pc.frame_start = frameStart
    pc.frame_end = frameEnd

    #bpy.ops.ptcache.bake({"point_cache": pc}, bake=True)
    bpy.ops.ptcache.bake_all(bake=True)
    scene.frame_set(frameEnd)
    
    
    bpy.ops.object.select_all(action='DESELECT')
    model.select_set(True)
    bpy.ops.object.visual_transform_apply()
    bpy.ops.ptcache.free_bake_all()
    
    

    #Update the location of the potentially parent body:
    if model.type == "EMPTY":
        meshObject = getMeshes(model)
        model.location = meshObject[0].matrix_world.translation
        
        model.rotation_euler = meshObject[0].matrix_world.to_euler('XYZ')
        bpy.ops.object.visual_transform_apply()
    #raise KeyboardInterrupt()
    scene.rigidbody_world.enabled = False
    
    



# Place piece with random position + rotation but within the frame of the camera
# 2/28 NOTE: DUE TO THE POSITION OF THE CAMERA, THE DISTRIBUTION OF THE PIECES IS TERRIBLE (ONLY FAR AWAY AND CLOSE)
# THE RANGE OF Y VALUES INBETWEEN THE TWO EXTREMES IS VERY SMALL. WILL NEED TO THINK OF A SOLUTION TO THIS
# RANDOM TRANSFORMATIONS: WILL HAVE TO FIGURE OUT PIECE ON SIDES AS WELL
# WILL WANT TO VARY PIECE COLOR AS WELL AS LIGHTING CONDITIONS (I think power should definitely be upped)

def placePiece(frame):
    global currentModel

    # Get camera bounding box
    camTopLeft = frame[1]
    camTopRight = frame[3]
    camBotLeft = frame[0]
    camBotRight = frame[2]

    # Calculate the maximum y distance from the camera that a piece of modelHeight can be placed
    modelHeight = getHighestPoint(currentModel)
    maxDistanceFromCam = getCamMaxDistance(modelHeight)
    maxY = cam.location.y + maxDistanceFromCam

    # Calculate the x camera view width due to the y changes
    maxXDeviation = camBotRight[0] + ((camTopRight[0]-camBotRight[0]) * (maxY - camBotLeft[1]))/(camTopRight[1] - camBotRight[1])

    # Adjust camera bounding box (changes in Y will mean changes in x as well)
    camTopRight[1] = maxY
    camTopLeft[1] = maxY
    camTopRight[0] = maxXDeviation
    camTopLeft[0] = -maxXDeviation

    # Calculate the max deviation from the center for random transformations
    maxYDeviation= (camTopLeft[1] - camBotLeft[1])/2

    # Randomly decide light and color
    randomLight(camBotLeft[1], maxY)
    randomColor(currentModel)

    # Move model to center of Y deviation to allow for better random transformation distribution
    xStart = 0
    yStart = camTopLeft[1] - maxYDeviation
    # Drop a piece at the "center" defined by xStart and yStart (this will get our random rotation)
    dropPiece(currentModel, xStart, yStart)

    # PLACE PIECE RANDOMLY INSIDE USING RANDOMIZE TRANSFORM AND CHECK IF WITHIN BOUNDS OF PLANE
    notInside = True
    numTries = 0
    while(notInside):
        #print("attempting to place " + str(numTries))

        # Move dropped piece back to the center
        currentModel.location.x = xStart
        currentModel.location.y = yStart

        # Apply random x and y transformations to the piece
        bpy.ops.object.select_all(action='DESELECT')
        currentModel.select_set(True)
        bpy.ops.object.randomize_transform(random_seed=random.randint(0,1000), use_loc=True, loc=(maxXDeviation,maxYDeviation,0))
        bpy.context.view_layer.update()

        # Calculate the footprint of the piece, and check if it inside the bounding box of the camera, if not, transform again from the center
        pieceFootprint = getFootprint(currentModel)
        
        camBoundingBoxPoints = np.array([[camTopLeft[0],camTopLeft[1]],[camTopRight[0],camTopRight[1]],[camBotLeft[0],camBotLeft[1]],[camBotRight[0],camBotRight[1]]])

        notInside = not contains(pieceFootprint, camBoundingBoxPoints)
        numTries += 1
        if(numTries > 15):
            currentModel.location.x = 0
            currentModel.location.y = 0
            break

# Returns true if all points in array x are inside polygon outlined by array y
def contains(x, y):
    boundingBoxPath = mplPath.Path(y)
    r = 0.001
    numInside = 0
    for corner in x:
        if boundingBoxPath.contains_point(corner, radius=r):
            numInside += 1
    if numInside == 4:
        return True
    else:
        return False

# Gets footprint of model passed in
def getFootprint(model):
    bb_vertices = [model.matrix_world @ Vector(bbvert) for bbvert in model.bound_box]

    sortedByZ = sorted(bb_vertices, key=lambda d: d[2])
    pieceFootprint = sortedByZ[:4]
    #print(pieceFootprint)
    pieceFootprint = flatten(pieceFootprint)
    return pieceFootprint

# Flattens 3D vectors into 2D footprint
def flatten(array):
    flattenedVectors = []
    for vector in array:
        point = (vector[0], vector[1])
        flattenedVectors.append(point)
    return flattenedVectors


# Returns the highest point of the model
def getHighestPoint(model):
    z_coords = []
    maxZ = -1000000
    for coord in model.bound_box:
        worldCoord = model.matrix_world @ Vector( (coord[0], coord[1], coord[2]))
        maxZ = max(maxZ, worldCoord.z)
    return maxZ

# Returns the max distance from the camera where the height of the piece will not be cut off
def getCamMaxDistance(modelHeight):
    global cam
    camHeight = cam.location.z
    distance = (math.tan(math.radians(cameraAngleOfView))) * (camHeight - modelHeight)
    return distance

# Returns the points on the plane where the camera view intersects (this is where we will place our model)
def getCamView():
    global cam
    coords = []
    mw = cam.matrix_world
    o = mw.translation
    camdata = cam.data

    tr, br, bl, tl = [mw @ f for f in camdata.view_frame(scene=scene)]
    x = tr - tl
    y = tr - br
    for image_coord in ((0, 0), (0, 1), (1, 0), (1, 1)):
        cx, cy = image_coord
        v = (bl + (cx * x + cy * y)) - o
        pt = ilp(o, o + v, plane_co, plane_no, True)
        coords.append(pt)
    return coords

# Import Model
def importModel(model_path):
    path = os.path.join(models_path, model_path)
    bpy.ops.import_scene.importldraw(filepath=path)
    current_name = bpy.context.selected_objects[0].name

    theModel = bpy.data.objects[current_name]

    #Add model to rigidbody

    #SKIP IF TYPE IS EMPTY
    if(theModel.type == "EMPTY" and (len(theModel.children) == 0)):
        return(theModel)

    theModel = joinMeshes(theModel)

    bpy.ops.object.select_all(action='DESELECT')
    theModel.select_set(True)
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = 'ACTIVE'
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')

    return(theModel)

# Remove Model
def removeModel():
    global currentModel
    trueModels = selectMeshes(currentModel)

    bpy.ops.object.select_all(action='DESELECT')
    for modelMesh in trueModels:
        modelMesh.select_set(True)

    #NOTE: OLD
    # bpy.ops.object.select_all(action='DESELECT')
    # currentModel.select_set(True)
    
    bpy.ops.object.delete()

# Scene Set Up
def setUpScene():
    # Set Render Scenes
    scene = bpy.data.scenes['Scene']
    scene.render.resolution_x = renderResolution
    scene.render.resolution_y = renderResolution
    scene.render.image_settings.color_mode = 'RGB'
    bpy.context.scene.frame_end = frameEnd

    # Deselect all, select cube, then delete
    bpy.ops.object.select_all(action='DESELECT')
    cube = bpy.context.scene.objects.get("Cube")
    if cube:
        bpy.data.objects['Cube'].select_set(True)
        bpy.ops.object.delete()

    # Creating references to cam and light (Global defined so that cam and light global variables referenced)
    global cam
    global light
    cam = bpy.data.objects['Camera']
    light = bpy.data.objects['Light']

    # Set light settings
    light.data.type = 'POINT'
    light.data.energy = 100
    light.location = (0, 0, 5)
    light.rotation_euler = (0, 0, 0)

    # Set camera settings
    cam.location = (0, -5, 5)
    cam.rotation_euler = (0.785398, 0, 0)

    # Create a plane
    bpy.ops.object.select_all(action='DESELECT')
    oldPlane = bpy.context.scene.objects.get("Plane")
    if oldPlane:
        bpy.data.objects['Plane'].select_set(True)
        bpy.ops.object.delete()

    bpy.ops.mesh.primitive_plane_add(
        size = 15,
        calc_uvs = True,
        align = 'WORLD',
        enter_editmode=False,
        location = (0, 0, 0),
        rotation = (0, 0, 0),
        scale = (0, 0, 0))
    current_name = bpy.context.selected_objects[0].name
    plane = bpy.data.objects[current_name]
    plane.name = "paper"
    plane.data.name = "paper_mesh"

    #Add solidifier to plane
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    bpy.context.object.modifiers["Solidify"].thickness = 0.5

    #Add plane to rigidbody
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = 'PASSIVE'
    bpy.context.object.rigid_body.friction = 1

    if (len(plane.data.materials.items()) != 0):
        plane.data.materials.clear()
    else:
        plane.data.materials.append(paper_texture)

# def getAxisOrientedBoundingBox(footPrint):
#     footprint_left = 999999
#     footprint_right = -999999
#     footprint_bot = 999999
#     footprint_top = -999999
#     for foot in footPrint:
#         if foot[0] > footprint_right:
#             footprint_right = foot[0]
#         if foot[0] < footprint_left:
#             footprint_left = foot[0]
#         if foot[1] < footprint_bot:
#             footprint_bot = foot[1]
#         if foot[1] > footprint_top:
#             footprint_top = foot[1]
#     return [footprint_left, footprint_right, footprint_bot, footprint_top]

# Main function
def main():
    setUpScene()
    execute()

# Call main function
if __name__ == "__main__":
    main()

# What will design of this function look like
# Iterate over all files referenced in a text file for model names and 